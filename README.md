# Service Desk Manager v2.1

A comprehensive service desk automation tool for managing email campaigns, network diagnostics, RDP session management, and Active Directory operations.

**Created by Jack Whatley**

## Features

### 📧 Email Management
- **Bulk Email Sending**: Send personalized emails to multiple recipients from Excel or CSV files
- **Template Support**: Use Outlook email templates (.oft files) with dynamic keyword replacement
- **Keyword Mapping**: Automatically extract placeholders ({{Name}}, {{IP}}, etc.) from templates and map them to spreadsheet columns
- **Template Editing**: Edit templates directly in Outlook without leaving the application
- **Preview Mode**: Preview emails before sending to verify content
- **BCC Support**: Optionally BCC emails to a specified address
- **Progress Tracking**: Real-time progress bar showing email sending status

### 🔍 Network Diagnostics (Ping)
- **Batch Ping Operations**: Ping multiple hostnames/IPs simultaneously
- **IP Resolution**: Automatic DNS resolution and IP address lookup
- **Multithreaded Execution**: Concurrent pinging for fast results
- **CSV Export**: Save results to CSV file for reporting
- **Response Time Tracking**: Capture ping response times for performance analysis

### 🖥️ RDP Management
- **Bulk RDP Session Launcher**: Launch multiple RDP sessions simultaneously from a list of computer names or IPs
- **RDP Credential Auto-Typer**: Always-on-top popup window that auto-types credentials into RDP sessions
  - Useful when copy/paste is disabled in RDP
  - 3-second countdown before typing
  - Options: Username only, Password only, or Both
  - Auto-types credentials with Tab and Enter key simulation
  - Window stays pinned on top of all applications

### 🗂️ Active Directory Management
- **Computer Deletion**: Delete computers from Active Directory with safety confirmations
  - Shows computer description and current OU before deletion
  - Warns user to check ServiceNow before proceeding
  - Permission checking with user-friendly error messages
- **PC Movement**: Move computers between Organizational Units
  - Single computer movement with dropdown OU selection
  - Bulk movement from Excel spreadsheet import
  - Pre-configured OU list from config file
- **User Search**: Search for users by full name or user ID
  - Searches both displayName and sAMAccountName
  - Displays Windows-style OU path (e.g., domain.com\IT\Users)
  - Does not require admin credentials
- **PowerShell AD Integration**: Uses the ActiveDirectory PowerShell module for faster AD operations
   - Connection management with configurable AD server/base DN settings
  - Permission error detection and user-friendly messages
  - DN to Windows path conversion for readability

### 📁 Template Management
- **Template Repository**: Store and manage multiple email templates
- **Auto-Sync**: Templates are automatically copied to Outlook's template folder on startup
- **Quick Access**: Dropdown selection of all available templates
- **Refresh Function**: Reload template list without restarting

### 🔐 Security
- **In-Memory Credentials**: Admin credentials stored in memory only (deleted on app close)
- **No Disk Persistence**: Credentials never written to disk
- **Copy/Paste Protection**: Password fields block copy/paste operations
- **Secure Input**: Password fields use masked input

## How It Works

### Email Tab (Step-by-Step)

**Step 1: Load Recipient Data**
1. Click "Browse..." to select an Excel (.xlsx, .xls) or CSV file
2. File must contain at least an "email" column (case-insensitive)
3. Preview shows first 5 rows with up to 5 columns
4. Specify email column name if different (default: "email")

**Step 2: Select Email Template**
1. Choose a template from the dropdown
2. Keywords found in the template appear automatically
3. Click "Refresh" to reload templates
4. Click "✏️ Edit Template" to modify in Outlook
5. Click "➕ Add Template" to import a new template

**Step 3: Map Keywords to Columns**
1. For each keyword found in the template (e.g., {{Name}}, {{IP}})
2. Select which column from your spreadsheet contains the data
3. Use "[Select Column]" placeholder if a keyword isn't needed

**Step 4: Send Emails**
1. Optionally add a BCC email
2. Check "Preview Mode" to display emails without sending
3. Click "Send Emails" to start
4. Progress bar shows real-time sending status

### Ping Tab (Step-by-Step)

**Step 1: Load Hostnames**
1. Click "Browse..." to select an Excel or CSV file
2. File must contain a hostname column (looks for: hostname, host, etc.)
3. Preview shows loaded hostnames

**Step 2: Run Ping**
1. Click "Ping All" to test all hostnames
2. Results show hostname, IP address, status, and response time
3. Statuses: "Reachable", "Unreachable", "Timeout", "DNS failed"

