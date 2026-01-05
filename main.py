from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFileDialog, QWidget,
    QMessageBox, QTableWidget, QPushButton, QTableWidgetItem,
    QTextEdit, QCheckBox, QLabel, QHBoxLayout, QGroupBox,QTabWidget,
    QRadioButton,QComboBox,QDoubleSpinBox,QInputDialog,QDialog,QListWidget,
    QDialogButtonBox

)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from database import DatabaseManager
import sys
import pandas as pd
import numpy as np
import os
from datetime import datetime
from scipy import stats
from scipy.stats import ttest_1samp,ttest_ind,chi2_contingency,f_oneway
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class StatCalculator(QMainWindow):

    def __init__(self):
        super().__init__()

        # Initialize variables
        self.data = None
        self.current_dataset_id = None
        self.dataManager = DatabaseManager()
        self.fileName = None
        self.original_data = None
        self.alpha = 0.05

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

        #tests tab
        test_tab = QWidget()
        test_layout = QVBoxLayout()

        self.create_tests_panel()
        test_layout.addWidget(self.test_panel)

        self.test_results_text = QTextEdit()
        self.test_results_text.setReadOnly(True)
        self.test_results_text.setPlaceholderText("Test results will appear here")
        test_layout.addWidget(self.test_results_text)

        test_layout.addStretch()
        test_tab.setLayout(test_layout)

        #plot tab
        plot_tab = QWidget()
        plot_layout = QVBoxLayout()

        self.create_plots_panel()
        plot_layout.addWidget(self.plot_panel)

        plot_layout.addStretch()
        plot_tab.setLayout(plot_layout)

        #tabs
        self.tabs.addTab(data_tab,"Data View")
        self.tabs.addTab(calc_tab,"Calculations")
        self.tabs.addTab(clean_tab,"Data Cleaning")
        self.tabs.addTab(test_tab,"statistical Tests")
        self.tabs.addTab(plot_tab,"Plotting")

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

        if self.data is not None:
            columns = self.data.columns.tolist()
            self.column1_combo.clear()
            self.column1_combo.addItems(columns)
            self.column1_combo.setEnabled(True)

            self.column2_combo.clear()
            self.column2_combo.addItems(columns)
            self.column2_combo.setEnabled(True)

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

    def create_tests_panel(self):
        self.test_panel = QGroupBox("test panel")
        test_layout = QVBoxLayout()

        #test selection buttons
        select_test = QGroupBox("select a test")
        select_test_layout = QVBoxLayout()

        self.OneT_test = QRadioButton("One-Sample T-Test")
        self.TwoT_test = QRadioButton("Two-Sample T-Test")
        self.PairedT_test = QRadioButton("Paired T-Test")
        self.Chi2_test = QRadioButton("Chi-Square Test")
        self.Anova = QRadioButton("Anova")

        self.OneT_test.setChecked(True)

        select_test_layout.addWidget(self.OneT_test)
        select_test_layout.addWidget(self.TwoT_test)
        select_test_layout.addWidget(self.PairedT_test)
        select_test_layout.addWidget(self.Chi2_test)
        select_test_layout.addWidget(self.Anova)

        select_test.setLayout(select_test_layout)
        test_layout.addWidget(select_test)

        #column selection buttons
        select_column = QGroupBox("select column")
        column_layout = QVBoxLayout()

        column_layout.addWidget(QLabel("Column 1: "))
        self.column1_combo = QComboBox()
        self.column1_combo.setEnabled(False)
        column_layout.addWidget(self.column1_combo)

        column_layout.addWidget(QLabel("Column 2: "))
        self.column2_combo = QComboBox()
        self.column2_combo.setEnabled(False)
        column_layout.addWidget(self.column2_combo)

        select_column.setLayout(column_layout)
        test_layout.addWidget(select_column)

        #Parameters
        params_group = QGroupBox("Test Parameters")
        params_layout = QVBoxLayout()

        params_layout.addWidget(QLabel("Significance level (α) :"))
        self.params = QDoubleSpinBox()
        self.params.setRange(0.01,0.1)
        self.params.setDecimals(2)
        self.params.setSingleStep(0.01)
        self.params.setValue(0.05)
        self.params.setPrefix("α = ")
        self.params.valueChanged.connect(self.alpha_changed)

        params_layout.addWidget(self.params)
        params_group.setLayout(params_layout)
        test_layout.addWidget(params_group)

        #run calculations button
        RunT_btn = QPushButton("Run Test")
        RunT_btn.clicked.connect(self.run_test)
        test_layout.addWidget(RunT_btn)

        self.test_panel.setLayout(test_layout)

        self.OneT_test.toggled.connect(self.update_column_selection)
        self.TwoT_test.toggled.connect(self.update_column_selection)
        self.PairedT_test.toggled.connect(self.update_column_selection)
        self.Chi2_test.toggled.connect(self.update_column_selection)
        self.Anova.toggled.connect(self.update_column_selection)

    def alpha_changed(self,value):
        self.alpha = value

    def update_column_selection(self):
        has_data = self.data is not None

        if self.OneT_test.isChecked():
            self.column1_combo.setEnabled(has_data)
            self.column2_combo.setEnabled(False)

        elif self.TwoT_test.isChecked() or self.PairedT_test.isChecked():
            self.column1_combo.setEnabled(has_data)
            self.column2_combo.setEnabled(has_data)

        elif self.Chi2_test.isChecked():
            self.column1_combo.setEnabled(has_data)
            self.column2_combo.setEnabled(has_data)

        elif self.Anova.isChecked():

            self.column1_combo.setEnabled(False)
            self.column2_combo.setEnabled(False)

    def run_test(self):
        if self.data is None :
            QMessageBox.warning(self,"No data","Please load data first")
            return

        if self.OneT_test.isChecked():
            self.run_one_sample_ttest()
        elif self.TwoT_test.isChecked():
            self.run_two_sample_ttest()
        elif self.PairedT_test.isChecked():
            self.run_paired_ttest()
        elif self.Chi2_test.isChecked():
            self.run_chi_square_test()
        elif self.Anova.isChecked():
            self.run_anova_test()

    def run_one_sample_ttest(self):
        column_name = self.column1_combo.currentText()

        if not column_name:
            QMessageBox().warning(self,"No column","Please select a column")
            return

        data = self.data[column_name].dropna()

        if len(data) == 0:
            QMessageBox.warning(self,"Error","Selected an empty column")
            return

        if not pd.api.types.is_numeric_dtype(data):
            QMessageBox.warning(self,"Error","Selected a non numeric column")
            return

        test_value,ok=QInputDialog.getDouble(
            self,
            "Population Mean",
            "Enter the population men to test against : ",
            value = data.mean(),
            decimals=2
        )

        if not ok:
            return

        try:
            statistic,p_value = stats.ttest_1samp(data,test_value)

            results = []
            results.append("="*60)
            results.append("ONE-SAMPLE T-TEST RESULTS")
            results.append("="*60)
            results.append(f'Date : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            results.append(f"Dataset : {self.fileName}")
            results.append(f"")
            results.append("--- Test Information ---")
            results.append(f"Column : {column_name}")
            results.append(f"Sample Size : {len(data)}")
            results.append(f"Population Mean (HO) : {test_value}")
            results.append("")
            results.append("--- Sample test ---")
            results.append(f"Sample Mean : {data.mean():.4f}")
            results.append(f"Sample std Dev : {data.std()/np.sqrt(len(data)):.4f}")
            results.append("")
            results.append("--- Test Results ---")
            results.append(f"Test Statistic (t) : {statistic:.4f}")
            results.append(f"p-Value : {p_value:.4f}")
            results.append(f"Significance level (α) : {self.alpha}")
            results.append(f"Degree of freedom : {len(data) - 1}")
            results.append("")

            if p_value<self.alpha:
                results.append("--- Interpretation ---")
                results.append("STATISTICALLY SIGNIFICANT (p<α)")
                results.append("")
                results.append("Decision : Reject the null hypothesis")
                results.append(f"Conclusion : the sample mean ({data.mean():.4f}) is")
                results.append(f"significantly different from the population mean ({test_value})")
            else:
                results.append("--- Interpretation ---")
                results.append("NOT STATISTICALLY SIGNIFICANT")
                results.append("")
                results.append("Decision : Fail to reject the null hypothesis")
                results.append(f"Conclusion : the sample mean ({data.mean():.4f}) is")
                results.append(f"not significantly different from the population mean ({test_value})")

            results.append("")
            results.append("="*60)

            self.test_results_text.setText("\n".join(results))
            self.statusbar.showMessage("One-Sample T-Test completed")

            test_results_dict = {
                'test_type' : 'One-Sample T-Test',
                'column' : column_name,
                'test_value' : test_value,
                'statistic' : float(statistic),
                'p_value' : float(p_value),
                'alpha' : self.alpha,
                'significance' : p_value < self.alpha
            }

            self.dataManager.save_analysis(
                self.current_dataset_id,
                f"One-Sample T-Test - {column_name}",
                ['Statistical test'],
                test_results_dict
            )

        except Exception as e:
            QMessageBox.critical(self,"Error",f"test failed : {str(e)}")

    def run_two_sample_ttest(self):
        col1_name = self.column1_combo.currentText()
        col2_name = self.column2_combo.currentText()

        if not col1_name or not col2_name :
            QMessageBox.warning(self,"no column","please select columns for test")
            return
        if col1_name == col2_name:
            QMessageBox.warning(self,"Same column","please choose two different columns")
            return

        data1 = self.data[col1_name].dropna()
        data2 = self.data[col2_name].dropna()

        if len(data1) == 0 or len(data2) == 0:
            QMessageBox.warning(self,"Error","one or both columns are empty")
            return
        if not (pd.api.types.is_numeric_dtype(data1) and pd.api.types.is_numeric_dtype(data2)):
            QMessageBox.warning(self,"Error","both columns need to be numric")
            return

        try:
            statistic,p_value = stats.ttest_ind(data1,data2)
            results = []
            results.append("=" * 60)
            results.append("TWO-SAMPLE T-TEST RESULTS")
            results.append("=" * 60)
            results.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append(f"Dataset: {self.fileName}")
            results.append("")
            results.append("--- Columns Tested ---")
            results.append(f"Group 1: {col1_name} (n={len(data1)})")
            results.append(f"Group 2: {col2_name} (n={len(data2)})")
            results.append("")
            results.append("--- Group Statistics ---")
            results.append(f"Group 1 Mean: {data1.mean():.4f} (SD: {data1.std():.4f})")
            results.append(f"Group 2 Mean: {data2.mean():.4f} (SD: {data2.std():.4f})")
            results.append(f"Mean Difference: {data1.mean() - data2.mean():.4f}")
            results.append("")
            results.append("--- Test Results ---")
            results.append(f"Test Statistic (t): {statistic:.4f}")
            results.append(f"P-Value: {p_value:.4f}")
            results.append(f"Significance level (α) : {self.alpha}")
            results.append("")

            if p_value < self.alpha:
                results.append("--- Interpretation ---")
                results.append("✅ STATISTICALLY SIGNIFICANT (p < α)")
                results.append("")
                results.append("Decision: REJECT the null hypothesis")
                results.append(f"Conclusion: There IS a significant difference between")
                results.append(f"{col1_name} and {col2_name}.")
            else:
                results.append("--- Interpretation ---")
                results.append("❌ NOT STATISTICALLY SIGNIFICANT (p ≥ α)")
                results.append("")
                results.append("Decision: FAIL TO REJECT the null hypothesis")
                results.append(f"Conclusion: There is NO significant difference between")
                results.append(f"{col1_name} and {col2_name}.")

            results.append("")
            results.append("="*60)

            self.test_results_text.setText("\n".join(results))
            self.statusbar.showMessage("Two-Sample T-Test completed")

            test_results_dict = {
                'test_type': 'Two-Sample T-Test',
                'column1': col1_name,
                'column2': col2_name,
                'statistic': float(statistic),
                'p_value': float(p_value),
                'alpha': self.alpha,
                'significant': p_value < self.alpha
            }

            self.dataManager.save_analysis(
                self.current_dataset_id,
                f"Two-Sample T-Test - {col1_name} vs {col2_name}",
                ['Statistical Test'],
                test_results_dict
            )

        except Exception as e:
            QMessageBox.critical(self,"Error",f"test failed : {str(e)}")

    def run_paired_ttest(self):
        col1_name = self.column1_combo.currentText()
        col2_name = self.column2_combo.currentText()

        if not col1_name or not col2_name:
            QMessageBox.warning(self, "No Columns", "Please select two columns!")
            return

        if col1_name == col2_name:
            QMessageBox.warning(self, "Same Column", "Please select two different columns!")
            return

        data1 = self.data[col1_name]
        data2 = self.data[col2_name]

        valid_mask = data1.notna() & data2.notna()
        data1_clean = data1[valid_mask]
        data2_clean = data2[valid_mask]

        if len(data1_clean) == 0:
            QMessageBox.warning(self, "Error", "No valid paired observations found!")
            return

        if not (pd.api.types.is_numeric_dtype(data1_clean) and pd.api.types.is_numeric_dtype(data2_clean)):
            QMessageBox.warning(self, "Error", "Both columns must be numeric!")
            return

        try:
            statistic, p_value = stats.ttest_rel(data1_clean, data2_clean)

            differences = data1_clean - data2_clean
            mean_diff = differences.mean()

            results = []
            results.append("=" * 60)
            results.append("PAIRED T-TEST RESULTS")
            results.append("=" * 60)
            results.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append(f"Dataset: {self.fileName}")
            results.append("")
            results.append("--- Test Information ---")
            results.append("Test Type: Paired Samples T-Test")
            results.append("(Tests if the mean difference between paired observations is zero)")
            results.append("")
            results.append("--- Columns Tested ---")
            results.append(f"Column 1: {col1_name}")
            results.append(f"Column 2: {col2_name}")
            results.append(f"Valid Pairs: {len(data1_clean)}")
            results.append("")
            results.append("--- Descriptive Statistics ---")
            results.append(f"{col1_name} Mean: {data1_clean.mean():.4f} (SD: {data1_clean.std():.4f})")
            results.append(f"{col2_name} Mean: {data2_clean.mean():.4f} (SD: {data2_clean.std():.4f})")
            results.append("")
            results.append("--- Difference Statistics ---")
            results.append(f"Mean Difference: {mean_diff:.4f}")
            results.append(f"Std Dev of Differences: {differences.std():.4f}")
            results.append(f"Standard Error: {differences.std() / np.sqrt(len(differences)):.4f}")
            results.append("")
            results.append("--- Test Results ---")
            results.append(f"Test Statistic (t): {statistic:.4f}")
            results.append(f"P-Value: {p_value:.4f}")
            results.append(f"Significance Level (α): {self.alpha}")
            results.append(f"Degrees of Freedom: {len(data1_clean) - 1}")
            results.append("")

            if p_value < self.alpha:
                results.append("--- Interpretation ---")
                results.append("STATISTICALLY SIGNIFICANT (p < α)")
                results.append("")
                results.append("Decision: REJECT the null hypothesis")
                results.append("")
                results.append("Conclusion: There IS a significant difference between")
                results.append(f"the paired observations in {col1_name} and {col2_name}.")
                results.append("")
                if mean_diff > 0:
                    results.append(f"On average, {col1_name} is higher than {col2_name} by {abs(mean_diff):.4f}.")
                else:
                    results.append(f"On average, {col2_name} is higher than {col1_name} by {abs(mean_diff):.4f}.")
            else:
                results.append("--- Interpretation ---")
                results.append("NOT STATISTICALLY SIGNIFICANT (p ≥ α)")
                results.append("")
                results.append("Decision: FAIL TO REJECT the null hypothesis")
                results.append("")
                results.append("Conclusion: There is NO significant difference between")
                results.append(f"the paired observations in {col1_name} and {col2_name}.")

            results.append("")
            results.append("=" * 60)

            self.test_results_text.setText("\n".join(results))
            self.statusbar.showMessage("Paired T-Test completed!")

            test_results_dict = {
                'test_type': 'Paired T-Test',
                'column1': col1_name,
                'column2': col2_name,
                'mean_difference': float(mean_diff),
                'statistic': float(statistic),
                'p_value': float(p_value),
                'alpha': self.alpha,
                'significant': p_value < self.alpha
            }

            self.dataManager.save_analysis(
                self.current_dataset_id,
                f"Paired T-Test - {col1_name} vs {col2_name}",
                ['Statistical Test'],
                test_results_dict
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed: {str(e)}")

    def run_chi_square_test(self):
        col1_name = self.column1_combo.currentText()
        col2_name = self.column2_combo.currentText()

        if not col1_name or not col2_name:
            QMessageBox.warning(self, "No Columns", "Please select two columns!")
            return

        if col1_name == col2_name:
            QMessageBox.warning(self, "Same Column", "Please select two different columns!")
            return

        data1 = self.data[col1_name].dropna()
        data2 = self.data[col2_name].dropna()

        if len(data1) == 0 or len(data2) == 0:
            QMessageBox.warning(self, "Error", "One or both columns are empty!")
            return

        unique1 = data1.nunique()
        unique2 = data2.nunique()

        if unique1 > 20 or unique2 > 20:
            reply = QMessageBox.question(
                self,
                "Many Categories",
                f"Column 1 has {unique1} unique values and Column 2 has {unique2}.\n"
                "Chi-square works best with categorical data (few categories).\n\n"
                "Continue anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        try:
            contingency_table = pd.crosstab(
                self.data[col1_name],
                self.data[col2_name],
                dropna=True
            )

            chi2_stat, p_value, dof, expected_freq = stats.chi2_contingency(contingency_table)

            results = []
            results.append("=" * 60)
            results.append("CHI-SQUARE TEST OF INDEPENDENCE")
            results.append("=" * 60)
            results.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append(f"Dataset: {self.fileName}")
            results.append("")
            results.append("--- Test Information ---")
            results.append("Tests whether two categorical variables are independent")
            results.append("")
            results.append("--- Variables Tested ---")
            results.append(f"Variable 1: {col1_name} ({unique1} categories)")
            results.append(f"Variable 2: {col2_name} ({unique2} categories)")
            results.append("")
            results.append("--- Contingency Table ---")
            results.append(str(contingency_table))
            results.append("")
            results.append("--- Test Results ---")
            results.append(f"Chi-Square Statistic (χ²): {chi2_stat:.4f}")
            results.append(f"P-Value: {p_value:.4f}")
            results.append(f"Degrees of Freedom: {dof}")
            results.append(f"Significance Level (α): {self.alpha}")
            results.append("")

            min_expected = expected_freq.min()
            results.append("--- Assumption Check ---")
            results.append(f"Minimum Expected Frequency: {min_expected:.2f}")
            if min_expected < 5:
                results.append("WARNING: Some expected frequencies < 5")
                results.append("Results may not be reliable!")
            else:
                results.append("All expected frequencies >= 5 (assumption satisfied)")
            results.append("")

            if p_value < self.alpha:
                results.append("--- Interpretation ---")
                results.append("STATISTICALLY SIGNIFICANT (p < α)")
                results.append("")
                results.append("Decision: REJECT the null hypothesis")
                results.append("")
                results.append(f"Conclusion: {col1_name} and {col2_name} are NOT independent.")
                results.append("There IS a significant association between these variables.")
            else:
                results.append("--- Interpretation ---")
                results.append("NOT STATISTICALLY SIGNIFICANT (p ≥ α)")
                results.append("")
                results.append("Decision: FAIL TO REJECT the null hypothesis")
                results.append("")
                results.append(f"Conclusion: {col1_name} and {col2_name} are independent.")
                results.append("There is NO significant association between these variables.")

            results.append("")
            results.append("=" * 60)

            self.test_results_text.setText("\n".join(results))
            self.statusbar.showMessage("Chi-Square Test completed!")

            test_results_dict = {
                'test_type': 'Chi-Square Test',
                'variable1': col1_name,
                'variable2': col2_name,
                'chi2_statistic': float(chi2_stat),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'alpha': self.alpha,
                'significant': p_value < self.alpha
            }

            self.dataManager.save_analysis(
                self.current_dataset_id,
                f"Chi-Square Test - {col1_name} vs {col2_name}",
                ['Statistical Test'],
                test_results_dict
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed: {str(e)}")

    def run_anova_test(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return

        numeric_cols = self.data.select_dtypes(include=['number']).columns.tolist()

        if len(numeric_cols) < 3:
            QMessageBox.warning(
                self,
                "Not Enough Groups",
                "ANOVA requires at least 3 groups (numeric columns).\n"
                f"Your dataset has only {len(numeric_cols)} numeric columns."
            )
            return

        from PySide6.QtWidgets import QDialog, QListWidget, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Columns for ANOVA")
        dialog_layout = QVBoxLayout()

        dialog_layout.addWidget(QLabel("Select at least 3 columns to compare:"))

        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.MultiSelection)
        list_widget.addItems(numeric_cols)
        dialog_layout.addWidget(list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)

        dialog.setLayout(dialog_layout)

        if dialog.exec() != QDialog.Accepted:
            return

        selected_items = list_widget.selectedItems()
        selected_cols = [item.text() for item in selected_items]

        if len(selected_cols) < 3:
            QMessageBox.warning(self, "Not Enough Groups", "Please select at least 3 columns!")
            return

        try:
            groups = []
            group_stats = []

            for col in selected_cols:
                data = self.data[col].dropna()
                groups.append(data)
                group_stats.append({
                    'name': col,
                    'n': len(data),
                    'mean': data.mean(),
                    'std': data.std()
                })

            f_stat, p_value = stats.f_oneway(*groups)

            all_data = pd.concat([self.data[col].dropna() for col in selected_cols])
            grand_mean = all_data.mean()

            results = []
            results.append("=" * 60)
            results.append("ONE-WAY ANOVA RESULTS")
            results.append("=" * 60)
            results.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            results.append(f"Dataset: {self.fileName}")
            results.append("")
            results.append("--- Test Information ---")
            results.append("Tests whether means of 3+ groups are all equal")
            results.append(f"Number of Groups: {len(selected_cols)}")
            results.append("")
            results.append("--- Groups Compared ---")
            for i, stats_dict in enumerate(group_stats, 1):
                results.append(f"Group {i}: {stats_dict['name']}")
                results.append(
                    f"  n = {stats_dict['n']}, Mean = {stats_dict['mean']:.4f}, SD = {stats_dict['std']:.4f}")
            results.append("")
            results.append(f"Grand Mean (all groups): {grand_mean:.4f}")
            results.append("")
            results.append("--- ANOVA Results ---")
            results.append(f"F-Statistic: {f_stat:.4f}")
            results.append(f"P-Value: {p_value:.4f}")
            results.append(f"Significance Level (α): {self.alpha}")
            results.append("")

            if p_value < self.alpha:
                results.append("--- Interpretation ---")
                results.append("STATISTICALLY SIGNIFICANT (p < α)")
                results.append("")
                results.append("Decision: REJECT the null hypothesis")
                results.append("")
                results.append("Conclusion: At least one group mean is significantly")
                results.append("different from the others.")
                results.append("")
                results.append("NOTE: ANOVA doesn't tell you WHICH groups differ.")
                results.append("Consider post-hoc tests (e.g., Tukey HSD) to find out.")
            else:
                results.append("--- Interpretation ---")
                results.append("NOT STATISTICALLY SIGNIFICANT (p ≥ α)")
                results.append("")
                results.append("Decision: FAIL TO REJECT the null hypothesis")
                results.append("")
                results.append("Conclusion: All group means are not significantly")
                results.append("different from each other.")

            results.append("")
            results.append("=" * 60)

            self.test_results_text.setText("\n".join(results))
            self.statusbar.showMessage("ANOVA completed!")

            test_results_dict = {
                'test_type': 'One-Way ANOVA',
                'groups': selected_cols,
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'alpha': self.alpha,
                'significant': p_value < self.alpha,
                'group_means': {stat['name']: float(stat['mean']) for stat in group_stats}
            }

            self.dataManager.save_analysis(
                self.current_dataset_id,
                f"ANOVA - {', '.join(selected_cols[:3])}{'...' if len(selected_cols) > 3 else ''}",
                ['Statistical Test'],
                test_results_dict
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"ANOVA failed: {str(e)}")

    def create_plots_panel(self):
        self.plot_panel = QGroupBox("Plot Panel")
        plot_layout = QHBoxLayout()


        #right side
        right_plot_panel = QGroupBox("plot controls")
        right_layout = QVBoxLayout()
        #left side
        left_plot_panel = QGroupBox("Plot display")
        left_layout = QVBoxLayout()

        #plot selection panel
        select_plot = QGroupBox("select the plot type you like")
        plot_selection_layout = QVBoxLayout()

        Histogram = QRadioButton("Histogram")
        Box_plot = QRadioButton("Box plot")
        Scatter_plot = QRadioButton("Scatter plot")
        Plot_bar = QRadioButton("Plot bar")
        Line_plot = QRadioButton("Line plot")
        Correlation_Heatmap = QRadioButton("Correlation heatmap")

        plot_selection_layout.addWidget(Histogram)
        plot_selection_layout.addWidget(Box_plot)
        plot_selection_layout.addWidget(Scatter_plot)
        plot_selection_layout.addWidget(Line_plot)
        plot_selection_layout.addWidget(Correlation_Heatmap)

        select_plot.setLayout(plot_selection_layout)
        right_layout.addWidget(select_plot)

        #Column selection

        select_column = QGroupBox("select columns for plotting")
        column_selection_layout = QVBoxLayout()

        column_selection_layout.addWidget(QLabel("Column 1: "))
        self.column1_combo = QComboBox()
        self.column1_combo.setEnabled(False)
        column_selection_layout.addWidget(self.column1_combo)

        column_selection_layout.addWidget(QLabel("Column 2: "))
        self.column2_combo = QComboBox()
        self.column2_combo.setEnabled(False)
        column_selection_layout.addWidget(self.column2_combo)

        select_column.setLayout(column_selection_layout)
        right_layout.addWidget(select_column)

        #buttons

        select_button = QGroupBox()
        button_selection_layout = QVBoxLayout()

        Generate_button = QPushButton("Generate plot")
        Save_button = QPushButton("Save button")

        button_selection_layout.addWidget(Generate_button)
        button_selection_layout.addWidget(Save_button)

        select_button.setLayout(button_selection_layout)

        right_layout.addWidget(select_button)

        right_plot_panel.setLayout(right_layout)

        plot_layout.addWidget(right_plot_panel,stretch=1)

        #left side
        self.Plot_display = QTextEdit()
        self.Plot_display.setReadOnly(True)
        self.Plot_display.setPlaceholderText("Plots will display here")

        left_layout.addWidget(self.Plot_display)
        left_plot_panel.setLayout(left_layout)

        plot_layout.addWidget(left_plot_panel,stretch=2)

        self.plot_panel.setLayout(plot_layout)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatCalculator()
    window.show()
    sys.exit(app.exec())


