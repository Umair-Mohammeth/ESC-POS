import customtkinter as ctk
from auth import verify_pin
from tkinter import messagebox

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        # Center content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        inner_frame = ctk.CTkFrame(self)
        inner_frame.grid(row=1, column=0, padx=20, pady=20)

        self.title = ctk.CTkLabel(inner_frame, text="POS System Login", font=("Segoe UI", 24, "bold"))
        self.title.pack(pady=20)

        self.pin_input = ctk.CTkEntry(inner_frame, placeholder_text="Enter PIN", show="*", width=250, height=45, font=("Segoe UI", 18), justify="center")
        self.pin_input.pack(pady=10)
        self.pin_input.bind("<Return>", lambda e: self.verify_login())

        # Keypad
        keypad_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        keypad_frame.pack(pady=10)

        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 1), ('Clear', 3, 0), ('Enter', 3, 2)
        ]

        for text, row, col in buttons:
            btn = ctk.CTkButton(keypad_frame, text=text, width=70, height=70, font=("Segoe UI", 16, "bold"),
                               command=lambda ch=text: self.on_key_click(ch))
            if text == "Enter":
                btn.configure(fg_color="#28A745", hover_color="#218838")
            elif text == "Clear":
                btn.configure(fg_color="#DC3545", hover_color="#bd2130")
            
            btn.grid(row=row, column=col, padx=5, pady=5)

    def on_key_click(self, char):
        if char == "Enter":
            self.verify_login()
        elif char == "Clear":
            self.pin_input.delete(0, 'end')
        else:
            self.pin_input.insert('end', char)

    def verify_login(self):
        pin = self.pin_input.get()
        user = verify_pin(pin)
        if user:
            self.pin_input.delete(0, 'end')
            self.on_login_success(user)
        else:
            messagebox.showwarning("Login Attempt", "Invalid PIN")
            self.pin_input.delete(0, 'end')