**Step 3: Export Results**
1. Click "Export Results" to save to CSV
2. File saved to `output/ping_results.csv`

### RDP Tab (Step-by-Step)

**Launch RDP Sessions:**
1. Enter computer names or IP addresses (one per line) in the text area
2. Click "Launch RDP Sessions" to open multiple RDP windows simultaneously
3. Status shows number of sessions launched

**RDP Credential Auto-Typer:**
1. Set your admin credentials in the Settings tab first
2. Click "Open Auto-Typer" to launch the always-on-top popup window
3. In your RDP session, click the appropriate button:
   - **Username**: Auto-types username only
   - **Password**: Auto-types password + presses Enter
   - **Both**: Auto-types username + Tab + password + Enter
4. 3-second countdown appears before typing begins
5. Window stays pinned on top for easy access across multiple RDP sessions
6. Useful when copy/paste is disabled in RDP environments

### Active Directory Tab (Step-by-Step)

**Delete Computer:**
1. Set your admin credentials in the Settings tab first
2. Enter the computer hostname to delete
3. Click "Delete Computer"
4. Review the confirmation dialog showing:
   - Computer description
   - Current OU path
   - Warning to check ServiceNow first
5. Confirm to permanently delete from Active Directory

**Move Computer (Single):**
1. Set your admin credentials in the Settings tab first
2. Enter the computer hostname to move
3. Select target Organizational Unit from dropdown
4. Click "Move Computer"
5. Computer is moved to the selected OU

**Move Computer (Bulk):**
1. Prepare an Excel file with a "hostname" column
2. Click "Browse..." to select the Excel file
3. Select target Organizational Unit from dropdown
4. Click "Bulk Move"
5. All computers in the spreadsheet are moved to the selected OU
6. Status shows success/failure count

**User Search:**
1. Enter user's full name or user ID
2. Click "Search User"
3. Results display:
   - Full name (displayName)
   - User ID (sAMAccountName)
   - OU path in Windows format (e.g., domain.com\IT\Users)
4. No admin credentials required for this operation

### Settings Tab

**Configure Credentials:**
1. Enter your admin username (e.g., domain\username)
2. Enter your admin password (masked input, copy/paste blocked)
3. Credentials stored in memory only
4. Credentials deleted when application closes
5. Never written to disk for security

## Installation

### Requirements
- Windows 10/11
- Python 3.8+
- Microsoft Outlook (for email functionality)
- Excel or CSV files for data
- Active Directory PowerShell module installed (RSAT AD tools)
- LDAP/Active Directory access (for AD operations)

### Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Active Directory (Optional)**:
   - Edit `src/config.ini` with your LDAP server details:
   ```ini
   [AD]
   ldap_server = dc.yourdomain.com
   ldap_port = 389
   ldap_base_dn = DC=yourdomain,DC=com
   organizational_units = Workstations:OU=Workstations,OU=Computers,DC=yourdomain,DC=com | Servers:OU=Servers,OU=Computers,DC=yourdomain,DC=com
   ```
   - Use pipe (|) to separate multiple OUs
   - Format: `FriendlyName:LDAP_DN | FriendlyName:LDAP_DN`

3. **Run the application**:
   ```bash
   python app.py
   ```

### Build EXE (Windows)

Run the build script at [install/build_exe.ps1](install/build_exe.ps1), or use the command below from the project root:

```powershell
python -m PyInstaller --clean --noconsole --onefile --name "ServiceDeskManager" --icon "icons\scotiabank_logo_icon_170755.png" --add-data "templates;templates" --add-data "icons;icons" --add-data "output;output" --add-data "logs;logs" "app.py"
```

3. **First Run**:
   - Templates from `templates/` folder are automatically copied to Outlook
   - No additional setup required

## File Structure

```
SendEmailsManager/
├── app.py                 # Main application entry point
├── main.py               # Legacy script reference
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── src/
│   ├── __init__.py
│   ├── config.py        # Configuration and paths
│   ├── config.ini       # LDAP/AD configuration
│   ├── email_manager.py # Email sending logic
│   ├── email_tab.py     # Email UI tab
│   ├── ping_manager.py  # Ping operations logic
│   ├── ping_tab.py      # Ping UI tab
│   ├── rdp_tab.py       # RDP session and auto-typer UI
│   ├── ad_tab.py        # Active Directory operations UI
│   ├── settings_tab.py  # Credential management UI
│   ├── ldap_manager.py  # LDAP/AD operations logic
│   ├── template_manager.py  # Template handling
│   ├── utils.py         # Utility functions
│   └── __pycache__/     # Python cache
├── templates/           # Email templates (.oft files)
├── output/             # Results and exports
│   └── ping_results.csv
└── icons/              # Application icons
```

