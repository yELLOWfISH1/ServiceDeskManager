"""
Remote Desktop Protocol (RDP) Tab - RDP Credential Auto-Typer
"""
import time
import subprocess
import pyautogui
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QMessageBox, QDialog, QApplication, QTextEdit, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon


class RDPAutoTyperWindow(QDialog):
    """
    Always-on-top popup window for auto-typing RDP credentials
    """
    
    def __init__(self, username, password, parent=None):
        super().__init__(None)  # Don't set parent to prevent focus issues
        self.username = username
        self.password = password
        self.setup_ui()
    
    def setup_ui(self):
        """Create the auto-typer popup window"""
        self.setWindowTitle("RDP Auto-Typer")
        self.setModal(False)
        
        # Set window icon
        icon_path = Path(__file__).parent.parent / "icons" / "scotiabank_logo_icon_170755.png"
        if icon_path.exists():
            try:
                self.setWindowIcon(QIcon(str(icon_path)))
            except Exception:
                pass
        
        # Make window stay on top of all other windows and prevent resizing
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.MSWindowsFixedSizeDialogHint
        )
        
        # Set fixed size (half the original)
        self.setFixedSize(200, 210)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1419;
            }
            QPushButton {
                background-color: #c41e3a;
                color: white;
                border: none;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #4a0a15;
            }
            QPushButton:pressed {
                background-color: #2d0609;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("RDP Auto-Typer")
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: #c41e3a;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Username button
        username_btn = QPushButton("⌨️ Username")
        username_btn.clicked.connect(self.type_username)
        username_btn.setMinimumHeight(28)
        layout.addWidget(username_btn)
        
        # Password button
        password_btn = QPushButton("🔒 Password")
        password_btn.clicked.connect(self.type_password)
        password_btn.setMinimumHeight(28)
        layout.addWidget(password_btn)
        
        # Both button
        both_btn = QPushButton("🔑 Both")
        both_btn.clicked.connect(self.type_both)
        both_btn.setMinimumHeight(28)
        layout.addWidget(both_btn)
        
        # Status/Ready indicator at bottom
        self.status_label = QLabel("✅ Ready")
        self.status_label.setStyleSheet("font-size: 10px; color: #4CAF50; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def countdown_and_type(self, type_func):
        """Show countdown then execute typing function"""
        # Keep window on top and focused
        self.raise_()
        self.activateWindow()
        
        # Countdown
        for i in range(3, 0, -1):
            self.status_label.setText(f"typing in {i}")
            self.status_label.setStyleSheet("font-size: 10px; color: #FFC107; font-weight: bold;")
            self.update()
            
            # Process events to keep UI responsive and window on top
            QApplication.processEvents()
            time.sleep(1)
            QApplication.processEvents()
        
        # Execute typing
        self.status_label.setText("✍️ typing...")
        self.update()
        QApplication.processEvents()
        time.sleep(0.2)
        QApplication.processEvents()
        
        try:
            type_func()
            self.status_label.setText("✅ done!")
            self.status_label.setStyleSheet("font-size: 10px; color: #4CAF50; font-weight: bold;")
        except Exception as e:
            self.status_label.setText(f"❌ error")
            self.status_label.setStyleSheet("font-size: 10px; color: #f44336; font-weight: bold;")
        
        self.update()
        QApplication.processEvents()
        
        # Keep window focused and on top
        self.raise_()
        self.activateWindow()
        
        # Reset status after 2 seconds
        QTimer.singleShot(2000, lambda: self.reset_status())
    
    def reset_status(self):
        """Reset status to ready"""
        self.status_label.setText("✅ Ready")
        self.status_label.setStyleSheet("font-size: 10px; color: #4CAF50; font-weight: bold;")
        self.update()
    
    def type_username(self):
        """Auto-type username only"""
        self.countdown_and_type(lambda: pyautogui.write(self.username, interval=0.05))
    
    def type_password(self):
        """Auto-type password only"""
        def type_pwd():
            pyautogui.write(self.password, interval=0.05)
            time.sleep(0.1)
            pyautogui.press('return')
        
        self.countdown_and_type(type_pwd)
    
    def type_both(self):
        """Auto-type username, press Tab, then password, then Enter"""
        def type_sequence():
            pyautogui.write(self.username, interval=0.05)
            time.sleep(0.2)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.write(self.password, interval=0.05)
            time.sleep(0.1)
            pyautogui.press('return')
        
        self.countdown_and_type(type_sequence)


class RDPTab(QWidget):
    """Remote Desktop Protocol operations tab"""
    
    def __init__(self, settings_tab=None):
        super().__init__()
        self.settings_tab = settings_tab
        self.auto_typer_window = None
        self.setup_ui()

    def setup_ui(self):
        """Create the RDP tab UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # ===== LAUNCH RDP SESSIONS SECTION =====
        launcher_title = QLabel("Launch RDP Sessions")
        launcher_title.setObjectName("section-title")
        launcher_title.setStyleSheet("color: #4a90e2;")
        main_layout.addWidget(launcher_title)
        
        launcher_container = QFrame()
        launcher_layout = QVBoxLayout()
        launcher_layout.setContentsMargins(0, 0, 0, 0)
        launcher_layout.setSpacing(8)
        
        # Instructions
        instructions = QLabel("Enter computer names or IPs (one per line):")
        instructions.setStyleSheet("color: #999999; font-size: 10px;")
        launcher_layout.addWidget(instructions)
        
        # Text area for computer names
        self.computer_names_input = QTextEdit()
        self.computer_names_input.setPlaceholderText("Example:\nCOMPUTER-01\nCOMPUTER-02\n192.168.1.100")
        self.computer_names_input.setMinimumHeight(80)
        self.computer_names_input.setStyleSheet("""
            QTextEdit {
                background-color: #0f1419;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 10px;
            }
        """)
        launcher_layout.addWidget(self.computer_names_input)
        
        # Launch button
        launch_btn = QPushButton("Launch RDP Sessions")
        launch_btn.setMinimumHeight(32)
        launch_btn.clicked.connect(self.launch_rdp_sessions)
        launcher_layout.addWidget(launch_btn)
        
        # Status label
        self.launcher_status = QLabel("")
        self.launcher_status.setStyleSheet("font-size: 10px; color: #888888;")
        self.launcher_status.setWordWrap(True)
        launcher_layout.addWidget(self.launcher_status)
        
        launcher_container.setLayout(launcher_layout)
        main_layout.addWidget(launcher_container)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator1)
        
        # ===== RDP AUTO-TYPER SECTION =====
        typer_title = QLabel("RDP Credential Auto-Typer")
        typer_title.setObjectName("section-title")
        typer_title.setStyleSheet("color: #c41e3a;")
        main_layout.addWidget(typer_title)
        
        typer_container = QFrame()
        typer_layout = QVBoxLayout()
        typer_layout.setContentsMargins(0, 0, 0, 0)
        typer_layout.setSpacing(8)
        
        # Description
        description = QLabel(
            "Opens a popup window to auto-type credentials into RDP sessions.\n"
            "Use when copy/paste is disabled in RDP."
        )
        description.setStyleSheet("color: #999999; font-size: 10px;")
        description.setWordWrap(True)
        typer_layout.addWidget(description)
        
        # Open button
        open_typer_btn = QPushButton("Open Auto-Typer")
        open_typer_btn.setMinimumHeight(32)
        open_typer_btn.clicked.connect(self.open_auto_typer)
        typer_layout.addWidget(open_typer_btn)
        
        typer_container.setLayout(typer_layout)
        main_layout.addWidget(typer_container)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator2)
        
        # ===== TIPS SECTION =====
        tips_title = QLabel("Tips")
        tips_title.setObjectName("section-title")
        tips_title.setStyleSheet("color: #2ecc71;")
        main_layout.addWidget(tips_title)
        
        tips_container = QFrame()
        tips_layout = QVBoxLayout()
        tips_layout.setContentsMargins(0, 0, 0, 0)
        tips_layout.setSpacing(4)
        
        tips = QLabel(
            "• Set your admin credentials in the Settings tab\n"
            "• Auto-Typer stays on top of all windows\n"
            "• 3-second countdown before typing begins"
        )
        tips.setStyleSheet("color: #999999; font-size: 10px;")
        tips.setWordWrap(True)
        tips_layout.addWidget(tips)
        
        tips_container.setLayout(tips_layout)
        main_layout.addWidget(tips_container)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def open_auto_typer(self):
        """Open the auto-typer window"""
        # Get credentials from settings tab
        username, password = self.get_credentials()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                "Credentials Required",
                "Please enter your credentials in the Settings tab first.\n\n"
                "The Auto-Typer needs username and password to function."
            )
            return
        
        # Close existing window if open
        if self.auto_typer_window:
            self.auto_typer_window.close()
        
        # Create and show new auto-typer window (no parent to prevent focus issues)
        self.auto_typer_window = RDPAutoTyperWindow(username, password)
        self.auto_typer_window.show()
        self.auto_typer_window.raise_()
        self.auto_typer_window.activateWindow()
        
        self.status_label.setText("✅ Auto-Typer window opened and pinned on top")
        self.status_label.setStyleSheet("font-size: 10px; color: #4CAF50;")
    
    def launch_rdp_sessions(self):
        """Launch RDP sessions for each computer name entered"""
        # Get computer names from text input
        computer_names_text = self.computer_names_input.toPlainText().strip()
        
        if not computer_names_text:
            self.launcher_status.setText("❌ Please enter at least one computer name")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #f44336;")
            return
        
        # Parse computer names (split by newline)
        computer_names = [name.strip() for name in computer_names_text.split('\n') if name.strip()]
        
        if not computer_names:
            self.launcher_status.setText("❌ Please enter at least one computer name")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #f44336;")
            return
        
        # Launch RDP sessions
        failed_count = 0
        for computer_name in computer_names:
            try:
                # Launch mstsc (Remote Desktop Connection) for each computer
                subprocess.Popen(['mstsc.exe', f'/v:{computer_name}'])
            except Exception as e:
                failed_count += 1
        
        # Show status
        success_count = len(computer_names) - failed_count
        if failed_count == 0:
            self.launcher_status.setText(f"✅ Launched {success_count} RDP session(s)")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #4CAF50;")
        else:
            self.launcher_status.setText(f"⚠️ Launched {success_count}/{len(computer_names)} - {failed_count} failed")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #FFC107;")
    
    def get_credentials(self):
        """Get credentials from settings tab"""
        if self.settings_tab:
            return self.settings_tab.get_credentials()
        return None, None
