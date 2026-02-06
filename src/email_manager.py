"""
Email Manager module for email template and sending operations
"""
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import win32com.client as win32

from .config import DEFAULT_EMAIL_BCC, DEFAULT_KEYWORDS
from .template_manager import TemplateManager
from .logger import log_info, log_error, log_warning


class EmailManager:
    """Manages email template operations and sending"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        try:
            self.outlook = win32.Dispatch("Outlook.Application")
        except Exception as e:
            self.outlook = None
        self.sent_count = 0
        self.failed_count = 0
        self.errors: List[str] = []
        log_info("Email Manager initialized")
    
    def get_available_templates(self) -> List[str]:
        """Get list of available email templates"""
        return self.template_manager.get_available_templates()
    
    def validate_template_and_keywords(
        self,
        template_name: str,
        required_keywords: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate template and check for required keywords
        
        Args:
            template_name: Name of the template
            required_keywords: List of keywords that must be in template
            
        Returns:
            Tuple of (is_valid, missing_keywords)
        """
        template_path = self.template_manager.get_template_path(template_name)
        if not template_path:
            return False, ["Template not found"]
        
        is_valid, missing = self.template_manager.validate_template(
            template_path,
            required_keywords
        )
        return is_valid, missing
    
    def extract_template_keywords(self, template_name: str) -> List[str]:
        """
        Extract all keywords from a template
        
        Args:
            template_name: Name of the template
            
        Returns:
            List of keywords found in template
        """
        template_path = self.template_manager.get_template_path(template_name)
        if not template_path:
            return []
        
        return self.template_manager.extract_keywords_from_template(template_path)
    
    def send_emails(
        self,
        data_df: pd.DataFrame,
        template_path: Path,
        keyword_mapping: Dict[str, str],
        bcc_email: str = DEFAULT_EMAIL_BCC,
        preview_mode: bool = False,
        progress_callback=None,
    ) -> str:
        """
        Send emails based on template and data. This signature matches the UI worker.

        Args:
            data_df: DataFrame containing recipient data
            template_path: Path to the template file (.oft or .msg)
            keyword_mapping: Dict mapping keyword names (without brackets) to column names
            bcc_email: Email to BCC
            preview_mode: If True, only preview without sending
            progress_callback: Optional callback receiving (current_count, total)

        Returns:
            Summary string of results
        """
        self.sent_count = 0
        self.failed_count = 0
        self.errors = []

        if template_path is None or not Path(template_path).exists():
            return "Template not found"

        # Validate template has required keywords (keyword_mapping keys expected without brackets)
        required_keywords = list(keyword_mapping.keys())
        is_valid, missing = self.template_manager.validate_template(
            template_path,
            required_keywords,
        )
        if not is_valid:
            return f"Missing keywords in template: {', '.join(missing)}"

        # Normalize column names in dataframe
        data_df.columns = data_df.columns.str.lower()
        
        # Find email column (case-insensitive)
        email_col = None
        email_aliases = ["email", "email address", "email_address", "mail", "e-mail"]
        for alias in email_aliases:
            if alias in data_df.columns:
                email_col = alias
                break
        
        if not email_col:
            return f"No email column found. Expected one of: {', '.join(email_aliases)}"

        total = len(data_df)
        processed = 0
        
        # Use Outlook from win32com - matches the working main.py approach
        try:
            outlook_app = win32.Dispatch("Outlook.Application")
        except Exception as e:
            return f"Failed to connect to Outlook: {str(e)}"

        # Iterate rows and send
        for index, row in data_df.iterrows():
            try:
                template_str = str(template_path)
                
                if not Path(template_str).exists():
                    raise ValueError(f"Template not found: {template_str}")
                
                mail = outlook_app.CreateItemFromTemplate(template_str)
                
                email = str(row[email_col]).strip()
                
                if not email or email.lower() == "nan":
                    self.failed_count += 1
                    self.errors.append(f"Row {index + 1}: Missing or invalid email address")
                else:
                    for keyword, column_name in keyword_mapping.items():
                        col = column_name.lower()
                        if col in data_df.columns:
                            value = str(row[col]).strip()
                            token = f'{{{{{keyword}}}}}'
                            mail.HTMLBody = mail.HTMLBody.replace(token, value)
                            mail.Body = mail.Body.replace(token, value)
                    
                    mail.To = email
                    if bcc_email:
                        mail.BCC = bcc_email
                    
                    if preview_mode:
                        mail.Display()
                        self.sent_count += 1
                    else:
                        mail.Send()
                        log_info(f"Email sent successfully to {email}")
                        self.sent_count += 1
                
            except Exception as e:
                self.failed_count += 1
                log_error(f"Failed to send email at row {index + 1}", e)
                self.errors.append(f"Row {index + 1}: {str(e)}")
            
            processed += 1
            if progress_callback:
                try:
                    progress_callback(processed, total)
                except Exception:
                    pass
        
        return f"Sent: {self.sent_count}, Failed: {self.failed_count}." if not self.errors else f"Sent: {self.sent_count}, Failed: {self.failed_count}. Errors: {'; '.join(self.errors[:5])}"
    
    def send_custom_email(
        self,
        to_email: str,
        subject: str = "",
        body: str = "",
        html_body: str = "",
        bcc_email: str = DEFAULT_EMAIL_BCC,
        preview_mode: bool = False
    ) -> Tuple[bool, str]:
        """
        Send a custom email without template
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: HTML body
            bcc_email: Email to BCC
            preview_mode: If True, display without sending
            
        Returns:
            Tuple of (success, message)
        """
        try:
            mail = self.outlook.CreateItem(0)
            mail.To = to_email
            mail.Subject = subject
            
            if html_body:
                mail.HTMLBody = html_body
            elif body:
                mail.Body = body
            
            if bcc_email:
                mail.BCC = bcc_email
            
            if preview_mode:
                mail.Display()
            else:
                mail.Send()
            
            return True, "Email sent successfully"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    def preview_email_with_data(
        self,
        template_name: str,
        data_row: Dict[str, str],
        keyword_mapping: Dict[str, str]
    ) -> Tuple[bool, str]:
        """
        Preview an email with sample data before sending all
        
        Args:
            template_name: Name of the template
            data_row: Dictionary with sample data
            keyword_mapping: Mapping of keywords to columns
            
        Returns:
            Tuple of (success, message/error)
        """
        try:
            template_path = self.template_manager.get_template_path(template_name)
            if not template_path:
                return False, "Template not found"
            
            mail = self.outlook.CreateItemFromTemplate(str(template_path))
            
            # Replace keywords with sample data
            for keyword, column_name in keyword_mapping.items():
                if column_name in data_row:
                    value = str(data_row[column_name]).strip()
                    mail.HTMLBody = mail.HTMLBody.replace(keyword, value)
                    mail.Body = mail.Body.replace(keyword, value)
            
            # Set to sample email
            mail.To = "preview@example.com"
            mail.Display()
            
            return True, "Preview displayed"
        except Exception as e:
            return False, f"Error previewing email: {str(e)}"
