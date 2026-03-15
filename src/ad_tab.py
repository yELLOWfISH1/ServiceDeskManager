"""
Active Directory Tab - User Search
"""
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from .ldap_manager import LDAPManager


class ADTab(QWidget):
    """Active Directory user search tab"""

    def __init__(self):
        super().__init__()
        self.ldap_config = self.load_ad_config()
        self.setup_ui()

    def load_ad_config(self):
        """Load AD configuration from config.ini"""
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / "config.ini"
        if config_path.exists():
            config.read(config_path)
            return dict(config.items('AD')) if 'AD' in config else {}
        return {}

    def setup_ui(self):
        """Create a minimal AD search UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        title = QLabel("Search Active Directory Users")
        title.setObjectName("section-title")
        title.setStyleSheet("color: #2ecc71;")
        main_layout.addWidget(title)

        info_label = QLabel("Enter full or partial name/user ID to list all matches")
        info_label.setStyleSheet("color: #999999; font-size: 10px;")
        main_layout.addWidget(info_label)

        search_row = QHBoxLayout()
        self.user_search = QLineEdit()
        self.user_search.setPlaceholderText("e.g., Jack or jsmith")
        search_row.addWidget(self.user_search)

        search_btn = QPushButton("Search")
        search_btn.setMinimumHeight(32)
        search_btn.setMaximumWidth(100)
        search_btn.clicked.connect(self.search_user)
        search_row.addWidget(search_btn)

        main_layout.addLayout(search_row)

        self.user_result = QTextEdit()
        self.user_result.setReadOnly(True)
        self.user_result.setMinimumHeight(180)
        self.user_result.setStyleSheet("""
            QTextEdit {
                background-color: #0f1419;
                color: #2ecc71;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 10px;
            }
        """)
        main_layout.addWidget(self.user_result)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def test_ad_connection(self, show_dialog=True):
        """Simple AD connection test."""
        manager = LDAPManager(
            self.ldap_config.get('ldap_server', ''),
            int(self.ldap_config.get('ldap_port', '389')),
            self.ldap_config.get('ldap_base_dn', ''),
            '',
            ''
        )

        ok = manager.connect()
        manager.disconnect()

        if show_dialog:
            from PySide6.QtWidgets import QMessageBox
            if ok:
                QMessageBox.information(self, "AD Connection Test", "✅ AD connection successful.")
            else:
                QMessageBox.warning(
                    self,
                    "AD Connection Test",
                    "❌ AD connection failed.\n\nCheck src/config.ini and network connectivity."
                )

        return ok

    def search_user(self):
        """Search for users by partial name or user ID."""
        search_term = self.user_search.text().strip()
        if not search_term:
            self.user_result.setText("❌ Please enter a name or user ID")
            return

        manager = LDAPManager(
            self.ldap_config.get('ldap_server', ''),
            int(self.ldap_config.get('ldap_port', '389')),
            self.ldap_config.get('ldap_base_dn', ''),
            '',
            ''
        )

        if not manager.connect():
            self.user_result.setText("❌ Failed to connect to AD server")
            return

        users = manager.search_users(search_term)
        manager.disconnect()

        if not users:
            self.user_result.setText(f"❌ No users found for '{search_term}'")
            return

        lines = [f"Found {len(users)} user(s):", ""]
        for i, user_info in enumerate(users, start=1):
            lines.append(f"[{i}] Display Name: {user_info['displayName']}")
            lines.append(f"    User ID: {user_info['sAMAccountName']}")
            lines.append(f"    OU: {user_info['ou_windows']}")
            lines.append("")

        lines.append("[Easy Copy: Highlight and Ctrl+C]")
        self.user_result.setText("\n".join(lines))
        self.user_search.clear()
