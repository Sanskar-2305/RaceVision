from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QMessageBox,
)
from PySide6.QtWidgets import QProgressDialog
from PySide6.QtCore import QThread, Signal, Qt, QTimer

# from PySide6.QtGui import QPixmap, QFont
import sys
import os
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from src.f1_data import (
    get_race_weekends_by_year,
    get_race_weekends_by_place,
    get_all_unique_race_names,
    load_session,
)
from src.gui.settings_dialog import SettingsDialog
from src.lib.season import get_season


# Worker thread to fetch schedule without blocking UI
class FetchScheduleWorker(QThread):
    result = Signal(object)
    error = Signal(str)

    def __init__(self, year, parent=None):
        super().__init__(parent)
        self.year = year

    def run(self):  # check
        try:
            # enable cache if available in project
            try:
                from src.f1_data import enable_cache

                enable_cache()
            except Exception:
                pass
            events = get_race_weekends_by_year(self.year)
            self.result.emit(events)
        except Exception as e:
            self.error.emit(str(e))


class RaceSelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.loading_session = False
        self.selected_session_title = None
        self.current_year = get_season()
        self.selected_year = self.current_year

        self.setWindowTitle("RaceVision - F1 Analytics")
        self._setup_ui()
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        self.setWindowState(self.windowState())

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        central_widget.setStyleSheet("""
            QWidget {
                background-color: #0B0D12;
                color: #F5F7FA;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QLabel {
                color: #F5F7FA;
            }

            QComboBox {
                background-color: #151A22;
                color: #F5F7FA;
                border: 1px solid #2A303A;
                border-radius: 6px;
                padding: 8px;
                min-height: 20px;
            }

            QComboBox:hover {
                border: 1px solid #00D9FF;
            }

            QPushButton {
                background-color: #151A22;
                color: #F5F7FA;
                border: 1px solid #2A303A;
                border-radius: 6px;
                padding: 8px 14px;
            }

            QPushButton:hover {
                background-color: #00D9FF;
                color: #0B0D12;
            }

            QTreeWidget {
                background-color: #11151C;
                color: #F5F7FA;
                border: 1px solid #2A303A;
                border-radius: 6px;
            }

            QTreeWidget::item {
                padding: 6px;
            }

            QTreeWidget::item:selected {
                background-color: #00D9FF;
                color: #0B0D12;
            }

            QHeaderView::section {
                background-color: #151A22;
                color: #00D9FF;
                padding: 8px;
                border: none;
            }
        """)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 28)
        main_layout.setSpacing(16)
        central_widget.setLayout(main_layout)

        # Header (title)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)

# RaceVision branding
        header_label = QLabel("RACEVISION")
        font = header_label.font()
        font.setPointSize(24)
        font.setBold(True)
        header_label.setFont(font)
        header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        header_label.setStyleSheet("""
    QLabel {
        color: #00D9FF;
        letter-spacing: 2px;
        padding: 5px 0;
    }
""")

# Subtitle
        subtitle_label = QLabel("F1 ANALYTICS & RACE VISUALIZATION")
        subtitle_font = subtitle_label.font()
        subtitle_font.setPointSize(9)
        subtitle_font.setBold(True)
        subtitle_label.setFont(subtitle_font)

        subtitle_label.setStyleSheet("""
    QLabel {
        color: #8B93A1;
        padding-left: 12px;
    }
""")

