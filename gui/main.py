import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QFontDatabase

# Add project root to sys.path if not running from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("2MHDBMRIPS Digital Twin")
    
    # Setup fonts
    fonts_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    if os.path.exists(fonts_dir):
        for font in ["JetBrainsMono-Regular.ttf", "Inter-Regular.ttf"]:
            f_path = os.path.join(fonts_dir, font)
            if os.path.exists(f_path):
                QFontDatabase.addApplicationFont(f_path)

    # Setup icon
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    # Load QSS
    qss_path = os.path.join(os.path.dirname(__file__), "assets", "qss", "dark_industrial.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
            
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
