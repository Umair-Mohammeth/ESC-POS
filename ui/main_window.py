import customtkinter as ctk
from ui.login_view import LoginView
from ui.cashier_view import CashierView
from ui.stocker_view import StockerView
from ui.manager_view import ManagerView
from ui.admin_view import AdminView
from styles import THEME_COLORS

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Modern POS System")
        self.geometry("1280x820")
        
        # Set modern theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure window background with gradient color
        self.configure(fg_color=THEME_COLORS["background"])

        # Main container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
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
        
        # Clear previous app frame if exists
        if "app" in self.frames:
            self.frames["app"].destroy()
        
        # Create appropriate view based on role
        if role == 'cashier':
            self.frames["app"] = CashierView(self.container, self.current_user, self.logout)
        elif role == 'stocker':
            self.frames["app"] = StockerView(self.container, self.current_user, self.logout)
        elif role == 'manager':
            self.frames["app"] = ManagerView(self.container, self.current_user, self.logout)
        elif role == 'admin':
            self.frames["app"] = AdminView(self.container, self.current_user, self.logout)
        else:
            # Fallback for unknown roles
            self.frames["app"] = CashierView(self.container, self.current_user, self.logout)
            
        self.frames["app"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("app")

    def show_frame(self, page_name):
        """Bring the specified frame to the front"""
        frame = self.frames[page_name]
        frame.tkraise()

    def logout(self):
        """Handle user logout"""
        if self.current_user:
            # Log logout action
            try:
                from database import log_user_action
                log_user_action(self.current_user['id'], "LOGOUT")
            except:
                pass
                
        if "app" in self.frames:
            self.frames["app"].destroy()
        
        self.current_user = None
        self.show_login()

    def simulate_role(self, role):
        """Simulate a specific role view"""
        # Close current app frame
        if "app" in self.frames:
            self.frames["app"].destroy()
            
        # Create simulated user context (keep original self.current_user as Admin)
        simulated_user = self.current_user.copy()
        simulated_user['role'] = role
        simulated_user['name'] = f"{self.current_user['name']} (Simulated {role.title()})"
        
        # Launch appropriate view but return to Admin on logout/exit simulation
        if role == 'cashier':
            self.frames["app"] = CashierView(self.container, simulated_user, self.restore_admin_view)
        elif role == 'stocker':
            self.frames["app"] = StockerView(self.container, simulated_user, self.restore_admin_view)
        elif role == 'manager':
            self.frames["app"] = ManagerView(self.container, simulated_user, self.restore_admin_view)
        
        self.frames["app"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("app")

    def restore_admin_view(self):
        """Restore the admin view after simulation"""
        if "app" in self.frames:
            self.frames["app"].destroy()
            
        # Re-create AdminView with the original admin user
        self.frames["app"] = AdminView(self.container, self.current_user, self.logout)
        self.frames["app"].grid(row=0, column=0, sticky="nsew")
        self.show_frame("app")
