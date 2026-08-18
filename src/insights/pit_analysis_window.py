"""
RaceVision - Pit Stop Analysis

Analyzes pre-computed race lap data to identify:
- Pit stops
- Tyre strategy
- Stint lengths
- Compound changes
"""

from PySide6.QtWidgets import (
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
from src.lib.tyres import get_tyre_compound_str


BG = "#282828"
PANEL = "#1E1E1E"
TEXT = "#E0E0E0"
DIM = "#999999"
BORDER = "#444444"


class PitAnalysisWindow(PitWallWindow):
    """
    Pit wall insight for analysing pit stops and tyre strategy.
    """

    def __init__(self):
        self._lap_times = {}
        self._drivers = []

        super().__init__()

        self.setWindowTitle("RaceVision | Pit Stop Analysis")
        self.resize(1200, 1000)

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        central.setStyleSheet(
            f"""
            QWidget {{
                background-color: {BG};
                color: {TEXT};
            }}

            QComboBox {{
                background-color: {PANEL};
                color: {TEXT};
                border: 1px solid {BORDER};
                padding: 7px;
                min-width: 150px;
            }}

            QTableWidget {{
                background-color: {PANEL};
                color: {TEXT};
                border: 1px solid {BORDER};
                gridline-color: {BORDER};
            }}

            QHeaderView::section {{
                background-color: #151515;
                color: {TEXT};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            """
        )

        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # -----------------------------------------------------
        # Header
        # -----------------------------------------------------

        title = QLabel("PIT STOP ANALYSIS")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))

        subtitle = QLabel("Race strategy, pit stops and tyre stint analysis")
        subtitle.setStyleSheet(f"color: {DIM};")

        root.addWidget(title)
        root.addWidget(subtitle)

        # -----------------------------------------------------
        # Driver selector
        # -----------------------------------------------------

        selector_row = QHBoxLayout()

        driver_label = QLabel("Driver:")
        driver_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        self.driver_combo = QComboBox()

        self.driver_combo.currentTextChanged.connect(self._update_driver_detail)

        selector_row.addWidget(driver_label)
        selector_row.addWidget(self.driver_combo)
        selector_row.addStretch()

        root.addLayout(selector_row)

        # -----------------------------------------------------
        # Summary table
        # -----------------------------------------------------

        summary_label = QLabel("Race Strategy Summary")
        summary_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        root.addWidget(summary_label)

        self.summary_table = QTableWidget(0, 4)

        self.summary_table.setHorizontalHeaderLabels(
            [
                "Driver",
                "Stops",
                "Strategy",
                "Pit Laps",
            ]
        )

        self.summary_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.summary_table.verticalHeader().setVisible(False)
        self.summary_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.summary_table.itemSelectionChanged.connect(self._summary_row_selected)

        root.addWidget(self.summary_table)

        # -----------------------------------------------------
        # Driver detail
        # -----------------------------------------------------

        self.detail_title = QLabel("Select a driver")

        self.detail_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        root.addWidget(self.detail_title)

        self.detail_table = QTableWidget(0, 5)
        [
            "Stint",
            "Compound",
            "Start Lap",
            "End Lap",
            "Length",
        ]

        self.detail_table.setHorizontalHeaderLabels(
            [
                "Stint",
                "Compound",
                "Start Lap",
                "End Lap",
                "Length",
            ]
        )

        self.detail_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.detail_table.verticalHeader().setVisible(False)

        root.addWidget(self.detail_table)

        # -----------------------------------------------------
        # Pit stop details
        # -----------------------------------------------------

        pit_label = QLabel("Pit Stop Details")
        pit_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        root.addWidget(pit_label)

        self.pit_table = QTableWidget(0, 4)

        self.pit_table.setHorizontalHeaderLabels(
            [
                "Pit Lap",
                "From",
                "To",
                "Detection",
            ]
        )

        self.pit_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.pit_table.verticalHeader().setVisible(False)
        root.addWidget(self.pit_table)

        # -----------------------------------------------------
        # Pit stop performance
        # -----------------------------------------------------

        performance_label = QLabel("Pit Stop Performance")
        performance_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        root.addWidget(performance_label)

        self.performance_table = QTableWidget(0, 6)

        self.performance_table.setHorizontalHeaderLabels(
            [
                "Pit Lap",
                "Change",
                "Before Pace",
                "Out Lap",
                "After Pace",
                "Recovery",
            ]
        )

        self.performance_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.performance_table.verticalHeader().setVisible(False)

        root.addWidget(self.performance_table)
        # -----------------------------------------------------
        # Pit stop effectiveness
        # -----------------------------------------------------

        effectiveness_label = QLabel("Pit Stop Effectiveness")

        effectiveness_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        root.addWidget(effectiveness_label)

        self.effectiveness_table = QTableWidget(0, 4)

        self.effectiveness_table.setHorizontalHeaderLabels(
            [
                "Pit Lap",
                "Tyre Change",
                "Score",
                "Rating",
            ]
        )

        self.effectiveness_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.effectiveness_table.verticalHeader().setVisible(False)

        root.addWidget(self.effectiveness_table)
                # -----------------------------------------------------
        # Race-wide strategy comparison
        # -----------------------------------------------------

        strategy_label = QLabel(
            "Strategy Comparison"
        )

        strategy_label.setFont(
            QFont("Arial", 14, QFont.Weight.Bold)
        )

        root.addWidget(strategy_label)

        self.strategy_table = QTableWidget(0, 4)

        self.strategy_table.setHorizontalHeaderLabels(
            [
                "Driver",
                "Stops",
                "Strategy",
                "Avg Stint",
            ]
        )

        self.strategy_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.strategy_table.verticalHeader().setVisible(False)

        root.addWidget(self.strategy_table)

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        self.status_label = QLabel("Waiting for telemetry...")

        self.status_label.setStyleSheet(f"color: {DIM};")

        root.addWidget(self.status_label)

    # ---------------------------------------------------------
    # Telemetry
    # ---------------------------------------------------------

    def on_telemetry_data(self, data):

        lap_times = data.get("lap_times")

        if not lap_times:
            return

        self._lap_times = lap_times

        drivers = sorted(code for code, entries in lap_times.items() if entries)

        if drivers != self._drivers:
            self._drivers = drivers

            current_driver = self.driver_combo.currentText()

            self.driver_combo.blockSignals(True)

            self.driver_combo.clear()
            self.driver_combo.addItems(drivers)

            if current_driver in drivers:
                self.driver_combo.setCurrentText(current_driver)
            elif drivers:
                self.driver_combo.setCurrentIndex(0)

            self.driver_combo.blockSignals(False)

        self._update_summary()

        self._update_driver_detail(self.driver_combo.currentText())

        session_data = data.get("session_data", {})

        lap = session_data.get("lap", "?")

        total = session_data.get("total_laps", "?")

        self.status_label.setText(f"Live telemetry  •  Lap {lap}/{total}")

    # ---------------------------------------------------------
    # Compound helper
    # ---------------------------------------------------------

    @staticmethod
    def _compound_name(value):

        try:
            if value is None:
                return "UNKNOWN"

            if isinstance(value, str):
                return value.upper()

            return get_tyre_compound_str(int(value)).upper()

        except Exception:
            return "UNKNOWN"

    # ---------------------------------------------------------
    # Lap time helper
    # ---------------------------------------------------------

    @staticmethod
    def _lap_seconds(entry):

        if not entry:
            return None

        value = entry.get("time_s")

        if value is None:
            return None

        try:
            value = float(value)

            if value <= 0:
                return None

            return value

        except (TypeError, ValueError):
            return None

    # ---------------------------------------------------------
    # Pit detection
    # ---------------------------------------------------------

    def _find_pit_stops(self, entries):

        entries = sorted(entries, key=lambda item: item.get("lap", 0))

        pit_stops = []

        for index, entry in enumerate(entries):
            lap = entry.get("lap")

            if lap is None:
                continue

            # Official FastF1 pit entry
            official_pit = bool(entry.get("is_pit_entry"))

            next_entry = entries[index + 1] if index + 1 < len(entries) else None

            inferred_pit = False

            if next_entry:
                current_tyre = entry.get("tyre", -1)

                next_tyre = next_entry.get("tyre", -1)

                current_life = entry.get("tyre_life", -1)

                next_life = next_entry.get("tyre_life", -1)

                compound_changed = (
                    current_tyre != -1 and next_tyre != -1 and current_tyre != next_tyre
                )

                tyre_reset = (
                    current_life >= 0
                    and next_life >= 0
                    and next_life <= 2
                    and next_life + 1 < current_life
                )

                inferred_pit = compound_changed or tyre_reset

            if official_pit or inferred_pit:
                from_compound = self._compound_name(entry.get("tyre"))

                to_compound = (
                    self._compound_name(next_entry.get("tyre"))
                    if next_entry
                    else "UNKNOWN"
                )

                # Avoid duplicate detections
                if pit_stops:
                    if pit_stops[-1]["lap"] == lap:
                        continue

                pit_stops.append(
                    {
                        "lap": int(lap),
                        "from": from_compound,
                        "to": to_compound,
                        "confidence": ("Official" if official_pit else "Inferred"),
                    }
                )

        return pit_stops

    # ---------------------------------------------------------
    # Stint calculation
    # ---------------------------------------------------------

    def _build_stints(self, entries, pit_stops):

        entries = sorted(entries, key=lambda item: item.get("lap", 0))

        valid_entries = [entry for entry in entries if entry.get("lap") is not None]

        if not valid_entries:
            return []

        pit_laps = {stop["lap"] for stop in pit_stops}

        stints = []

        current_start = valid_entries[0].get("lap")

        current_tyre = self._compound_name(valid_entries[0].get("tyre"))

        previous_lap = current_start

        for entry in valid_entries[1:]:
            lap = entry.get("lap")

            tyre = self._compound_name(entry.get("tyre"))

            # A pit normally ends the previous stint
            if previous_lap in pit_laps or tyre != current_tyre:
                stints.append(
                    {
                        "compound": current_tyre,
                        "start": current_start,
                        "end": previous_lap,
                        "length": (previous_lap - current_start + 1),
                    }
                )

                current_start = lap
                current_tyre = tyre

            previous_lap = lap

        # Final stint
        stints.append(
            {
                "compound": current_tyre,
                "start": current_start,
                "end": previous_lap,
                "length": (previous_lap - current_start + 1),
            }
        )

        return stints

    # ---------------------------------------------------------
    # Driver strategy
    # ---------------------------------------------------------

    def _get_driver_strategy(self, code):

        entries = self._lap_times.get(code, [])

        if not entries:
            return [], []

        pit_stops = self._find_pit_stops(entries)

        stints = self._build_stints(entries, pit_stops)

        return pit_stops, stints
        # ---------------------------------------------------------

    # Pit stop performance
    # ---------------------------------------------------------

    def _get_pit_performance(self, code):

        entries = self._lap_times.get(code, [])

        if not entries:
            return []

        entries = sorted(entries, key=lambda item: item.get("lap", 0))

        pit_stops, _ = self._get_driver_strategy(code)

        results = []

        for stop in pit_stops:
            pit_lap = stop["lap"]

            before_entry = None
            out_entry = None
            after_entry = None

            # Find useful laps around the stop
            for entry in entries:
                lap = entry.get("lap")

                if lap is None:
                    continue

                if lap == pit_lap - 1:
                    before_entry = entry

                elif lap == pit_lap + 1:
                    out_entry = entry

                elif lap == pit_lap + 2:
                    after_entry = entry

            before = self._lap_seconds(before_entry) if before_entry else None

            out_lap = self._lap_seconds(out_entry) if out_entry else None

            after = self._lap_seconds(after_entry) if after_entry else None

            # Determine how many laps were needed
            # to return close to pre-stop pace.
            recovery = "N/A"

            if before is not None:
                for offset in range(1, 6):
                    candidate = next(
                        (
                            entry
                            for entry in entries
                            if entry.get("lap") == pit_lap + offset
                        ),
                        None,
                    )

                    if not candidate:
                        continue

                    candidate_time = self._lap_seconds(candidate)

                    if candidate_time is None:
                        continue

                    # Within 1% of pre-stop pace
                    if candidate_time <= before * 1.01:
                        recovery = f"{offset} lap"
                        if offset != 1:
                            recovery += "s"

                        break

            results.append(
                {
                    "lap": pit_lap,
                    "change": (f"{stop['from']} → {stop['to']}"),
                    "before": before,
                    "out_lap": out_lap,
                    "after": after,
                    "recovery": recovery,
                }
            )

        return results
        # ---------------------------------------------------------
    # Race-wide strategy comparison
    # ---------------------------------------------------------

    def _get_strategy_comparison(self):

        comparison = []

        for code in sorted(self._lap_times.keys()):

            pit_stops, stints = (
                self._get_driver_strategy(code)
            )

            if not stints:
                continue

            strategy = " → ".join(
                stint["compound"]
                for stint in stints
            )

            average_stint = (
                sum(
                    stint["length"]
                    for stint in stints
                )
                / len(stints)
            )

            comparison.append(
                {
                    "driver": code,
                    "stops": len(pit_stops),
                    "strategy": strategy,
                    "avg_stint": average_stint,
                }
            )

        return comparison

    # ---------------------------------------------------------
    # Pit stop effectiveness score
    # ---------------------------------------------------------

    def _calculate_pit_effectiveness(self, result):

        before = result.get("before")
        out_lap = result.get("out_lap")
        after = result.get("after")
        recovery = result.get("recovery")

        if before is None:
            return 0, "N/A"

        score = 100.0

        # Out-lap penalty
        if out_lap is not None:
            out_loss = max(0.0, out_lap - before)
            score -= min(25.0, out_loss * 3.0)

        # Post-stop pace penalty
        if after is not None:
            after_loss = max(0.0, after - before)
            score -= min(25.0, after_loss * 4.0)

            # Reward genuine pace improvement
            if after < before:
                score += min(10.0, (before - after) * 5.0)

        # Recovery penalty
        if isinstance(recovery, str):
            try:
                recovery_laps = int(recovery.split()[0])

                if recovery_laps == 1:
                    score += 5.0
                elif recovery_laps == 2:
                    score -= 2.0
                elif recovery_laps == 3:
                    score -= 8.0
                elif recovery_laps >= 4:
                    score -= 15.0

            except (ValueError, IndexError):
                pass

        score = max(0, min(100, round(score)))

        if score >= 85:
            rating = "Excellent"
        elif score >= 70:
            rating = "Good"
        elif score >= 50:
            rating = "Average"
        else:
            rating = "Poor"

        return score, rating

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def _update_summary(self):

        self.summary_table.setRowCount(0)

        for code in self._drivers:
            pit_stops, stints = self._get_driver_strategy(code)

            if not stints:
                continue

            row = self.summary_table.rowCount()

            self.summary_table.insertRow(row)

            strategy = " → ".join(stint["compound"] for stint in stints)

            pit_laps = ", ".join(str(stop["lap"]) for stop in pit_stops)

            values = [
                code,
                str(len(pit_stops)),
                strategy,
                pit_laps or "None",
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.summary_table.setItem(row, column, item)

    # ---------------------------------------------------------
    # Driver detail
    # ---------------------------------------------------------

    def _update_driver_detail(self, code):

        if not code:
            return

        pit_stops, stints = self._get_driver_strategy(code)

        self.detail_title.setText(
            f"{code}  •  {len(pit_stops)} Pit Stop{'s' if len(pit_stops) != 1 else ''}"
        )

        # -----------------------------------------------------
        # Stint table
        # -----------------------------------------------------

        self.detail_table.setRowCount(0)

        for index, stint in enumerate(stints, start=1):
            row = self.detail_table.rowCount()

            self.detail_table.insertRow(row)

            values = [
                f"Stint {index}",
                stint["compound"],
                str(stint["start"]),
                str(stint["end"]),
                f"{stint['length']} laps",
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.detail_table.setItem(row, column, item)

        # -----------------------------------------------------
        # Pit stop table
        # -----------------------------------------------------

        self.pit_table.setRowCount(0)

        for stop in pit_stops:
            row = self.pit_table.rowCount()

            self.pit_table.insertRow(row)

            values = [
                str(stop["lap"]),
                stop["from"],
                stop["to"],
                stop["confidence"],
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.pit_table.setItem(row, column, item)
        # -----------------------------------------------------
        # Pit stop performance table
        # -----------------------------------------------------

        performance = self._get_pit_performance(code)

        self.performance_table.setRowCount(0)

        for result in performance:
            row = self.performance_table.rowCount()

            self.performance_table.insertRow(row)

            def format_time(value):

                if value is None:
                    return "N/A"

                return f"{value:.3f}s"

            values = [
                str(result["lap"]),
                result["change"],
                format_time(result["before"]),
                format_time(result["out_lap"]),
                format_time(result["after"]),
                result["recovery"],
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.performance_table.setItem(row, column, item)
        # -----------------------------------------------------
        # Pit stop effectiveness
        # -----------------------------------------------------

        self.effectiveness_table.setRowCount(0)

        for result in performance:
            score, rating = self._calculate_pit_effectiveness(result)

            row = self.effectiveness_table.rowCount()

            self.effectiveness_table.insertRow(row)

            values = [
                str(result["lap"]),
                result["change"],
                str(score),
                rating,
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.effectiveness_table.setItem(row, column, item)
                        # -----------------------------------------------------
        # Race-wide strategy comparison
        # -----------------------------------------------------

        comparison = self._get_strategy_comparison()

        self.strategy_table.setRowCount(0)

        for result in comparison:

            row = self.strategy_table.rowCount()

            self.strategy_table.insertRow(row)

            values = [
                result["driver"],
                str(result["stops"]),
                result["strategy"],
                f'{result["avg_stint"]:.1f} laps',
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.strategy_table.setItem(
                    row,
                    column,
                    item
                )

    # ---------------------------------------------------------
    # Summary row selection
    # ---------------------------------------------------------

    def _summary_row_selected(self):

        selected = self.summary_table.selectedItems()

        if not selected:
            return

        row = selected[0].row()

        driver_item = self.summary_table.item(row, 0)

        if driver_item:
            self.driver_combo.setCurrentText(driver_item.text())


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    window = PitAnalysisWindow()
    window.show()

    sys.exit(app.exec())
