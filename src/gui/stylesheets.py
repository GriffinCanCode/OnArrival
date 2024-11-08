MAIN_STYLE = """
QMainWindow {
    background-color: #F8F9FA;
}
QLabel {
    color: #2C3E50;
    font-size: 14px;
}
QPushButton {
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
    min-width: 120px;
    opacity: 0.9;
}
QPushButton:hover {
    opacity: 1;
    margin-top: -1px;
    margin-bottom: 1px;
}
QPushButton:pressed {
    opacity: 0.85;
    margin-top: 1px;
    margin-bottom: -1px;
}
QLineEdit {
    padding: 12px 16px;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    background-color: white;
    font-size: 14px;
    min-width: 200px;
    color: #2C3E50;
}
QLineEdit:focus {
    border-color: #3498DB;
    background-color: #F8F9FA;
}
QLineEdit:hover {
    border-color: #BDC3C7;
}
QTabWidget::pane {
    border: 1px solid #E0E0E0;
    background-color: white;
    border-radius: 12px;
    padding: 20px;
}
QTabBar::tab {
    background-color: #E0E0E0;
    padding: 12px 24px;
}
QComboBox {
    padding: 12px 16px;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    background-color: white;
    font-size: 14px;
    min-width: 200px;
    color: #2C3E50;
}
QComboBox:focus {
    border-color: #3498DB;
    background-color: #F8F9FA;
}
QComboBox:hover {
    border-color: #BDC3C7;
}
"""

DELETE_BUTTON_STYLE = """
QPushButton {
    background-color: #E74C3C;
    max-width: 100px;
    min-width: 80px;
    padding: 8px 16px;
    border-bottom: 2px solid #C0392B;
}
QPushButton:hover {
    background-color: #C0392B;
    margin-top: -1px;
    margin-bottom: 1px;
}
QPushButton:pressed {
    background-color: #A93226;
    margin-top: 1px;
    margin-bottom: -1px;
    border-bottom: 1px solid #C0392B;
}
""" 