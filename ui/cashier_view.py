import customtkinter as ctk
from database import get_product_by_barcode, search_products, create_transaction
from tkinter import messagebox

class CashierView(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        self.logout_callback = logout_callback
        self.cart = [] # List of dicts
        self.init_ui()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Left Panel (Search & Cart)
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        title = ctk.CTkLabel(header, text=f"Cashier: {self.user['name']}", font=("Segoe UI", 20, "bold"))
        title.pack(side="left")

        logout_btn = ctk.CTkButton(header, text="Logout", width=80, fg_color="#DC3545", hover_color="#bd2130", command=self.logout_callback)
        logout_btn.pack(side="right")

        # Search Bar
        self.search_var = ctk.StringVar()
        self.search_bar = ctk.CTkEntry(left_panel, placeholder_text="Scan Barcode or Search Product...", height=45, font=("Segoe UI", 16))
        self.search_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.search_bar.bind("<Return>", lambda e: self.handle_search())

        # Cart Display (Scrollable Frame)
        self.cart_frame = ctk.CTkScrollableFrame(left_panel, label_text="Shopping Cart")
        self.cart_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right Panel (Total & Pay)
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        self.total_label = ctk.CTkLabel(right_panel, text="Total: $0.00", font=("Segoe UI", 32, "bold"), text_color="#28A745")
        self.total_label.pack(pady=40)

        pay_btn = ctk.CTkButton(right_panel, text="PAY NOW\n(Spacebar)", height=100, font=("Segoe UI", 20, "bold"), 
                               fg_color="#28A745", hover_color="#218838", command=self.process_payment)
        pay_btn.pack(pady=10, padx=20, fill="x")

        clear_btn = ctk.CTkButton(right_panel, text="Clear Cart", height=50, font=("Segoe UI", 16), 
                                 fg_color="#6C757D", command=self.clear_cart)
        clear_btn.pack(pady=10, padx=20, fill="x")

        self.search_bar.focus_set()
        self.master.bind_all("<space>", self.on_space_press)

    def on_space_press(self, event):
        # Only if focus is not on search bar or if cart is populated
        if self.cart:
            self.process_payment()

    def handle_search(self):
        query = self.search_bar.get().strip()
        if not query: return

        product = get_product_by_barcode(query)
        if product:
            self.add_to_cart(product)
            self.search_bar.delete(0, 'end')
        else:
            results = search_products(query)
            if len(results) == 1:
                self.add_to_cart(results[0])
                self.search_bar.delete(0, 'end')
            elif len(results) > 1:
                messagebox.showinfo("Results", f"Found {len(results)} products. Be more specific.")
            else:
                messagebox.showwarning("Not Found", "Product not found.")

    def add_to_cart(self, product):
        if product['stock_quantity'] <= 0:
            messagebox.showwarning("Stock", "Out of stock!")
            return

        for item in self.cart:
            if item['id'] == product['id']:
                item['qty'] += 1
                item['subtotal'] = item['qty'] * item['price']
                self.update_cart_display()
                return

        self.cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'qty': 1,
            'subtotal': product['price']
        })
        self.update_cart_display()

    def update_cart_display(self):
        # Clear frame
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        total = 0
        for i, item in enumerate(self.cart):
            row = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=item['name'], width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"${item['price']:.2f}", width=80).pack(side="left")
            ctk.CTkLabel(row, text=f"x{item['qty']}", width=50).pack(side="left")
            ctk.CTkLabel(row, text=f"${item['subtotal']:.2f}", width=80).pack(side="left")
            
            rem_btn = ctk.CTkButton(row, text="X", width=30, height=30, fg_color="#DC3545", command=lambda x=i: self.remove_item(x))
            rem_btn.pack(side="right", padx=5)
            
            total += item['subtotal']

        self.total_label.configure(text=f"Total: ${total:.2f}")

    def remove_item(self, index):
        del self.cart[index]
        self.update_cart_display()

    def clear_cart(self):
        self.cart = []
        self.update_cart_display()

    def process_payment(self):
        if not self.cart: return
        total = sum(i['subtotal'] for i in self.cart)
        try:
            create_transaction(self.user['id'], self.cart, total)
            messagebox.showinfo("Success", f"Sale Complete: ${total:.2f}")
            self.clear_cart()
        except Exception as e:
            messagebox.showerror("Error", str(e))
