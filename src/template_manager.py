"""
Template Manager module for handling email template management and validation
"""
import os
import shutil
from pathlib import Path
from typing import List, Tuple
import win32com.client as win32

from .config import (
    TEMPLATES_DIR,
    OUTLOOK_TEMPLATES_DEFAULT,
    DEFAULT_KEYWORDS,
    TEMPLATE_EXTENSIONS,
    DEFAULT_TEMPLATE_NAME,
)


class TemplateManager:
    """Manages email templates and template validation"""
    
    def __init__(self):
        self.local_templates_dir = TEMPLATES_DIR
        self.outlook_templates_dir = OUTLOOK_TEMPLATES_DEFAULT
        self.default_keywords = DEFAULT_KEYWORDS
        # Copy all templates from local folder to Outlook templates folder on startup
        self.copy_all_local_templates_to_outlook()
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available templates from Outlook template folder only
        (templates should be copied there at startup)
        
        Returns:
            List of template file names (without path)
        """
        templates = []
        
        # Only check Outlook templates folder (this is where Outlook can access them)
        if self.outlook_templates_dir.exists():
            for file in self.outlook_templates_dir.iterdir():
                if file.suffix.lower() in TEMPLATE_EXTENSIONS:
                    templates.append(file.name)
        
        return sorted(templates)
    
    def get_template_path(self, template_name: str) -> Path | None:
        """
        Get full path to template file
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Path object if template found, None otherwise
        """
        # Check local templates first
        local_path = self.local_templates_dir / template_name
        if local_path.exists():
            return local_path
        
        # Check Outlook templates
        outlook_path = self.outlook_templates_dir / template_name
        if outlook_path.exists():
            return outlook_path
        
        return None
    
    def copy_template_to_outlook(self, template_path: Path) -> bool:
        """
        Copy a template to the Outlook templates folder
        
        Args:
            template_path: Path to the template file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not template_path.exists():
                return False

            destination = self.outlook_templates_dir / template_path.name

            # If destination already exists, do not overwrite
            if destination.exists():
                return True

            shutil.copy2(template_path, destination)
            return True
        except PermissionError as pe:
            print(f"Permission denied copying template to Outlook: {pe}")
            return False
        except Exception as e:
            print(f"Error copying template to Outlook: {e}")
            return False

    def ensure_default_template_in_outlook(self, template_name: str = DEFAULT_TEMPLATE_NAME) -> bool:
        """
        Ensure the default template (from app templates folder) is present in the user's
        Outlook Templates folder. If it is already present, do nothing.

        Returns True if template is present or was successfully copied, False otherwise.
        """
        try:
            local_path = self.local_templates_dir / template_name
            if not local_path.exists():
                # No default template available in app templates folder
                return False

            dest_path = self.outlook_templates_dir / template_name
            if dest_path.exists():
                # Already present in user's templates folder
                return True

            # Attempt to copy; handle permission errors
            try:
                shutil.copy2(local_path, dest_path)
                return True
            except PermissionError:
                # Permission issues writing to Outlook templates folder
                print(f"Permission denied when copying {template_name} to {self.outlook_templates_dir}")
                return False
            except Exception as e:
                print(f"Failed to copy default template: {e}")
                return False
        except Exception as e:
            print(f"Error ensuring default template in outlook: {e}")
            return False
    
    def copy_all_local_templates_to_outlook(self) -> None:
        """
        Copy all templates from the app's local templates folder to the user's Outlook Templates folder.
        This allows Outlook to access and use them for CreateItemFromTemplate.
        """
        if not self.local_templates_dir.exists():
            return
        
        try:
            for template_file in self.local_templates_dir.iterdir():
                if template_file.suffix.lower() in TEMPLATE_EXTENSIONS:
                    dest_path = self.outlook_templates_dir / template_file.name
                    
                    # Only copy if it doesn't already exist or is outdated
                    if not dest_path.exists() or template_file.stat().st_mtime > dest_path.stat().st_mtime:
                        try:
                            shutil.copy2(template_file, dest_path)
                            print(f"Copied template: {template_file.name}")
                        except PermissionError:
                            print(f"Permission denied copying {template_file.name} to Outlook templates")
                        except Exception as e:
                            print(f"Error copying {template_file.name}: {e}")
        except Exception as e:
            print(f"Error in copy_all_local_templates_to_outlook: {e}")
    
    def validate_template(self, template_path: Path, required_keywords: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that template contains required keywords
        
        Args:
            template_path: Path to the template file
            required_keywords: List of keywords that must be in the template
            
        Returns:
            Tuple of (is_valid, missing_keywords)
        """
        try:
            if template_path.suffix.lower() == ".oft":
                return self._validate_oft_template(template_path, required_keywords)
            elif template_path.suffix.lower() == ".msg":
                return self._validate_msg_template(template_path, required_keywords)
            else:
                return False, ["Unsupported template format"]
        except Exception as e:
            return False, [f"Error validating template: {str(e)}"]
    
    def _validate_oft_template(self, template_path: Path, required_keywords: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate .oft (Outlook template) file
        
        Args:
            template_path: Path to the .oft file
            required_keywords: List of keywords to check
            
        Returns:
            Tuple of (is_valid, missing_keywords)
        """
        try:
            outlook = win32.Dispatch("Outlook.Application")
            mail = outlook.CreateItemFromTemplate(str(template_path))
            
            # Get template content (both HTML and plain text body)
            template_content = mail.HTMLBody + mail.Body
            
            missing = []
            for keyword in required_keywords:
                # Validate presence of the double-curly placeholder {{Keyword}}
                if f'{{{{{keyword}}}}}' not in template_content:
                    missing.append(keyword)
            
            # Clean up
            mail.Close(0)
            
            return len(missing) == 0, missing
        except Exception as e:
            return False, [f"Error reading OFT template: {str(e)}"]
    
    def _validate_msg_template(self, template_path: Path, required_keywords: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate .msg (Outlook message) file
        
        Args:
            template_path: Path to the .msg file
            required_keywords: List of keywords to check
            
        Returns:
            Tuple of (is_valid, missing_keywords)
        """
        try:
            outlook = win32.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            mail = namespace.OpenSharedItem(str(template_path))
            
            # Get template content
            template_content = mail.HTMLBody + mail.Body
            
            missing = []
            for keyword in required_keywords:
                # Validate presence of the double-curly placeholder {{Keyword}}
                if f'{{{{{keyword}}}}}' not in template_content:
                    missing.append(keyword)
            
            # Clean up
            mail.Close(0)
            
            return len(missing) == 0, missing
        except Exception as e:
            return False, [f"Error reading MSG template: {str(e)}"]
    
    def extract_keywords_from_template(self, template_path: Path) -> List[str]:
        """
        Extract all keywords from a template (placeholders using double-curly tags like {{Name}})
        
        Args:
            template_path: Path to the template file
            
        Returns:
            List of keywords found
        """
        try:
            if template_path.suffix.lower() == ".oft":
                outlook = win32.Dispatch("Outlook.Application")
                mail = outlook.CreateItemFromTemplate(str(template_path))
                template_content = mail.HTMLBody + mail.Body
                mail.Close(0)
            elif template_path.suffix.lower() == ".msg":
                outlook = win32.Dispatch("Outlook.Application")
                namespace = outlook.GetNamespace("MAPI")
                mail = namespace.OpenSharedItem(str(template_path))
                template_content = mail.HTMLBody + mail.Body
                mail.Close(0)
            else:
                return []
            
            # Extract double-curly placeholders like {{Name}} to avoid HTML/XML tags
            import re
            placeholder_re = re.compile(r'\{\{\s*([A-Za-z0-9 _\-]{1,50})\s*\}\}')

            matches = placeholder_re.findall(template_content)

            seen = set()
            keywords = []
            for m in matches:
                key = m.strip()
                if key and key not in seen:
                    seen.add(key)
                    keywords.append(key)

            return keywords
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
