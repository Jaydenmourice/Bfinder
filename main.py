from PyQt5 import QtCore, QtGui, QtWidgets
import PyPDF2
from PyQt5.QtWidgets import QLabel, QPushButton, QFileDialog, QVBoxLayout, QDialog, QLineEdit
import os
import sys
import keyring
from xhtml2pdf import pisa

from functions.bug_exp import (
    scan_html_file, scan_js_file, scan_php_file, scan_css_file,
    scan_ts_file, scan_json_file, scan_env_file, scan_xml_file,
    scan_sql_file, get_bug_explanation
)
from functions.sec_tip import get_random_security_tips


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        icon = QtGui.QIcon("images/icon.png")
        self.setWindowIcon(icon)
        self.setFixedSize(300, 150)

        self.layout = QVBoxLayout()

        self.password_label = QLabel("Enter System Password:")
        self.layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_password)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def check_password(self):
        entered_password = self.password_input.text()
        stored_password = keyring.get_password("system", "user") or "4321"
        if entered_password == stored_password:
            self.accept()
        else:
            self.password_input.clear()
            self.password_label.setText("Incorrect Password. Try again.")


class BfinderWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._ui = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._ui is not None:
            cw = self.centralWidget()
            self._ui.adjust_layout(cw.width(), cw.height())