# Settings button
        settings_btn = QPushButton("⚙  Settings")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setFixedHeight(36)
        settings_btn.setMinimumWidth(110)
        settings_btn.clicked.connect(self.open_settings)

        header_layout.addWidget(header_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        header_layout.addWidget(settings_btn)

        main_layout.addLayout(header_layout)

        # Year selection
        year_layout = QHBoxLayout()
        year_label = QLabel("SEASON")
        year_label.setStyleSheet("""
            color: #8B93A1;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        self.year_combo = QComboBox()
        self.year_combo.addItem("All Years")

        for year in range(2018, self.current_year + 1):
            self.year_combo.addItem(str(year))

        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self.load_by_year)
        self.year_combo.setMinimumHeight(38)

        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_combo)
        main_layout.addLayout(year_layout)

        # Race Selection
        place_layout = QHBoxLayout()
        place_label = QLabel("GRAND PRIX")
        place_label.setStyleSheet("""
            color: #8B93A1;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        self.place_combo = QComboBox()
        self.place_combo.addItem("All Races")
        self.place_combo.addItems(get_all_unique_race_names())
        self.place_combo.currentTextChanged.connect(self.load_by_place)
        self.place_combo.setMinimumHeight(38)        

        place_layout.addWidget(place_label)
        place_layout.addWidget(self.place_combo)
        main_layout.addLayout(place_layout)

        # Main content: left = schedule, right = session list
        content_layout = QHBoxLayout()

        # Schedule tree (left)
        self.schedule_tree = QTreeWidget()

        self.schedule_tree.setHeaderLabels([
        "ROUND",
        "GRAND PRIX",
        "COUNTRY",
        "DATE"
    ])

        self.schedule_tree.setRootIsDecorated(False)
        self.schedule_tree.setAlternatingRowColors(False)
        self.schedule_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.schedule_tree.setMinimumHeight(400)

        self.schedule_tree.setColumnWidth(0, 70)
        self.schedule_tree.setColumnWidth(1, 250)
        self.schedule_tree.setColumnWidth(2, 150)
        self.schedule_tree.setColumnWidth(3, 150)

        content_layout.addWidget(self.schedule_tree, 3)
        self.schedule_tree.setStyleSheet("""
    QTreeWidget {
        background-color: #11151C;
        color: #F5F7FA;
        border: 1px solid #2A303A;
        border-radius: 8px;
        outline: none;
        font-size: 13px;
    }

    QTreeWidget::item {
        height: 38px;
        padding: 4px;
        border-bottom: 1px solid #1E242D;
    }

    QTreeWidget::item:hover {
        background-color: #19212B;
    }

    QTreeWidget::item:selected {
        background-color: #00D9FF;
        color: #0B0D12;
    }

    QHeaderView::section {
        background-color: #151A22;
        color: #00D9FF;
        border: none;
        border-bottom: 1px solid #2A303A;
        padding: 10px;
        font-size: 11px;
        font-weight: bold;
    }
""")        

        # Session panel (right)
        self.session_panel = QWidget()
        self.session_panel_layout = QVBoxLayout()
        self.session_panel.setLayout(self.session_panel_layout)
        self.session_panel_layout.setAlignment(Qt.AlignTop)
        header_lbl = QLabel(" Available Sessions")
        hdr_font = header_lbl.font()
        hdr_font.setPointSize(14)
        hdr_font.setBold(True)
        header_lbl.setFont(hdr_font)
        header_lbl.setStyleSheet("""
            color: #00D9FF;
            font-size: 13px;
            font-weight: bold;
            padding-bottom: 8px;
        """)
        self.session_panel_layout.addWidget(header_lbl)

        # placeholder spacer
        self.session_list_container = QWidget()
        self.session_list_layout = QVBoxLayout()
        self.session_list_container.setLayout(self.session_list_layout)
        self.session_panel_layout.addWidget(self.session_list_container)

        content_layout.addWidget(self.session_panel, 1)

        main_layout.addLayout(content_layout)

        # connect click handler
        self.schedule_tree.itemClicked.connect(self.on_race_clicked)

        # Load initial schedule
        # hide sessions panel until a weekend is selected
        self.session_panel.hide()
        self.load_schedule(year=self.current_year)

    def load_schedule(self, year=None, events=None):
        if self.loading_session:
            return

        self.schedule_tree.clear()
        # hide sessions panel while loading / when nothing selected
        try:
            self.session_panel.hide()
        except Exception:
            pass

        # Race filter
        if events is not None:
            self.populate_schedule(events)
            self.loading_session = False
            return

        # Year filter
        if year is not None:
            self.loading_session = True
            self.worker = FetchScheduleWorker(int(year))
            self.worker.result.connect(self.populate_schedule)
            self.worker.error.connect(self.show_error)
            self.worker.start()
            return

        self.loading_session = False

    def load_by_year(self, year_text):
        if self.loading_session:
            return

        # Reset by_race filter
        if year_text != "All Years":
            self.place_combo.blockSignals(True)
            self.place_combo.setCurrentText("All Races")
            self.place_combo.blockSignals(False)

        if year_text == "All Years":
            self.selected_year = None
            self.schedule_tree.clear()
            return

        if not year_text.isdigit():
            return

        self.selected_year = int(year_text)
        self.load_schedule(year=self.selected_year)

    def load_by_place(self, race_name):
        if race_name == "All Races":
            if self.selected_year is not None:
                self.load_schedule(year=self.selected_year)
            return

        # Reset year filter
        self.year_combo.blockSignals(True)
        self.year_combo.setCurrentText("All Years")
        self.year_combo.blockSignals(False)
        self.selected_year = None

        self.schedule_tree.clear()

        events = get_race_weekends_by_place(race_name)
        self.load_schedule(events=events)

    def populate_schedule(self, events):
        for event in events:
            # Ensure all columns are strings (QTreeWidgetItem expects text)
            round_str = str(event.get("round_number", ""))
            name = str(event.get("event_name", ""))
            country = str(event.get("country", ""))
            date = str(event.get("date", ""))

            event_item = QTreeWidgetItem([round_str, name, country, date])
            event_item.setData(0, Qt.UserRole, event)
            self.schedule_tree.addTopLevelItem(event_item)

        # Make sure the round column is wide enough to be visible
        try:
            self.schedule_tree.resizeColumnToContents(0)
            self.schedule_tree.resizeColumnToContents(1)
        except Exception:
            pass

        self.loading_session = False

    def on_race_clicked(self, item, column):
        ev = item.data(0, Qt.UserRole)
        # ensure the sessions panel is visible when a race is selected
        try:
            self.session_panel.show()
        except Exception:
            pass
        # determine sessions to show
        ev_type = (ev.get("type") or "").lower()
        sessions = ["Qualifying", "Race"]
        if "sprint" in ev_type:
            sessions.insert(0, "Sprint Qualifying")
            # show sprint-related session
            sessions.insert(2, "Sprint")

        # clear existing session widgets
        for i in reversed(range(self.session_list_layout.count())):
            w = self.session_list_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # determine which sessions have already occurred (data available)
        now = datetime.now(timezone.utc)
        session_dates = ev.get("session_dates", {})
        
        print("SESSION DATES:", session_dates)

        available_sessions = []
        for s in sessions:
            session_date_str = session_dates.get(s)
            if session_date_str:
                try:
                    session_dt = datetime.fromisoformat(session_date_str)
                    if session_dt <= now:
                        available_sessions.append(s)
                except Exception:
                    available_sessions.append(s)
            else:
                # no date info means historical data — assume available
                available_sessions.append(s)

        if not available_sessions:
            label = QLabel("Sessions not available")
            label.setAlignment(Qt.AlignCenter)
            self.session_list_layout.addWidget(label)
        else:
           for s in sessions:
            if s in available_sessions:
                btn = QPushButton(s)

            btn.setMinimumHeight(44)
            btn.setCursor(Qt.PointingHandCursor)

            btn.setStyleSheet("""
            QPushButton {
                background-color: #151A22;
                color: #F5F7FA;
                border: 1px solid #2A303A;
                border-radius: 8px;
                padding: 10px 14px;
                text-align: left;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #00D9FF;
                color: #0B0D12;
                border: 1px solid #00D9FF;
            }

            QPushButton:pressed {
                background-color: #00AFCF;
                color: #0B0D12;
            }
             """)

            btn.clicked.connect(
                lambda _, sname=s, e=ev:
                self._on_session_button_clicked(e, sname)
        )

        self.session_list_layout.addWidget(btn)

    def _on_session_button_clicked(self, ev, session_label):
        """Launch main.py in a separate process to run the selected session.

        Uses the same CLI flags that `main.py` understands: `--qualifying`,
        `--sprint-qualifying`, `--sprint`. Runs the command detached so the
        Qt UI remains responsive.
        """
        try:
            year = ev.get("year") or self.selected_year
        except Exception:
            year = None

        try:
            round_no = int(ev.get("round_number"))
        except Exception:
            round_no = None

        # map button labels to CLI flags
        flag = None
        if session_label == "Qualifying":
            flag = "--qualifying"
        elif session_label == "Sprint Qualifying":
            flag = "--sprint-qualifying"
        elif session_label == "Sprint":
            flag = "--sprint"

        main_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "main.py")
        )
        cmd = [sys.executable, main_path, "--viewer"]
        if year is not None:
            cmd += ["--year", str(year)]
        if round_no is not None:
            cmd += ["--round", str(round_no)]
        if flag:
            cmd.append(flag)
        if "--verbose" in sys.argv:
            cmd.append("--verbose")
        # Show a modal loading dialog and load the session in a background thread.
        dlg = QProgressDialog("Loading session data...", None, 0, 0, self)
        dlg.setWindowTitle("Loading")
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setCancelButton(None)
        dlg.setMinimumDuration(0)
        dlg.setRange(0, 0)
        dlg.show()
        QApplication.processEvents()

        # Map label -> fastf1 session type code
        session_code = "R"
        if session_label == "Qualifying":
            session_code = "Q"
        elif session_label == "Sprint Qualifying":
            session_code = "SQ"
        elif session_label == "Sprint":
            session_code = "S"

        class FetchSessionWorker(QThread):
            result = Signal(object)
            error = Signal(str)

            def __init__(self, year, round_no, session_type, parent=None):
                super().__init__(parent)
                self.year = year
                self.round_no = round_no
                self.session_type = session_type

            def run(self):
                try:
                    try:
                        from src.f1_data import enable_cache

                        enable_cache()
                    except Exception:
                        pass
                    sess = load_session(self.year, self.round_no, self.session_type)
                    self.result.emit(sess)
                except Exception as e:
                    self.error.emit(str(e))

        def _on_loaded(session_obj):
            # create a unique ready-file path and pass it to the child
            ready_path = os.path.join(
                tempfile.gettempdir(), f"f1_ready_{uuid.uuid4().hex}"
            )
            cmd_with_ready = list(cmd) + ["--ready-file", ready_path]

            try:
                proc = subprocess.Popen(cmd_with_ready)
            except Exception as exc:
                try:
                    dlg.close()
                except Exception:
                    pass
                QMessageBox.critical(
                    self, "Playback error", f"Failed to start playback:\n{exc}"
                )
                return

            # Poll for ready file or child exit
            timer = QTimer(self)

            def _check_ready():
                try:
                    if os.path.exists(ready_path):
                        try:
                            dlg.close()
                        except Exception:
                            pass
                        timer.stop()
                        try:
                            os.remove(ready_path)
                        except Exception:
                            pass
                        return
                    # if process exited early, show error
                    if proc.poll() is not None:
                        try:
                            dlg.close()
                        except Exception:
                            pass
                        timer.stop()
                        QMessageBox.critical(
                            self,
                            "Playback error",
                            "Playback process exited before signaling readiness",
                        )
                except Exception:
                    # ignore transient file-system errors
                    pass

            timer.timeout.connect(_check_ready)
            timer.start(200)
            # keep references
            self._play_proc = proc
            self._ready_timer = timer

        def _on_error(msg):
            try:
                dlg.close()
            except Exception:
                pass
            QMessageBox.critical(
                self, "Load error", f"Failed to load session data:\n{msg}"
            )

        worker = FetchSessionWorker(year, round_no, session_code)
        worker.result.connect(_on_loaded)
        worker.error.connect(_on_error)
        # Keep a reference so it doesn't get GC'd
        self._session_worker = worker
        worker.start()

    def show_error(self, message):
        QMessageBox.critical(self, "Error", f"Failed to load schedule: {message}")
        self.loading_session = False

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
