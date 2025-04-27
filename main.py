import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)

    # Load QSS Style
    with open("styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