## Template Setup

### Creating a Template

1. **In Outlook**, create a new email
2. **Add placeholders** using double-curly brackets:
   ```
   Hello {{Name}},
   
   Your new IP address is {{IP}}.
   
   Best regards,
   IT Support
   ```
3. **Save as template** (.oft file) to `templates/` folder
4. **Restart** the application (or click Refresh)
5. The template appears in the dropdown

### Supported Placeholder Format

- Use `{{KeywordName}}` for dynamic content
- Keywords are case-sensitive
- Spaces around keyword names are trimmed

## Logging

All application events are logged for troubleshooting:
- Email sending success/failures
- Ping operations and results
- File loading and parsing
- Template operations
- Errors and exceptions

View logs in **Windows Event Viewer** under:
- Application and Services Logs → Service Desk Manager

## Configuration

### Email Configuration
Edit `src/config.py` to customize:
- Default BCC email address
- Outlook templates path
- Output directory
- Timeout values
- Application title

### Active Directory Configuration
Edit `src/config.ini` to configure LDAP/AD settings:
- **ldap_server**: Your domain controller hostname or IP
- **ldap_port**: LDAP port (default: 389)
- **ldap_base_dn**: Base distinguished name for your domain
- **organizational_units**: Pipe-separated list of OUs in format `FriendlyName:LDAP_DN`

Example `config.ini`:
```ini
[AD]
ldap_server = dc01.yourdomain.com
ldap_port = 389
ldap_base_dn = DC=yourdomain,DC=com
organizational_units = Workstations:OU=Workstations,OU=Computers,DC=yourdomain,DC=com | Servers:OU=Servers,OU=Computers,DC=yourdomain,DC=com | Laptops:OU=Laptops,OU=Computers,DC=yourdomain,DC=com
```

## Troubleshooting

### Template Not Appearing
1. Ensure template is in `.oft` or `.msg` format
2. Click "Refresh" button
3. Check that file is in `templates/` folder

### "No email column found"
- Spreadsheet must have a column named: email, Email, email address, or Email Address
- Rename your column or provide data in the correct format

### Outlook Permission Errors
- Templates must be in Outlook's template folder
- Application auto-copies on startup
- If issues persist, manually copy .oft files to: `C:\Users\<YourUsername>\AppData\Roaming\Microsoft\Templates\`

### Ping Timeout
- Check network connectivity
- Increase timeout in `src/config.py`
- Verify hostname/IP address is correct

### RDP Auto-Typer Not Working
- Ensure credentials are set in Settings tab
- Check that RDP window is focused before clicking auto-type buttons
- Wait for 3-second countdown to complete
- Verify target field accepts keyboard input

### Active Directory Access Denied
- Verify admin credentials are correct in Settings tab
- Ensure your account has permissions for the operation:
  - Computer deletion requires Delete permissions
  - PC movement requires Write permissions
  - User search does not require admin credentials
- Check LDAP server configuration in `src/config.ini`
- Verify LDAP server is reachable (port 389)

### "No OUs configured"
- Check `src/config.ini` exists and has [AD] section
- Verify `organizational_units` line uses pipe (|) separator
- Ensure LDAP DNs are correctly formatted
- Example: `Test:OU=Test,DC=domain,DC=com | Prod:OU=Prod,DC=domain,DC=com`

## Dependencies

Key Python packages (see `requirements.txt` for versions):
- **PySide6**: GUI framework
- **pandas**: Data manipulation for Excel/CSV
- **openpyxl**: Excel file reading
- **pywin32**: Windows integration (Outlook COM)
- **pyautogui**: Keyboard automation for RDP auto-typer
- **PowerShell ActiveDirectory module**: Active Directory operations backend
- **keyring**: Secure credential storage (legacy)

## Keyboard Shortcuts

- `Ctrl+Q`: Quit application
- `Tab`: Navigate between fields

## Tips

- **Bulk Operations**: Process hundreds of emails/pings per batch
- **Template Preview**: Use Preview Mode before full send
- **Data Validation**: Ensure email column has no blanks
- **Reusable Spreadsheets**: Keep data files updated for repeated campaigns

## Future Enhancements

- SMS notifications
- Database integration
- Advanced analytics dashboard
- Scheduled email campaigns
- Custom report generation

## Support

For issues or feature requests, contact your IT support team.

---

**Version**: 1.0  
**Last Updated**: February 2026
