import sys
import os
from PySide6.QtWidgets import QApplication

def main():
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    try:
        app = QApplication(sys.argv)
        styles_path = "UI/styles.qss"
        if os.path.exists(styles_path):
            with open(styles_path, "r") as f:
                app.setStyleSheet(f.read())
        else:
            print(f"\nStyle file not found: {styles_path}")
            print("Continuing without custom styles...")
        try:
            from UI.main_window import MainWindow
            win = MainWindow()
            win.show()
        except ImportError as e:
            print(f"\nError importing MainWindow: {e}")
            print("Make sure the UI module exists and is properly configured.")
            return
        except Exception as e:
            print(f"Error creating main window: {e}")
            return
        sys.exit(app.exec())
    except Exception as e:
        print(f"\n Error starting application: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have a display server running")
        print("2. If using WSL, install and configure an X server")
        print("3. Try running: export QT_QPA_PLATFORM=xcb")
        print("4. Check if all dependencies are installed: pip install PySide6")

if __name__ == "__main__":
    main()
