import customtkinter as ctk
from ui.login_view import LoginView
from ui.cashier_view import CashierView
from ui.stocker_view import StockerView
from ui.manager_view import ManagerView
from ui.admin_view import AdminView

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Professional POS System")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_user = None

        # Start with Login
        self.show_login()

    def show_login(self):
        if "login" in self.frames:
            self.frames["login"].destroy()
        
        self.frames["login"] = LoginView(self.container, self.on_login_success)
        self.frames["login"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("login")

    def on_login_success(self, user):
        self.current_user = user
        role = user['role']
        
        if role == 'cashier':
            self.frames["app"] = CashierView(self.container, self.current_user, self.logout)
        elif role == 'stocker':
            self.frames["app"] = StockerView(self.container, self.current_user, self.logout)
        elif role == 'manager':
            self.frames["app"] = ManagerView(self.container, self.current_user, self.logout)
        elif role == 'admin':
            self.frames["app"] = AdminView(self.container, self.current_user, self.logout)
            
        self.frames["app"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("app")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def logout(self):
        if "app" in self.frames:
            self.frames["app"].destroy()
        self.show_login()
