
# Modern Dark High-Contrast Theme
THEME_COLORS = {
    "primary": "#007BFF",       # Bright Blue
    "secondary": "#6C757D",     # Grey
    "success": "#28A745",       # Green
    "danger": "#DC3545",        # Red
    "warning": "#FFC107",       # Yellow
    "info": "#17A2B8",          # Cyan
    "dark": "#343A40",          # Dark Grey
    "light": "#F8F9FA",         # Near White
    "background": "#121212",    # Very Dark Grey (Almost Black)
    "surface": "#1E1E1E",       # Dark Grey Surface
    "text": "#FFFFFF",          # White Text
    "text_muted": "#B0B0B0"     # Light Grey Text
}

STYLESHEET = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 14pt;
    color: #FFFFFF;
}

/* Buttons */
QPushButton {
    background-color: #007BFF;
    color: white;
    border: none;
    padding: 15px;
    border-radius: 8px;
    font-weight: bold;
    min-height: 50px; /* Minimum height per requirements */
}

QPushButton:hover {
    background-color: #0056b3;
}

QPushButton:pressed {
    background-color: #004085;
}

QPushButton#dangerBtn {
    background-color: #DC3545;
}
QPushButton#dangerBtn:hover {
    background-color: #bd2130;
}

QPushButton#successBtn {
    background-color: #28A745;
}
QPushButton#successBtn:hover {
    background-color: #218838;
}

QPushButton#warningBtn {
    background-color: #FFC107;
    color: #212529;
}

/* Input Fields */
QLineEdit {
    background-color: #1E1E1E;
    border: 2px solid #343A40;
    border-radius: 5px;
    padding: 10px;
    color: #FFFFFF;
    font-size: 16pt;
}

QLineEdit:focus {
    border: 2px solid #007BFF;
}

/* Lists and Tables */
QListWidget, QTableWidget {
    background-color: #1E1E1E;
    border: 1px solid #343A40;
    gridline-color: #343A40;
}

QHeaderView::section {
    background-color: #343A40;
    padding: 5px;
    border: 1px solid #1E1E1E;
    color: #FFFFFF;
}

/* Labels */
QLabel {
    color: #FFFFFF;
}

QLabel#header {
    font-size: 24pt;
    font-weight: bold;
    margin-bottom: 20px;
}

QLabel#error {
    color: #DC3545;
}

/* Cards/Containers */
QFrame#card {
    background-color: #1E1E1E;
    border-radius: 10px;
    padding: 20px;
}
"""
