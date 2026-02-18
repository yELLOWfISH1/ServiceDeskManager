"""
LDAP Manager - Active Directory operations using ldap3
"""
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
from typing import Tuple, Optional, Dict, List


class LDAPManager:
    """Manager for Active Directory LDAP operations"""
    
    def __init__(self, server_address: str, server_port: int, base_dn: str, username: str, password: str):
        """
        Initialize LDAP connection parameters
        
        Args:
            server_address: LDAP server hostname or IP
            server_port: LDAP server port (usually 389 or 636)
            base_dn: Base DN for searches (e.g., "DC=mydomain,DC=com")
            username: Admin username
            password: Admin password
        """
        self.server_address = server_address
        self.server_port = server_port
        self.base_dn = base_dn
        self.username = username
        self.password = password
        self.connection = None
    
    def connect(self) -> bool:
        """
        Establish LDAP connection
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            server = Server(self.server_address, port=self.server_port, get_info=ALL)
            self.connection = Connection(server, user=self.username, password=self.password)
            return self.connection.bind()
        except Exception as e:
            print(f"LDAP Connection Error: {e}")
            return False
    
    def disconnect(self):
        """Close LDAP connection"""
        if self.connection:
            self.connection.unbind()
            self.connection = None
    
    def get_computer_info(self, hostname: str) -> Optional[Dict]:
        """
        Get computer object information (Description and OU)
        
        Args:
            hostname: Computer hostname (e.g., "COMPUTER-01")
        
        Returns:
            Dict with 'description' and 'ou' keys, or None if not found
        """
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            # Search for computer by name
            search_filter = f"(&(objectClass=computer)(cn={hostname}))"
            self.connection.search(self.base_dn, search_filter, attributes=['description', 'distinguishedName'])
            
            if not self.connection.entries:
                return None
            
            entry = self.connection.entries[0]
            description = entry.description.value if hasattr(entry, 'description') and entry.description else "No description"
            dn = entry.distinguishedName.value
            
            # Extract OU from DN (everything except the CN part)
            ou = dn.split(',', 1)[1] if ',' in dn else "Unknown OU"
            
            return {
                'description': str(description),
                'ou': str(ou),
                'dn': str(dn)
            }
        except Exception as e:
            print(f"Error getting computer info: {e}")
            return None
    
    def delete_computer(self, hostname: str) -> Tuple[bool, str]:
        """
        Delete a computer object from AD
        
        Args:
            hostname: Computer hostname (e.g., "COMPUTER-01")
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.connection:
            if not self.connect():
                return False, "Failed to connect to LDAP server"
        
        try:
            # Get full DN by searching for the computer
            search_filter = f"(&(objectClass=computer)(cn={hostname}))"
            self.connection.search(self.base_dn, search_filter, attributes=['distinguishedName'])
            
            if not self.connection.entries:
                return False, f"Computer '{hostname}' not found in AD"
            
            dn = self.connection.entries[0].distinguishedName.value
            
            # Delete the computer object
            self.connection.delete(dn)
            
            if self.connection.result['result'] == 0:
                return True, f"Computer '{hostname}' successfully deleted from AD"
            elif self.connection.result['result'] == 49:
                # LDAP error 49 means invalid credentials or access denied
                return False, "Access Denied: Your admin account does not have permission to delete computers in AD. Contact your domain administrator."
            elif self.connection.result['result'] in [12, 1]:
                # LDAP errors for insufficient access rights
                return False, "Access Denied: Your admin account does not have sufficient permissions to delete this computer object."
            else:
                return False, f"Failed to delete: {self.connection.result['message']}"
        
        except Exception as e:
            error_msg = str(e).lower()
            if 'insufficient access' in error_msg or '0x80070005' in error_msg:
                return False, "Access Denied: Your admin account does not have permission to delete computers in AD."
            return False, f"Error deleting computer: {str(e)}"
    
    def move_computer(self, hostname: str, target_ou: str) -> Tuple[bool, str]:
        """
        Move a computer object to a different OU
        
        Args:
            hostname: Computer hostname
            target_ou: Target OU DN (e.g., "OU=Workstations,DC=mydomain,DC=com")
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.connection:
            if not self.connect():
                return False, "Failed to connect to LDAP server"
        
        try:
            # Get the current DN of the computer
            search_filter = f"(&(objectClass=computer)(cn={hostname}))"
            self.connection.search(self.base_dn, search_filter, attributes=['distinguishedName'])
            
            if not self.connection.entries:
                return False, f"Computer '{hostname}' not found in AD"
            
            current_dn = self.connection.entries[0].distinguishedName.value
            rdn = f"CN={hostname}"
            
            # Move the computer (modify_dn operation)
            self.connection.modify_dn(current_dn, rdn, new_superior=target_ou)
            
            if self.connection.result['result'] == 0:
                return True, f"Computer '{hostname}' successfully moved to {target_ou}"
            elif self.connection.result['result'] == 49:
                # LDAP error 49 means invalid credentials or access denied
                return False, "Access Denied: Your admin account does not have permission to move computers in AD. Contact your domain administrator."
            elif self.connection.result['result'] in [12, 1]:
                # LDAP errors for insufficient access rights
                return False, "Access Denied: Your admin account does not have sufficient permissions to move this computer object."
            else:
                return False, f"Failed to move: {self.connection.result['message']}"
        
        except Exception as e:
            error_msg = str(e).lower()
            if 'insufficient access' in error_msg or '0x80070005' in error_msg:
                return False, "Access Denied: Your admin account does not have permission to move computers in AD."
            return False, f"Error moving computer: {str(e)}"
    
    def search_user(self, search_term: str) -> Optional[Dict]:
        """
        Search for a user by name or user ID
        
        Args:
            search_term: Full name or user ID (sAMAccountName)
        
        Returns:
            Dict with user info including OU in both LDAP and Windows formats
        """
        try:
            # Try searching by display name OR sAMAccountName - handles both name and userid
            search_filter = f"(&(objectClass=user)(|(displayName=*{search_term}*)(sAMAccountName={search_term})))"
            self.connection.search(self.base_dn, search_filter, attributes=['displayName', 'sAMAccountName', 'distinguishedName'])
            
            if not self.connection.entries:
                return None
            
            entry = self.connection.entries[0]
            dn = entry.distinguishedName.value
            display_name = entry.displayName.value if hasattr(entry, 'displayName') and entry.displayName else "N/A"
            sam_account = entry.sAMAccountName.value if hasattr(entry, 'sAMAccountName') and entry.sAMAccountName else "N/A"
            
            # Extract OU from DN (LDAP format)
            ou_ldap = dn.split(',', 1)[1] if ',' in dn else "Unknown OU"
            
            # Convert DN to Windows-style path
            ou_windows = self._dn_to_windows_path(dn)
            
            return {
                'displayName': str(display_name),
                'sAMAccountName': str(sam_account),
                'ou_ldap': str(ou_ldap),
                'ou_windows': str(ou_windows),
                'dn': str(dn)
            }
        except Exception as e:
            print(f"Error searching user: {e}")
            return None
    
    def _dn_to_windows_path(self, dn: str) -> str:
        r"""
        Convert LDAP DN to Windows-style OU path
        
        Example:
            Input: CN=John Smith,OU=Users,OU=TestOU,DC=mydomain,DC=com
            Output: mydomain.com\TestOU\Users
        
        Args:
            dn: Distinguished Name string
        
        Returns:
            Windows-style path (domain\OU1\OU2\...)
        """
        try:
            # Split DN into parts
            parts = [p.strip() for p in dn.split(',')]
            
            # Extract DC parts for domain
            dc_parts = []
            ou_parts = []
            
            for part in parts:
                if part.startswith('DC='):
                    dc_parts.append(part.split('=')[1])
                elif part.startswith('OU='):
                    ou_parts.append(part.split('=')[1])
            
            # Build Windows path: domain\OU1\OU2\... (reverse OU order)
            domain = '.'.join(dc_parts) if dc_parts else 'domain'
            if ou_parts:
                ou_parts.reverse()  # Reverse to get correct hierarchy
                windows_path = domain + '\\' + '\\'.join(ou_parts)
            else:
                windows_path = domain
            
            return windows_path
        except Exception as e:
            return f"Error converting path: {str(e)}"
    
    @staticmethod
    def convert_windows_path_to_dn(windows_ou_path: str, base_dc: str) -> str:
        """
        Convert Windows-style OU path to LDAP DN format
        
        Example:
            Input: "mydomain\\testou\\testcomputerou"
            Output: "OU=testcomputerou,OU=testou,DC=mydomain,DC=com"
        
        Args:
            windows_ou_path: Windows-style path (backslash separated)
            base_dc: Base DC string (e.g., "mydomain,com" or "mydomain,local")
        
        Returns:
            LDAP DN format
        """
        parts = windows_ou_path.split('\\')
        
        # Remove domain part if included
        if parts[0].lower() == parts[0].split('.')[0]:  # If first part looks like domain
            parts = parts[1:]
        
        # Build OU parts in reverse (LDAP format)
        ou_parts = [f"OU={part}" for part in reversed(parts)]
        
        # Add DC parts
        dc_parts = base_dc.split('.')
        dc_string = ','.join([f"DC={part}" for part in dc_parts])
        
        return ','.join(ou_parts) + (',' + dc_string if dc_string else '')
