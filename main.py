from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFileDialog, QWidget,
    QMessageBox, QTableWidget, QPushButton, QTableWidgetItem,
    QTextEdit, QCheckBox, QLabel, QHBoxLayout, QGroupBox,QTabWidget,
    QRadioButton,QComboBox,QDoubleSpinBox,QInputDialog,QDialog,QListWidget,
    QDialogButtonBox,QScrollArea

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
from PLOTCANVAS import PlotCanvas
from PDFgenerator import PDFGenerator
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


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
        self.last_statistics_results = None
        self.last_test_results = None
        self.last_cleaning_summary = None
        self.generated_plots = []

        # Setup UI
        self.setWindowTitle("Statistical Calculator")
        self.setGeometry(100, 100, 1100, 700)

        self.setup_ui()
        self.create_menubar()
        self.create_statusbar()

    def setup_ui(self):
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

        #Pdf report tab
        export_tab = QWidget()
        export_layout = QVBoxLayout()

        self.create_export_panel()
        export_layout.addWidget(self.export_panel)

        export_layout.addStretch()
        export_tab.setLayout(export_layout)

        #tabs
        self.tabs.addTab(data_tab,"Data View")
        self.tabs.addTab(calc_tab,"Calculations")
        self.tabs.addTab(clean_tab,"Data Cleaning")
        self.tabs.addTab(test_tab,"statistical Tests")
        self.tabs.addTab(plot_tab,"Plotting")
        self.tabs.addTab(export_tab,"Export/Reports")

        #central widget
        self.setCentralWidget(self.tabs)

    def create_calculation_panel(self):
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
        checked = (state != Qt.Checked)
        for checkbox in self.calc_checkboxes.values():
            checkbox.setChecked(checked)

    def create_menubar(self):
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

            self.populate_plot_columns()

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

            self.last_statistics_results = {
                'timestamp': datetime.now(),
                'dataset': self.fileName,
                'results': results_dict,
                'calculations': selected_calc
            }

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

        self.last_cleaning_summary = {
            'action': action,
            'before_rows': before_rows,
            'after_rows': after_rows,
            'before_missing': before_missing,
            'after_missing': after_missing,
            'timestamp': datetime.now()
        }

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

            self.last_test_results = {
                'type': 'One-Sample T-Test',
                'timestamp': datetime.now(),
                'column': column_name,
                'results': test_results_dict
            }

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

            self.last_test_results = {
                'type': 'Two-Sample T-Test',
                'timestamp': datetime.now(),
                'columns': [col1_name,col2_name],
                'results': test_results_dict
            }

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

            self.last_test_results = {
                'type': 'Paired T-Test',
                'timestamp': datetime.now(),
                'column': [col1_name,col2_name],
                'results': test_results_dict
            }

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

            self.last_test_results = {
                'type': 'Chi square Test',
                'timestamp': datetime.now(),
                'column': [col1_name,col2_name],
                'results': test_results_dict
            }

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

            self.last_test_results = {
                'type': 'Anova Test',
                'timestamp': datetime.now(),
                'column': selected_cols,
                'results': test_results_dict
            }

        except Exception as e:
            QMessageBox.critical(self, "Error", f"ANOVA failed: {str(e)}")

    def create_plots_panel(self):
        """Create plotting interface with dynamic column selection"""
        self.plot_panel = QGroupBox("Data Visualization")
        main_layout = QHBoxLayout()

        # RIGHT SIDE: Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()

        # Plot type selection
        plot_type_group = QGroupBox("Select Plot Type")
        plot_type_layout = QVBoxLayout()

        # Store radio buttons as instance variables
        self.histogram_radio = QRadioButton("Histogram (1 column)")
        self.boxplot_radio = QRadioButton("Box Plot (1+ columns)")
        self.scatter_radio = QRadioButton("Scatter Plot (2 columns)")
        self.bar_radio = QRadioButton("Bar Chart (1 column)")
        self.line_radio = QRadioButton("Line Plot (2 columns)")
        self.heatmap_radio = QRadioButton("Correlation Heatmap (all numeric)")
        self.violin_radio = QRadioButton("Violin Plot (1+ columns)")
        self.pairplot_radio = QRadioButton("Pair Plot (2-5 columns)")

        # Set default
        self.histogram_radio.setChecked(True)

        # Connect radio buttons to update column selection UI
        self.histogram_radio.toggled.connect(self.update_column_selection_ui)
        self.boxplot_radio.toggled.connect(self.update_column_selection_ui)
        self.scatter_radio.toggled.connect(self.update_column_selection_ui)
        self.bar_radio.toggled.connect(self.update_column_selection_ui)
        self.line_radio.toggled.connect(self.update_column_selection_ui)
        self.heatmap_radio.toggled.connect(self.update_column_selection_ui)
        self.violin_radio.toggled.connect(self.update_column_selection_ui)
        self.pairplot_radio.toggled.connect(self.update_column_selection_ui)

        plot_type_layout.addWidget(self.histogram_radio)
        plot_type_layout.addWidget(self.boxplot_radio)
        plot_type_layout.addWidget(self.scatter_radio)
        plot_type_layout.addWidget(self.bar_radio)
        plot_type_layout.addWidget(self.line_radio)
        plot_type_layout.addWidget(self.heatmap_radio)
        plot_type_layout.addWidget(self.violin_radio)
        plot_type_layout.addWidget(self.pairplot_radio)

        plot_type_group.setLayout(plot_type_layout)
        controls_layout.addWidget(plot_type_group)

        # Column selection - Multiple modes
        self.column_selection_group = QGroupBox("Select Column(s)")
        self.column_selection_layout = QVBoxLayout()

        # Mode 1: Single column dropdown (for histogram, bar, etc.)
        self.single_column_widget = QWidget()
        single_layout = QVBoxLayout()
        single_layout.addWidget(QLabel("Select Column:"))
        self.plot_single_combo = QComboBox()
        self.plot_single_combo.setEnabled(False)
        single_layout.addWidget(self.plot_single_combo)
        self.single_column_widget.setLayout(single_layout)

        # Mode 2: Two columns (for scatter, line)
        self.two_column_widget = QWidget()
        two_layout = QVBoxLayout()
        two_layout.addWidget(QLabel("X-axis Column:"))
        self.plot_x_combo = QComboBox()
        self.plot_x_combo.setEnabled(False)
        two_layout.addWidget(self.plot_x_combo)
        two_layout.addWidget(QLabel("Y-axis Column:"))
        self.plot_y_combo = QComboBox()
        self.plot_y_combo.setEnabled(False)
        two_layout.addWidget(self.plot_y_combo)
        self.two_column_widget.setLayout(two_layout)

        # Mode 3: Multiple columns with checkboxes (for boxplot, violin, pairplot)
        self.multi_column_widget = QWidget()
        multi_layout = QVBoxLayout()
        multi_layout.addWidget(QLabel("Select Columns (check multiple):"))

        # Scrollable area for checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)

        self.column_checkboxes_widget = QWidget()
        self.column_checkboxes_layout = QVBoxLayout()
        self.column_checkboxes = {}  # Will store column name -> checkbox
        self.column_checkboxes_widget.setLayout(self.column_checkboxes_layout)

        scroll.setWidget(self.column_checkboxes_widget)
        multi_layout.addWidget(scroll)

        # Select All / Clear All buttons
        checkbox_buttons = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_plot_columns)
        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.clicked.connect(self.clear_all_plot_columns)
        checkbox_buttons.addWidget(select_all_btn)
        checkbox_buttons.addWidget(clear_all_btn)
        multi_layout.addLayout(checkbox_buttons)

        self.multi_column_widget.setLayout(multi_layout)

        # Mode 4: No selection needed (for correlation heatmap - uses all numeric)
        self.no_column_widget = QWidget()
        no_layout = QVBoxLayout()
        no_layout.addWidget(QLabel("(Uses all numeric columns automatically)"))
        self.no_column_widget.setLayout(no_layout)

        # Add all modes to layout (will show/hide as needed)
        self.column_selection_layout.addWidget(self.single_column_widget)
        self.column_selection_layout.addWidget(self.two_column_widget)
        self.column_selection_layout.addWidget(self.multi_column_widget)
        self.column_selection_layout.addWidget(self.no_column_widget)

        self.column_selection_group.setLayout(self.column_selection_layout)
        controls_layout.addWidget(self.column_selection_group)

        # Buttons
        button_group = QGroupBox()
        button_layout = QVBoxLayout()

        generate_btn = QPushButton("Generate Plot")
        generate_btn.clicked.connect(self.generate_plot)
        button_layout.addWidget(generate_btn)

        save_btn = QPushButton("Save Plot")
        save_btn.clicked.connect(self.save_plot)
        button_layout.addWidget(save_btn)

        clear_btn = QPushButton("Clear Plot")
        clear_btn.clicked.connect(self.clear_plot)
        button_layout.addWidget(clear_btn)

        button_group.setLayout(button_layout)
        controls_layout.addWidget(button_group)

        controls_layout.addStretch()
        controls_widget.setLayout(controls_layout)

        # LEFT SIDE: Plot Display
        plot_display_widget = QWidget()
        plot_display_layout = QVBoxLayout()

        self.plot_canvas = PlotCanvas(self, width=8, height=6)
        plot_display_layout.addWidget(self.plot_canvas)

        plot_display_widget.setLayout(plot_display_layout)

        # Add to main layout
        main_layout.addWidget(controls_widget, 1)
        main_layout.addWidget(plot_display_widget, 3)

        self.plot_panel.setLayout(main_layout)

        # Initialize - show correct column selection
        self.update_column_selection_ui()


    def update_column_selection_ui(self):
        """Show/hide appropriate column selection based on plot type"""
        # Hide all first
        self.single_column_widget.hide()
        self.two_column_widget.hide()
        self.multi_column_widget.hide()
        self.no_column_widget.hide()

        # Show appropriate one based on selected plot
        if self.histogram_radio.isChecked() or self.bar_radio.isChecked():
            # Single column
            self.single_column_widget.show()

        elif self.scatter_radio.isChecked() or self.line_radio.isChecked():
            # Two columns
            self.two_column_widget.show()

        elif self.boxplot_radio.isChecked() or self.violin_radio.isChecked() or self.pairplot_radio.isChecked():
            # Multiple columns with checkboxes
            self.multi_column_widget.show()

        elif self.heatmap_radio.isChecked():
            # No selection needed
            self.no_column_widget.show()

    def populate_plot_columns(self):
        """Populate all plot column selectors with current data columns"""
        if self.data is None:
            return

        columns = self.data.columns.tolist()
        numeric_columns = self.data.select_dtypes(include=['number']).columns.tolist()

        # Single column dropdown
        self.plot_single_combo.clear()
        self.plot_single_combo.addItems(numeric_columns)
        self.plot_single_combo.setEnabled(True)

        # Two column dropdowns
        self.plot_x_combo.clear()
        self.plot_x_combo.addItems(numeric_columns)
        self.plot_x_combo.setEnabled(True)

        self.plot_y_combo.clear()
        self.plot_y_combo.addItems(numeric_columns)
        if len(numeric_columns) > 1:
            self.plot_y_combo.setCurrentIndex(1)  # Set to different column by default
        self.plot_y_combo.setEnabled(True)

        # Multiple column checkboxes
        # Clear existing checkboxes
        for checkbox in self.column_checkboxes.values():
            checkbox.deleteLater()
        self.column_checkboxes.clear()

        # Create new checkboxes for each numeric column
        for col in numeric_columns:
            checkbox = QCheckBox(col)
            self.column_checkboxes[col] = checkbox
            self.column_checkboxes_layout.addWidget(checkbox)

    def select_all_plot_columns(self):
        """Select all column checkboxes"""
        for checkbox in self.column_checkboxes.values():
            checkbox.setChecked(True)

    def clear_all_plot_columns(self):
        """Clear all column checkboxes"""
        for checkbox in self.column_checkboxes.values():
            checkbox.setChecked(False)

    def get_selected_plot_columns(self):
        """Get list of selected columns from checkboxes"""
        selected = []
        for col_name, checkbox in self.column_checkboxes.items():
            if checkbox.isChecked():
                selected.append(col_name)
        return selected

    def generate_plot(self):
        """Generate the selected plot with appropriate columns"""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return

        try:
            # HISTOGRAM (1 column)
            if self.histogram_radio.isChecked():
                col = self.plot_single_combo.currentText()
                if not col:
                    QMessageBox.warning(self, "No Column", "Select a column!")
                    return
                data = self.data[col].dropna()
                if len(data) == 0:
                    QMessageBox.warning(self, "Empty Data", f"{col} has no data!")
                    return
                self.plot_canvas.plot_histogram(data, title=f"Histogram: {col}")

            # BOX PLOT (1+ columns)
            elif self.boxplot_radio.isChecked():
                selected_cols = self.get_selected_plot_columns()
                if len(selected_cols) == 0:
                    QMessageBox.warning(self, "No Columns", "Select at least one column!")
                    return

                # Prepare data for multiple columns
                plot_data = []
                labels = []
                for col in selected_cols:
                    data = self.data[col].dropna()
                    if len(data) > 0:
                        plot_data.append(data)
                        labels.append(col)

                if len(plot_data) == 0:
                    QMessageBox.warning(self, "Empty Data", "Selected columns have no data!")
                    return

                self.plot_canvas.box_plot(plot_data, labels=labels,
                                              title=f"Box Plot: {', '.join(labels)}")

            # SCATTER PLOT (2 columns)
            elif self.scatter_radio.isChecked():
                x_col = self.plot_x_combo.currentText()
                y_col = self.plot_y_combo.currentText()

                if not x_col or not y_col:
                    QMessageBox.warning(self, "Missing Columns", "Select both X and Y columns!")
                    return

                if x_col == y_col:
                    QMessageBox.warning(self, "Same Column", "Select different columns for X and Y!")
                    return

                x_data = self.data[x_col].dropna()
                y_data = self.data[y_col].dropna()

                # Use common indices (intersection)
                common_idx = x_data.index.intersection(y_data.index)
                x_data = self.data.loc[common_idx, x_col]
                y_data = self.data.loc[common_idx, y_col]

                if len(x_data) == 0:
                    QMessageBox.warning(self, "No Data", "No valid data points for scatter plot!")
                    return

                self.plot_canvas.scatter(x_data, y_data,
                                              title=f"Scatter: {x_col} vs {y_col}",
                                              x_label=x_col, y_label=y_col)

            # BAR CHART (1 column - categorical)
            elif self.bar_radio.isChecked():
                col = self.plot_single_combo.currentText()
                if not col:
                    QMessageBox.warning(self, "No Column", "Select a column!")
                    return

                value_counts = self.data[col].value_counts().head(20)  # Limit to top 20
                if len(value_counts) == 0:
                    QMessageBox.warning(self, "No Data", f"{col} has no data!")
                    return

                self.plot_canvas.bar_chart(
                    value_counts.index.astype(str).tolist(),
                    value_counts.values.tolist(),
                    title=f"Bar Chart: {col}"
                )

            # LINE PLOT (2 columns)
            elif self.line_radio.isChecked():
                x_col = self.plot_x_combo.currentText()
                y_col = self.plot_y_combo.currentText()

                if not x_col or not y_col:
                    QMessageBox.warning(self, "Missing Columns", "Select both X and Y columns!")
                    return

                if x_col == y_col:
                    QMessageBox.warning(self, "Same Column", "Select different columns!")
                    return

                x_data = self.data[x_col].dropna()
                y_data = self.data[y_col].dropna()

                common_idx = x_data.index.intersection(y_data.index)
                x_data = self.data.loc[common_idx, x_col]
                y_data = self.data.loc[common_idx, y_col]

                if len(x_data) == 0:
                    QMessageBox.warning(self, "No Data", "No valid data points!")
                    return

                # Sort by x for better line plot
                sorted_idx = x_data.sort_values().index
                x_data = x_data[sorted_idx]
                y_data = y_data[sorted_idx]

                self.plot_canvas.line_plot(x_data, y_data,
                                           title=f"Line Plot: {x_col} vs {y_col}",
                                           x_label=x_col, y_label=y_col)

            # CORRELATION HEATMAP (all numeric columns)
            elif self.heatmap_radio.isChecked():
                numeric_data = self.data.select_dtypes(include=['number'])

                if numeric_data.empty:
                    QMessageBox.warning(self, "No Numeric Data",
                                        "Dataset has no numeric columns!")
                    return

                if len(numeric_data.columns) < 2:
                    QMessageBox.warning(self, "Not Enough Columns",
                                        "Need at least 2 numeric columns for correlation!")
                    return

                self.plot_canvas.correlation_heatmap(numeric_data)

            # VIOLIN PLOT (1+ columns)
            elif self.violin_radio.isChecked():
                selected_cols = self.get_selected_plot_columns()
                if len(selected_cols) == 0:
                    QMessageBox.warning(self, "No Columns", "Select at least one column!")
                    return

                # Use seaborn for violin plot
                try:
                    import seaborn as sns
                    self.plot_canvas.clear_plot()

                    plot_data = []
                    labels = []
                    for col in selected_cols:
                        data = self.data[col].dropna()
                        if len(data) > 0:
                            plot_data.append(data)
                            labels.append(col)

                    if len(plot_data) == 0:
                        QMessageBox.warning(self, "Empty Data", "No valid data!")
                        return

                    # Create violin plot
                    for i, (data, label) in enumerate(zip(plot_data, labels)):
                        parts = self.plot_canvas.ax.violinplot([data], positions=[i],
                                                               showmeans=True, showmedians=True)

                    self.plot_canvas.ax.set_xticks(range(len(labels)))
                    self.plot_canvas.ax.set_xticklabels(labels, rotation=45, ha='right')
                    self.plot_canvas.ax.set_title(f"Violin Plot: {', '.join(labels)}")
                    self.plot_canvas.ax.set_ylabel("Values")
                    self.plot_canvas.ax.grid(True, alpha=0.3)
                    self.plot_canvas.fig.tight_layout()
                    self.plot_canvas.draw()

                except ImportError:
                    QMessageBox.warning(self, "Missing Package",
                                        "Install seaborn: pip install seaborn")
                    return

            # PAIR PLOT (2-5 columns)
            elif self.pairplot_radio.isChecked():
                selected_cols = self.get_selected_plot_columns()

                if len(selected_cols) < 2:
                    QMessageBox.warning(self, "Not Enough Columns",
                                        "Select at least 2 columns!")
                    return

                if len(selected_cols) > 5:
                    QMessageBox.warning(self, "Too Many Columns",
                                        "Select maximum 5 columns for pair plot!")
                    return

                # Create pair plot using scatter plots
                import numpy as np
                n_cols = len(selected_cols)

                self.plot_canvas.fig.clear()

                for i, col1 in enumerate(selected_cols):
                    for j, col2 in enumerate(selected_cols):
                        ax = self.plot_canvas.fig.add_subplot(n_cols, n_cols, i * n_cols + j + 1)

                        if i == j:
                            # Diagonal: histogram
                            data = self.data[col1].dropna()
                            ax.hist(data, bins=15, edgecolor='black', alpha=0.7)
                            ax.set_ylabel('Frequency' if j == 0 else '')
                        else:
                            # Off-diagonal: scatter
                            x_data = self.data[col2].dropna()
                            y_data = self.data[col1].dropna()
                            common_idx = x_data.index.intersection(y_data.index)
                            ax.scatter(self.data.loc[common_idx, col2],
                                       self.data.loc[common_idx, col1], alpha=0.5, s=10)

                        # Labels
                        if i == n_cols - 1:
                            ax.set_xlabel(col2, fontsize=8)
                        else:
                            ax.set_xticklabels([])

                        if j == 0:
                            ax.set_ylabel(col1, fontsize=8)
                        else:
                            ax.set_yticklabels([])

                        ax.tick_params(labelsize=6)

                self.plot_canvas.fig.suptitle(f"Pair Plot: {', '.join(selected_cols)}")
                self.plot_canvas.fig.tight_layout()
                self.plot_canvas.draw()

            self.statusbar.showMessage("Plot generated successfully!")

            temp_plot_path = f"temp_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.plot_canvas.fig.savefig(temp_plot_path, dpi=150, bbox_inches='tight')
            self.generated_plots.append(temp_plot_path)


        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Plot Error",
                                 f"Failed to generate plot:\n{str(e)}")

    def save_plot(self):
        """Save the current plot to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf);;All Files (*)"
        )

        if file_path:
            try:
                self.plot_canvas.save_plot(file_path)
                self.statusbar.showMessage(f"Plot saved to {file_path}")
                QMessageBox.information(self, "Success", f"Plot saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save plot:\n{str(e)}")

    def clear_plot(self):
        """Clear the current plot"""
        self.plot_canvas.clear_plot()
        self.statusbar.showMessage("Plot cleared")

    def create_export_panel(self):
        self.export_panel = QGroupBox("Export & Report Generation")
        layout = QVBoxLayout()

        options_group = QGroupBox("Report Contents")
        options_layout = QVBoxLayout()

        self.include_data_info = QCheckBox("Include dataset information")
        self.include_data_info.setChecked(True)
        options_layout.addWidget(self.include_data_info)

        self.include_statistics = QCheckBox("Include statistical analysis results")
        self.include_statistics.setChecked(True)
        options_layout.addWidget(self.include_statistics)

        self.include_tests = QCheckBox("Include Statistical Test Results")
        self.include_tests.setChecked(True)
        options_layout.addWidget(self.include_tests)

        self.include_plots = QCheckBox("Include Generated Plots")
        self.include_plots.setChecked(True)
        options_layout.addWidget(self.include_plots)

        self.include_cleaning = QCheckBox("Include Data Cleaning Summary")
        self.include_cleaning.setChecked(True)
        options_layout.addWidget(self.include_cleaning)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        generate_btn = QPushButton("Generate PDF Report")
        generate_btn.setStyleSheet("""
               QPushButton {
                   background-color: #27ae60;
                   color: white;
                   padding: 15px;
                   font-size: 14px;
                   font-weight: bold;
                   border-radius: 5px;
               }
               QPushButton:hover {
                   background-color: #229954;
               }
           """)
        generate_btn.clicked.connect(self.generate_pdf_report)
        layout.addWidget(generate_btn)

        quick_group = QGroupBox("Quick Exports")
        quick_layout = QVBoxLayout()

        export_results_btn = QPushButton("Export Results to CSV")
        export_results_btn.clicked.connect(self.export_results_csv)
        quick_layout.addWidget(export_results_btn)

        export_data_btn = QPushButton("Export Current Data to CSV")
        export_data_btn.clicked.connect(self.export_data_csv)
        quick_layout.addWidget(export_data_btn)

        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)

        self.export_status = QLabel("")
        layout.addWidget(self.export_status)

        layout.addStretch()
        self.export_panel.setLayout(layout)

    def generate_pdf_report(self):
        """Generate comprehensive PDF report"""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return

        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"Report_{self.fileName}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        try:

            self.export_status.setText("Generating PDF report...")
            self.export_status.setStyleSheet("color: blue;")

            pdf = PDFGenerator(file_path)

            # Title
            pdf.add_title("Statistical Analysis Report")
            pdf.add_paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            pdf.add_paragraph(f"<b>Dataset:</b> {self.fileName}")
            pdf.add_line()
            pdf.add_spacer()

            # 1. Dataset Information
            if self.include_data_info.isChecked():
                pdf.add_heading("1. Dataset Information")

                rows, cols = self.data.shape
                missing = self.data.isnull().sum().sum()
                duplicates = self.data.duplicated().sum()

                data_info = [
                    ["Property", "Value"],
                    ["Total Rows", str(rows)],
                    ["Total Columns", str(cols)],
                    ["Missing Values", str(missing)],
                    ["Duplicate Rows", str(duplicates)],
                    ["Memory Usage", f"{self.data.memory_usage(deep=True).sum() / 1024:.2f} KB"]
                ]
                pdf.add_table(data_info, col_widths=[3 * inch, 3 * inch])

                # Column types
                pdf.add_paragraph("<b>Column Information:</b>")
                col_data = [["Column Name", "Data Type", "Non-Null Count"]]
                for col in self.data.columns:
                    col_data.append([
                        col,
                        str(self.data[col].dtype),
                        str(self.data[col].count())
                    ])
                pdf.add_table(col_data, col_widths=[2 * inch, 2 * inch, 2 * inch])
                pdf.add_page_break()

            # 2. Statistical Analysis
            if self.include_statistics.isChecked() and self.last_statistics_results:
                pdf.add_heading("2. Statistical Analysis Results")

                stats_data = [["Statistic", "Column", "Value"]]
                results = self.last_statistics_results['results']

                for col, calcs in results.items():
                    for calc_name, value in calcs.items():
                        stats_data.append([
                            calc_name,
                            col,
                            f"{value:.4f}" if value is not None else "N/A"
                        ])

                pdf.add_table(stats_data, col_widths=[2 * inch, 2 * inch, 2 * inch])
                pdf.add_spacer()

            # 3. Statistical Tests
            if self.include_tests.isChecked() and self.last_test_results:
                pdf.add_heading("3. Statistical Test Results")

                test = self.last_test_results
                pdf.add_paragraph(f"<b>Test Type:</b> {test['type']}")
                pdf.add_paragraph(f"<b>Performed:</b> {test['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                pdf.add_spacer(0.1)

                test_data = [["Parameter", "Value"]]
                for key, value in test['results'].items():
                    if isinstance(value, float):
                        test_data.append([str(key).replace('_', ' ').title(), f"{value:.4f}"])
                    else:
                        test_data.append([str(key).replace('_', ' ').title(), str(value)])

                pdf.add_table(test_data, col_widths=[3 * inch, 3 * inch])
                pdf.add_page_break()

            # 4. Plots
            if self.include_plots.isChecked() and len(self.generated_plots) > 0:
                pdf.add_heading("4. Data Visualizations")

                for i, plot_path in enumerate(self.generated_plots[-5:], 1):  # Last 5 plots
                    if os.path.exists(plot_path):
                        pdf.add_paragraph(f"<b>Plot {i}:</b>")
                        pdf.add_image(plot_path, width=6 * inch, height=4 * inch)
                        if i < len(self.generated_plots[-5:]):
                            pdf.add_page_break()

            # 5. Data Cleaning Summary
            if self.include_cleaning.isChecked() and self.last_cleaning_summary:
                pdf.add_page_break()
                pdf.add_heading("5. Data Cleaning Summary")

                clean_data = [["Operation", "Details"]]
                clean_data.append(["Action", self.last_cleaning_summary['action']])
                clean_data.append(["Rows Before", str(self.last_cleaning_summary['before_rows'])])
                clean_data.append(["Rows After", str(self.last_cleaning_summary['after_rows'])])
                clean_data.append(["Rows Removed",
                                   str(self.last_cleaning_summary['before_rows'] -
                                       self.last_cleaning_summary['after_rows'])])

                pdf.add_table(clean_data, col_widths=[2 * inch, 4 * inch])

            # Footer
            pdf.add_spacer()
            pdf.add_line()
            pdf.add_paragraph(
                f"<i>Report generated by Statistical Calculator v1.0 on "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
            )

            # Build PDF
            pdf.build()

            self.export_status.setText(f"✅ Report saved: {os.path.basename(file_path)}")
            self.export_status.setStyleSheet("color: green;")

            QMessageBox.information(
                self,
                "Success",
                f"PDF report generated successfully!\n\n{file_path}"
            )

            # Open the PDF
            reply = QMessageBox.question(
                self,
                "Open Report?",
                "Would you like to open the PDF report now?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                import subprocess
                import platform
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', file_path])
                else:  # Linux
                    subprocess.call(['xdg-open', file_path])

        except Exception as e:
            self.export_status.setText(f"❌ Error: {str(e)}")
            self.export_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")

    def export_results_csv(self):
        """Export analysis results to CSV"""
        if not self.last_statistics_results:
            QMessageBox.warning(self, "No Results", "No analysis results to export!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            f"Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Convert results to DataFrame
                results_list = []
                for col, calcs in self.last_statistics_results['results'].items():
                    for calc_name, value in calcs.items():
                        results_list.append({
                            'Column': col,
                            'Statistic': calc_name,
                            'Value': value
                        })

                df_results = pd.DataFrame(results_list)
                df_results.to_csv(file_path, index=False)

                QMessageBox.information(self, "Success", "Results exported successfully!")
                self.statusbar.showMessage(f"Exported: {os.path.basename(file_path)}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")

    def export_data_csv(self):
        """Export current dataset to CSV"""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "No data to export!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            f"{os.path.splitext(self.fileName)[0]}_exported.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )

        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.data.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self.data.to_excel(file_path, index=False)

                QMessageBox.information(self, "Success", "Data exported successfully!")
                self.statusbar.showMessage(f"Exported: {os.path.basename(file_path)}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatCalculator()
    window.show()
    sys.exit(app.exec())


