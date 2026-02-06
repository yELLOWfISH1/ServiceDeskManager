"""
Email Tab for Send Emails Manager - PySide6 Version
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QCheckBox, QProgressBar, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal

from .config import OUTPUT_DIR
from .template_manager import TemplateManager
from .email_manager import EmailManager
from .utils import load_spreadsheet


class EmailSendWorker(QThread):
    """Worker thread for sending emails"""
    progress = Signal(int)
    finished = Signal(bool, str)
    
    def __init__(self, email_manager, data, template_path, keyword_mapping, bcc, preview_mode):
        super().__init__()
        self.email_manager = email_manager
        self.data = data
        self.template_path = template_path
        self.keyword_mapping = keyword_mapping
        self.bcc = bcc
        self.preview_mode = preview_mode
    
    def run(self):
        try:
            result = self.email_manager.send_emails(
                self.data,
                self.template_path,
                self.keyword_mapping,
                self.bcc,
                self.preview_mode,
                progress_callback=lambda current, total: self.progress.emit(int((current / total) * 100) if total > 0 else 0)
            )
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))


class EmailTab(QWidget):
    """Email sending tab with PySide6"""
    
    def __init__(self):
        super().__init__()
        self.template_manager = TemplateManager()
        self.email_manager = EmailManager()
        self.current_data = None
        self.current_template_path = None
        self.send_worker = None
        self.keyword_mappings = {}
        
        self.setup_ui()

    def setup_ui(self):
        """Create the email tab UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Step 1: Load Data
        self.add_section(main_layout, "Step 1: Load Recipient Data", self.create_step1_ui())
        
        # Step 2: Select Template
        self.add_section(main_layout, "Step 2: Select Email Template", self.create_step2_ui())
        
        # Step 3: Map Keywords
        self.keyword_frame = QFrame()
        self.keyword_layout = QVBoxLayout()
        self.keyword_layout.setContentsMargins(0, 0, 0, 0)
        self.keyword_layout.setSpacing(8)
        self.keyword_frame.setLayout(self.keyword_layout)
        self.add_section(main_layout, "Step 3: Map Keywords to Columns", self.keyword_frame)
        
        # Step 4: Send Emails
        self.add_section(main_layout, "Step 4: Send Emails", self.create_step4_ui())
        
        main_layout.addStretch()
        self.setLayout(main_layout)

    def add_section(self, parent_layout, title, widget):
        """Add a labeled section to the layout"""
        section_label = QLabel(title)
        section_label.setObjectName("section-title")
        parent_layout.addWidget(section_label)
        parent_layout.addWidget(widget)

    def create_step1_ui(self):
        """Create step 1: load data"""
        container = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # File selection
        file_layout = QHBoxLayout()
        self.data_file_input = QLineEdit()
        self.data_file_input.setPlaceholderText("No file selected")
        self.data_file_input.setReadOnly(True)
        file_layout.addWidget(self.data_file_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_data_file)
        browse_btn.setMaximumWidth(100)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Email column input
        email_col_layout = QHBoxLayout()
        email_col_layout.addWidget(QLabel("Email Column:"))
        self.email_col_input = QLineEdit()
        self.email_col_input.setPlaceholderText("email")
        self.email_col_input.setText("email")
        email_col_layout.addWidget(self.email_col_input)
        email_col_layout.addStretch()
        layout.addLayout(email_col_layout)
        
        # Data preview
        self.data_preview = QTreeWidget()
        self.data_preview.setColumnCount(5)
        self.data_preview.setHeaderLabels(["Column 1", "Column 2", "Column 3", "Column 4", "Column 5"])
        self.data_preview.setMaximumHeight(120)
        layout.addWidget(self.data_preview)
        
        container.setLayout(layout)
        return container

    def create_step2_ui(self):
        """Create step 2: select template"""
        container = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Template selection
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        # Use index change so slot fires reliably and we can accept an optional arg
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_combo, 1)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_templates)
        refresh_btn.setMaximumWidth(80)
        template_layout.addWidget(refresh_btn)
        
        edit_btn = QPushButton("✏️ Edit Template")
        edit_btn.clicked.connect(self.edit_template)
        edit_btn.setMaximumWidth(120)
        template_layout.addWidget(edit_btn)
        
        add_btn = QPushButton("➕ Add Template")
        add_btn.clicked.connect(self.add_template)
        add_btn.setMaximumWidth(120)
        template_layout.addWidget(add_btn)
        
        layout.addLayout(template_layout)
        
        # Template info
        self.template_info = QLabel("Select a template to view details")
        self.template_info.setStyleSheet("color: #999999; font-size: 10px;")
        self.template_info.setWordWrap(True)
        layout.addWidget(self.template_info)
        
        container.setLayout(layout)
        self.refresh_templates()
        return container

    def create_step4_ui(self):
        """Create step 4: send emails"""
        container = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # BCC and options
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("BCC Email:"))
        self.bcc_input = QLineEdit()
        self.bcc_input.setPlaceholderText("Optional")
        options_layout.addWidget(self.bcc_input, 1)
        
        self.preview_checkbox = QCheckBox("Preview Mode (don't send)")
        options_layout.addWidget(self.preview_checkbox)
        layout.addLayout(options_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Send button
        send_btn = QPushButton("Send Emails")
        send_btn.setMinimumHeight(40)
        send_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
            }
        """)
        send_btn.clicked.connect(self.send_emails)
        layout.addWidget(send_btn)
        
        container.setLayout(layout)
        return container

    def browse_data_file(self):
        """Browse for data file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.current_data = load_spreadsheet(file_path)
                self.data_file_input.setText(file_path)
                
                # Validate email column exists
                email_col = self._find_email_column()
                if not email_col:
                    cols = ", ".join(self.current_data.columns[:10])
                    QMessageBox.warning(
                        self,
                        "Missing Email Column",
                        f"File has no email column.\n\n"
                        f"The system looks for: email, Email, email address, Email Address\n\n"
                        f"Your columns: {cols}\n\n"
                        f"Please rename one column to 'email' or add an email column."
                    )
                    self.current_data = None
                    self.data_file_input.setText("")
                    return
                
                self.refresh_data_preview()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load file: {e}")
    
    def _find_email_column(self):
        """Find email column (case-insensitive) from standard names"""
        if self.current_data is None:
            return None
        
        email_aliases = ["email", "email address", "email_address", "mail", "e-mail"]
        cols_lower = {col.lower(): col for col in self.current_data.columns}
        
        for alias in email_aliases:
            if alias in cols_lower:
                return cols_lower[alias]
        
        return None

    def refresh_data_preview(self):
        """Refresh data preview table"""
        self.data_preview.clear()
        
        if self.current_data is None:
            return
        
        # Set column headers
        cols = list(self.current_data.columns)[:5]
        self.data_preview.setColumnCount(len(cols))
        self.data_preview.setHeaderLabels(cols)
        
        # Add rows
        for idx, row in self.current_data.head(5).iterrows():
            items = []
            for col in cols:
                items.append(str(row[col])[:50])
            QTreeWidgetItem(self.data_preview, items)

    def refresh_templates(self):
        """Refresh template list"""
        templates = self.template_manager.get_available_templates()
        # Preserve current selection if possible
        prev = self.template_combo.currentText() if self.template_combo.count() > 0 else ""
        self.template_combo.clear()
        self.template_combo.addItems(templates)
        if prev and prev in templates:
            # restore previous selection
            self.template_combo.setCurrentText(prev)
        elif templates:
            # if nothing to restore, keep current index but trigger update by setting index 0
            self.template_combo.setCurrentIndex(0)

    def on_template_selected(self, _=None):
        """Handle template selection"""
        template_name = self.template_combo.currentText()
        if not template_name:
            self.template_info.setText("No template selected")
            return
        
        template_path = self.template_manager.get_template_path(template_name)
        if template_path:
            self.current_template_path = template_path
            keywords = self.template_manager.extract_keywords_from_template(template_path)
            self.template_info.setText(f"Keywords found: {', '.join(keywords)}")
            self.update_keyword_mapping_ui(keywords)
        else:
            self.template_info.setText("Template not found")

    def update_keyword_mapping_ui(self, keywords):
        """Update keyword mapping UI"""
        # Ensure keyword_layout exists
        if not hasattr(self, 'keyword_layout'):
            return
        
        # Clear previous widgets
        while self.keyword_layout.count():
            widget = self.keyword_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        if self.current_data is not None:
            columns = list(self.current_data.columns)
        else:
            columns = []
        
        self.keyword_mappings = {}
        
        for keyword in keywords:
            kw_layout = QHBoxLayout()
            kw_layout.addWidget(QLabel(keyword))
            
            combo = QComboBox()
            combo.addItems(["[Select Column]"] + columns)
            combo.setMinimumWidth(150)
            self.keyword_mappings[keyword] = combo
            
            kw_layout.addWidget(combo, 1)
            self.keyword_layout.addLayout(kw_layout)

    def add_template(self):
        """Add a new template"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Email Template",
            "",
            "Outlook Template (*.oft);;Outlook Message (*.msg);;All Files (*.*)"
        )
        
        if file_path:
            template_path = Path(file_path)
            if template_path.suffix.lower() not in ['.oft', '.msg']:
                QMessageBox.warning(self, "Invalid Format", "Only .oft and .msg files are supported")
                return
            
            success = self.template_manager.copy_template_to_outlook(template_path)
            if success:
                QMessageBox.information(self, "Success", f"Template '{template_path.name}' added successfully")
                self.refresh_templates()
            else:
                QMessageBox.warning(self, "Error", "Failed to add template")

    def edit_template(self):
        """Edit the currently selected template in Outlook"""
        template_name = self.template_combo.currentText()
        if not template_name:
            QMessageBox.warning(self, "Error", "Please select a template first")
            return
        
        template_path = self.template_manager.get_template_path(template_name)
        if not template_path:
            QMessageBox.warning(self, "Error", "Template not found")
            return
        
        try:
            import win32com.client as win32
            outlook = win32.Dispatch("Outlook.Application")
            # Open the template for editing
            mail = outlook.CreateItemFromTemplate(str(template_path))
            mail.Display()
            QMessageBox.information(
                self,
                "Edit Template",
                "Template opened in Outlook.\n\nMake your changes and save when done."
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open template: {str(e)}")

    def send_emails(self):
        """Send emails"""
        if self.current_data is None:
            QMessageBox.warning(self, "Error", "Please load a data file first")
            return
        
        if not self.current_template_path:
            QMessageBox.warning(self, "Error", "Please select a template")
            return
        
        # Build keyword mapping
        keyword_mapping = {}
        for keyword, combo in self.keyword_mappings.items():
            selected = combo.currentText()
            if selected != "[Select Column]":
                keyword_mapping[keyword] = selected
        
        if not keyword_mapping:
            QMessageBox.warning(self, "Error", "Please map at least one keyword")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Run email sending in thread
        self.send_worker = EmailSendWorker(
            self.email_manager,
            self.current_data,
            self.current_template_path,
            keyword_mapping,
            self.bcc_input.text(),
            self.preview_checkbox.isChecked()
        )
        self.send_worker.progress.connect(self.progress_bar.setValue)
        self.send_worker.finished.connect(self.on_send_finished)
        self.send_worker.start()

    def on_send_finished(self, success, message):
        """Handle send completion"""
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", f"Failed to send emails: {message}")
