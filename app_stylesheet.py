MODERN_STYLESHEET = """
/* ===== GLOBAL STYLES ===== */
QMainWindow {
    background-color: #f5f6fa;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

/* ===== MENU BAR ===== */
QMenuBar {
    background-color: #2c3e50;
    color: white;
    padding: 5px;
    font-weight: bold;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #34495e;
}

QMenuBar::item:pressed {
    background-color: #1abc9c;
}

QMenu {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    padding: 5px;
}

QMenu::item {
    padding: 8px 30px 8px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

/* ===== STATUS BAR ===== */
QStatusBar {
    background-color: #34495e;
    color: white;
    font-size: 9pt;
    padding: 5px;
}

/* ===== TAB WIDGET ===== */
QTabWidget::pane {
    border: 1px solid #bdc3c7;
    border-radius: 8px;
    background-color: white;
    padding: 10px;
}

QTabBar::tab {
    background-color: #ecf0f1;
    color: #2c3e50;
    border: 1px solid #bdc3c7;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: white;
    color: #3498db;
    border-bottom: 3px solid #3498db;
}

QTabBar::tab:hover {
    background-color: #d5dbdb;
}

/* ===== GROUP BOX ===== */
QGroupBox {
    background-color: #ffffff;
    border: 2px solid #3498db;
    border-radius: 8px;
    padding: 20px 15px 15px 15px;
    margin-top: 12px;
    padding: 15px;
    font-weight: bold;
    font-size: 11pt;
    color: #2c3e50;
}

QCheckBox, QRadioButton {
    spacing: 10px;  
    padding: 5px;   
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 5px 10px;
    background-color: #3498db;
    color: white;
    border-radius: 4px;
}

/* ===== PUSH BUTTONS ===== */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 10pt;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #2980b9;
    transform: translateY(-2px);
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

/* Different button styles */
QPushButton#successButton {
    background-color: #2ecc71;
}

QPushButton#successButton:hover {
    background-color: #27ae60;
}

QPushButton#dangerButton {
    background-color: #e74c3c;
}

QPushButton#dangerButton:hover {
    background-color: #c0392b;
}

QPushButton#warningButton {
    background-color: #f39c12;
}

QPushButton#warningButton:hover {
    background-color: #d68910;
}

/* ===== TABLE WIDGET ===== */
QTableWidget {
    background-color: white;
    alternate-background-color: #f8f9fa;
    gridline-color: #dfe6e9;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    selection-background-color: #3498db;
    selection-color: white;
}

QTableWidget::item {
    padding: 5px;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
    font-size: 10pt;
}

QHeaderView::section:hover {
    background-color: #2c3e50;
}

/* ===== TEXT EDIT / TEXT BROWSER ===== */
QTextEdit, QTextBrowser {
    background-color: #ffffff;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    color: #2c3e50;
}

QTextEdit:focus {
    border: 2px solid #3498db;
}

/* ===== CHECKBOXES ===== */
QCheckBox {
    spacing: 8px;
    color: #2c3e50;
    font-size: 10pt;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #bdc3c7;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
    image: url(checkmark.png);  /* You can use unicode ✓ or an image */
}

QCheckBox::indicator:hover {
    border-color: #3498db;
}

/* ===== RADIO BUTTONS ===== */
QRadioButton {
    spacing: 8px;
    color: #2c3e50;
    font-size: 10pt;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #bdc3c7;
    background-color: white;
}

QRadioButton::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}

QRadioButton::indicator:hover {
    border-color: #3498db;
}

/* ===== COMBO BOX ===== */
QComboBox {
    background-color: white;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 30px;
    color: #2c3e50;
}

QComboBox:hover {
    border-color: #3498db;
}

QComboBox:focus {
    border-color: #3498db;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: white;
    border: 2px solid #3498db;
    selection-background-color: #3498db;
    selection-color: white;
    border-radius: 4px;
}

/* ===== SPIN BOX ===== */
QDoubleSpinBox, QSpinBox {
    background-color: white;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 8px;
    min-height: 30px;
}

QDoubleSpinBox:hover, QSpinBox:hover {
    border-color: #3498db;
}

QDoubleSpinBox:focus, QSpinBox:focus {
    border-color: #3498db;
}

/* ===== LABELS ===== */
QLabel {
    color: #2c3e50;
    font-size: 10pt;
}

/* ===== SCROLL BAR ===== */
QScrollBar:vertical {
    background-color: #ecf0f1;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #95a5a6;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7f8c8d;
}

QScrollBar:horizontal {
    background-color: #ecf0f1;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #95a5a6;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #7f8c8d;
}

/* ===== SCROLL AREA ===== */
QScrollArea {
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    background-color: white;
}

/* ===== LIST WIDGET ===== */
QListWidget {
    background-color: white;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 5px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QListWidget::item:hover {
    background-color: #ecf0f1;
}

/* ===== DIALOG BUTTONS ===== */
QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* ===== TOOLTIPS ===== */
QToolTip {
    background-color: #2c3e50;
    color: white;
    border: 1px solid #34495e;
    border-radius: 4px;
    padding: 5px;
    font-size: 9pt;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    text-align: center;
    background-color: #ecf0f1;
    color: #2c3e50;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 4px;
}

QComboBox {
    padding: 10px 12px;  /* ✨ More padding */
    min-height: 35px;    /* ✨ Minimum height */
}

QPushButton {
    padding: 12px 20px;  /* ✨ More padding */
    min-height: 38px;    /* ✨ Minimum height */
    margin: 3px;         /* ✨ Space between buttons */
}

QLabel {
    padding: 3px 0px;    /* ✨ Vertical padding */
}

QDoubleSpinBox, QSpinBox {
    padding: 10px 8px;   /* ✨ More padding */
    min-height: 35px;    /* ✨ Minimum height */
}
"""