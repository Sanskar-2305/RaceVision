"""
RaceVision Driver Comparison

Compares two drivers using the pre-computed lap-time telemetry
already broadcast by the replay server.
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from src.gui.pit_wall_window import PitWallWindow


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def format_lap_time(seconds):
    if seconds is None or seconds <= 0:
        return "--"

    minutes = int(seconds // 60)
    secs = seconds % 60

    return f"{minutes}:{secs:06.3f}"


def format_delta(seconds):
    if seconds is None:
        return "--"

    if abs(seconds) < 0.0005:
        return "0.000s"

    return f"{seconds:+.3f}s"


# ------------------------------------------------------------
# Driver Comparison Window
# ------------------------------------------------------------

class DriverComparisonWindow(PitWallWindow):

    def __init__(self):
        self._lap_times = {}
        self._driver_colors = {}
        self._drivers = []

        super().__init__()

        self.setWindowTitle("RaceVision | Driver Comparison")
        self.setMinimumSize(900, 600)

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title = QLabel("RACEVISION  |  DRIVER COMPARISON")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #E0E0E0;")

        root.addWidget(title)

        subtitle = QLabel(
            "Compare lap pace and tyre usage between two drivers"
        )
        subtitle.setStyleSheet("color: #888888;")

        root.addWidget(subtitle)

        # ----------------------------------------------------
        # Driver selectors
        # ----------------------------------------------------

        selector_row = QHBoxLayout()
        selector_row.setSpacing(10)

        driver1_label = QLabel("Driver 1:")
        driver1_label.setFont(QFont("Arial", 11))

        self.driver1_combo = QComboBox()
        self.driver1_combo.setMinimumWidth(160)
        self.driver1_combo.addItem("Waiting for data...")

        driver2_label = QLabel("Driver 2:")
        driver2_label.setFont(QFont("Arial", 11))

        self.driver2_combo = QComboBox()
        self.driver2_combo.setMinimumWidth(160)
        self.driver2_combo.addItem("Waiting for data...")

        self.driver1_combo.currentTextChanged.connect(
            self._update_comparison
        )

        self.driver2_combo.currentTextChanged.connect(
            self._update_comparison
        )

        selector_row.addWidget(driver1_label)
        selector_row.addWidget(self.driver1_combo)

        selector_row.addSpacing(30)

        selector_row.addWidget(driver2_label)
        selector_row.addWidget(self.driver2_combo)

        selector_row.addStretch()

        root.addLayout(selector_row)

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        self.summary_label = QLabel(
            "Select two drivers to compare."
        )

        self.summary_label.setFont(
            QFont("Arial", 12, QFont.Weight.Bold)
        )

        self.summary_label.setStyleSheet(
            "color: #E0E0E0; padding: 8px;"
        )

        root.addWidget(self.summary_label)

        # ----------------------------------------------------
        # Comparison table
        # ----------------------------------------------------

        self.table = QTableWidget(0, 4)

        self.table.setHorizontalHeaderLabels(
            [
                "Metric",
                "Driver 1",
                "Driver 2",
                "Delta",
            ]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.verticalHeader().setVisible(False)

        self.table.setAlternatingRowColors(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #282828;
                color: #E0E0E0;
                gridline-color: #3A3A3A;
                border: 1px solid #444444;
            }

            QHeaderView::section {
                background-color: #181818;
                color: #E0E0E0;
                padding: 8px;
                border: none;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 8px;
            }

            QTableWidget::item:selected {
                background-color: #3A3A3A;
            }
        """)

        root.addWidget(self.table)

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_label = QLabel("Waiting for telemetry...")
        self.status_label.setStyleSheet(
            "color: #888888;"
        )

        root.addWidget(self.status_label)

    # --------------------------------------------------------
    # Telemetry
    # --------------------------------------------------------

    def on_telemetry_data(self, data):

        # Receive pre-computed lap times
        if "lap_times" in data:
            self._lap_times = data.get("lap_times") or {}

        # Receive driver colours
        if "driver_colors" in data:
            self._driver_colors = (
                data.get("driver_colors") or {}
            )

        frame = data.get("frame") or {}
        drivers = frame.get("drivers") or {}

        if not drivers:
            return

        incoming = sorted(drivers.keys())

        if incoming != self._drivers:
            self._drivers = incoming
            self._refresh_driver_selectors()

        self._update_comparison()

        session_data = data.get("session_data") or {}

        lap = session_data.get("lap", "?")
        total = session_data.get("total_laps", "?")

        self.status_label.setText(
            f"Live telemetry  •  Lap {lap}/{total}"
        )

    # --------------------------------------------------------
    # Driver selector refresh
    # --------------------------------------------------------

    def _refresh_driver_selectors(self):

        current1 = self.driver1_combo.currentText()
        current2 = self.driver2_combo.currentText()

        self.driver1_combo.blockSignals(True)
        self.driver2_combo.blockSignals(True)

        self.driver1_combo.clear()
        self.driver2_combo.clear()

        self.driver1_combo.addItems(self._drivers)
        self.driver2_combo.addItems(self._drivers)

        # Default to first two drivers
        if self._drivers:

            if current1 in self._drivers:
                self.driver1_combo.setCurrentText(current1)
            else:
                self.driver1_combo.setCurrentIndex(0)

        if len(self._drivers) > 1:

            if current2 in self._drivers:
                self.driver2_combo.setCurrentText(current2)
            else:
                self.driver2_combo.setCurrentIndex(1)

        self.driver1_combo.blockSignals(False)
        self.driver2_combo.blockSignals(False)

        self._update_comparison()

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def _get_driver_stats(self, code):

        entries = self._lap_times.get(code) or []

        valid = []

        for entry in entries:

            time_s = entry.get("time_s")

            if not isinstance(time_s, (int, float)):
                continue

            if time_s <= 0:
                continue

            # Ignore obviously invalid laps
            if time_s > 200:
                continue

            valid.append(entry)

        if not valid:
            return {
                "best": None,
                "average": None,
                "last": None,
                "laps": 0,
                "tyre": "--",
            }

        times = [
            float(entry["time_s"])
            for entry in valid
        ]

        best = min(times)
        average = sum(times) / len(times)
        last = times[-1]

        tyre = valid[-1].get("tyre")

        if tyre is None:
            tyre = "--"

        return {
            "best": best,
            "average": average,
            "last": last,
            "laps": len(valid),
            "tyre": str(tyre),
        }

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    def _update_comparison(self):

        if not hasattr(self, "driver1_combo"):
            return

        if not self._drivers:
            return

        d1 = self.driver1_combo.currentText()
        d2 = self.driver2_combo.currentText()

        if d1 not in self._lap_times:
            return

        if d2 not in self._lap_times:
            return

        if d1 == d2:

            self.summary_label.setText(
                "Select two different drivers."
            )

            return

        stats1 = self._get_driver_stats(d1)
        stats2 = self._get_driver_stats(d2)

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        if stats1["best"] and stats2["best"]:

            best_delta = (
                stats1["best"] - stats2["best"]
            )

            if best_delta < 0:
                faster = d1
            else:
                faster = d2

            self.summary_label.setText(
                f"Best lap: {faster} is "
                f"{abs(best_delta):.3f}s faster"
            )

        # ----------------------------------------------------
        # Table
        # ----------------------------------------------------

        rows = [
            (
                "Best Lap",
                stats1["best"],
                stats2["best"],
            ),
            (
                "Average Lap",
                stats1["average"],
                stats2["average"],
            ),
            (
                "Last Recorded Lap",
                stats1["last"],
                stats2["last"],
            ),
        ]

        self.table.setRowCount(len(rows) + 2)

        for row, (label, value1, value2) in enumerate(rows):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(label),
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    format_lap_time(value1)
                ),
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    format_lap_time(value2)
                ),
            )

            delta = None

            if value1 is not None and value2 is not None:
                delta = value1 - value2

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    format_delta(delta)
                ),
            )

        # ----------------------------------------------------
        # Lap count
        # ----------------------------------------------------

        row = 3

        self.table.setItem(
            row,
            0,
            QTableWidgetItem("Recorded Laps"),
        )

        self.table.setItem(
            row,
            1,
            QTableWidgetItem(
                str(stats1["laps"])
            ),
        )

        self.table.setItem(
            row,
            2,
            QTableWidgetItem(
                str(stats2["laps"])
            ),
        )

        self.table.setItem(
            row,
            3,
            QTableWidgetItem("--"),
        )

        # ----------------------------------------------------
        # Current tyre
        # ----------------------------------------------------

        row = 4

        self.table.setItem(
            row,
            0,
            QTableWidgetItem("Latest Tyre"),
        )

        self.table.setItem(
            row,
            1,
            QTableWidgetItem(
                stats1["tyre"]
            ),
        )

        self.table.setItem(
            row,
            2,
            QTableWidgetItem(
                stats2["tyre"]
            ),
        )

        self.table.setItem(
            row,
            3,
            QTableWidgetItem("--"),
        )

        # ----------------------------------------------------
        # Colour driver columns
        # ----------------------------------------------------

        self._apply_driver_color(
            self.table.item(0, 1),
            d1,
        )

        self._apply_driver_color(
            self.table.item(0, 2),
            d2,
        )

    # --------------------------------------------------------
    # Driver colour
    # --------------------------------------------------------

    def _apply_driver_color(self, item, code):

        if item is None:
            return

        colour = self._driver_colors.get(code)

        if not colour:
            return

        item.setForeground(
            Qt.GlobalColor.white
        )

    # --------------------------------------------------------
    # Connection
    # --------------------------------------------------------

    def on_connection_status_changed(self, status):

        if status != "Connected":

            self.status_label.setText(
                str(status)
            )


# ------------------------------------------------------------
# Standalone testing
# ------------------------------------------------------------

def main():

    app = QApplication(sys.argv)

    window = DriverComparisonWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()