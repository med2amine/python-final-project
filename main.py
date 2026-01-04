from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFileDialog, QWidget,
    QMessageBox, QTableWidget, QPushButton, QTableWidgetItem,
    QTextEdit, QCheckBox, QLabel, QHBoxLayout, QGroupBox,QTabWidget
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
        self.original_data = None

        # Setup UI
        self.setWindowTitle("Statistical Calculator")
        self.setGeometry(100, 100, 1100, 700)

        self.setup_ui()
        self.create_menubar()
        self.create_statusbar()

    def setup_ui(self):
        """Setup the main user interface"""
        #tab widget
        self.tabs = QTabWidget()

        #data view
        data_tab = QWidget()
        data_layout = QVBoxLayout()

        # Table
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Results text
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here...")

        data_layout.addWidget(self.table)
        data_layout.addWidget(self.results_text)
        data_tab.setLayout(data_layout)

        #calculations

        calc_tab = QWidget()
        calc_layout = QVBoxLayout()

        # Calculation panel
        self.create_calculation_panel()
        calc_layout.addWidget(self.select_calculations)  # ✅ Add stored widget

        # Calculate button
        self.calc_button = QPushButton('Calculate Statistics')
        self.calc_button.clicked.connect(self.run_calculations)
        self.calc_button.setEnabled(False)
        calc_layout.addWidget(self.calc_button)

        # Clear button
        clear_btn = QPushButton("Clear Data")
        clear_btn.clicked.connect(self.clear_data)
        calc_layout.addWidget(clear_btn)

        # Push buttons to top
        calc_layout.addStretch()
        calc_tab.setLayout(calc_layout)

        #data handling panel
        clean_tab = QWidget()
        clean_layout = QVBoxLayout()

        self.create_cleaning_panel()
        clean_layout.addWidget(self.data_cleaning)

        clean_layout.addStretch()
        clean_tab.setLayout(clean_layout)

        #tabs
        self.tabs.addTab(data_tab,"Data View")
        self.tabs.addTab(calc_tab,"Calculations")
        self.tabs.addTab(clean_tab,"Data Cleaning")

        #central widget
        self.setCentralWidget(self.tabs)

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
        checked = (state != Qt.Checked)
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
        self.original_data = self.data.copy()

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

    def create_cleaning_panel(self):
        self.data_cleaning = QGroupBox("data cleaning")
        cleaning_layout = QHBoxLayout()
        show_data = QPushButton("Show Data")
        show_data.clicked.connect(self.showData)
        missing_values = QPushButton("Handle Missing Values")
        missing_values.clicked.connect(self.missingValues)
        R_duplicates = QPushButton("Remove Duplicates")
        R_duplicates.clicked.connect(self.removeDups)
        cleaning_layout.addWidget(show_data)
        cleaning_layout.addWidget(R_duplicates)
        cleaning_layout.addWidget(missing_values)
        reset = QPushButton("reset to original")
        reset.clicked.connect(self.reset_data)
        cleaning_layout.addWidget(reset)
        self.data_cleaning.setLayout(cleaning_layout)

    def showData(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return
        rows, cols = self.data.shape
        column_type = self.data.dtypes
        null_values = self.data.isnull().sum()
        dups_values = self.data.duplicated().sum()

        infos = []
        infos.append("=== Data Information ===")
        infos.append(f'dataset : {self.fileName}')
        infos.append(f'total rows : {rows}')
        infos.append(f'total columns : {cols}')
        infos.append("--- Column Information ---")
        for col in self.data.columns :
            infos.append(
                f"{col} | "
                f"type={column_type[col]} | "
                f"nulls={null_values[col]} | "
            )
        infos.append("--- Data Quality ---")
        infos.append(f'total missing values : {null_values.sum()}')
        infos.append(f'duplicated rows : {dups_values}')
        self.results_text.setText("\n".join(infos))

    def missingValues(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return

        before_rows = len(self.data)
        before_missing = self.data.isnull().sum().sum()

        nulls = self.data.isnull().sum().sum()
        if nulls == 0:
            self.results_text.setText("No missing values found in dataset")
            return

        options = QMessageBox()
        options.setWindowTitle("Handle Missing Values")
        options.setText(f"Found {nulls} missing values.\n\nChoose how to handle them:")

        btn_remove = options.addButton("Remove Rows", QMessageBox.ActionRole)
        btn_mean = options.addButton("Fill with Mean", QMessageBox.ActionRole)
        btn_median = options.addButton("Fill with Median", QMessageBox.ActionRole)
        btn_mode = options.addButton("Fill with Mode", QMessageBox.ActionRole)
        btn_cancel = options.addButton("Cancel", QMessageBox.RejectRole)

        options.exec()
        clicked = options.clickedButton()

        action_taken = None

        if clicked == btn_remove:
            self.data.dropna(inplace=True)
            action_taken = "Removed rows with missing values"

        elif clicked == btn_mean:
            numeric_cols = self.data.select_dtypes(include=['number']).columns
            self.data[numeric_cols] = self.data[numeric_cols].fillna(self.data[numeric_cols].mean())
            action_taken = "Filled missing values with mean"

        elif clicked == btn_median:
            numeric_cols = self.data.select_dtypes(include=['number']).columns
            self.data[numeric_cols] = self.data[numeric_cols].fillna(self.data[numeric_cols].median())
            action_taken = "Filled missing values with median"

        elif clicked == btn_mode:
            for col in self.data.columns:
                if self.data[col].isnull().any():
                    mode_value = self.data[col].mode()
                    if not mode_value.empty:
                        self.data[col].fillna(mode_value.iloc[0], inplace=True)
            action_taken = "Filled missing values with mode"

        else:
            self.results_text.setText("Operation cancelled")
            return

        after_rows = len(self.data)
        after_missing = self.data.isnull().sum().sum()

        self.display_data_in_table(self.data)

        summary = self.show_cleaning_summary(
            action_taken,
            before_rows,
            after_rows,
            before_missing,
            after_missing
        )
        self.results_text.setText(summary)

        cleaned_id = self.save_cleaned_data_to_db(action_taken)
        if cleaned_id:
            self.statusbar.showMessage(f"{action_taken} and saved to database")
        else:
            self.statusbar.showMessage(f"{action_taken} (database save failed)")

    def removeDups(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return

        before_rows = len(self.data)
        dups = self.data.duplicated().sum()

        if dups == 0:
            self.results_text.setText("No duplicate rows found in dataset")
            return

        reply = QMessageBox.question(
            self,
            "Remove Duplicates",
            f"Found {dups} duplicate rows.\n\nDo you want to remove them?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.data.drop_duplicates(inplace=True)
            after_rows = len(self.data)

            self.display_data_in_table(self.data)

            summary = self.show_cleaning_summary(
                "Removed duplicate rows",
                before_rows,
                after_rows,
                0,
                0
            )
            self.results_text.setText(summary)

            cleaned_id = self.save_cleaned_data_to_db(f"Removed {dups} duplicate rows")
            if cleaned_id:
                self.statusbar.showMessage(f"Removed {dups} duplicates and saved to database")
            else:
                self.statusbar.showMessage(f"Removed {dups} duplicates (database save failed)")
        else:
            self.results_text.setText("Operation cancelled")

    def show_cleaning_summary(self, action, before_rows, after_rows, before_missing, after_missing):

        rows_removed = before_rows - after_rows

        summary = []
        summary.append("=" * 60)
        summary.append("DATA CLEANING APPLIED")
        summary.append("=" * 60)
        summary.append(f"Action: {action}")
        summary.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        summary.append("BEFORE:")
        summary.append(f"  Rows: {before_rows}")
        summary.append(f"  Missing Values: {before_missing}")
        summary.append("")
        summary.append("AFTER:")
        summary.append(f"  Rows: {after_rows}")

        if rows_removed > 0:
            summary.append(f"  Rows Removed: {rows_removed}")

        summary.append(f"  Missing Values: {after_missing}")
        summary.append("")
        summary.append("=" * 60)
        summary.append("Data updated successfully!")
        summary.append("=" * 60)

        return "\n".join(summary)

    def reset_data(self):
        if self.original_data is None:
            QMessageBox.warning(self, "No Data", "No original data to reset to!")
            return

        reply = QMessageBox.question(
            self,
            "Reset Data",
            "This will discard all cleaning operations.\n\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.data = self.original_data.copy()
            self.display_data_in_table(self.data)
            self.results_text.setText(
                "=" * 60 + "\n" +
                "DATA RESET TO ORIGINAL\n" +
                "=" * 60 + "\n" +
                f"Restored original dataset: {self.fileName}\n" +
                f"Rows: {len(self.data)}\n" +
                f"Columns: {len(self.data.columns)}\n" +
                "=" * 60
            )
            self.statusbar.showMessage("Data reset to original state")

    def save_cleaned_data_to_db(self, cleaning_action):

        if self.data is None or self.current_dataset_id is None:
            return None

        try:
            base_name = os.path.splitext(self.fileName)[0]
            extension = os.path.splitext(self.fileName)[1]
            cleaned_filename = f"{base_name}_cleaned{extension}"

            cleaned_dataset_id = self.dataManager.register_dataset(
                cleaned_filename,
                f"Cleaned: {cleaning_action}",
                self.data
            )

            if cleaned_dataset_id:
                cleaning_details = {
                    'action': cleaning_action,
                    'original_dataset_id': str(self.current_dataset_id),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'rows_before': len(self.original_data) if self.original_data is not None else 0,
                    'rows_after': len(self.data),
                    'columns': len(self.data.columns)
                }

                self.dataManager.save_analysis(
                    cleaned_dataset_id,
                    f"Cleaning - {cleaning_action}",
                    ['Data Cleaning'],
                    {'cleaning_info': cleaning_details}
                )

                print(f"Cleaned data saved to database with ID: {cleaned_dataset_id}")
                return cleaned_dataset_id

            return None

        except Exception as e:
            print(f"Error saving cleaned data: {str(e)}")
            return None



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatCalculator()
    window.show()
    sys.exit(app.exec())


