from PyQt5 import QtCore, QtGui, QtWidgets
import PyPDF2
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout,
    QDialog, QLineEdit, QWidget, QScrollArea, QStackedWidget,
    QGroupBox, QFormLayout, QFrame
)
import os
import sys
import json
import keyring
from datetime import datetime
from xhtml2pdf import pisa

from functions.bug_exp import (
    scan_html_file, scan_js_file, scan_php_file, scan_css_file,
    scan_ts_file, scan_json_file, scan_env_file, scan_xml_file,
    scan_sql_file, get_bug_explanation
)
from functions.sec_tip import get_random_security_tips

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "scan_history.json")
CONTACT_FILE = os.path.join(BASE_DIR, "contact_info.json")

DARK_BG    = "rgb(12, 16, 32)"
PANEL_BG   = "rgb(20, 28, 54)"
CARD_BG    = "rgb(26, 36, 68)"
ACCENT     = "#4a9eff"

BTN_GREEN  = f"font: bold 11pt; color: white; border-radius: 8px; background: {ACCENT};"
BTN_RED    = "font: bold 10pt; color: white; border-radius: 8px; background: #c0392b;"
BTN_SMALL  = f"font: bold 9pt; color: white; border-radius: 4px; background: {ACCENT};"
NAV_NORMAL = "font: bold 10pt; color: #a0b4d0; background: transparent;"
NAV_ACTIVE = f"font: bold 10pt; color: {ACCENT}; background: transparent;"
GROUP_BOX  = f"""
    QGroupBox {{
        color: white; font: bold 11pt;
        border: 1px solid {ACCENT}; border-radius: 6px;
        margin-top: 10px; padding: 8px;
        background: {PANEL_BG};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; color: {ACCENT}; }}
"""
INPUT_STYLE = f"background: {CARD_BG}; color: white; border: 1px solid #2a3a6a; border-radius: 4px; padding: 4px;"


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setWindowIcon(QtGui.QIcon("images/icon.png"))
        self.setFixedSize(300, 150)
        layout = QVBoxLayout()
        self.password_label = QLabel("Enter System Password:")
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.check_password)
        layout.addWidget(login_btn)
        self.setLayout(layout)

    def check_password(self):
        entered = self.password_input.text()
        stored = keyring.get_password("system", "user") or "4321"
        if entered == stored:
            self.accept()
        else:
            self.password_input.clear()
            self.password_label.setText("Incorrect Password. Try again.")


class BugTracerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._ui = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._ui is not None:
            cw = self.centralWidget()
            self._ui.adjust_layout(cw.width(), cw.height())


