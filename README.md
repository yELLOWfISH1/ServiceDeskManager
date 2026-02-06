# Service Desk Manager

A comprehensive service desk automation tool for managing email campaigns and network diagnostics with templating support.

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

### 📁 Template Management
- **Template Repository**: Store and manage multiple email templates
- **Auto-Sync**: Templates are automatically copied to Outlook's template folder on startup
- **Quick Access**: Dropdown selection of all available templates
- **Refresh Function**: Reload template list without restarting

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

## Installation

### Requirements
- Windows 10/11
- Python 3.8+
- Microsoft Outlook (for email functionality)
- Excel or CSV files for data

### Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
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
│   ├── app.py           # (Legacy, replaced by app.py in root)
│   ├── config.py        # Configuration and paths
│   ├── email_manager.py # Email sending logic
│   ├── email_tab.py     # Email UI tab
│   ├── ping_manager.py  # Ping operations logic
│   ├── ping_tab.py      # Ping UI tab
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

Edit `src/config.py` to customize:
- Default BCC email address
- Outlook templates path
- Output directory
- Timeout values
- Application title

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
