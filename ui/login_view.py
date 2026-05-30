import customtkinter as ctk
from auth import verify_pin
from tkinter import messagebox
from database import log_user_action
from styles import (
    THEME_COLORS, RADIUS, SPACING, FONTS, ICONS,
    create_glass_frame, create_gradient_label
)

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="transparent")
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        # Create gradient background effect
        self.configure(fg_color=[THEME_COLORS["background"], THEME_COLORS["background_light"]])
        
        # Center content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Glassmorphic login card
        login_card = create_glass_frame(
            self,
            fg_color=THEME_COLORS["glass_bg"],
            corner_radius=RADIUS["xl"]
        )
        login_card.grid(row=1, column=0, padx=40, pady=40, ipadx=30, ipady=30)

        # Modern title with gradient effect
        title_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        title_frame.pack(pady=(20, 10))
        
        icon_label = ctk.CTkLabel(
            title_frame,
            text="🔐",
            font=(FONTS["primary"], 48)
        )
        icon_label.pack()
        
        self.title = create_gradient_label(
            title_frame,
            text="POS System",
            font=(FONTS["primary"], 32, "bold"),
            text_color=THEME_COLORS["text"]
        )
        self.title.pack(pady=(10, 0))
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Enter your PIN to continue",
            font=(FONTS["primary"], 14),
            text_color=THEME_COLORS["text_secondary"]
        )
        subtitle.pack()

        # Modern PIN input with enhanced styling
        pin_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        pin_frame.pack(pady=20)
        
        self.pin_input = ctk.CTkEntry(
            pin_frame,
            placeholder_text="• • • •",
            show="•",
            width=300,
            height=60,
            font=(FONTS["primary"], 24),
            justify="center",
            fg_color=THEME_COLORS["surface"],
            border_color=THEME_COLORS["gradient_mid"],
            border_width=2,
            corner_radius=RADIUS["md"]
        )
        self.pin_input.pack()
        self.pin_input.bind("<Return>", lambda e: self.verify_login())
        self.pin_input.bind("<FocusIn>", self.on_focus_in)
        self.pin_input.bind("<FocusOut>", self.on_focus_out)

        # Modern keypad with enhanced buttons
        keypad_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        keypad_frame.pack(pady=20)

        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('Clear', 3, 0), ('0', 3, 1), ('Enter', 3, 2)
        ]

        for text, row, col in buttons:
            if text == "Enter":
                btn = ctk.CTkButton(
                    keypad_frame,
                    text=f"✓ {text}",
                    width=90,
                    height=75,
                    font=(FONTS["primary"], 16, "bold"),
                    fg_color=THEME_COLORS["success"],
                    hover_color=THEME_COLORS["success_hover"],
                    corner_radius=RADIUS["md"],
                    command=lambda ch=text: self.on_key_click(ch)
                )
            elif text == "Clear":
                btn = ctk.CTkButton(
                    keypad_frame,
                    text=f"✕ {text}",
                    width=90,
                    height=75,
                    font=(FONTS["primary"], 16, "bold"),
                    fg_color=THEME_COLORS["danger"],
                    hover_color=THEME_COLORS["danger_hover"],
                    corner_radius=RADIUS["md"],
                    command=lambda ch=text: self.on_key_click(ch)
                )
            else:
                btn = ctk.CTkButton(
                    keypad_frame,
                    text=text,
                    width=90,
                    height=75,
                    font=(FONTS["primary"], 20, "bold"),
                    fg_color=THEME_COLORS["gradient_mid"],
                    hover_color=THEME_COLORS["gradient_start"],
                    corner_radius=RADIUS["md"],
                    command=lambda ch=text: self.on_key_click(ch)
                )
            
            btn.grid(row=row, column=col, padx=6, pady=6)

        # Footer text
        footer = ctk.CTkLabel(
            login_card,
            text="Secure Point of Sale System",
            font=(FONTS["primary"], 11),
            text_color=THEME_COLORS["text_muted"]
        )
        footer.pack(pady=(10, 20))

    def on_focus_in(self, event):
        """Highlight border when focused"""
        self.pin_input.configure(border_color=THEME_COLORS["gradient_accent"])

    def on_focus_out(self, event):
        """Reset border when unfocused"""
        self.pin_input.configure(border_color=THEME_COLORS["gradient_mid"])

    def on_key_click(self, char):
        if char == "Enter":
            self.verify_login()
        elif char == "Clear":
            self.pin_input.delete(0, 'end')
        else:
            current = self.pin_input.get()
            if len(current) < 4:  # PIN length limited to 4
                self.pin_input.insert('end', char)

    def verify_login(self):
        pin = self.pin_input.get()
        if not pin:
            return
            
        user = verify_pin(pin)
        if user:
            self.pin_input.delete(0, 'end')
            # Success feedback
            self.pin_input.configure(border_color=THEME_COLORS["success"])
            # Log login action
            log_user_action(user['id'], "LOGIN")
            
            self.master.after(200, lambda: self.on_login_success(user))
        else:
            # Error feedback
            self.pin_input.configure(border_color=THEME_COLORS["danger"])
            messagebox.showwarning("Authentication Failed", "Invalid PIN. Please try again.")
            self.pin_input.delete(0, 'end')
            # Reset border color
            self.master.after(500, lambda: self.pin_input.configure(border_color=THEME_COLORS["gradient_mid"]))
