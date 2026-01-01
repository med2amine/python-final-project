from PySide6.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QFileDialog,QWidget,QMessageBox,QTableWidget,QPushButton,QTableWidgetItem,QTextEdit,QCheckBox,QLabel,QHBoxLayout,QGroupBox
import PySide6.QtCore
from PySide6.QtGui import QAction
from database import DatabaseManager
import sys
import pandas as pd
import os

class StatCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        container = QWidget()
        self.table = QTableWidget()
        self.layout = QVBoxLayout(container)
        self.layout.addWidget(self.table)
        self.setCentralWidget(container)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setVisible(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.create_calculation_panel()
        self.CalculateButton()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("results will appear here")
        self.layout.addWidget(self.results_text)

        self.data = None
        self.currentDatasedtId = None
        self.clearButton()
        self.setWindowTitle("Statistical Calculator")
        self.setGeometry(100,100,900,600)
        self.create_menubar()
        self.create_statusbar()

        self.dataManager = DatabaseManager()



    def create_menubar(self):
        Menubar = self.menuBar()

        fileMenu = Menubar.addMenu("&File")

        open_action = QAction("&Open",self)
        open_action.setShortcut("Ctrl+O")

        open_action.triggered.connect(self.Openaction)
        fileMenu.addAction(open_action)

        exit_action = QAction("&Exit",self)
        exit_action.setShortcut("Ctrl+Q")

        exit_action.triggered.connect(self.close)
        fileMenu.addAction(exit_action)

        editMenu = Menubar.addMenu("&Edit")

        helpMenu = Menubar.addMenu("&Help")

        about = QAction("&About",self)
        about.triggered.connect(self.show_about)
        helpMenu.addAction(about)

    def create_statusbar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("ready")

    def Openaction(self):
        file_path,_ = QFileDialog.getOpenFileName(
            self,
            "open csv file",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files(*)"
        )

        if not file_path:
            return

        self.statusbar.showMessage("Loading file...")
        try :
            if file_path.lower().endswith(".csv"):
                self.data = pd.read_csv(file_path)
            elif file_path.lower().endswith((".xlsx", ".xls")):
                self.data = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file type")


            row,cols = self.data.shape
            fileName = os.path.basename(file_path)

            self.display_data_in_table(self.data)


            self.statusbar.showMessage(
                f"Loaded : {file_path}| Rows : {row},Columns : {cols}"
            )

            self.currentDatasedtId = self.dataManager.register_dataset(
                fileName,
                file_path,
                self.data
            )

            if self.currentDatasedtId:
                print(f"✅ Dataset saved to database with ID: {self.currentDatasedtId}")

        except Exception as e:
            self.statusbar.showMessage(f"Error : {str(e)}")
            return



    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About",
            "Statistical Calculator v1.0\n\n"
            "A tool for statistical analysis and data visualization.\n\n"
            "Created for Python School Project 2024"
        )

    def display_data_in_table(self,dataframe,max_rows=100):
        try:
            rows_to_show = min(len(dataframe),max_rows)

            if len(dataframe)>max_rows:
                QMessageBox.information(
                    self,
                    "large dataset",
                    f'dataset had {len(dataframe)} rows. \n'
                    f"Displaying first {max_rows} rows only.\n\n"
                    f"All data is loaded and will be used in calculations."

                )
            self.table.setRowCount(rows_to_show)
            self.table.setColumnCount(len(dataframe.columns))

            self.table.setHorizontalHeaderLabels(dataframe.columns.tolist())

            for row_indx  in range(rows_to_show):
                for col_indx,value in enumerate(dataframe.iloc[row_indx]):
                    self.table.setItem(
                        row_indx,
                        col_indx,
                        QTableWidgetItem(str(value))
                    )

            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(
                self,
                "display Error",
                f'failed to display data : {str(e)}'
            )
    def clearButton(self):
        clButton = QPushButton("clear data")
        clButton.clicked.connect(self.clear_data)
        self.layout.addWidget(clButton)

    def clear_data(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        self.data = None
        self.currentDatasedtId = None
        self.statusbar.showMessage('data cleared')

    def create_calculation_panel(self):
        self.select_calculations = QGroupBox('select calculations')
        calcLayout = QVBoxLayout()

        self.calc_checkboxes = {}
        calculations = [
            'Mean',
            'Median',
            'Mode',
            'Strandard Deviation',
            'Variance',
            'Min',
            'Max',
            'Count'
        ]

        for calc in calculations:
            checkbox = QCheckBox(calc)
            self.calc_checkboxes[calc] = checkbox
            calcLayout.addWidget(checkbox)

        self.select_calculations.setLayout(calcLayout)

        self.layout.addWidget(self.select_calculations)

    def CalculateButton(self):
        self.Cbutton = QPushButton('Calculate')
        self.Cbutton.clicked.connect(self.run_calculations)
        self.Cbutton.setEnabled(False)
        self.layout.addWidget(self.Cbutton)

    def run_calculations(self):
        print('doing calculations')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatCalculator()
    window.show()
    sys.exit(app.exec())



