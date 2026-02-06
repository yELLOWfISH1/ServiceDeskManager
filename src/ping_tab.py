"""
Ping Tab for Send Emails Manager - PySide6 Version
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QProgressBar, QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor

from .config import OUTPUT_DIR
from .ping_manager import PingManager
from .utils import load_spreadsheet, save_dataframe_to_file


class PingWorker(QThread):
    """Worker thread for pinging hosts"""
    finished = Signal(bool, str, object)
    
    def __init__(self, ping_manager, data, hostname_column):
        super().__init__()
        self.ping_manager = ping_manager
        self.data = data
        self.hostname_column = hostname_column
    
    def run(self):
        try:
            hostnames = self.data[self.hostname_column].tolist()
            self.ping_manager.ping_multiple(hostnames)
            results_df = self.ping_manager.get_results_dataframe()
            self.finished.emit(True, "Ping completed successfully", results_df)
        except Exception as e:
            self.finished.emit(False, str(e), None)


class PingTab(QWidget):
    """Ping hosts tab with PySide6"""
    
    def __init__(self):
        super().__init__()
        self.ping_manager = PingManager()
        self.current_data = None
        self.ping_worker = None
        self.results_df = None
        
        self.setup_ui()

    def setup_ui(self):
        """Create the ping tab UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Title
        title = QLabel("Ping Multiple Hosts")
        title.setObjectName("section-title")
        main_layout.addWidget(title)
        
        # File selection
        file_layout = QHBoxLayout()
        self.host_file_input = QLineEdit()
        self.host_file_input.setPlaceholderText("No file selected")
        self.host_file_input.setReadOnly(True)
        file_layout.addWidget(self.host_file_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_host_file)
        browse_btn.setMaximumWidth(100)
        file_layout.addWidget(browse_btn)
        main_layout.addLayout(file_layout)
        
        # Hostname column
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("Hostname Column:"))
        self.hostname_col_input = QLineEdit()
        self.hostname_col_input.setPlaceholderText("hostname")
        self.hostname_col_input.setText("hostname")
        col_layout.addWidget(self.hostname_col_input)
        col_layout.addStretch()
        main_layout.addLayout(col_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Ping button
        ping_btn = QPushButton("Start Pinging")
        ping_btn.setMinimumHeight(40)
        ping_btn.clicked.connect(self.start_pinging)
        main_layout.addWidget(ping_btn)
        
        # Results table
        self.results_table = QTreeWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHeaderLabels(["Hostname", "IP Address", "Status", "Response Time"])
        main_layout.addWidget(self.results_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        export_csv_btn = QPushButton("Export as CSV")
        export_csv_btn.clicked.connect(lambda: self.export_results("csv"))
        export_layout.addWidget(export_csv_btn)
        
        export_excel_btn = QPushButton("Export as Excel")
        export_excel_btn.clicked.connect(lambda: self.export_results("excel"))
        export_layout.addWidget(export_excel_btn)
        
        main_layout.addLayout(export_layout)
        
        self.setLayout(main_layout)

    def browse_host_file(self):
        """Browse for host file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Hosts File",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.current_data = load_spreadsheet(file_path)
                self.host_file_input.setText(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load file: {e}")

    def start_pinging(self):
        """Start pinging hosts"""
        if self.current_data is None:
            QMessageBox.warning(self, "Error", "Please load a hosts file first")
            return
        
        hostname_col = self.hostname_col_input.text().strip()
        if not hostname_col:
            QMessageBox.warning(self, "Error", "Please specify a hostname column")
            return
        
        if hostname_col not in self.current_data.columns:
            QMessageBox.warning(self, "Error", f"Column '{hostname_col}' not found in file")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_table.clear()
        
        # Set progress callback and run pinging in thread
        self.ping_manager.set_progress_callback(
            lambda current, total: self.progress_bar.setValue(int((current / total) * 100) if total > 0 else 0)
        )
        self.ping_worker = PingWorker(self.ping_manager, self.current_data, hostname_col)
        self.ping_worker.finished.connect(self.on_ping_finished)
        self.ping_worker.start()

    def on_ping_finished(self, success, message, results_df):
        """Handle ping completion"""
        self.progress_bar.setVisible(False)
        
        if not success:
            QMessageBox.warning(self, "Error", f"Ping failed: {message}")
            return
        
        self.results_df = results_df
        self.display_results(results_df)
        QMessageBox.information(self, "Success", message)

    def display_results(self, results_df):
        """Display ping results in table"""
        self.results_table.clear()
        self.results_table.setColumnCount(4)
        self.results_table.setHeaderLabels(["Hostname", "IP Address", "Status", "Response Time"])
        
        for idx, row in results_df.iterrows():
            items = [
                str(row.get('Hostname', '')),
                str(row.get('IP Address', '')),
                str(row.get('Ping Status', '')),
                str(row.get('Response Time', ''))
            ]
            tree_item = QTreeWidgetItem(self.results_table, items)
            # Ensure text is white for visibility on dark background
            for col in range(4):
                tree_item.setForeground(col, QColor("#ffffff"))

    def export_results(self, format_type):
        """Export results to file"""
        if self.results_df is None or self.results_df.empty:
            QMessageBox.warning(self, "Error", "No results to export")
            return
        
        try:
            if format_type == "csv":
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export as CSV",
                    str(OUTPUT_DIR / "ping_results.csv"),
                    "CSV Files (*.csv)"
                )
                if file_path:
                    save_dataframe_to_file(self.results_df, file_path)
                    QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            
            elif format_type == "excel":
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export as Excel",
                    str(OUTPUT_DIR / "ping_results.xlsx"),
                    "Excel Files (*.xlsx)"
                )
                if file_path:
                    save_dataframe_to_file(self.results_df, file_path)
                    QMessageBox.information(self, "Success", f"Results exported to {file_path}")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export results: {e}")
