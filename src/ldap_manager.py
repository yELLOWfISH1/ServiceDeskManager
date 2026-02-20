"""
Active Directory Manager - AD operations via PowerShell ActiveDirectory module.

Note:
The class name remains LDAPManager to preserve compatibility with existing imports.
"""
import json
import subprocess
from typing import Tuple, Optional, Dict


class LDAPManager:
    """Manager for Active Directory operations (PowerShell AD module backend)."""
    
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
        self.connected = False

    @staticmethod
    def _escape_ps(value: str) -> str:
        """Escape single quotes for PowerShell single-quoted strings."""
        return (value or "").replace("'", "''")

    def _credential_block(self) -> str:
        """Build PowerShell credential block if username/password are provided."""
        if self.username and self.password:
            user = self._escape_ps(self.username)
            pwd = self._escape_ps(self.password)
            return (
                f"$SecurePass = ConvertTo-SecureString '{pwd}' -AsPlainText -Force; "
                f"$Cred = New-Object System.Management.Automation.PSCredential('{user}', $SecurePass); "
            )
        return "$Cred = $null; "

    def _server_arg(self) -> str:
        """Build optional -Server argument for AD cmdlets."""
        if self.server_address:
            return f"-Server '{self._escape_ps(self.server_address)}'"
        return ""

    def _search_base_arg(self) -> str:
        """Build optional -SearchBase argument."""
        if self.base_dn:
            return f"-SearchBase '{self._escape_ps(self.base_dn)}'"
        return ""

    def _run_ps(self, script: str) -> Tuple[bool, str, str]:
        """Run a PowerShell script and return (success, stdout, stderr)."""
        try:
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    script,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            ok = completed.returncode == 0
            return ok, (completed.stdout or "").strip(), (completed.stderr or "").strip()
        except Exception as e:
            return False, "", str(e)

    @staticmethod
    def _format_error(error_text: str) -> str:
        text = (error_text or "").strip()
        lowered = text.lower()
        if "access is denied" in lowered or "insufficient access" in lowered or "unauthorized" in lowered:
            return "Access Denied: Your account does not have permission for this AD operation."
        if "active directory module" in lowered or "import-module" in lowered:
            return "ActiveDirectory PowerShell module is not available. Install RSAT AD tools."
        if "cannot find an object" in lowered:
            return "Object not found in Active Directory."
        return text if text else "Unknown error while executing AD operation."
    
    def connect(self) -> bool:
        """
        Establish LDAP connection
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        credential_block = self._credential_block()
        server_arg = self._server_arg()
        script = (
            "$ErrorActionPreference='Stop'; "
            "Import-Module ActiveDirectory -ErrorAction Stop; "
            f"{credential_block}"
            "$testParams = @{}; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $testParams['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            "if ($Cred) { $testParams['Credential'] = $Cred }; "
            "$null = Get-ADDomain @testParams; "
            "Write-Output 'OK'"
        )
        ok, out, _ = self._run_ps(script)
        self.connected = ok and out == "OK"
        return self.connected
    
    def disconnect(self):
        """Close LDAP connection"""
        self.connected = False
    
    def get_computer_info(self, hostname: str) -> Optional[Dict]:
        """
        Get computer object information (Description and OU)
        
        Args:
            hostname: Computer hostname (e.g., "COMPUTER-01")
        
        Returns:
            Dict with 'description' and 'ou' keys, or None if not found
        """
        if not self.connected:
            if not self.connect():
                return None

        host = self._escape_ps(hostname)
        credential_block = self._credential_block()
        server_arg = self._server_arg()
        search_base_arg = self._search_base_arg()
        script = (
            "$ErrorActionPreference='Stop'; "
            "Import-Module ActiveDirectory -ErrorAction Stop; "
            f"{credential_block}"
            "$params = @{ Filter = \"Name -eq '" + host + "'\"; Properties = @('Description','DistinguishedName') }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $params['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            f"if ('{self._escape_ps(self.base_dn)}') {{ $params['SearchBase'] = '{self._escape_ps(self.base_dn)}' }}; "
            "if ($Cred) { $params['Credential'] = $Cred }; "
            "$comp = Get-ADComputer @params | Select-Object -First 1 Name,Description,DistinguishedName; "
            "if (-not $comp) { Write-Output '{}' ; exit 0 }; "
            "$comp | ConvertTo-Json -Compress"
        )
        ok, out, _ = self._run_ps(script)
        if not ok or not out:
            return None

        try:
            data = json.loads(out)
            if not data:
                return None
            dn = str(data.get("DistinguishedName", ""))
            ou = dn.split(',', 1)[1] if ',' in dn else "Unknown OU"
            return {
                'description': str(data.get('Description') or "No description"),
                'ou': str(ou),
                'dn': dn,
            }
        except Exception:
            return None
    
    def delete_computer(self, hostname: str) -> Tuple[bool, str]:
        """
        Delete a computer object from AD
        
        Args:
            hostname: Computer hostname (e.g., "COMPUTER-01")
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.connected:
            if not self.connect():
                return False, "Failed to connect to AD server"

        host = self._escape_ps(hostname)
        credential_block = self._credential_block()
        script = (
            "$ErrorActionPreference='Stop'; "
            "Import-Module ActiveDirectory -ErrorAction Stop; "
            f"{credential_block}"
            "$params = @{ Filter = \"Name -eq '" + host + "'\" }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $params['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            f"if ('{self._escape_ps(self.base_dn)}') {{ $params['SearchBase'] = '{self._escape_ps(self.base_dn)}' }}; "
            "if ($Cred) { $params['Credential'] = $Cred }; "
            "$comp = Get-ADComputer @params | Select-Object -First 1 DistinguishedName; "
            "if (-not $comp) { throw \"Computer not found\" }; "
            "$removeParams = @{ Identity = $comp.DistinguishedName; Confirm = $false }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $removeParams['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            "if ($Cred) { $removeParams['Credential'] = $Cred }; "
            "Remove-ADComputer @removeParams; "
            "Write-Output 'OK'"
        )
        ok, out, err = self._run_ps(script)
        if ok and out == "OK":
            return True, f"Computer '{hostname}' successfully deleted from AD"

        if "Computer not found" in err:
            return False, f"Computer '{hostname}' not found in AD"
        return False, self._format_error(err)
    
    def move_computer(self, hostname: str, target_ou: str) -> Tuple[bool, str]:
        """
        Move a computer object to a different OU
        
        Args:
            hostname: Computer hostname
            target_ou: Target OU DN (e.g., "OU=Workstations,DC=mydomain,DC=com")
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.connected:
            if not self.connect():
                return False, "Failed to connect to AD server"

        host = self._escape_ps(hostname)
        target = self._escape_ps(target_ou)
        credential_block = self._credential_block()
        script = (
            "$ErrorActionPreference='Stop'; "
            "Import-Module ActiveDirectory -ErrorAction Stop; "
            f"{credential_block}"
            "$params = @{ Filter = \"Name -eq '" + host + "'\" }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $params['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            f"if ('{self._escape_ps(self.base_dn)}') {{ $params['SearchBase'] = '{self._escape_ps(self.base_dn)}' }}; "
            "if ($Cred) { $params['Credential'] = $Cred }; "
            "$comp = Get-ADComputer @params | Select-Object -First 1 DistinguishedName; "
            "if (-not $comp) { throw \"Computer not found\" }; "
            "$moveParams = @{ Identity = $comp.DistinguishedName; TargetPath = '" + target + "' }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $moveParams['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            "if ($Cred) { $moveParams['Credential'] = $Cred }; "
            "Move-ADObject @moveParams; "
            "Write-Output 'OK'"
        )
        ok, out, err = self._run_ps(script)
        if ok and out == "OK":
            return True, f"Computer '{hostname}' successfully moved to {target_ou}"

        if "Computer not found" in err:
            return False, f"Computer '{hostname}' not found in AD"
        return False, self._format_error(err)

    def update_computer_description(self, hostname: str, description: str) -> Tuple[bool, str]:
        """
        Update a computer object's Description in AD.

        Args:
            hostname: Computer hostname
            description: New description (empty string clears value)

        Returns:
            Tuple of (success, message)
        """
        if not self.connected:
            if not self.connect():
                return False, "Failed to connect to AD server"

        host = self._escape_ps(hostname)
        desc = self._escape_ps(description)
        credential_block = self._credential_block()
        script = (
            "$ErrorActionPreference='Stop'; "
            "Import-Module ActiveDirectory -ErrorAction Stop; "
            f"{credential_block}"
            "$params = @{ Filter = \"Name -eq '" + host + "'\" }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $params['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            f"if ('{self._escape_ps(self.base_dn)}') {{ $params['SearchBase'] = '{self._escape_ps(self.base_dn)}' }}; "
            "if ($Cred) { $params['Credential'] = $Cred }; "
            "$comp = Get-ADComputer @params | Select-Object -First 1 DistinguishedName; "
            "if (-not $comp) { throw \"Computer not found\" }; "
            "$setParams = @{ Identity = $comp.DistinguishedName }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $setParams['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            "if ($Cred) { $setParams['Credential'] = $Cred }; "
            "if ('" + desc + "' -eq '') { $setParams['Clear'] = @('Description') } else { $setParams['Description'] = '" + desc + "' }; "
            "Set-ADComputer @setParams; "
            "Write-Output 'OK'"
        )
        ok, out, err = self._run_ps(script)
        if ok and out == "OK":
            return True, f"Computer '{hostname}' description updated successfully"
        if "Computer not found" in err:
            return False, f"Computer '{hostname}' not found in AD"
        return False, self._format_error(err)

    def search_users(self, search_term: str):
        """
        Search for all users matching name/userid fragments.

        Args:
            search_term: name or userid fragment

        Returns:
            list[dict]: matching users
        """
        if not self.connected:
            if not self.connect():
                return []

        term = self._escape_ps(search_term)
        credential_block = self._credential_block()
        script = (
            "$ErrorActionPreference='Stop'; "
            "Import-Module ActiveDirectory -ErrorAction Stop; "
            f"{credential_block}"
            "$filter = \"SamAccountName -like '*" + term + "*' -or UserPrincipalName -like '*" + term + "*' -or Name -like '*" + term + "*' -or DisplayName -like '*" + term + "*'\"; "
            "$params = @{ Filter = $filter; Properties = @('DisplayName','SamAccountName','DistinguishedName') }; "
            f"if ('{self._escape_ps(self.server_address)}') {{ $params['Server'] = '{self._escape_ps(self.server_address)}' }}; "
            f"if ('{self._escape_ps(self.base_dn)}') {{ $params['SearchBase'] = '{self._escape_ps(self.base_dn)}' }}; "
            "if ($Cred) { $params['Credential'] = $Cred }; "
            "$users = Get-ADUser @params | Sort-Object Name | Select-Object DisplayName,SamAccountName,DistinguishedName; "
            "if (-not $users) { Write-Output '[]'; exit 0 }; "
            "$users | ConvertTo-Json -Compress"
        )
        ok, out, _ = self._run_ps(script)
        if not ok or not out:
            return []

        try:
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            results = []
            for entry in data:
                dn = str(entry.get("DistinguishedName", ""))
                ou_ldap = dn.split(',', 1)[1] if ',' in dn else "Unknown OU"
                results.append({
                    'displayName': str(entry.get('DisplayName') or "N/A"),
                    'sAMAccountName': str(entry.get('SamAccountName') or "N/A"),
                    'ou_ldap': str(ou_ldap),
                    'ou_windows': str(self._dn_to_windows_path(dn)),
                    'dn': dn,
                })
            return results
        except Exception:
            return []
    
    def search_user(self, search_term: str) -> Optional[Dict]:
        """
        Search for a user by name or user ID
        
        Args:
            search_term: Full name or user ID (sAMAccountName)
        
        Returns:
            Dict with user info including OU in both LDAP and Windows formats
        """
        users = self.search_users(search_term)
        return users[0] if users else None
    
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
