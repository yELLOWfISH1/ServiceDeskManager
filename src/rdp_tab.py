"""
Remote Desktop Protocol (RDP) Tab - Bulk session launcher only
"""
import subprocess
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QTextEdit
from PySide6.QtCore import Qt


class RDPTab(QWidget):
    """Remote Desktop Protocol operations tab (bulk launch only)"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Create the RDP tab UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        title = QLabel("Launch RDP Sessions")
        title.setObjectName("section-title")
        title.setStyleSheet("color: #4a90e2;")
        main_layout.addWidget(title)

        instructions = QLabel("Enter computer names or IPs (one per line):")
        instructions.setStyleSheet("color: #999999; font-size: 10px;")
        main_layout.addWidget(instructions)

        self.computer_names_input = QTextEdit()
        self.computer_names_input.setPlaceholderText("Example:\nCOMPUTER-01\nCOMPUTER-02\n192.168.1.100")
        self.computer_names_input.setMinimumHeight(100)
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
        main_layout.addWidget(self.computer_names_input)

        launch_btn = QPushButton("Launch RDP Sessions")
        launch_btn.setMinimumHeight(32)
        launch_btn.clicked.connect(self.launch_rdp_sessions)
        main_layout.addWidget(launch_btn)

        self.launcher_status = QLabel("")
        self.launcher_status.setStyleSheet("font-size: 10px; color: #888888;")
        self.launcher_status.setWordWrap(True)
        main_layout.addWidget(self.launcher_status)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def launch_rdp_sessions(self):
        """Launch RDP sessions for each computer name entered"""
        computer_names_text = self.computer_names_input.toPlainText().strip()

        if not computer_names_text:
            self.launcher_status.setText("❌ Please enter at least one computer name")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #f44336;")
            return

        computer_names = [name.strip() for name in computer_names_text.split('\n') if name.strip()]

        if not computer_names:
            self.launcher_status.setText("❌ Please enter at least one computer name")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #f44336;")
            return

        failed_count = 0
        for computer_name in computer_names:
            try:
                subprocess.Popen(['mstsc.exe', f'/v:{computer_name}'])
            except Exception as e:
                failed_count += 1

        success_count = len(computer_names) - failed_count
        if failed_count == 0:
            self.launcher_status.setText(f"✅ Launched {success_count} RDP session(s)")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #4CAF50;")
        else:
            self.launcher_status.setText(f"⚠️ Launched {success_count}/{len(computer_names)} - {failed_count} failed")
            self.launcher_status.setStyleSheet("font-size: 10px; color: #FFC107;")
