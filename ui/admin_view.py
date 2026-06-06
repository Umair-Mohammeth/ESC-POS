import customtkinter as ctk
import database as db
from tkinter import messagebox
from ui.custom_dialogs import AddProductDialog, EditProductDialog, AddUserDialog, EditUserDialog
from styles import (
    THEME_COLORS, RADIUS, SPACING, FONTS, ICONS,
    create_card_frame, get_status_color
)

class AdminView(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master, fg_color=THEME_COLORS["background"])
        self.user = user
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Modern Header
        header = ctk.CTkFrame(
            self,
            fg_color=THEME_COLORS["background_light"],
            corner_radius=0,
            height=70
        )
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            header_content,
            text=f"{ICONS['settings']} Admin Control Panel",
            font=(FONTS["primary"], 20, "bold"),
            text_color=THEME_COLORS["text"]
        ).pack(side="left")
        
        # Right header controls (Role Switcher & Logout)
        right_header = ctk.CTkFrame(header_content, fg_color="transparent")
        right_header.pack(side="right")
        
        # Role Switcher
        self.role_var = ctk.StringVar(value="View As...")
        role_switch = ctk.CTkOptionMenu(
            right_header,
            values=["Cashier", "Manager", "Stocker"],
            command=self.switch_role_view,
            variable=self.role_var,
            width=120,
            fg_color=THEME_COLORS["surface"],
            button_color=THEME_COLORS["gradient_mid"],
            button_hover_color=THEME_COLORS["gradient_start"]
        )
        role_switch.pack(side="left", padx=10)
        
        ctk.CTkButton(
            right_header,
            text=f"{ICONS['logout']} Logout",
            width=100,
            height=35,
            fg_color=THEME_COLORS["danger"],
            hover_color=THEME_COLORS["danger_hover"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 14, "bold"),
            command=self.logout_callback
        ).pack(side="left")

        # Modern Tabview
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=THEME_COLORS["background"],
            segmented_button_fg_color=THEME_COLORS["background_light"],
            segmented_button_selected_color=THEME_COLORS["gradient_mid"],
            segmented_button_selected_hover_color=THEME_COLORS["gradient_start"],
            corner_radius=RADIUS["lg"]
        )
        self.tabview.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        self.tabview.add("Products")
        self.tabview.add("Users")
        self.tabview.add("System Logs") # Added Logs tab

        # Products Tab
        p_tab = self.tabview.tab("Products")
        
        # Add button
        add_p_btn = ctk.CTkButton(
            p_tab,
            text=f"{ICONS['add']} Add New Product",
            height=45,
            fg_color=THEME_COLORS["gradient_mid"],
            hover_color=THEME_COLORS["gradient_start"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 15, "bold"),
            command=self.add_product_dialog
        )
        add_p_btn.pack(pady=15, padx=15, anchor="w")
        
        self.p_scroll = ctk.CTkScrollableFrame(
            p_tab,
            fg_color="transparent"
        )
        self.p_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Users Tab
        u_tab = self.tabview.tab("Users")
        
        add_u_btn = ctk.CTkButton(
            u_tab,
            text=f"{ICONS['add']} Add New User",
            height=45,
            fg_color=THEME_COLORS["gradient_mid"],
            hover_color=THEME_COLORS["gradient_start"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 15, "bold"),
            command=self.add_user_dialog
        )
        add_u_btn.pack(pady=15, padx=15, anchor="w")
        
        self.u_scroll = ctk.CTkScrollableFrame(
            u_tab,
            fg_color="transparent"
        )
        self.u_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Logs Tab
        l_tab = self.tabview.tab("System Logs")
        self.l_scroll = ctk.CTkScrollableFrame(l_tab, fg_color="transparent")
        self.l_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        self.load_products()
        self.load_users()
        self.load_logs()

    def switch_role_view(self, role):
        """Switch view to simulate another role"""
        main_window = self.master.master
        if hasattr(main_window, 'simulate_role'):
            main_window.simulate_role(role.lower())
        self.role_var.set("View As...")

    def load_products(self):
        for w in self.p_scroll.winfo_children():
            w.destroy()
            
        prods = db.get_all_products()
        
        if not prods:
            ctk.CTkLabel(
                self.p_scroll,
                text="No products yet. Add your first product!",
                font=(FONTS["primary"], 14),
                text_color=THEME_COLORS["text_muted"]
            ).pack(pady=30)
            return
        
        for p in prods:
            # Modern product card
            card = create_card_frame(
                self.p_scroll,
                fg_color=THEME_COLORS["background_light"],
                corner_radius=RADIUS["lg"]
            )
            card.pack(fill="x", pady=8, padx=5)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=20, pady=15)
            
            # Top row: name and buttons
            top_row = ctk.CTkFrame(content, fg_color="transparent")
            top_row.pack(fill="x")
            
            # Product icon and name
            name_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            name_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                name_frame,
                text=f"{ICONS['product']} {p['name']}",
                font=(FONTS["primary"], 16, "bold"),
                text_color=THEME_COLORS["text"],
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                name_frame,
                text=f"• {p.get('category', 'General')}",
                font=(FONTS["primary"], 12),
                text_color=THEME_COLORS["text_muted"]
            ).pack(side="left", padx=10)
            
            # Action buttons
            btn_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            btn_frame.pack(side="right")
            
            ctk.CTkButton(
                btn_frame,
                text=f"{ICONS['edit']} Edit",
                width=80,
                height=35,
                fg_color=THEME_COLORS["gradient_mid"],
                hover_color=THEME_COLORS["gradient_start"],
                corner_radius=RADIUS["sm"],
                font=(FONTS["primary"], 13, "bold"),
                command=lambda x=p: self.edit_product_dialog(x)
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                btn_frame,
                text=ICONS['delete'],
                width=45,
                height=35,
                fg_color=THEME_COLORS["danger"],
                hover_color=THEME_COLORS["danger_hover"],
                corner_radius=RADIUS["sm"],
                font=(FONTS["primary"], 14),
                command=lambda x=p['id']: self.del_prod(x)
            ).pack(side="left")
            
            # Bottom row: details
            details_row = ctk.CTkFrame(content, fg_color="transparent")
            details_row.pack(fill="x", pady=(10, 0))
            
            # Price
            price_badge = ctk.CTkFrame(
                details_row,
                fg_color=THEME_COLORS["surface"],
                corner_radius=RADIUS["sm"]
            )
            price_badge.pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(
                price_badge,
                text=f"${p['price']:.2f}",
                font=(FONTS["primary"], 14, "bold"),
                text_color=THEME_COLORS["gradient_accent"]
            ).pack(padx=12, pady=6)
            
            # Stock status
            stock = p['stock_quantity']
            if stock > 20:
                status, color = "In Stock", THEME_COLORS["success"]
            elif stock > 5:
                status, color = "Low Stock", THEME_COLORS["warning"]
            elif stock > 0:
                status, color = "Very Low", THEME_COLORS["danger"]
            else:
                status, color = "Out of Stock", THEME_COLORS["text_muted"]
            
            stock_badge = ctk.CTkFrame(
                details_row,
                fg_color=color,
                corner_radius=RADIUS["sm"]
            )
            stock_badge.pack(side="left")
            
            ctk.CTkLabel(
                stock_badge,
                text=f"{stock} units • {status}",
                font=(FONTS["primary"], 13, "bold"),
                text_color=THEME_COLORS["text"]
            ).pack(padx=12, pady=6)
            
            # Barcode if available
            if p.get('barcode'):
                ctk.CTkLabel(
                    details_row,
                    text=f"Barcode: {p['barcode']}",
                    font=(FONTS["primary"], 12),
                    text_color=THEME_COLORS["text_secondary"]
                ).pack(side="right")

    def load_users(self):
        for w in self.u_scroll.winfo_children():
            w.destroy()
            
        users = db.get_users()
        
        for u in users:
            # Modern user card
            card = create_card_frame(
                self.u_scroll,
                fg_color=THEME_COLORS["background_light"],
                corner_radius=RADIUS["lg"]
            )
            card.pack(fill="x", pady=8, padx=5)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=20, pady=15)
            
            # User info
            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                info_frame,
                text=f"{ICONS['user']} {u['name']}",
                font=(FONTS["primary"], 16, "bold"),
                text_color=THEME_COLORS["text"],
                anchor="w"
            ).pack(anchor="w")
            
            if u.get('username'):
                ctk.CTkLabel(
                    info_frame,
                    text=f"@{u['username']}",
                    font=(FONTS["primary"], 12),
                    text_color=THEME_COLORS["text_muted"],
                    anchor="w"
                ).pack(anchor="w")
            
            details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            details_frame.pack(anchor="w", pady=(5, 0))
            
            # Role badge
            role_colors = {
                'admin': THEME_COLORS["gradient_accent"],
                'manager': THEME_COLORS["gradient_mid"],
                'cashier': THEME_COLORS["success"],
                'stocker': THEME_COLORS["info"]
            }
            
            role_badge = ctk.CTkFrame(
                details_frame,
                fg_color=role_colors.get(u['role'], THEME_COLORS["surface"]),
                corner_radius=RADIUS["sm"]
            )
            role_badge.pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(
                role_badge,
                text=u['role'].upper(),
                font=(FONTS["primary"], 11, "bold"),
                text_color=THEME_COLORS["text"]
            ).pack(padx=10, pady=4)
            
            ctk.CTkLabel(
                details_frame,
                text=f"PIN: {u['pin']}",
                font=(FONTS["primary"], 13),
                text_color=THEME_COLORS["text_secondary"]
            ).pack(side="left")
            
            # Action buttons for users
            u_btn_frame = ctk.CTkFrame(content, fg_color="transparent")
            u_btn_frame.pack(side="right")

            ctk.CTkButton(
                u_btn_frame,
                text=f"{ICONS['edit']} Edit",
                width=80,
                height=35,
                fg_color=THEME_COLORS["gradient_mid"],
                hover_color=THEME_COLORS["gradient_start"],
                corner_radius=RADIUS["sm"],
                font=(FONTS["primary"], 13, "bold"),
                command=lambda x=u: self.edit_user_dialog(x)
            ).pack(side="left", padx=5)

            # Delete button (except for admin user)
            if u['id'] != 1:
                ctk.CTkButton(
                    u_btn_frame,
                    text=ICONS['delete'],
                    width=45,
                    height=35,
                    fg_color=THEME_COLORS["danger"],
                    hover_color=THEME_COLORS["danger_hover"],
                    corner_radius=RADIUS["sm"],
                    font=(FONTS["primary"], 14),
                    command=lambda x=u['id']: self.del_user(x)
                ).pack(side="left")

    def load_logs(self):
        """Load system usage logs"""
        for w in self.l_scroll.winfo_children():
            w.destroy()
        
        logs = db.get_user_logs()
        if not logs:
            ctk.CTkLabel(self.l_scroll, text="No system logs found.", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_muted"]).pack(pady=20)
            return

        for entry in logs:
            log_item = ctk.CTkFrame(self.l_scroll, fg_color=THEME_COLORS["surface"], corner_radius=RADIUS["sm"])
            log_item.pack(fill="x", pady=4)
            
            time_str = entry['timestamp'][:19]
            action = entry['action']
            user = entry['user_name'] or "Unknown"
            
            ctk.CTkLabel(log_item, text=f"[{time_str}]", width=150, font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(side="left", padx=10)
            ctk.CTkLabel(log_item, text=user, width=150, font=(FONTS["primary"], 13, "bold"), text_color=THEME_COLORS["text"]).pack(side="left")
            color = THEME_COLORS["success"] if "LOGIN" in action else THEME_COLORS["warning"]
            ctk.CTkLabel(log_item, text=action, font=(FONTS["primary"], 12, "bold"), text_color=color).pack(side="left", padx=20)

    def add_product_dialog(self):
        """Show modern add product dialog"""
        dialog = AddProductDialog(self)
        result = dialog.get_result()
        
        if result:
            db.add_product(
                result['name'],
                result['barcode'],
                result.get('category', 'General'),
                result['price'],
                result['stock']
            )
            messagebox.showinfo("Success", f"Product '{result['name']}' added successfully!")
            self.load_products()

    def edit_product_dialog(self, p):
        """Show modern edit product dialog"""
        dialog = EditProductDialog(self, p)
        result = dialog.get_result()
        
        if result:
            db.update_product(
                p['id'],
                result['name'],
                result['barcode'],
                result.get('category', 'General'),
                result['price'],
                result['stock']
            )
            messagebox.showinfo("Success", "Product updated successfully!")
            self.load_products()

    def del_prod(self, pid):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            db.delete_product(pid)
            messagebox.showinfo("Success", "Product deleted successfully!")
            self.load_products()

    def add_user_dialog(self):
        """Show modern add user dialog"""
        dialog = AddUserDialog(self)
        result = dialog.get_result()
        
        if result:
            try:
                db.add_user(result['name'], result.get('username'), result['pin'], result['role'])
                messagebox.showinfo("Success", f"User '{result['name']}' added successfully!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add user. Username might be taken.\n\nError: {str(e)}")

    def edit_user_dialog(self, u):
        """Show modern edit user dialog"""
        dialog = EditUserDialog(self, u)
        result = dialog.get_result()

        if result:
            try:
                db.update_user(u['id'], result['name'], result['username'], result['pin'], result['role'])
                messagebox.showinfo("Success", "User updated successfully!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update user.\n\nError: {str(e)}")

    def del_user(self, uid):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            db.delete_user(uid)
            messagebox.showinfo("Success", "User deleted successfully!")
            self.load_users()
