import sys
from PySide6.QtWidgets import QApplication
from UI.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # load styles
    with open("UI/styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    win = MainWindow()
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