class Ui_Bfinder(object):
    def setupUi(self, Bfinder):
        self.login_dialog = LoginDialog()
        if self.login_dialog.exec_() != QDialog.Accepted:
            sys.exit()

        self.bug_report_data = []

        Bfinder.setObjectName("Bfinder")
        Bfinder.resize(868, 586)
        Bfinder.setStyleSheet("\nbackground: rgb(119, 118, 123);")

        self.centralwidget = QtWidgets.QWidget(Bfinder)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 40, 91, 61))
        self.label.setText("")
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 20, 91, 81))
        self.label_2.setStyleSheet("background:transparent;")
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("images/logo.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setObjectName("label_2")

        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(20, 10, 231, 541))
        self.graphicsView.setStyleSheet(
            "background: rgb(94, 92, 100);\nborder-radius: 12px;\nborder: 2px solid #00bf63;"
        )
        self.graphicsView.setObjectName("graphicsView")

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(30, 120, 225, 71))
        self.widget.setStyleSheet("background:transparent;\ncursor:pointer;")
        self.widget.setObjectName("widget")

        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setGeometry(QtCore.QRect(12, 30, 180, 31))
        self.label_3.setStyleSheet(
            "font: 81 10pt \"Cantarell\";\nfont:bold;\ncolor: white;\nbackground:transparent;\n"
        )
        self.label_3.setObjectName("label_3")
        self.label_3.mousePressEvent = self.change_password_dialog

        self.label_4 = QtWidgets.QLabel(self.widget)
        self.label_4.setGeometry(QtCore.QRect(188, 30, 31, 31))
        self.label_4.setStyleSheet("background:transparent;")
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("images/change.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(740, 480, 101, 41))
        self.pushButton.setStyleSheet(
            "\nfont: 81 11pt \"Cantarell\";\nfont:bold;\ncolor:white;\nborder-radius:8px;\nbackground:#00bf63;\n"
        )
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.browse_directory)

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(270, 340, 451, 211))
        self.scrollArea.setStyleSheet(
            "background:rgb(94, 92, 100);\ncolor:white;\nborder: 1px solid #00bf63;\n"
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setLayout(QtWidgets.QVBoxLayout())
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 449, 209))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(270, 300, 451, 27))
        self.lineEdit.setStyleSheet(
            "border:none;\nfont: 81 11pt \"Cantarell\";\nfont:bold;\ncolor: white;\nbackground:transparent;"
        )
        self.lineEdit.setObjectName("lineEdit")

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(60, 480, 141, 41))
        self.pushButton_2.setStyleSheet(
            "\nfont: 81 11pt \"Cantarell\";\nfont:bold;\ncolor:white;\nborder-radius:8px;\nbackground:#00bf63;\n"
        )
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.print_report)

        self.scrollArea_2 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_2.setGeometry(QtCore.QRect(270, 80, 451, 211))
        self.scrollArea_2.setStyleSheet(
            "background:rgb(94, 92, 100);\ncolor:white;\nborder: 1px solid #00bf63;\n"
        )
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")

        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 449, 209))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.display_security_tips()

        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(270, 40, 451, 27))
        self.lineEdit_2.setStyleSheet(
            "border:none;\nfont: 81 11pt \"Cantarell\";\nfont:bold;\ncolor: white;\nbackground:transparent;"
        )
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setGeometry(QtCore.QRect(30, 200, 225, 71))
        self.widget_2.setStyleSheet("background:transparent;\ncursor:pointer;")
        self.widget_2.setObjectName("widget_2")

        self.label_5 = QtWidgets.QLabel(self.widget_2)
        self.label_5.setGeometry(QtCore.QRect(12, 30, 180, 31))
        self.label_5.setStyleSheet(
            "font: 81 10pt \"Cantarell\";\nfont:bold;\ncolor: white;\nbackground:transparent;\n"
        )
        self.label_5.setObjectName("label_5")
        self.label_5.mousePressEvent = self.show_usage_instructions

        self.label_6 = QtWidgets.QLabel(self.widget_2)
        self.label_6.setGeometry(QtCore.QRect(188, 30, 31, 31))
        self.label_6.setStyleSheet("background:transparent;")
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap("images/doc.png"))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")

        self.widget_3 = QtWidgets.QWidget(self.centralwidget)
        self.widget_3.setGeometry(QtCore.QRect(30, 280, 225, 71))
        self.widget_3.setStyleSheet("background:transparent;\ncursor:pointer;")
        self.widget_3.setObjectName("widget_3")

        self.label_7 = QtWidgets.QLabel(self.widget_3)
        self.label_7.setGeometry(QtCore.QRect(12, 30, 155, 31))
        self.label_7.setStyleSheet(
            "font: 81 10pt \"Cantarell\";\nfont:bold;\ncolor: white;\nbackground:transparent;\n"
        )
        self.label_7.setObjectName("label_7")
        self.label_7.mousePressEvent = self.show_contact_information

        self.label_8 = QtWidgets.QLabel(self.widget_3)
        self.label_8.setGeometry(QtCore.QRect(170, 30, 31, 31))
        self.label_8.setStyleSheet("background:transparent;")
        self.label_8.setText("")
        self.label_8.setPixmap(QtGui.QPixmap("images/con.png"))
        self.label_8.setScaledContents(True)
        self.label_8.setObjectName("label_8")

        self.pushButton_logout = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_logout.setGeometry(QtCore.QRect(60, 400, 141, 41))
        self.pushButton_logout.setStyleSheet(
            "\nfont: 81 10pt \"Cantarell\";\nfont:bold;\ncolor:white;\nborder-radius:8px;\nbackground:#c0392b;\n"
        )
        self.pushButton_logout.setObjectName("pushButton_logout")
        self.pushButton_logout.clicked.connect(self.logout)

        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(330, -160, 631, 601))
        self.label_9.setStyleSheet("background:none;")
        self.label_9.setText("")
        self.label_9.setPixmap(QtGui.QPixmap("images/ba.png"))
        self.label_9.setScaledContents(True)
        self.label_9.setObjectName("label_9")

        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(590, 110, 631, 601))
        self.label_10.setStyleSheet("background:none;")
        self.label_10.setText("")
        self.label_10.setPixmap(QtGui.QPixmap("images/ba.png"))
        self.label_10.setScaledContents(True)
        self.label_10.setObjectName("label_10")

        self.label_10.raise_()
        self.label_9.raise_()
        self.label.raise_()
        self.graphicsView.raise_()
        self.widget.raise_()
        self.pushButton.raise_()
        self.scrollArea.raise_()
        self.lineEdit.raise_()
        self.pushButton_2.raise_()
        self.pushButton_logout.raise_()
        self.scrollArea_2.raise_()
        self.lineEdit_2.raise_()
        self.widget_2.raise_()
        self.widget_3.raise_()
        self.label_2.raise_()
        Bfinder.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Bfinder)
        self.statusbar.setObjectName("statusbar")
        Bfinder.setStatusBar(self.statusbar)

        self.retranslateUi(Bfinder)
        QtCore.QMetaObject.connectSlotsByName(Bfinder)

    def retranslateUi(self, Bfinder):
        _translate = QtCore.QCoreApplication.translate
        Bfinder.setWindowTitle(_translate("Bfinder", "Bfinder"))
        self.label_3.setText(_translate("Bfinder", "Change password"))
        self.pushButton.setText(_translate("Bfinder", "Browse"))
        self.lineEdit.setText(_translate("Bfinder", "Potential bugs and vulnerabilities found"))
        self.lineEdit.setCursorPosition(0)
        self.pushButton_2.setText(_translate("Bfinder", "Print Report"))
        self.lineEdit_2.setText(_translate("Bfinder", "Software Security Tips"))
        self.lineEdit_2.setCursorPosition(0)
        self.label_5.setText(_translate("Bfinder", "Documentation"))
        self.label_7.setText(_translate("Bfinder", "Contacts"))
        self.pushButton_logout.setText(_translate("Bfinder", "Logout"))

    def adjust_layout(self, W, H):
        CONTENT_X = 270
        each_h = max(80, (H - 164) // 2)
        cw = W - CONTENT_X - 147          # keep same right gap as original for Browse button

        # Sidebar stretches full height
        self.graphicsView.setGeometry(20, 10, 231, H - 45)

        # Tips panel
        self.lineEdit_2.setGeometry(CONTENT_X, 40, cw, 27)
        self.scrollArea_2.setGeometry(CONTENT_X, 80, cw, each_h)

        # Bugs panel
        bugs_label_y = 80 + each_h + 9
        bugs_y = bugs_label_y + 40
        self.lineEdit.setGeometry(CONTENT_X, bugs_label_y, cw, 27)
        self.scrollArea.setGeometry(CONTENT_X, bugs_y, cw, max(50, H - bugs_y - 35))

        # Buttons anchor to bottom
        self.pushButton.setGeometry(W - 128, H - 106, 101, 41)
        self.pushButton_2.setGeometry(60, H - 106, 141, 41)
        self.pushButton_logout.setGeometry(60, H - 186, 141, 41)

        # Background decorations scale with the window
        self.label_9.setGeometry(CONTENT_X, -160, W - CONTENT_X + 50, H + 200)
        self.label_10.setGeometry(W - 278, 110, 450, H)

    def logout(self):
        main_window = self.centralwidget.window()
        main_window.hide()
        login_dialog = LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            main_window.show()
        else:
            sys.exit()

    def change_password_dialog(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            new_password, ok = QtWidgets.QInputDialog.getText(
                None, "Change Password", "Enter New Password:", QtWidgets.QLineEdit.Password
            )
            if ok:
                keyring.set_password("system", "user", new_password)
                QtWidgets.QMessageBox.information(None, "Password Changed", "Password changed successfully.")

    def show_usage_instructions(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            instructions_text = (
                "Here are the instructions on how to use the application:\n\n"
                "1. Click the Browse button and select your project directory.\n\n"
                "2. Bfinder will recursively scan HTML, JavaScript, TypeScript, PHP, CSS, JSON, .env, XML, and SQL files.\n\n"
                "3. Potential bugs and vulnerabilities will appear in the bottom panel.\n\n"
                "4. Click Print Report to save an encrypted PDF of the results."
            )
            QtWidgets.QMessageBox.information(None, "How to Use", instructions_text)

    def show_contact_information(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            contact_info = "Contact Information:\n\nEmail: example@example.com\nPhone: +1234567890"
            QtWidgets.QMessageBox.information(None, "Contact Information", contact_info)

    def browse_directory(self):
        directory_path = QFileDialog.getExistingDirectory(None, "Select Directory", "", QFileDialog.ShowDirsOnly)
        if directory_path:
            self.bug_report_data = self.scan_directory(directory_path)
            self.display_bug_report(self.bug_report_data)

    def display_security_tips(self):
        security_tips = get_random_security_tips()
        layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        for tip in security_tips:
            tip_label = QtWidgets.QLabel(tip)
            tip_label.setWordWrap(True)
            tip_label.setStyleSheet("font: 11pt \"Cantarell\";\ncolor: white;\nbackground: transparent;")
            layout.addWidget(tip_label)

    def display_bug_report(self, bug_report):
        layout = self.scrollAreaWidgetContents.layout()
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        if not bug_report:
            label = QtWidgets.QLabel("No bugs found!")
            label.setStyleSheet("color: white; background: transparent;")
            layout.addWidget(label)
        else:
            for idx, bug in enumerate(bug_report, start=1):
                bug_type, file_path = bug[0], bug[1]
                explanation = bug[2] if len(bug) == 3 else "No explanation available"
                label = QtWidgets.QLabel(f"{idx}. {bug_type}: {explanation}\nFile: {file_path}")
                label.setWordWrap(True)
                label.setStyleSheet("color: white; background: transparent;")
                layout.addWidget(label)

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

    def print_report(self):
        if self.bug_report_data:
            self.generate_pdf_report(self.bug_report_data)
            QtWidgets.QMessageBox.information(None, "Report successfully", "Report printed successfully.")
        else:
            QtWidgets.QMessageBox.warning(None, "No report", "No report to print. Please browse a directory first.")

    def generate_pdf_report(self, bug_report):
        directory_path = os.path.dirname(bug_report[0][1]) if bug_report else "Unknown"
        directory_name = os.path.basename(directory_path)
        output_pdf = f"{directory_name}_report.pdf"

        header_html = """
        <div style="display: flex;">
            <img src="images/pro.png" width="100" height="100"/>
        </div>
        """

        table_html = """
        <table style="border-collapse: collapse; width: 100%; border: 1px solid black;">
            <tr style="background-color: grey; color: whitesmoke; text-align: center; font-weight: bold;">
                <th style="padding: 8px;">Bug Type</th>
                <th>File</th>
                <th>Explanation</th>
            </tr>
        """
        for bug in bug_report:
            bug_type, file_path = bug[0], bug[1]
            file_path_words = file_path.replace('\\', '/').split('/')
            truncated_file_path = '/'.join(file_path_words[:5])
            if len(file_path_words) > 5:
                truncated_file_path += '/...'
            explanation = get_bug_explanation(bug_type)
            table_html += f"""
            <tr>
                <td style="padding: 8px;">{bug_type}</td>
                <td style="padding: 8px;">{truncated_file_path}</td>
                <td style="padding-left: 12px;">{explanation}</td>
            </tr>
            """
        table_html += "</table>"

        html_content = f'<div>{header_html}</div><div>{table_html}</div>'

        with open(output_pdf, "wb") as pdf_file:
            pisa.CreatePDF(html_content, dest=pdf_file)

        system_password = keyring.get_password("system", "user")
        if system_password:
            self.encrypt_pdf(output_pdf, system_password)

    def truncate_text(self, text, max_words):
        words = text.split()
        if len(words) > max_words:
            lines = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
            return "<br>".join(lines)
        return text

    def encrypt_pdf(self, pdf_path, password):
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_writer = PyPDF2.PdfWriter()
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            pdf_writer.encrypt(password)
            with open(pdf_path, 'wb') as encrypted_pdf:
                pdf_writer.write(encrypted_pdf)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Bfinder = BfinderWindow()
    ui = Ui_Bfinder()
    ui.setupUi(Bfinder)
    Bfinder._ui = ui
    Bfinder.setMinimumSize(868, 586)
    icon = QtGui.QIcon("images/icon.png")
    Bfinder.setWindowIcon(icon)
    Bfinder.show()
    sys.exit(app.exec_())
