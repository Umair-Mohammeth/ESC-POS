import sys
import customtkinter as ctk
from database import init_db
from ui.main_window import MainWindow

def main():
    # Initialize Database
    print("Initializing Database...")
    init_db()
    
    # Start Application
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
