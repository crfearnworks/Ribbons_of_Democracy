import sys
from PyQt6.QtWidgets import QApplication
from .components.ribbon_designer import RibbonDesigner

def main():
    app = QApplication(sys.argv)
    window = RibbonDesigner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()