class Ui_BugTracer(object):

    # ── Setup ─────────────────────────────────────────────────────────────────

    def setupUi(self, BugTracer):
        dlg = LoginDialog()
        if dlg.exec_() != QDialog.Accepted:
            sys.exit()

        self.bug_report_data = []
        self.selected_directory = ""
        self._nav_labels = []
        self._nav_widgets = []

        BugTracer.setObjectName("BugTracer")
        BugTracer.resize(868, 586)
        BugTracer.setStyleSheet(f"background: {DARK_BG};")

        self.centralwidget = QWidget(BugTracer)
        self.centralwidget.setObjectName("centralwidget")

        # ── Sidebar background ────────────────────────────────────────────────
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(20, 10, 231, 541))
        self.graphicsView.setStyleSheet(
            f"background: {PANEL_BG}; border-radius: 12px; border: 2px solid {ACCENT}; border-top: 3px solid #7ab8ff;"
        )

        # Logo
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 20, 91, 81))
        self.label_2.setStyleSheet("background: transparent;")
        self.label_2.setPixmap(QtGui.QPixmap("images/logo.png"))
        self.label_2.setScaledContents(True)

        # ── Navigation items ─────────────────────────────────────────────────
        _nav_defs = [
            (115, "Home",     "images/change.png", 0),
            (178, "Settings", "images/change.png", 1),
            (241, "History",  "images/doc.png",    2),
            (304, "Reports",  "images/doc.png",    3),
            (367, "About",    "images/con.png",    4),
        ]
        for y, text, icon_path, page_idx in _nav_defs:
            w = QWidget(self.centralwidget)
            w.setGeometry(QtCore.QRect(30, y, 225, 60))
            w.setStyleSheet("background: transparent;")

            text_lbl = QLabel(text, w)
            text_lbl.setGeometry(QtCore.QRect(12, 16, 158, 28))
            text_lbl.setStyleSheet(NAV_NORMAL)
            text_lbl.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            text_lbl.mousePressEvent = lambda e, idx=page_idx: (
                self.navigate(idx) if e.button() == QtCore.Qt.LeftButton else None
            )

            icon_lbl = QLabel(w)
            icon_lbl.setGeometry(QtCore.QRect(178, 16, 28, 28))
            icon_lbl.setStyleSheet("background: transparent;")
            icon_lbl.setPixmap(QtGui.QPixmap(icon_path))
            icon_lbl.setScaledContents(True)
            icon_lbl.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            icon_lbl.mousePressEvent = lambda e, idx=page_idx: (
                self.navigate(idx) if e.button() == QtCore.Qt.LeftButton else None
            )

            self._nav_labels.append(text_lbl)
            self._nav_widgets.append(w)

        # ── Sidebar buttons ───────────────────────────────────────────────────
        self.pushButton_logout = QPushButton("Logout", self.centralwidget)
        self.pushButton_logout.setGeometry(QtCore.QRect(60, 437, 141, 41))
        self.pushButton_logout.setStyleSheet(BTN_RED)
        self.pushButton_logout.clicked.connect(self.logout)

        self.pushButton_2 = QPushButton("Print Report", self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(60, 490, 141, 41))
        self.pushButton_2.setStyleSheet(BTN_GREEN)
        self.pushButton_2.clicked.connect(self.print_report)

        # ── Stacked content widget ────────────────────────────────────────────
        self.stacked = QStackedWidget(self.centralwidget)
        self.stacked.setGeometry(QtCore.QRect(270, 20, 578, 521))
        self.stacked.setStyleSheet("background: transparent;")

        self.stacked.addWidget(self._build_home_page())      # 0
        self.stacked.addWidget(self._build_settings_page())  # 1
        self.stacked.addWidget(self._build_history_page())   # 2
        self.stacked.addWidget(self._build_reports_page())   # 3
        self.stacked.addWidget(self._build_about_page())     # 4

        # ── Background decorations ────────────────────────────────────────────
        self.label_9 = QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(330, -160, 631, 601))
        self.label_9.setStyleSheet("background: none;")
        self.label_9.setPixmap(QtGui.QPixmap("images/ba.png"))
        self.label_9.setScaledContents(True)

        self.label_10 = QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(590, 110, 631, 601))
        self.label_10.setStyleSheet("background: none;")
        self.label_10.setPixmap(QtGui.QPixmap("images/ba.png"))
        self.label_10.setScaledContents(True)

        # ── Z-order ───────────────────────────────────────────────────────────
        self.label_10.raise_()
        self.label_9.raise_()
        self.graphicsView.raise_()
        for w in self._nav_widgets:
            w.raise_()
        self.pushButton_logout.raise_()
        self.pushButton_2.raise_()
        self.stacked.raise_()
        self.label_2.raise_()

        BugTracer.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(BugTracer)
        BugTracer.setStatusBar(self.statusbar)
        BugTracer.setWindowTitle("BugTracer")

        self.navigate(0)

    # ── Page builders ─────────────────────────────────────────────────────────

    def _build_home_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        tips_hdr = QLabel("Software Security Tips")
        tips_hdr.setStyleSheet(
            "font: bold 11pt; color: white; background: transparent; border: none;"
        )
        layout.addWidget(tips_hdr)

        self.scrollArea_2 = QScrollArea()
        self.scrollArea_2.setStyleSheet(
            f"background: {PANEL_BG}; color: white; border: 1px solid {ACCENT};"
        )
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setLayout(QVBoxLayout())
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        layout.addWidget(self.scrollArea_2, stretch=2)
        self._populate_tips()

        bugs_hdr = QLabel("Potential bugs and vulnerabilities found")
        bugs_hdr.setStyleSheet(
            "font: bold 11pt; color: white; background: transparent; border: none;"
        )
        layout.addWidget(bugs_hdr)

        self.scrollArea = QScrollArea()
        self.scrollArea.setStyleSheet(
            f"background: {PANEL_BG}; color: white; border: 1px solid {ACCENT};"
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setLayout(QVBoxLayout())
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        layout.addWidget(self.scrollArea, stretch=2)

        # ── Bottom bar: path display + Browse + Scan ──────────────────────────
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 6, 0, 0)
        bottom.setSpacing(8)

        self.path_label = QLabel("No folder selected")
        self.path_label.setStyleSheet(
            f"color: #7ab8ff; font: 10pt; background: {CARD_BG};"
            f" border: 1px solid #2a3a6a; border-radius: 4px; padding: 3px 8px;"
        )
        bottom.addWidget(self.path_label, stretch=1)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedSize(90, 36)
        browse_btn.setStyleSheet(BTN_GREEN)
        browse_btn.clicked.connect(self.browse_pick_directory)
        bottom.addWidget(browse_btn)

        self.scan_btn = QPushButton("Scan")
        self.scan_btn.setFixedSize(90, 36)
        self.scan_btn.setEnabled(False)
        self.scan_btn.setStyleSheet(f"""
            QPushButton {{ font: bold 11pt; color: white; border-radius: 8px; background: {ACCENT}; }}
            QPushButton:disabled {{ background: #1a2a4a; color: #3a5080; }}
        """)
        self.scan_btn.clicked.connect(self.start_scan)
        bottom.addWidget(self.scan_btn)

        layout.addLayout(bottom)
        return page

    def _build_settings_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(16)

        title = QLabel("Settings")
        title.setStyleSheet("font: bold 16pt; color: white; background: transparent;")
        outer.addWidget(title)

        # Change Password group
        pw_box = QGroupBox("Change Password")
        pw_box.setStyleSheet(GROUP_BOX)
        pw_lay = QVBoxLayout(pw_box)
        pw_lay.setSpacing(8)

        self.new_pw_input = QLineEdit()
        self.new_pw_input.setPlaceholderText("New password")
        self.new_pw_input.setEchoMode(QLineEdit.Password)
        self.new_pw_input.setStyleSheet(INPUT_STYLE)
        pw_lay.addWidget(self.new_pw_input)

        self.confirm_pw_input = QLineEdit()
        self.confirm_pw_input.setPlaceholderText("Confirm new password")
        self.confirm_pw_input.setEchoMode(QLineEdit.Password)
        self.confirm_pw_input.setStyleSheet(INPUT_STYLE)
        pw_lay.addWidget(self.confirm_pw_input)

        save_pw_btn = QPushButton("Save Password")
        save_pw_btn.setStyleSheet(
            f"background: {ACCENT}; color: white; font: bold 10pt; border-radius: 6px; padding: 6px;"
        )
        save_pw_btn.clicked.connect(self.save_password)
        pw_lay.addWidget(save_pw_btn)
        outer.addWidget(pw_box)

        # Contact Information group
        contact_box = QGroupBox("Contact Information")
        contact_box.setStyleSheet(GROUP_BOX)
        contact_lay = QFormLayout(contact_box)
        contact_lay.setSpacing(8)
        lbl_style = "color: white; font: bold 10pt; background: transparent;"

        self.contact_name = QLineEdit()
        self.contact_name.setStyleSheet(INPUT_STYLE)
        self.contact_email = QLineEdit()
        self.contact_email.setStyleSheet(INPUT_STYLE)
        self.contact_phone = QLineEdit()
        self.contact_phone.setStyleSheet(INPUT_STYLE)

        for lbl_text, field in [
            ("Name:",  self.contact_name),
            ("Email:", self.contact_email),
            ("Phone:", self.contact_phone),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(lbl_style)
            contact_lay.addRow(lbl, field)

        self._load_contact_info()

        save_contact_btn = QPushButton("Save Contact Info")
        save_contact_btn.setStyleSheet(
            f"background: {ACCENT}; color: white; font: bold 10pt; border-radius: 6px; padding: 6px;"
        )
        save_contact_btn.clicked.connect(self.save_contact_info)
        spacer_lbl = QLabel("")
        spacer_lbl.setStyleSheet("background: transparent;")
        contact_lay.addRow(spacer_lbl, save_contact_btn)
        outer.addWidget(contact_box)

        outer.addStretch()
        return page

    def _build_history_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        hdr_row = QHBoxLayout()
        title = QLabel("Scan History")
        title.setStyleSheet("font: bold 16pt; color: white; background: transparent;")
        hdr_row.addWidget(title)
        hdr_row.addStretch()
        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet(BTN_RED)
        clear_btn.setFixedHeight(32)
        clear_btn.clicked.connect(self._clear_history)
        hdr_row.addWidget(clear_btn)
        outer.addLayout(hdr_row)

        self.history_scroll = QScrollArea()
        self.history_scroll.setStyleSheet(
            f"background: {PANEL_BG}; border: 1px solid {ACCENT};"
        )
        self.history_scroll.setWidgetResizable(True)
        self.history_contents = QWidget()
        self.history_layout = QVBoxLayout(self.history_contents)
        self.history_layout.setSpacing(6)
        self.history_layout.setContentsMargins(8, 8, 8, 8)
        self.history_layout.addStretch()
        self.history_scroll.setWidget(self.history_contents)
        outer.addWidget(self.history_scroll)

        self._refresh_history_view()
        return page

    def _build_reports_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        hdr_row = QHBoxLayout()
        title = QLabel("Generated Reports")
        title.setStyleSheet("font: bold 16pt; color: white; background: transparent;")
        hdr_row.addWidget(title)
        hdr_row.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(BTN_SMALL)
        refresh_btn.setFixedHeight(32)
        refresh_btn.clicked.connect(self._refresh_reports_view)
        hdr_row.addWidget(refresh_btn)
        outer.addLayout(hdr_row)

        self.reports_scroll = QScrollArea()
        self.reports_scroll.setStyleSheet(
            f"background: {PANEL_BG}; border: 1px solid {ACCENT};"
        )
        self.reports_scroll.setWidgetResizable(True)
        self.reports_contents = QWidget()
        self.reports_layout = QVBoxLayout(self.reports_contents)
        self.reports_layout.setSpacing(6)
        self.reports_layout.setContentsMargins(8, 8, 8, 8)
        self.reports_layout.addStretch()
        self.reports_scroll.setWidget(self.reports_contents)
        outer.addWidget(self.reports_scroll)

        self._refresh_reports_view()
        return page

    def _build_about_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(10)

        title = QLabel("About BugTracer")
        title.setStyleSheet("font: bold 16pt; color: white; background: transparent;")
        outer.addWidget(title)

        subtitle = QLabel("Version 1.0  •  Security Scanner for Web Projects")
        subtitle.setStyleSheet("font: 10pt; color: #7ab8ff; background: transparent;")
        outer.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {ACCENT};")
        sep.setFixedHeight(2)
        outer.addWidget(sep)

        docs_scroll = QScrollArea()
        docs_scroll.setStyleSheet(
            f"background: {PANEL_BG}; border: 1px solid {ACCENT};"
        )
        docs_scroll.setWidgetResizable(True)
        docs_inner = QWidget()
        docs_lay = QVBoxLayout(docs_inner)
        docs_lay.setContentsMargins(14, 14, 14, 14)
        docs_lay.setSpacing(10)

        sections = [
            ("How to Use",
             "1. Click Browse and select your project directory.\n"
             "2. BugTracer recursively scans all supported file types in that directory.\n"
             "3. Results appear on the Home screen under 'Potential bugs and vulnerabilities found'.\n"
             "4. Click Print Report to generate an encrypted PDF of the results."),
            ("Supported File Types",
             ".html  —  .js  —  .ts  —  .php  —  .css  —  .json  —  .env  —  .xml  —  .sql"),
            ("Password & Security",
             "Reports are encrypted with your system password.\n"
             "The default password is 4321.\n"
             "Change it in Settings → Change Password before sharing reports."),
            ("Scan History",
             "Every scan is automatically saved to scan_history.json in the app directory.\n"
             "View past scans on the History page. Clear history at any time."),
            ("Reports",
             "All generated PDF reports are listed on the Reports page.\n"
             "You can open or delete reports directly from there."),
        ]
        for heading, body in sections:
            h = QLabel(heading)
            h.setStyleSheet(
                f"font: bold 11pt; color: {ACCENT}; background: transparent;"
            )
            docs_lay.addWidget(h)
            b = QLabel(body)
            b.setWordWrap(True)
            b.setStyleSheet("font: 10pt; color: white; background: transparent;")
            docs_lay.addWidget(b)

        docs_lay.addStretch()
        docs_scroll.setWidget(docs_inner)
        outer.addWidget(docs_scroll)
        return page

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, index):
        self.stacked.setCurrentIndex(index)
        if index == 2:
            self._refresh_history_view()
        elif index == 3:
            self._refresh_reports_view()
        for i, lbl in enumerate(self._nav_labels):
            lbl.setStyleSheet(NAV_ACTIVE if i == index else NAV_NORMAL)

    # ── Responsive layout ─────────────────────────────────────────────────────

    def adjust_layout(self, W, H):
        CONTENT_X = 270
        self.graphicsView.setGeometry(20, 10, 231, H - 45)
        self.stacked.setGeometry(CONTENT_X, 20, W - CONTENT_X - 20, H - 65)
        self.pushButton_2.setGeometry(60, H - 96, 141, 41)
        self.pushButton_logout.setGeometry(60, H - 149, 141, 41)
        self.label_9.setGeometry(CONTENT_X, -160, W - CONTENT_X + 50, H + 200)
        self.label_10.setGeometry(W - 278, 110, 450, H)

    # ── Home page: tips & bugs ────────────────────────────────────────────────

    def _populate_tips(self):
        layout = self.scrollAreaWidgetContents_2.layout()
        for tip in get_random_security_tips():
            lbl = QLabel(tip)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font: 11pt; color: white; background: transparent;")
            layout.addWidget(lbl)

    def display_bug_report(self, bug_report):
        layout = self.scrollAreaWidgetContents.layout()
        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        if not bug_report:
            lbl = QLabel("No bugs found!")
            lbl.setStyleSheet("color: white; background: transparent;")
            layout.addWidget(lbl)
        else:
            for idx, bug in enumerate(bug_report, start=1):
                bug_type, file_path = bug[0], bug[1]
                explanation = bug[2] if len(bug) == 3 else get_bug_explanation(bug_type)
                lbl = QLabel(f"{idx}. {bug_type}: {explanation}\nFile: {file_path}")
                lbl.setWordWrap(True)
                lbl.setStyleSheet("color: white; background: transparent;")
                layout.addWidget(lbl)

    # ── Scan ─────────────────────────────────────────────────────────────────

    def scan_directory(self, directory):
        bug_report = []
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                if file_name.endswith('.js'):
                    bug_report.extend(scan_js_file(full_path))
                elif file_name.endswith('.html'):
                    bug_report.extend(scan_html_file(full_path))
                elif file_name.endswith('.php'):
                    bug_report.extend(scan_php_file(full_path))
                elif file_name.endswith('.css'):
                    bug_report.extend(scan_css_file(full_path))
                elif file_name.endswith('.ts') and not file_name.endswith('.d.ts'):
                    bug_report.extend(scan_ts_file(full_path))
                elif file_name.endswith('.json'):
                    bug_report.extend(scan_json_file(full_path))
                elif file_name == '.env' or file_name.startswith('.env.'):
                    bug_report.extend(scan_env_file(full_path))
                elif file_name.endswith('.xml'):
                    bug_report.extend(scan_xml_file(full_path))
                elif file_name.endswith('.sql'):
                    bug_report.extend(scan_sql_file(full_path))
        return bug_report

    def browse_pick_directory(self):
        path = QFileDialog.getExistingDirectory(
            None, "Select Directory", "",
            QFileDialog.DontResolveSymlinks | QFileDialog.DontUseNativeDialog
        )
        if path:
            self.selected_directory = path
            display = path if len(path) <= 55 else "..." + path[-52:]
            self.path_label.setText(display)
            self.path_label.setToolTip(path)
            self.scan_btn.setEnabled(True)
            self.navigate(0)

    def start_scan(self):
        if not self.selected_directory:
            return
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning…")
        QtWidgets.QApplication.processEvents()
        self.bug_report_data = self.scan_directory(self.selected_directory)
        self.display_bug_report(self.bug_report_data)
        self._save_to_history(self.selected_directory, self.bug_report_data)
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan")

    # ── Scan History ─────────────────────────────────────────────────────────

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_to_history(self, directory, bug_report):
        history = self._load_history()
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "directory": directory,
            "issue_count": len(bug_report),
            "issues": [{"type": b[0], "file": b[1]} for b in bug_report],
        }
        history.insert(0, entry)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history[:50], f, indent=2)

    def _refresh_history_view(self):
        while self.history_layout.count() > 1:
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        history = self._load_history()
        if not history:
            lbl = QLabel("No scan history yet. Browse a directory to start scanning.")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #7ab8ff; font: 10pt; background: transparent;")
            self.history_layout.insertWidget(0, lbl)
            return

        for i, entry in enumerate(history):
            card = QFrame()
            card.setStyleSheet(
                f"background: {CARD_BG}; border: 1px solid {ACCENT}; border-radius: 4px;"
            )
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(10, 8, 10, 8)
            card_lay.setSpacing(3)

            ts = QLabel(entry["timestamp"])
            ts.setStyleSheet(f"color: {ACCENT}; font: bold 10pt; background: transparent;")
            card_lay.addWidget(ts)

            d = QLabel(f"Directory: {entry['directory']}")
            d.setWordWrap(True)
            d.setStyleSheet("color: white; font: 10pt; background: transparent;")
            card_lay.addWidget(d)

            n = QLabel(f"Issues found: {entry['issue_count']}")
            n.setStyleSheet("color: white; font: 10pt; background: transparent;")
            card_lay.addWidget(n)

            self.history_layout.insertWidget(i, card)

    def _clear_history(self):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        self._refresh_history_view()

    # ── Reports ───────────────────────────────────────────────────────────────

    def _refresh_reports_view(self):
        while self.reports_layout.count() > 1:
            item = self.reports_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pdfs = sorted(
            f for f in os.listdir(BASE_DIR) if f.endswith('_report.pdf')
        )
        if not pdfs:
            lbl = QLabel(
                "No reports found. Scan a directory and click Print Report to create one."
            )
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #7ab8ff; font: 10pt; background: transparent;")
            self.reports_layout.insertWidget(0, lbl)
            return

        for i, pdf in enumerate(pdfs):
            full_path = os.path.join(BASE_DIR, pdf)
            row = QFrame()
            row.setStyleSheet(
                f"background: {CARD_BG}; border: 1px solid {ACCENT}; border-radius: 4px;"
            )
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(10, 6, 10, 6)

            name_lbl = QLabel(pdf)
            name_lbl.setStyleSheet("color: white; font: 10pt; background: transparent;")
            row_lay.addWidget(name_lbl, stretch=1)

            open_btn = QPushButton("Open")
            open_btn.setFixedWidth(70)
            open_btn.setStyleSheet(BTN_SMALL)
            open_btn.clicked.connect(lambda _, p=full_path: os.startfile(p))
            row_lay.addWidget(open_btn)

            del_btn = QPushButton("Delete")
            del_btn.setFixedWidth(70)
            del_btn.setStyleSheet(
                "background: #c0392b; color: white; font: bold 9pt; border-radius: 4px;"
            )
            del_btn.clicked.connect(lambda _, p=full_path: self._delete_report(p))
            row_lay.addWidget(del_btn)

            self.reports_layout.insertWidget(i, row)

    def _delete_report(self, pdf_path):
        reply = QtWidgets.QMessageBox.question(
            None, "Delete Report", f"Delete {pdf_path}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                os.remove(pdf_path)
            except OSError:
                pass
            self._refresh_reports_view()

    # ── Settings ──────────────────────────────────────────────────────────────

    def save_password(self):
        new_pw = self.new_pw_input.text()
        confirm = self.confirm_pw_input.text()
        if not new_pw:
            QtWidgets.QMessageBox.warning(None, "Error", "Password cannot be empty.")
            return
        if new_pw != confirm:
            QtWidgets.QMessageBox.warning(None, "Error", "Passwords do not match.")
            return
        keyring.set_password("system", "user", new_pw)
        self.new_pw_input.clear()
        self.confirm_pw_input.clear()
        QtWidgets.QMessageBox.information(None, "Success", "Password changed successfully.")

    def _load_contact_info(self):
        if os.path.exists(CONTACT_FILE):
            try:
                with open(CONTACT_FILE) as f:
                    data = json.load(f)
                self.contact_name.setText(data.get("name", ""))
                self.contact_email.setText(data.get("email", ""))
                self.contact_phone.setText(data.get("phone", ""))
            except Exception:
                pass

    def save_contact_info(self):
        data = {
            "name":  self.contact_name.text(),
            "email": self.contact_email.text(),
            "phone": self.contact_phone.text(),
        }
        with open(CONTACT_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        QtWidgets.QMessageBox.information(None, "Saved", "Contact information saved.")

    # ── Print / PDF ───────────────────────────────────────────────────────────

    def print_report(self):
        if not self.bug_report_data:
            QtWidgets.QMessageBox.warning(
                None, "No Report", "No report to print. Please scan a directory first."
            )
            return
        self.generate_pdf_report(self.bug_report_data)
        QtWidgets.QMessageBox.information(None, "Report Saved", "Report saved successfully.")
        self.navigate(3)  # switch to Reports page so user sees the new file

    def generate_pdf_report(self, bug_report):
        directory_path = os.path.dirname(bug_report[0][1]) if bug_report else "."
        directory_name = os.path.basename(directory_path)
        output_pdf = os.path.join(BASE_DIR, f"{directory_name}_report.pdf")
        generated_at = datetime.now().strftime("%Y-%m-%d  %H:%M")

        header_html = f"""
        <table style="width:100%;border-bottom:2px solid #1a3a6a;padding-bottom:8px;margin-bottom:10px;">
            <tr>
                <td style="width:70px;vertical-align:middle;">
                    <img src="images/logo.png" width="60" height="60"/>
                </td>
                <td style="vertical-align:middle;padding-left:10px;">
                    <span style="font-size:20pt;font-weight:bold;color:#1a3a6a;">BugTracer</span><br/>
                    <span style="font-size:11pt;color:#555555;">Security Vulnerability Report</span>
                </td>
                <td style="text-align:right;vertical-align:middle;font-size:9pt;color:#555555;">
                    Generated: {generated_at}<br/>
                    Total issues: {len(bug_report)}
                </td>
            </tr>
        </table>
        <p style="font-size:9pt;color:#333333;margin-bottom:14px;">
            <strong>Scanned directory:</strong> {directory_path}
        </p>
        """

        table_html = """
        <table style="border-collapse:collapse;width:100%;border:1px solid #cccccc;">
            <tr style="background-color:#1a3a6a;color:white;text-align:left;font-weight:bold;">
                <th style="padding:8px;width:25%;">Bug Type</th>
                <th style="padding:8px;width:25%;">File</th>
                <th style="padding:8px;">Explanation</th>
            </tr>
        """
        for i, bug in enumerate(bug_report):
            bug_type, file_path = bug[0], bug[1]
            parts = file_path.replace('\\', '/').split('/')
            short_path = '/'.join(parts[:5]) + ('/...' if len(parts) > 5 else '')
            explanation = get_bug_explanation(bug_type)
            row_bg = "#f5f8ff" if i % 2 == 0 else "#ffffff"
            table_html += (
                f"<tr style='background-color:{row_bg};'>"
                f"<td style='padding:8px;border:1px solid #dddddd;'>{bug_type}</td>"
                f"<td style='padding:8px;border:1px solid #dddddd;font-size:8pt;'>{short_path}</td>"
                f"<td style='padding:8px;border:1px solid #dddddd;font-size:9pt;'>{explanation}</td>"
                f"</tr>"
            )
        table_html += "</table>"

        html = f"<div>{header_html}</div><div>{table_html}</div>"
        with open(output_pdf, "wb") as f:
            pisa.CreatePDF(html, dest=f)

        pw = keyring.get_password("system", "user")
        if pw:
            self.encrypt_pdf(output_pdf, pw)

    def encrypt_pdf(self, pdf_path, password):
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

    # ── Auth ──────────────────────────────────────────────────────────────────

    def logout(self):
        main_window = self.centralwidget.window()
        main_window.hide()
        dlg = LoginDialog()
        if dlg.exec_() == QDialog.Accepted:
            main_window.show()
        else:
            sys.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    BugTracer = BugTracerWindow()
    ui = Ui_BugTracer()
    ui.setupUi(BugTracer)
    BugTracer._ui = ui
    BugTracer.setMinimumSize(868, 586)
    BugTracer.setWindowIcon(QtGui.QIcon("images/icon.png"))
    BugTracer.show()
    sys.exit(app.exec_())
