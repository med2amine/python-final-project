from PySide6.QtWidgets import QApplication,QMainWindow,QMenuBar,QVBoxLayout,QStatusBar,QFileDialog,QWidget,QMessageBox
import PySide6.QtCore
from PySide6.QtGui import QAction
from database import DatabaseManager
import sys
import pandas as pd
import os

class StatCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        mainWindow = QWidget()
        self.setCentralWidget(mainWindow)

        self.setWindowTitle("Statistical Calculator")
        self.setGeometry(100,100,900,600)
        self.create_menubar()
        self.data = None
        self.currentDatasedtId = None
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
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
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

            self.statusbar.showMessage(
                f"Loaded : {file_path}| Rows : {row},Columns : {cols}"
            )

            self.current_dataset_id = self.dataManager.register_dataset(
                fileName,
                file_path,
                self.data
            )

            if self.current_dataset_id:
                print(f"✅ Dataset saved to database with ID: {self.current_dataset_id}")

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












if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatCalculator()
    window.show()
    sys.exit(app.exec())



