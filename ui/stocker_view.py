import customtkinter as ctk
from database import get_all_products, update_product_stock
from tkinter import messagebox, simpledialog

class StockerView(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        self.logout_callback = logout_callback
        self.init_ui()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(header, text="Inventory Management", font=("Segoe UI", 20, "bold")).pack(side="left", padx=10)
        
        ctk.CTkButton(header, text="Refresh", width=100, command=self.load_products).pack(side="right", padx=10)
        ctk.CTkButton(header, text="Logout", width=100, fg_color="#DC3545", command=self.logout_callback).pack(side="right", padx=10)

        # Product List
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Product Stock Levels")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.load_products()

    def load_products(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        products = get_all_products()
        
        # Headers
        h_row = ctk.CTkFrame(self.scroll_frame, fg_color="gray30")
        h_row.pack(fill="x", pady=2)
        ctk.CTkLabel(h_row, text="Name", width=200, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(h_row, text="Barcode", width=120).pack(side="left")
        ctk.CTkLabel(h_row, text="Stock", width=80).pack(side="left")
        ctk.CTkLabel(h_row, text="Action", width=100).pack(side="right", padx=5)

        for p in products:
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=p['name'], width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=p['barcode'], width=120).pack(side="left")
            
            stock_color = "transparent"
            text_color = "white"
            if p['stock_quantity'] < 10:
                text_color = "#DC3545"
            
            ctk.CTkLabel(row, text=str(p['stock_quantity']), width=80, text_color=text_color, font=("Segoe UI", 14, "bold")).pack(side="left")
            
            ctk.CTkButton(row, text="Add Stock", width=80, fg_color="#28A745", 
                          command=lambda pid=p['id'], name=p['name']: self.add_stock(pid, name)).pack(side="right", padx=5)

    def add_stock(self, pid, name):
        qty = simpledialog.askinteger("Add Stock", f"How many {name} to add?", initialvalue=10, minvalue=1)
        if qty:
            update_product_stock(pid, qty)
            self.load_products()
            messagebox.showinfo("Success", "Stock updated.")
