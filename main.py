from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFileDialog, QWidget,
    QMessageBox, QTableWidget, QPushButton, QTableWidgetItem,
    QTextEdit, QCheckBox, QLabel, QHBoxLayout, QGroupBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from database import DatabaseManager
import sys
import pandas as pd
import os
from datetime import datetime


class StatCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize variables
        self.data = None
        self.current_dataset_id = None
        self.dataManager = DatabaseManager()
        self.fileName = None

        # Setup UI
        self.setWindowTitle("Statistical Calculator")
        self.setGeometry(100, 100, 1100, 700)

        self.setup_ui()
        self.create_menubar()
        self.create_statusbar()

    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        container = QWidget()
        main_layout = QHBoxLayout(container)

        # Left side
        left_layout = QVBoxLayout()

        # Table
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.table)

        # Results text
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here...")
        left_layout.addWidget(self.results_text)

        # Right side
        right_layout = QVBoxLayout()

        # Calculation panel
        self.create_calculation_panel()
        right_layout.addWidget(self.select_calculations)  # ✅ Add stored widget

        # Calculate button
        self.calc_button = QPushButton('Calculate Statistics')
        self.calc_button.clicked.connect(self.run_calculations)
        self.calc_button.setEnabled(False)
        right_layout.addWidget(self.calc_button)

        # Clear button
        clear_btn = QPushButton("Clear Data")
        clear_btn.clicked.connect(self.clear_data)
        right_layout.addWidget(clear_btn)

        # Push buttons to top
        right_layout.addStretch()

        # Add layouts to main
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)

        self.setCentralWidget(container)

    def create_calculation_panel(self):
        """Create panel with calculation checkboxes"""
        self.select_calculations = QGroupBox('Select Calculations')
        calc_layout = QVBoxLayout()

        self.calc_checkboxes = {}
        calculations = [
            'Mean',
            'Median',
            'Mode',
            'Standard Deviation',
            'Variance',
            'Min',
            'Max',
            'Count'
        ]

        for calc in calculations:
            checkbox = QCheckBox(calc)
            self.calc_checkboxes[calc] = checkbox
            calc_layout.addWidget(checkbox)

        calc_layout.addWidget(QLabel(""))
        select_all_cb = QCheckBox("Select All")
        select_all_cb.stateChanged.connect(self.toggle_all_calculations)
        calc_layout.addWidget(select_all_cb)

        self.select_calculations.setLayout(calc_layout)

    def toggle_all_calculations(self, state):
        """Select or deselect all calculation checkboxes"""
        checked = (state == Qt.Checked)
        for checkbox in self.calc_checkboxes.values():
            checkbox.setChecked(checked)

    def create_menubar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_statusbar(self):
        """Create status bar"""
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")

    def open_file(self):
        """Open and load data file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )

        if not file_path:
            return

        self.statusbar.showMessage("Loading file...")

        try:
            # Load file
            if file_path.lower().endswith(".csv"):
                self.data = pd.read_csv(file_path)
            elif file_path.lower().endswith((".xlsx", ".xls")):
                self.data = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")

            # Get file info
            rows, cols = self.data.shape
            self.fileName = os.path.basename(file_path)

            # Display in table
            self.display_data_in_table(self.data)

            # Update status
            self.statusbar.showMessage(
                f"Loaded: {self.fileName} | Rows: {rows}, Columns: {cols}"
            )

            # Save to database
            self.current_dataset_id = self.dataManager.register_dataset(
                self.fileName,
                file_path,
                self.data
            )

            if self.current_dataset_id:
                print(f"Dataset saved to database with ID: {self.current_dataset_id}")

            # Enable calculate button
            self.calc_button.setEnabled(True)

        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            self.statusbar.showMessage(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.data = None
            return

    def display_data_in_table(self, dataframe, max_rows=1000):
        """Display DataFrame in table widget"""
        try:
            rows_to_show = min(len(dataframe), max_rows)

            if len(dataframe) > max_rows:
                QMessageBox.information(
                    self,
                    "Large Dataset",
                    f"Dataset has {len(dataframe)} rows.\n"
                    f"Displaying first {max_rows} rows only.\n\n"
                    f"All data is loaded and will be used in calculations."
                )

            self.table.setRowCount(rows_to_show)
            self.table.setColumnCount(len(dataframe.columns))
            self.table.setHorizontalHeaderLabels(dataframe.columns.tolist())

            for row_idx in range(rows_to_show):
                for col_idx, value in enumerate(dataframe.iloc[row_idx]):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)

            self.table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Display Error",
                f"Failed to display data: {str(e)}"
            )

    def run_calculations(self):
        """Run selected statistical calculations"""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return

        selected_calc = [
            name for name, checkbox in self.calc_checkboxes.items()
            if checkbox.isChecked()
        ]

        if not selected_calc:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one calculation!"
            )
            return

        try:
            # Filter to numeric columns only
            numeric_data = self.data.select_dtypes(include=['number'])  # ✅ Fixed typo

            if numeric_data.empty:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No numeric columns found in dataset!"
                )
                return

            # Prepare results display
            results = []
            results.append("=" * 50)
            results.append("STATISTICAL ANALYSIS RESULTS")
            results.append("=" * 50)
            results.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")  # ✅ Fixed format
            results.append(f"Dataset: {self.fileName}")
            results.append(f"Rows: {len(self.data)} | Columns: {len(numeric_data.columns)}")
            results.append("")
            results.append("-" * 50)
            results.append("RESULTS")
            results.append("-" * 50)
            results.append("")

            # Store results for database
            results_dict = {}

            # Calculate for each selected stat
            for calc in selected_calc:
                results.append(f"=== {calc} ===")

                if calc == "Mean":
                    res = numeric_data.mean()
                elif calc == "Median":
                    res = numeric_data.median()
                elif calc == "Mode":
                    res = numeric_data.mode().iloc[0] if not numeric_data.mode().empty else None  # ✅ Fixed
                elif calc == "Standard Deviation":
                    res = numeric_data.std()
                elif calc == "Variance":
                    res = numeric_data.var()
                elif calc == "Min":
                    res = numeric_data.min()
                elif calc == "Max":
                    res = numeric_data.max()
                elif calc == "Count":
                    res = numeric_data.count()
                else:
                    continue

                for col, value in res.items():
                    results.append(
                        f"  {col}: {value:.4f}" if isinstance(value, float)
                        else f"  {col}: {value}"
                    )

                    if col not in results_dict:
                        results_dict[col] = {}
                    results_dict[col][calc] = float(value) if pd.notna(value) else None

                results.append("")

            results.append("=" * 50)

            # Display results
            self.results_text.setText("\n".join(results))

            # Save to database
            analysis_id = self.dataManager.save_analysis(
                self.current_dataset_id,
                f"Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                selected_calc,
                results_dict
            )

            if analysis_id:
                self.statusbar.showMessage("Calculations completed and saved!")
                print(f"Analysis saved with ID: {analysis_id}")
            else:
                self.statusbar.showMessage("Calculations completed but save failed")

        except Exception as e:
            error_msg = f"Calculation error: {str(e)}"
            self.statusbar.showMessage(error_msg)
            QMessageBox.critical(self, "Calculation Error", error_msg)

    def clear_data(self):
        """Clear table and reset data"""
        self.table.clearContents()
        self.table.setRowCount(0)
        self.results_text.clear()
        self.data = None
        self.current_dataset_id = None
        self.fileName = None
        self.calc_button.setEnabled(False)
        self.statusbar.showMessage("Data cleared. Ready to load new file.")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About",
            "Statistical Calculator v1.0\n\n"
            "A tool for statistical analysis and data visualization.\n\n"
            "Created for Python School Project 2024"
        )

    def closeEvent(self, event):
        """Handle window close event"""
        self.dataManager.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatCalculator()
    window.show()
    sys.exit(app.exec())


