from PyQt6.QtWidgets import QApplication
from gui.gui import main
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main()
    window.show()
    sys.exit(app.exec())