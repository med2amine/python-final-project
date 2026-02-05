from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTextEdit, QProgressBar,
                               QSpinBox, QCheckBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
import pandas as pd
import time


class DataPreviewDialog(QDialog):

    def __init__(self, dataframe, parent=None):
        super().__init__(parent)
        self.df = dataframe
        self.setWindowTitle("Data Preview")
        self.setGeometry(200, 200, 900, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in data...")
        self.search_input.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Stats summary
        stats_text = self.get_data_summary()
        stats_label = QTextEdit()
        stats_label.setReadOnly(True)
        stats_label.setText(stats_text)
        stats_label.setMaximumHeight(150)
        layout.addWidget(stats_label)

        # Table (simplified - you'd use QTableWidget here)
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setFont(QFont("Courier", 9))
        self.update_display()
        layout.addWidget(self.data_display)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def get_data_summary(self):
        summary = []
        summary.append("=== DATA SUMMARY ===")
        summary.append(f"Rows: {len(self.df)}")
        summary.append(f"Columns: {len(self.df.columns)}")
        summary.append(f"Memory: {self.df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        summary.append(f"Missing Values: {self.df.isnull().sum().sum()}")
        summary.append(f"\nNumeric Columns: {len(self.df.select_dtypes(include=['number']).columns)}")
        summary.append(f"Categorical Columns: {len(self.df.select_dtypes(include=['object']).columns)}")
        return "\n".join(summary)

    def update_display(self, filtered_df=None):
        df_to_show = filtered_df if filtered_df is not None else self.df
        display_text = df_to_show.head(50).to_string()
        self.data_display.setText(display_text)

    def filter_data(self, search_text):
        if not search_text:
            self.update_display()
            return

        # Search in all columns
        mask = self.df.apply(lambda row: row.astype(str).str.contains(
            search_text, case=False, na=False).any(), axis=1)
        filtered = self.df[mask]
        self.update_display(filtered)


class ExportProgressDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing...")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("Starting...")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(150)
        layout.addWidget(self.detail_text)

        self.setLayout(layout)
        self.resize(400, 200)

    def update_progress(self, value, status="", details=""):
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)
        if details:
            self.detail_text.append(details)


class DataValidationDialog(QDialog):

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.setWindowTitle("Data Validation Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Configure validation rules:"))

        # Null tolerance
        null_layout = QHBoxLayout()
        null_layout.addWidget(QLabel("Max allowed null % per column:"))
        self.null_spinbox = QSpinBox()
        self.null_spinbox.setRange(0, 100)
        self.null_spinbox.setValue(10)
        self.null_spinbox.setSuffix("%")
        null_layout.addWidget(self.null_spinbox)
        layout.addLayout(null_layout)

        # Duplicate handling
        self.remove_dups = QCheckBox("Automatically remove duplicates")
        layout.addWidget(self.remove_dups)

        # Outlier detection
        self.detect_outliers = QCheckBox("Flag outliers (±3 std dev)")
        layout.addWidget(self.detect_outliers)

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_settings(self):
        return {
            'max_null_percent': self.null_spinbox.value(),
            'remove_duplicates': self.remove_dups.isChecked(),
            'detect_outliers': self.detect_outliers.isChecked()
        }


class AnalysisWorker(QThread):

    progress = Signal(int, str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, data, calculations):
        super().__init__()
        self.data = data
        self.calculations = calculations

    def run(self):
        try:
            results = {}
            total = len(self.calculations)

            for i, calc in enumerate(self.calculations):
                # Simulate processing
                time.sleep(0.1)  # Remove in production

                # Emit progress
                progress_pct = int((i + 1) / total * 100)
                self.progress.emit(progress_pct, f"Computing {calc}...")

                # Perform calculation
                # (Your actual calculation code here)
                results[calc] = "result"

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class QuickStatsWidget(QDialog):

    def __init__(self, data, column_name, parent=None):
        super().__init__(parent)
        self.data = data
        self.column = column_name
        self.setWindowTitle(f"Quick Stats: {column_name}")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        stats_text = self.calculate_quick_stats()

        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setText(stats_text)
        text_display.setFont(QFont("Courier", 10))
        layout.addWidget(text_display)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
        self.resize(400, 350)

    def calculate_quick_stats(self):
        series = self.data[self.column]

        stats = []
        stats.append(f"=== {self.column} ===\n")
        stats.append(f"Data Type: {series.dtype}")
        stats.append(f"Count: {series.count()}")
        stats.append(f"Missing: {series.isnull().sum()}")
        stats.append(f"Unique: {series.nunique()}\n")

        if pd.api.types.is_numeric_dtype(series):
            stats.append("--- Numeric Statistics ---")
            stats.append(f"Mean: {series.mean():.4f}")
            stats.append(f"Median: {series.median():.4f}")
            stats.append(f"Std Dev: {series.std():.4f}")
            stats.append(f"Min: {series.min():.4f}")
            stats.append(f"Max: {series.max():.4f}")
            stats.append(f"Q1: {series.quantile(0.25):.4f}")
            stats.append(f"Q3: {series.quantile(0.75):.4f}")
        else:
            stats.append("--- Category Statistics ---")
            top_values = series.value_counts().head(5)
            stats.append("\nTop 5 values:")
            for val, count in top_values.items():
                stats.append(f"  {val}: {count}")

        return "\n".join(stats)



KEYBOARD_SHORTCUTS = {
    'Ctrl+O': 'Open file',
    'Ctrl+S': 'Save analysis',
    'Ctrl+E': 'Export report',
    'Ctrl+R': 'Run calculations',
    'Ctrl+C': 'Clear data',
    'Ctrl+F': 'Find in data',
    'Ctrl+Q': 'Quit application',
    'F5': 'Refresh history',
    'Ctrl+P': 'Generate plot',
    'Ctrl+T': 'Run statistical test'
}


def show_keyboard_shortcuts_dialog(parent=None):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Keyboard Shortcuts")
    layout = QVBoxLayout()

    text = QTextEdit()
    text.setReadOnly(True)

    shortcuts_text = "=== KEYBOARD SHORTCUTS ===\n\n"
    for key, action in KEYBOARD_SHORTCUTS.items():
        shortcuts_text += f"{key:15} - {action}\n"

    text.setText(shortcuts_text)
    text.setFont(QFont("Courier", 10))
    layout.addWidget(text)

    close_btn = QPushButton("Close")
    close_btn.clicked.connect(dialog.accept)
    layout.addWidget(close_btn)

    dialog.setLayout(layout)
    dialog.resize(400, 400)
    dialog.exec()