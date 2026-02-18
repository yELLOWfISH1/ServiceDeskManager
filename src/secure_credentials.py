"""
Secure credential management using Windows Credential Manager
Credentials are encrypted by Windows DPAPI (Data Protection API)
"""
import keyring
from keyring.errors import KeyringError
from PySide6.QtWidgets import QLineEdit, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent


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
    
    def keyPressEvent(self, event: QKeyEvent):
        """Override to block copy/paste keyboard shortcuts"""
        # Block Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+Insert, Shift+Insert
        if event.matches(QKeyEvent.Copy) or \
           event.matches(QKeyEvent.Paste) or \
           event.matches(QKeyEvent.Cut) or \
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


class CredentialManager:
    """
    Manages secure credential storage using Windows Credential Manager
    
    Uses keyring library which interfaces with Windows DPAPI:
    - Credentials are encrypted by Windows
    - Stored securely in Windows Credential Manager
    - Can only be accessed by the same user on the same machine
    """
    
    SERVICE_NAME_PREFIX = "ServiceDeskManager"
    
    @staticmethod
    def save_credentials(credential_type: str, username: str, password: str) -> bool:
        """
        Save credentials securely
        
        Args:
            credential_type: Type of credential (e.g., 'AD', 'RDP')
            username: Username to store
            password: Password to store (will be encrypted by Windows)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            service_name = f"{CredentialManager.SERVICE_NAME_PREFIX}_{credential_type}"
            
            # Store password using Windows Credential Manager
            keyring.set_password(service_name, username, password)
            
            # Store the username separately (so we can retrieve it later)
            keyring.set_password(f"{service_name}_username", "default", username)
            
            return True
        except KeyringError as e:
            print(f"Failed to save credentials: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error saving credentials: {e}")
            return False
    
    @staticmethod
    def load_credentials(credential_type: str) -> tuple[str, str]:
        """
        Load credentials securely
        
        Args:
            credential_type: Type of credential (e.g., 'AD', 'RDP')
            
        Returns:
            Tuple of (username, password) or (None, None) if not found
        """
        try:
            service_name = f"{CredentialManager.SERVICE_NAME_PREFIX}_{credential_type}"
            
            # Retrieve username first
            username = keyring.get_password(f"{service_name}_username", "default")
            if not username:
                return None, None
            
            # Retrieve password using the username
            password = keyring.get_password(service_name, username)
            if not password:
                return None, None
            
            return username, password
        except KeyringError as e:
            print(f"Failed to load credentials: {e}")
            return None, None
        except Exception as e:
            print(f"Unexpected error loading credentials: {e}")
            return None, None
    
    @staticmethod
    def delete_credentials(credential_type: str) -> bool:
        """
        Delete stored credentials
        
        Args:
            credential_type: Type of credential (e.g., 'AD', 'RDP')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            service_name = f"{CredentialManager.SERVICE_NAME_PREFIX}_{credential_type}"
            
            # Get username first
            username = keyring.get_password(f"{service_name}_username", "default")
            if username:
                # Delete password
                try:
                    keyring.delete_password(service_name, username)
                except KeyringError:
                    pass  # Already deleted or doesn't exist
                
                # Delete username
                try:
                    keyring.delete_password(f"{service_name}_username", "default")
                except KeyringError:
                    pass  # Already deleted or doesn't exist
            
            return True
        except Exception as e:
            print(f"Error deleting credentials: {e}")
            return False
    
    @staticmethod
    def has_credentials(credential_type: str) -> bool:
        """
        Check if credentials exist for the given type
        
        Args:
            credential_type: Type of credential (e.g., 'AD', 'RDP')
            
        Returns:
            True if credentials exist, False otherwise
        """
        username, password = CredentialManager.load_credentials(credential_type)
        return username is not None and password is not None
