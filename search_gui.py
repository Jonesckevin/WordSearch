#!/usr/bin/env python3
"""
WordSearch GUI - Modern Qt6 Interface
Cross-platform GUI for file and content searching
"""

import sys
import os
import subprocess
import csv
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QProgressBar, QCheckBox, QGroupBox,
    QSplitter, QHeaderView, QMessageBox, QStatusBar, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

class SearchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, script_path, args):
        super().__init__()
        self.script_path = script_path
        self.args = args
        
    def run(self):
        try:
            self.progress.emit("Starting search...")
            
            # Determine which script to run based on OS
            if os.name == 'nt':  # Windows
                cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'File-FY.ps1'] + self.args
            else:  # Unix/Linux
                cmd = ['bash', 'File-FY.sh'] + self.args
            
            process = subprocess.Popen(
                cmd,
                cwd=self.script_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.finished.emit(stdout)
            else:
                self.error.emit(f"Error: {stderr}")
                
        except Exception as e:
            self.error.emit(f"Failed to run search: {str(e)}")

class ModernSearchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_dir = Path(__file__).parent
        self.search_thread = None
        self.current_theme = "Dark Mode"  # Default theme changed to dark
        self.themes = self.setup_themes()
        self.init_ui()
        self.apply_theme(self.current_theme)
        
    def setup_themes(self):
        """Define available themes with color schemes"""
        return {
            "Modern Blue": {
                "primary": "#4A90E2",
                "primary_hover": "#357ABD", 
                "primary_pressed": "#2968A3",
                "secondary": "#E8F4FD",
                "background": "#F5F7FA",
                "surface": "#FFFFFF",
                "surface_alt": "#F9FAFB",
                "text": "#2D3748",
                "text_secondary": "#718096",
                "border": "#E2E8F0",
                "border_focus": "#4A90E2",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #4A90E2, stop: 1 #357ABD)"
            },
            "Dark Mode": {
                "primary": "#BB86FC",
                "primary_hover": "#985EFF",
                "primary_pressed": "#7C3AED",
                "secondary": "#2D1B69",
                "background": "#121212",
                "surface": "#1E1E1E",
                "surface_alt": "#2A2A2A",
                "text": "#E0E0E0",
                "text_secondary": "#B0B0B0",
                "border": "#404040",
                "border_focus": "#BB86FC",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #BB86FC, stop: 1 #985EFF)"
            },
            "Green Nature": {
                "primary": "#22C55E",
                "primary_hover": "#16A34A",
                "primary_pressed": "#15803D",
                "secondary": "#DCFCE7",
                "background": "#F0FDF4",
                "surface": "#FFFFFF",
                "surface_alt": "#F7FEF8",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "border": "#D1FAE5",
                "border_focus": "#22C55E",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #22C55E, stop: 1 #16A34A)"
            },
            "Orange Sunset": {
                "primary": "#F97316",
                "primary_hover": "#EA580C",
                "primary_pressed": "#C2410C",
                "secondary": "#FED7AA",
                "background": "#FFF7ED",
                "surface": "#FFFFFF",
                "surface_alt": "#FEF3E8",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "border": "#FDBA74",
                "border_focus": "#F97316",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #F97316, stop: 1 #EA580C)"
            },
            "Purple Pro": {
                "primary": "#8B5CF6",
                "primary_hover": "#7C3AED",
                "primary_pressed": "#6D28D9",
                "secondary": "#EDE9FE",
                "background": "#FAF9FF",
                "surface": "#FFFFFF",
                "surface_alt": "#F5F3FF",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "border": "#D8B4FE",
                "border_focus": "#8B5CF6",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #8B5CF6, stop: 1 #7C3AED)"
            },
            "Red Power": {
                "primary": "#EF4444",
                "primary_hover": "#DC2626",
                "primary_pressed": "#B91C1C",
                "secondary": "#FEE2E2",
                "background": "#FEF2F2",
                "surface": "#FFFFFF",
                "surface_alt": "#FEF8F8",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "border": "#FECACA",
                "border_focus": "#EF4444",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #EF4444, stop: 1 #DC2626)"
            },
            "Vampire": {
                "primary": "#DC143C",
                "primary_hover": "#B91C3C",
                "primary_pressed": "#991B3C",
                "secondary": "#4A0E0E",
                "background": "#0D0D0D",
                "surface": "#1A1A1A",
                "surface_alt": "#2D1B1B",
                "text": "#F5F5F5",
                "text_secondary": "#CCCCCC",
                "border": "#444444",
                "border_focus": "#DC143C",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #DC143C, stop: 1 #8B0000)"
            }
        }
    
    def init_ui(self):
        self.setWindowTitle("WordSearch - Modern File & Content Search")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        self.create_header(main_layout)
        
        # Create main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Search configuration
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
    def create_header(self, parent_layout):
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(60)
        self.header_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.themes[self.current_theme]["header_bg"]};
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        
        header_layout = QHBoxLayout(self.header_frame)
        
        title_label = QLabel("🔍 WordSearch")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        subtitle_label = QLabel("Advanced File & Content Search Tool")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                background: transparent;
            }
        """)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(self.themes.keys()))
        self.theme_combo.setCurrentText(self.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
                font-size: 11px;
                min-width: 120px;
            }
            QComboBox:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
                width: 0;
                height: 0;
            }
        """)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        header_layout.addLayout(theme_layout)
        
        parent_layout.addWidget(self.header_frame)
        
    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search Configuration Group
        config_group = QGroupBox("Search Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Search path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Search Path:"))
        self.path_edit = QLineEdit(".")
        self.path_browse_btn = QPushButton("Browse")
        self.path_browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_browse_btn)
        config_layout.addLayout(path_layout)
        
        # Search terms
        config_layout.addWidget(QLabel("Search Terms:"))
        self.terms_edit = QTextEdit()
        self.terms_edit.setMaximumHeight(100)
        self.terms_edit.setPlaceholderText("Enter search terms, one per line...")
        config_layout.addWidget(self.terms_edit)
        
        # Regex patterns
        config_layout.addWidget(QLabel("Regex Patterns (optional):"))
        self.regex_edit = QTextEdit()
        self.regex_edit.setMaximumHeight(80)
        self.regex_edit.setPlaceholderText("Enter regex patterns, one per line...")
        config_layout.addWidget(self.regex_edit)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.case_sensitive_cb = QCheckBox("Case Sensitive")
        self.verbose_cb = QCheckBox("Verbose Output")
        
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.verbose_cb)
        
        # Search button
        self.search_btn = QPushButton("🚀 Start Search")
        self.search_btn.setFixedHeight(40)
        self.search_btn.clicked.connect(self.start_search)
        
        # Save results button
        self.save_btn = QPushButton("💾 Save Results")
        self.save_btn.setFixedHeight(35)
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)  # Disabled until results are available
        
        # Button layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.save_btn)
        
        # Layout assembly
        left_layout.addWidget(config_group)
        left_layout.addWidget(options_group)
        left_layout.addStretch()
        left_layout.addLayout(button_layout)
        
        return left_widget
        
    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Results tabs
        self.tabs = QTabWidget()
        
        # Results table tab
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Type", "File Path", "File Name", "Line", "Term", "Match"
        ])
        
        # Make table read-only
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Auto-resize columns
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tabs.addTab(self.results_table, "📊 Results Table")
        
        # Log output tab
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.log_output, "📜 Log Output")
        
        # Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.tabs.addTab(self.summary_text, "📈 Summary")
        
        right_layout.addWidget(self.tabs)
        
        return right_widget
        
    def change_theme(self, theme_name):
        """Change the application theme"""
        self.current_theme = theme_name
        self.apply_theme(theme_name)
        
        # Refresh summary with new theme colors if results exist
        if self.results_table.rowCount() > 0:
            self.update_summary(self.results_table.rowCount())
        
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        theme = self.themes[theme_name]
        
        # Update header background
        if hasattr(self, 'header_frame'):
            self.header_frame.setStyleSheet(f"""
                QFrame {{
                    background: {theme["header_bg"]};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """)
        
        # Apply main stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme["background"]};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme["border"]};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {theme["primary"]};
            }}
            
            QPushButton {{
                background-color: {theme["primary"]};
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {theme["primary_hover"]};
            }}
            
            QPushButton:pressed {{
                background-color: {theme["primary_pressed"]};
            }}
            
            QPushButton:disabled {{
                background-color: {theme["border"]};
                color: {theme["text_secondary"]};
            }}
            
            QLineEdit, QTextEdit {{
                border: 2px solid {theme["border"]};
                border-radius: 6px;
                padding: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                selection-background-color: {theme["primary"]};
                selection-color: white;
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {theme["border_focus"]};
            }}
            
            QTableWidget {{
                gridline-color: {theme["border"]};
                background-color: {theme["surface"]};
                alternate-background-color: {theme["surface_alt"]};
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                color: {theme["text"]};
            }}
            
            QTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            
            QTableWidget::item:hover {{
                background-color: {theme["secondary"]};
            }}
            
            QHeaderView::section {{
                background-color: {theme["surface_alt"]};
                padding: 8px;
                border: none;
                font-weight: bold;
                color: {theme["text"]};
                border-bottom: 1px solid {theme["border"]};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                border-radius: 6px;
            }}
            
            QTabBar::tab {{
                background-color: {theme["surface_alt"]};
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: {theme["text_secondary"]};
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme["surface"]};
                color: {theme["primary"]};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover {{
                background-color: {theme["secondary"]};
            }}
            
            QCheckBox {{
                font-weight: normal;
                spacing: 8px;
                color: {theme["text"]};
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme["border"]};
                border-radius: 3px;
                background-color: {theme["surface"]};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {theme["primary"]};
                border: 2px solid {theme["primary"]};
            }}
            
            QLabel {{
                color: {theme["text"]};
            }}
            
            QStatusBar {{
                background-color: {theme["surface"]};
                border-top: 1px solid {theme["border"]};
                color: {theme["text"]};
            }}
            
            QProgressBar {{
                border: 1px solid {theme["border"]};
                border-radius: 3px;
                text-align: center;
                background-color: {theme["surface_alt"]};
            }}
            
            QProgressBar::chunk {{
                background-color: {theme["primary"]};
                border-radius: 2px;
            }}
            
            QComboBox {{
                border: 2px solid {theme["border"]};
                border-radius: 6px;
                padding: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                selection-background-color: {theme["primary"]};
            }}
            
            QComboBox:focus {{
                border-color: {theme["border_focus"]};
            }}
            
            QComboBox::drop-down {{
                border: none;
                background-color: {theme["primary"]};
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
                width: 0;
                height: 0;
            }}
            
            QComboBox QAbstractItemView {{
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                selection-background-color: {theme["primary"]};
                selection-color: white;
            }}
        """)
        
    def apply_modern_style(self):
        """Legacy method - now handled by apply_theme"""
        pass
        
    def save_results(self):
        """Save search results to a user-selected file"""
        if self.results_table.rowCount() == 0:
            QMessageBox.information(self, "No Results", "No search results to save.")
            return
            
        # Get save file path
        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Search Results",
            f"search_results_{timestamp}.csv",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Determine file format based on extension
            if file_path.lower().endswith('.csv'):
                self.save_as_csv(file_path)
            else:
                self.save_as_text(file_path)
                
            QMessageBox.information(self, "Save Successful", f"Results saved to:\n{file_path}")
            self.status_bar.showMessage(f"Results saved to {Path(file_path).name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save results:\n{str(e)}")
            
    def save_as_csv(self, file_path):
        """Save results as CSV file"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write headers
            headers = []
            for col in range(self.results_table.columnCount()):
                header_item = self.results_table.horizontalHeaderItem(col)
                headers.append(header_item.text() if header_item else f"Column_{col}")
            writer.writerow(headers)
            
            # Write data
            for row in range(self.results_table.rowCount()):
                row_data = []
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)
                
    def save_as_text(self, file_path):
        """Save results as formatted text file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("WordSearch Results\n")
            f.write("=" * 50 + "\n\n")
            
            # Write summary
            f.write(f"Search Path: {self.path_edit.text()}\n")
            f.write(f"Case Sensitive: {'Yes' if self.case_sensitive_cb.isChecked() else 'No'}\n")
            f.write(f"Total Results: {self.results_table.rowCount()}\n\n")
            
            # Write results
            for row in range(self.results_table.rowCount()):
                f.write(f"Result #{row + 1}:\n")
                for col in range(self.results_table.columnCount()):
                    header_item = self.results_table.horizontalHeaderItem(col)
                    header = header_item.text() if header_item else f"Column_{col}"
                    item = self.results_table.item(row, col)
                    value = item.text() if item else ""
                    f.write(f"  {header}: {value}\n")
                f.write("\n")
    
    def browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Search Directory")
        if folder:
            self.path_edit.setText(folder)
            
    def start_search(self):
        if self.search_thread and self.search_thread.isRunning():
            return
            
        # Prepare search terms and regex files
        self.prepare_search_files()
        
        # Build command arguments
        args = []
        
        if os.name == 'nt':  # Windows PowerShell
            if self.path_edit.text().strip():
                args.extend(['-SearchPath', self.path_edit.text().strip()])
            if self.case_sensitive_cb.isChecked():
                args.append('-CaseSensitive')
            if self.verbose_cb.isChecked():
                args.append('-Verbose')
        else:  # Unix/Linux Bash
            if self.path_edit.text().strip():
                args.extend(['-p', self.path_edit.text().strip()])
            if self.case_sensitive_cb.isChecked():
                args.append('-c')
            if self.verbose_cb.isChecked():
                args.append('-v')
        
        # Clear previous results
        self.clear_results()
        
        # Start search thread
        self.search_thread = SearchThread(self.script_dir, args)
        self.search_thread.progress.connect(self.update_progress)
        self.search_thread.finished.connect(self.search_finished)
        self.search_thread.error.connect(self.search_error)
        
        # Update UI
        self.search_btn.setText("⏳ Searching...")
        self.search_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_bar.showMessage("Search in progress...")
        
        self.search_thread.start()
        
    def prepare_search_files(self):
        # Write search terms to .terms_list
        terms_text = self.terms_edit.toPlainText().strip()
        if terms_text:
            with open(self.script_dir / '.terms_list', 'w', encoding='utf-8') as f:
                for line in terms_text.split('\n'):
                    line = line.strip()
                    if line:
                        f.write(f"{line}\n")
        
        # Write regex patterns to .regex_list
        regex_text = self.regex_edit.toPlainText().strip()
        if regex_text:
            with open(self.script_dir / '.regex_list', 'w', encoding='utf-8') as f:
                for line in regex_text.split('\n'):
                    line = line.strip()
                    if line:
                        f.write(f"{line}\n")
        
    def update_progress(self, message):
        self.log_output.append(message)
        self.status_bar.showMessage(message)
        
    def search_finished(self, output):
        self.search_btn.setText("🚀 Start Search")
        self.search_btn.setEnabled(True)
        self.save_btn.setEnabled(True)  # Enable save button after search completes
        self.progress_bar.setVisible(False)
        
        self.log_output.append("\n" + output)
        self.load_results()
        self.status_bar.showMessage("Search completed")
        
        # Switch to results tab
        self.tabs.setCurrentIndex(0)
        
    def search_error(self, error):
        self.search_btn.setText("🚀 Start Search")
        self.search_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.log_output.append(f"\nERROR: {error}")
        self.status_bar.showMessage("Search failed")
        
        QMessageBox.critical(self, "Search Error", f"Search failed:\n{error}")
        
    def load_results(self):
        csv_file = self.script_dir / 'search_results.csv'
        if not csv_file.exists():
            return
            
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                headers = next(csv_reader, None)  # Skip header
                
                rows = list(csv_reader)
                self.results_table.setRowCount(len(rows))
                
                for row_idx, row in enumerate(rows):
                    for col_idx, cell_data in enumerate(row[:6]):  # Limit to 6 columns
                        item = QTableWidgetItem(str(cell_data))
                        self.results_table.setItem(row_idx, col_idx, item)
                
                # Update summary
                self.update_summary(len(rows))
                
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Failed to load results:\n{str(e)}")
            
    def update_summary(self, total_matches):
        # Count different types of matches
        filename_matches = 0
        content_matches = 0
        
        for row in range(self.results_table.rowCount()):
            search_type_item = self.results_table.item(row, 0)
            if search_type_item:
                search_type = search_type_item.text()
                if 'FileName' in search_type:
                    filename_matches += 1
                elif 'Content' in search_type:
                    content_matches += 1
        
        # Get current theme colors for summary
        theme = self.themes[self.current_theme]
        
        summary = f"""
        <html>
        <head>
        <style>
        body {{
            background-color: {theme["surface"]};
            color: {theme["text"]};
            font-family: Arial, sans-serif;
            margin: 10px;
        }}
        h2 {{
            color: {theme["primary"]};
            border-bottom: 2px solid {theme["primary"]};
            padding-bottom: 5px;
        }}
        h3 {{
            color: {theme["text"]};
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        th {{
            background-color: {theme["surface_alt"]};
            color: {theme["text"]};
            padding: 12px;
            border: 1px solid {theme["border"]};
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border: 1px solid {theme["border"]};
            background-color: {theme["surface"]};
            color: {theme["text"]};
        }}
        tr:nth-child(even) td {{
            background-color: {theme["surface_alt"]};
        }}
        .highlight {{
            color: {theme["primary"]};
            font-weight: bold;
        }}
        p {{
            color: {theme["text"]};
            line-height: 1.5;
        }}
        </style>
        </head>
        <body>
        <h2>🔍 Search Results Summary</h2>
        <table>
        <tr>
            <th>Metric</th>
            <th>Count</th>
        </tr>
        <tr>
            <td>Total Matches</td>
            <td class="highlight">{total_matches}</td>
        </tr>
        <tr>
            <td>Filename Matches</td>
            <td>{filename_matches}</td>
        </tr>
        <tr>
            <td>Content Matches</td>
            <td>{content_matches}</td>
        </tr>
        </table>
        
        <h3>⚙️ Search Configuration</h3>
        <p><b>Search Path:</b> {self.path_edit.text()}</p>
        <p><b>Case Sensitive:</b> {'Yes' if self.case_sensitive_cb.isChecked() else 'No'}</p>
        <p><b>Terms Count:</b> {len([t for t in self.terms_edit.toPlainText().split('\n') if t.strip()])}</p>
        <p><b>Theme:</b> {self.current_theme}</p>
        </body>
        </html>
        """
        
        self.summary_text.setHtml(summary)
        
    def clear_results(self):
        self.results_table.setRowCount(0)
        self.log_output.clear()
        self.summary_text.clear()
        self.save_btn.setEnabled(False)  # Disable save button when results are cleared

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("WordSearch")
    app.setOrganizationName("WordSearch Tools")
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass
    
    window = ModernSearchGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
