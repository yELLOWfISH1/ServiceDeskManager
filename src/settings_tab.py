"""
Settings Tab - Application-wide settings and credentials
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QGroupBox, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QKeySequence


class SecurePasswordField(QLineEdit):
    """
    Custom password field that:
    - Disables copy/paste operations
    - Masks input
    - Prevents context menu
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        self.setPlaceholderText("Enter password (copy/paste disabled)")
        # Ensure password mask characters are visible
        self.setStyleSheet("""
            QLineEdit {
                color: #ffffff;
                background-color: #1a1f26;
            }
        """)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Override to block copy/paste keyboard shortcuts"""
        # Block Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+Insert, Shift+Insert
        if event.matches(QKeySequence.Copy) or \
           event.matches(QKeySequence.Paste) or \
           event.matches(QKeySequence.Cut) or \
           (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Insert) or \
           (event.modifiers() == Qt.ShiftModifier and event.key() == Qt.Key_Insert):
            # Ignore the event
            event.ignore()
            return
        
        # Allow all other keys
        super().keyPressEvent(event)
    
    def contextMenuEvent(self, event):
        """Override to prevent right-click context menu"""
        # Block the context menu entirely
        event.ignore()
    
    def createStandardContextMenu(self):
        """Override to return empty menu"""
        return QMenu(self)


class SettingsTab(QWidget):
    """Application settings and credential management"""
    
    # Signal emitted when credentials are updated
    credentials_updated = Signal()
    
    def __init__(self):
        super().__init__()
        # In-memory storage only (cleared when app closes)
        self._username = ""
        self._password = ""
        self.setup_ui()

    def setup_ui(self):
        """Create the settings tab UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Title
        title = QLabel("Application Settings")
        title.setObjectName("section-title")
        main_layout.addWidget(title)
        
        # === Admin Credentials Section ===
        cred_group = QGroupBox("Administrator Credentials")
        cred_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c41e3a;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #1a1f26;
            }
            QGroupBox::title {
                color: #c41e3a;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        cred_layout = QVBoxLayout()
        cred_layout.setSpacing(10)
        
        # Info message
        info_label = QLabel(
            "🔒 Session-Only Credentials\n"
            "These credentials are stored in memory during your session and are automatically "
            "deleted when the application closes."
        )
        info_label.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        info_label.setWordWrap(True)
        cred_layout.addWidget(info_label)
        
        # Username field
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("username")
        self.username_field.textChanged.connect(self._on_credentials_changed)
        username_layout.addWidget(self.username_field)
        cred_layout.addLayout(username_layout)
        
        # Password field (secure - no copy/paste)
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_field = SecurePasswordField()
        self.password_field.textChanged.connect(self._on_credentials_changed)
        password_layout.addWidget(self.password_field)
        cred_layout.addLayout(password_layout)
        
        # Security notice
        security_notice = QLabel("⚠️ Copy/Paste disabled for security • Credentials stored in memory only")
        security_notice.setStyleSheet("color: #c41e3a; font-size: 9px; font-style: italic;")
        cred_layout.addWidget(security_notice)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.clear_creds_btn = QPushButton("🗑️ Clear Credentials")
        self.clear_creds_btn.clicked.connect(self.clear_credentials)
        self.clear_creds_btn.setMinimumHeight(32)
        button_layout.addWidget(self.clear_creds_btn)
        
        cred_layout.addLayout(button_layout)
        
        # Credential status
        self.cred_status_label = QLabel("ℹ️ Enter administrator credentials")
        self.cred_status_label.setStyleSheet("color: #888888; font-size: 10px;")
        cred_layout.addWidget(self.cred_status_label)
        
        cred_group.setLayout(cred_layout)
        main_layout.addWidget(cred_group)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # === Security Info Section ===
        security_group = QGroupBox("Security Information")
        security_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #1a1f26;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        security_layout = QVBoxLayout()
        
        security_info = QLabel(
            "✓ Credentials stored in RAM only\n"
            "✓ Automatically deleted when application closes\n"
            "✓ Never written to disk or Windows Credential Manager\n"
            "✓ Copy/paste protection on password field\n"
            "✓ Not logged or transmitted anywhere\n\n"
            "Note: You will need to re-enter credentials each time you start the application."
        )
        security_info.setStyleSheet("""
            color: #b0b0b0;
            font-size: 10px;
            line-height: 1.6;
        """)
        security_info.setWordWrap(True)
        security_layout.addWidget(security_info)
        
        security_group.setLayout(security_layout)
        main_layout.addWidget(security_group)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def _on_credentials_changed(self):
        """Called when username or password is changed"""
        self._username = self.username_field.text().strip()
        self._password = self.password_field.text()
        
        if self._username and self._password:
            self.cred_status_label.setText(f"✅ Credentials set for: {self._username}")
            self.cred_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
        else:
            self.cred_status_label.setText("ℹ️ Enter administrator credentials")
            self.cred_status_label.setStyleSheet("color: #888888; font-size: 10px;")
        
        # Notify other tabs that credentials have been updated
        self.credentials_updated.emit()
    
    def get_credentials(self):
        """
        Get current credentials from memory
        
        Returns:
            Tuple of (username, password) or (None, None) if not set
        """
        if self._username and self._password:
            return self._username, self._password
        return None, None
    
    def has_credentials(self):
        """Check if credentials are currently set"""
        return bool(self._username and self._password)
    
    def clear_credentials(self):
        """Clear credentials from memory"""
        reply = QMessageBox.question(
            self,
            "Clear Credentials",
            "Are you sure you want to clear the credentials from memory?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._username = ""
            self._password = ""
            self.username_field.clear()
            self.password_field.clear()
            self.cred_status_label.setText("ℹ️ Credentials cleared from memory")
            self.cred_status_label.setStyleSheet("color: #888888; font-size: 10px;")
            self.credentials_updated.emit()
