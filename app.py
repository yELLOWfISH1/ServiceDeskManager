"""
Service Desk Manager - PySide6 GUI Application
Professional service desk automation tool
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QFrame
)
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import Qt, QTimer

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import APP_TITLE, APP_WIDTH, APP_HEIGHT, OUTPUT_DIR
from src.email_tab import EmailTab
from src.ping_tab import PingTab
from src.logger import log_info, log_error


class SendEmailsManager(QMainWindow):
    """Main application window with PySide6"""

    def __init__(self):
        super().__init__()
        log_info("Starting Service Desk Manager application")
        
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)
        self.setMinimumSize(1000, 700)
        
        # Set window icon
        icon_path = Path(__file__).parent / "icons" / "scotiabank_logo_icon_170755.png"
        if icon_path.exists():
            try:
                self.setWindowIcon(QIcon(str(icon_path)))
            except Exception as e:
                log_error("Failed to load window icon", e)
        
        # Apply stylesheet
        self.apply_stylesheet()
        
        # Create UI
        self.create_ui()
        log_info("Application UI created successfully")

    def apply_stylesheet(self):
        """Apply professional red/dark theme stylesheet"""
        style = """
        QMainWindow {
            background-color: #0f1419;
        }
        
        QWidget {
            background-color: #0f1419;
            color: #ffffff;
        }
        
        QTabWidget::pane {
            border: none;
            background-color: #0f1419;
        }
        
        QTabBar::tab {
            background-color: #1a1f26;
            color: #ffffff;
            padding: 8px 20px;
            border: none;
            border-bottom: 3px solid transparent;
            font-weight: bold;
        }
        
        QTabBar::tab:selected {
            background-color: #c41e3a;
            border-bottom: 3px solid #ff4455;
            color: #ffffff;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #252d35;
            color: #ff9999;
        }
        
        QPushButton {
            background-color: #c41e3a;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 11px;
        }
        
        QPushButton:hover {
            background-color: #e6233d;
        }
        
        QPushButton:pressed {
            background-color: #a01830;
        }
        
        QPushButton:disabled {
            background-color: #555555;
            color: #999999;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            background-color: #1a1f26;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 6px;
            selection-background-color: #c41e3a;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #c41e3a;
            background-color: #262d35;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QLabel#title {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
        }
        
        QLabel#subtitle {
            font-size: 11px;
            color: #999999;
        }
        
        QLabel#section-title {
            font-size: 13px;
            font-weight: bold;
            color: #c41e3a;
        }
        
        QCheckBox {
            color: #ffffff;
            spacing: 6px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #1a1f26;
            border: 1px solid #333333;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #c41e3a;
            border: 1px solid #c41e3a;
            border-radius: 3px;
        }
        
        QProgressBar {
            background-color: #1a1f26;
            border: 1px solid #333333;
            border-radius: 4px;
            height: 24px;
            text-align: center;
            color: #ffffff;
        }
        
        QProgressBar::chunk {
            background-color: #c41e3a;
            border-radius: 2px;
        }
        
        QTreeWidget, QTableWidget {
            background-color: #1a1f26;
            alternate-background-color: #252d35;
            gridline-color: #333333;
            border: 1px solid #333333;
            border-radius: 4px;
        }
        
        QTreeWidget::item:selected, QTableWidget::item:selected {
            background-color: #c41e3a;
            color: #ffffff;
        }
        
        QHeaderView::section {
            background-color: #0f1419;
            color: #ffffff;
            padding: 6px;
            border: none;
            border-right: 1px solid #333333;
            font-weight: bold;
        }
        
        QScrollBar:vertical {
            background-color: #1a1f26;
            width: 12px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #c41e3a;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #e6233d;
        }
        
        QScrollBar:horizontal {
            background-color: #1a1f26;
            height: 12px;
            border: none;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #c41e3a;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #e6233d;
        }
        
        QFrame#header {
            background-color: #1a1f26;
            border-bottom: 1px solid #333333;
            padding: 16px;
        }
        
        QFrame#footer {
            background-color: #1a1f26;
            border-top: 1px solid #333333;
            padding: 12px;
        }
        """
        self.setStyleSheet(style)

    def create_ui(self):
        """Create main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setObjectName("mainTabs")
        
        # Email tab (primary)
        email_tab = EmailTab()
        tabs.addTab(email_tab, "Send Emails")
        
        # Ping tab (secondary)
        ping_tab = PingTab()
        tabs.addTab(ping_tab, "Ping Hosts")
        
        main_layout.addWidget(tabs, 1)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
        central_widget.setLayout(main_layout)

    def create_header(self):
        """Create header frame with title and description"""
        header = QFrame()
        header.setObjectName("header")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        title = QLabel(APP_TITLE)
        title.setObjectName("title")
        layout.addWidget(title)
        
        subtitle = QLabel(
            "This is for Scotiabank Service Desk for sending bulk emails to customers "
            "for upcoming changes, to include as much information as possible"
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        header.setLayout(layout)
        return header

    def create_footer(self):
        """Create footer with status and action buttons"""
        footer = QFrame()
        footer.setObjectName("footer")
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #999999; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        # Spacer
        layout.addStretch()
        
        # Open Output Folder button
        open_folder_btn = QPushButton("Open Output Folder")
        open_folder_btn.clicked.connect(self.open_output_folder)
        layout.addWidget(open_folder_btn)
        
        # About button
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about)
        layout.addWidget(about_btn)
        
        footer.setLayout(layout)
        return footer

    def open_output_folder(self):
        """Open output folder in file explorer"""
        try:
            import subprocess
            subprocess.Popen(f'explorer "{OUTPUT_DIR}"')
            self.status_label.setText("Opened output folder")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        
        about_text = f"""{APP_TITLE}

Version: 1.0

Description:
This is for Scotiabank Service Desk for sending bulk emails to customers for upcoming changes. The tool is designed to include as much information as possible in each message, validate templates, and streamline bulk communication workflows.

Features:
• Compose and send bulk emails using Outlook templates
• Extract and map template keywords to spreadsheet columns
• Preview messages and send in preview mode
• Secondary utilities for resolving hostnames and pinging IPs

Built with PySide6 for a professional interface."""
        
        QMessageBox.information(self, "About", about_text)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Show splash screen
    from src.splash_screen import create_splash_screen
    splash = create_splash_screen()
    
    try:
        window = SendEmailsManager()
        
        # Connect splash finished signal to show main window and close splash
        def on_splash_finished():
            splash.close()
            window.show()
        
        splash.finished.connect(on_splash_finished)
        
        sys.exit(app.exec())
    except Exception as e:
        log_error("Fatal error during application startup", e)
        splash.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
