import customtkinter as ctk
from database import (
    get_all_products, get_users, get_user_logs, add_product,
    update_product, delete_product, add_user, update_user, delete_user
)
from tkinter import messagebox
from ui.custom_dialogs import (
    AddProductDialog, EditProductDialog, AddUserDialog, EditUserDialog
)
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
        header = ctk.CTkFrame(self, fg_color=THEME_COLORS["background_light"], corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(header_content, text=f"{ICONS['settings']} Admin Control Panel", font=(FONTS["primary"], 20, "bold"), text_color=THEME_COLORS["text"]).pack(side="left")
        
        right_header = ctk.CTkFrame(header_content, fg_color="transparent")
        right_header.pack(side="right")
        
        self.role_var = ctk.StringVar(value="View As...")
        role_switch = ctk.CTkOptionMenu(right_header, values=["Cashier", "Manager", "Stocker"], command=self.switch_role_view, variable=self.role_var, width=120, fg_color=THEME_COLORS["surface"], button_color=THEME_COLORS["gradient_mid"])
        role_switch.pack(side="left", padx=10)
        
        ctk.CTkButton(right_header, text=f"{ICONS['logout']} Logout", width=100, height=35, fg_color=THEME_COLORS["danger"], hover_color=THEME_COLORS["danger_hover"], corner_radius=RADIUS["md"], font=(FONTS["primary"], 14, "bold"), command=self.logout_callback).pack(side="left")

        # Tabview
        self.tabview = ctk.CTkTabview(self, fg_color=THEME_COLORS["background"], segmented_button_selected_color=THEME_COLORS["gradient_mid"], corner_radius=RADIUS["lg"])
        self.tabview.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        self.tabview.add("Products")
        self.tabview.add("Users")
        self.tabview.add("System Logs")

        # Products Tab
        p_tab = self.tabview.tab("Products")
        ctk.CTkButton(p_tab, text=f"{ICONS['add']} Add Product", height=45, fg_color=THEME_COLORS["gradient_mid"], command=self.add_product_dialog).pack(pady=15, padx=15, anchor="w")
        self.p_scroll = ctk.CTkScrollableFrame(p_tab, fg_color="transparent")
        self.p_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Users Tab
        u_tab = self.tabview.tab("Users")
        ctk.CTkButton(u_tab, text=f"{ICONS['add']} Add User", height=45, fg_color=THEME_COLORS["gradient_mid"], command=self.add_user_dialog).pack(pady=15, padx=15, anchor="w")
        self.u_scroll = ctk.CTkScrollableFrame(u_tab, fg_color="transparent")
        self.u_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Logs Tab
        l_tab = self.tabview.tab("System Logs")
        self.l_scroll = ctk.CTkScrollableFrame(l_tab, fg_color="transparent")
        self.l_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        self.load_products()
        self.load_users()
        self.load_logs()

    def switch_role_view(self, role):
        main_window = self.master.master
        if hasattr(main_window, 'simulate_role'):
            main_window.simulate_role(role.lower())
        self.role_var.set("View As...")

    def load_products(self):
        for w in self.p_scroll.winfo_children(): w.destroy()
        prods = get_all_products()
        if not prods:
            ctk.CTkLabel(self.p_scroll, text="No products found.", text_color=THEME_COLORS["text_muted"]).pack(pady=30)
            return
        
        for p in prods:
            card = create_card_frame(self.p_scroll, fg_color=THEME_COLORS["background_light"])
            card.pack(fill="x", pady=8, padx=5)
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=20, pady=15)
            top_row = ctk.CTkFrame(content, fg_color="transparent")
            top_row.pack(fill="x")
            name_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            name_frame.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(name_frame, text=f"{ICONS['product']} {p['name']}", font=(FONTS["primary"], 16, "bold"), anchor="w").pack(side="left")
            ctk.CTkLabel(name_frame, text=f"• {p.get('category', 'General')}", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_muted"]).pack(side="left", padx=10)
            btn_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            btn_frame.pack(side="right")
            ctk.CTkButton(btn_frame, text=f"{ICONS['edit']} Edit", width=80, height=35, command=lambda x=p: self.edit_product_dialog(x)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text=ICONS['delete'], width=45, height=35, fg_color=THEME_COLORS["danger"], command=lambda x=p['id']: self.del_prod(x)).pack(side="left")
            details_row = ctk.CTkFrame(content, fg_color="transparent")
            details_row.pack(fill="x", pady=(10, 0))
            price_badge = ctk.CTkFrame(details_row, fg_color=THEME_COLORS["surface"], corner_radius=RADIUS["sm"])
            price_badge.pack(side="left", padx=(0, 10))
            ctk.CTkLabel(price_badge, text=f"${p['price']:.2f}", font=(FONTS["primary"], 14, "bold"), text_color=THEME_COLORS["gradient_accent"]).pack(padx=12, pady=6)
            stock = p['stock_quantity']
            color = THEME_COLORS["success"] if stock > 20 else (THEME_COLORS["warning"] if stock > 5 else THEME_COLORS["danger"])
            stock_badge = ctk.CTkFrame(details_row, fg_color=color, corner_radius=RADIUS["sm"])
            stock_badge.pack(side="left")
            ctk.CTkLabel(stock_badge, text=f"{stock} units", font=(FONTS["primary"], 13, "bold")).pack(padx=12, pady=6)
            if p.get('barcode'): ctk.CTkLabel(details_row, text=f"Barcode: {p['barcode']}", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(side="right")

    def load_users(self):
        for w in self.u_scroll.winfo_children(): w.destroy()
        users = get_users()
        for u in users:
            card = create_card_frame(self.u_scroll, fg_color=THEME_COLORS["background_light"])
            card.pack(fill="x", pady=8, padx=5)
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=20, pady=15)
            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info_frame, text=f"{ICONS['user']} {u['name']}", font=(FONTS["primary"], 16, "bold"), anchor="w").pack(anchor="w")
            if u.get('username'): ctk.CTkLabel(info_frame, text=f"@{u['username']}", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_muted"], anchor="w").pack(anchor="w")
            details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            details_frame.pack(anchor="w", pady=(5, 0))
            role_colors = {'admin': THEME_COLORS["gradient_accent"], 'manager': THEME_COLORS["gradient_mid"], 'cashier': THEME_COLORS["success"], 'stocker': THEME_COLORS["info"]}
            role_badge = ctk.CTkFrame(details_frame, fg_color=role_colors.get(u['role'], THEME_COLORS["surface"]), corner_radius=RADIUS["sm"])
            role_badge.pack(side="left", padx=(0, 10))
            ctk.CTkLabel(role_badge, text=u['role'].upper(), font=(FONTS["primary"], 11, "bold")).pack(padx=10, pady=4)
            ctk.CTkLabel(details_frame, text=f"PIN: {u['pin']}", font=(FONTS["primary"], 13), text_color=THEME_COLORS["text_secondary"]).pack(side="left")
            btn_frame = ctk.CTkFrame(content, fg_color="transparent")
            btn_frame.pack(side="right")
            ctk.CTkButton(btn_frame, text=f"{ICONS['edit']} Edit", width=80, height=35, command=lambda x=u: self.edit_user_dialog(x)).pack(side="left", padx=5)
            if u['id'] != 1: ctk.CTkButton(btn_frame, text=ICONS['delete'], width=45, height=35, fg_color=THEME_COLORS["danger"], command=lambda x=u['id']: self.del_user(x)).pack(side="left")

    def load_logs(self):
        for w in self.l_scroll.winfo_children(): w.destroy()
        logs = get_user_logs()
        if not logs:
            ctk.CTkLabel(self.l_scroll, text="No system logs found.", text_color=THEME_COLORS["text_muted"]).pack(pady=20)
            return
        for entry in logs:
            log_item = ctk.CTkFrame(self.l_scroll, fg_color=THEME_COLORS["surface"], corner_radius=RADIUS["sm"])
            log_item.pack(fill="x", pady=4)
            time_str = entry['timestamp'][:19]
            action = entry['action']
            user = entry['user_name'] or "Unknown"
            ctk.CTkLabel(log_item, text=f"[{time_str}]", width=150, font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(side="left", padx=10)
            ctk.CTkLabel(log_item, text=user, width=150, font=(FONTS["primary"], 13, "bold")).pack(side="left")
            color = THEME_COLORS["success"] if "LOGIN" in action else THEME_COLORS["warning"]
            ctk.CTkLabel(log_item, text=action, font=(FONTS["primary"], 12, "bold"), text_color=color).pack(side="left", padx=20)

    def add_product_dialog(self):
        dialog = AddProductDialog(self)
        res = dialog.get_result()
        if res:
            add_product(res['name'], res['barcode'], res['category'], res['price'], res['stock'])
            messagebox.showinfo("Success", f"Product '{res['name']}' added!")
            self.load_products()

    def edit_product_dialog(self, p):
        dialog = EditProductDialog(self, p)
        res = dialog.get_result()
        if res:
            update_product(p['id'], res['name'], res['barcode'], res['category'], res['price'], res['stock'])
            messagebox.showinfo("Success", "Product updated!")
            self.load_products()

    def del_prod(self, pid):
        if messagebox.askyesno("Confirm", "Delete this product?"):
            delete_product(pid); self.load_products()

    def add_user_dialog(self):
        dialog = AddUserDialog(self)
        res = dialog.get_result()
        if res:
            try:
                add_user(res['name'], res['username'], res['pin'], res['role'])
                messagebox.showinfo("Success", f"User '{res['name']}' added!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add user: {e}")

    def edit_user_dialog(self, u):
        dialog = EditUserDialog(self, u)
        res = dialog.get_result()
        if res:
            try:
                update_user(u['id'], res['name'], res['username'], res['pin'], res['role'])
                messagebox.showinfo("Success", "User updated!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user: {e}")

    def del_user(self, uid):
        if messagebox.askyesno("Confirm", "Delete this user?"):
            delete_user(uid); self.load_users()
