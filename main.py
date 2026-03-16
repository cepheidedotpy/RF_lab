"""
TEMIS MEMS LAB - SUMMIT 11K Machine Interface
Entry point for the application.
"""
import argparse
import ttkbootstrap as ttk
from src.gui.main_window import Window
from src.gui.gui_utils import default_style


def main():
    parser = argparse.ArgumentParser(description="SUMMIT 11K Machine Interface")
    parser.add_argument('--offline', action='store_true',
                        help='Run in offline mode without connecting to hardware.')
    args = parser.parse_args()

    root = ttk.Window(themename=default_style)
    app = Window(root, offline_mode=args.offline)
    root.mainloop()


if __name__ == '__main__':
    main()
