import customtkinter as ctk
import database as db
from tkinter import messagebox, simpledialog

class AdminView(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(header, text="Admin Control Panel", font=("Segoe UI", 20, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header, text="Logout", width=100, fg_color="#DC3545", command=self.logout_callback).pack(side="right", padx=10)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("Products")
        self.tabview.add("Users")

        # Products Tab
        p_tab = self.tabview.tab("Products")
        ctk.CTkButton(p_tab, text="+ Add New Product", command=self.add_product_dialog).pack(pady=5, anchor="w")
        self.p_scroll = ctk.CTkScrollableFrame(p_tab)
        self.p_scroll.pack(fill="both", expand=True)

        # Users Tab
        u_tab = self.tabview.tab("Users")
        ctk.CTkButton(u_tab, text="+ Add New User", command=self.add_user_dialog).pack(pady=5, anchor="w")
        self.u_scroll = ctk.CTkScrollableFrame(u_tab)
        self.u_scroll.pack(fill="both", expand=True)

        self.load_products()
        self.load_users()

    def load_products(self):
        for w in self.p_scroll.winfo_children(): w.destroy()
        prods = db.get_all_products()
        for p in prods:
            row = ctk.CTkFrame(self.p_scroll)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=p['name'], width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"${p['price']:.2f}", width=80).pack(side="left")
            ctk.CTkLabel(row, text=f"S:{p['stock_quantity']}", width=60).pack(side="left")
            
            ctk.CTkButton(row, text="Del", width=50, fg_color="#DC3545", command=lambda x=p['id']: self.del_prod(x)).pack(side="right", padx=5)
            ctk.CTkButton(row, text="Edit", width=50, command=lambda x=p: self.edit_product_dialog(x)).pack(side="right", padx=5)

    def load_users(self):
        for w in self.u_scroll.winfo_children(): w.destroy()
        users = db.get_users()
        for u in users:
            row = ctk.CTkFrame(self.u_scroll)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=u['name'], width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=u['role'], width=100).pack(side="left")
            ctk.CTkLabel(row, text=f"PIN:{u['pin']}", width=80).pack(side="left")
            
            if u['id'] != 1:
                ctk.CTkButton(row, text="Del", width=50, fg_color="#DC3545", command=lambda x=u['id']: self.del_user(x)).pack(side="right", padx=5)

    def add_product_dialog(self):
        name = simpledialog.askstring("Add Product", "Name:")
        if not name: return
        barcode = simpledialog.askstring("Add Product", "Barcode:")
        price = simpledialog.askfloat("Add Product", "Price:")
        stock = simpledialog.askinteger("Add Product", "Stock Initial:")
        if name and price is not None:
            db.add_product(name, barcode or "", price, stock or 0)
            self.load_products()

    def edit_product_dialog(self, p):
        new_name = simpledialog.askstring("Edit Product", "New Name:", initialvalue=p['name'])
        new_price = simpledialog.askfloat("Edit Product", "New Price:", initialvalue=p['price'])
        new_stock = simpledialog.askinteger("Edit Product", "New Stock:", initialvalue=p['stock_quantity'])
        if new_name and new_price is not None:
            db.update_product(p['id'], new_name, p['barcode'], new_price, new_stock)
            self.load_products()

    def del_prod(self, pid):
        if messagebox.askyesno("Confirm", "Delete this product?"):
            db.delete_product(pid)
            self.load_products()

    def add_user_dialog(self):
        name = simpledialog.askstring("Add User", "Full Name:")
        if not name: return
        pin = simpledialog.askstring("Add User", "PIN (4 digits):")
        role = simpledialog.askstring("Add User", "Role (admin/manager/cashier/stocker):")
        if name and pin and role:
            db.add_user(name, pin, role.lower())
            self.load_users()

    def del_user(self, uid):
        if messagebox.askyesno("Confirm", "Delete this user?"):
            db.delete_user(uid)
            self.load_users()
