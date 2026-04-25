"""
Custom Dialog Windows with Modern Design
Matches the main dashboard aesthetic
"""

import customtkinter as ctk
from tkinter import messagebox
from styles import (
    THEME_COLORS, RADIUS, SPACING, FONTS, ICONS,
    create_card_frame
)


class ModernDialog(ctk.CTkToplevel):
    """Base class for modern dialog windows"""
    
    def __init__(self, parent, title, width=500, height=400):
        super().__init__(parent)
        
        self.result = None
        self.title(title)
        self.geometry(f"{width}x{height}")
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
        
        # Modern styling
        self.configure(fg_color=THEME_COLORS["background"])
        
        # Prevent resize
        self.resizable(False, False)
        
    def get_result(self):
        """Wait for dialog to close and return result"""
        self.wait_window()
        return self.result

    def create_input_field(self, parent, label, row=None, placeholder="", is_password=False):
        """Helper to create labeled input field with focus highlights"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            container,
            text=label,
            font=(FONTS["primary"], 14),
            text_color=THEME_COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            container,
            height=45,
            placeholder_text=placeholder,
            show="*" if is_password else "",
            font=(FONTS["primary"], 15),
            fg_color=THEME_COLORS["surface"],
            border_color=THEME_COLORS["surface_light"],
            border_width=2,
            corner_radius=RADIUS["md"]
        )
        entry.pack(fill="x")

        # Focus highlights
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=THEME_COLORS["surface_light"]))
        
        return entry, container


class ProductBaseDialog(ModernDialog):
    """Base class for product add/edit dialogs"""
    def __init__(self, parent, title, product=None):
        super().__init__(parent, title, width=600, height=680)
        self.product = product
        self.init_ui()

    def init_ui(self):
        main_card = create_card_frame(self, fg_color=THEME_COLORS["background_light"])
        main_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        icon = ICONS['edit'] if self.product else ICONS['product']
        ctk.CTkLabel(header, text=f"{icon} {self.title()}", font=(FONTS["primary"], 20, "bold")).pack(side="left")
        
        form = ctk.CTkFrame(main_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.name_entry, _ = self.create_input_field(form, "Product Name *")
        self.barcode_entry, _ = self.create_input_field(form, "Barcode (Optional)")
        self.category_entry, _ = self.create_input_field(form, "Category *")
        self.price_entry, _ = self.create_input_field(form, "Price ($) *")
        self.stock_entry, _ = self.create_input_field(form, "Stock Quantity *")
        
        if self.product:
            self.name_entry.insert(0, self.product['name'])
            self.barcode_entry.insert(0, self.product.get('barcode', ''))
            self.category_entry.insert(0, self.product.get('category', 'General'))
            self.price_entry.insert(0, str(self.product['price']))
            self.stock_entry.insert(0, str(self.product['stock_quantity']))
        else:
            self.category_entry.insert(0, "General")
            self.stock_entry.insert(0, "0")

        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text=f"{ICONS['close']} Cancel", fg_color="#334155", command=self.destroy).pack(side="right", padx=(10, 0))
        
        submit_txt = "Save Changes" if self.product else "Add Product"
        ctk.CTkButton(btn_frame, text=f"{ICONS['check']} {submit_txt}", command=self.submit).pack(side="right")
        
        self.name_entry.focus()

    def validate_inputs(self):
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()
        stock_str = self.stock_entry.get().strip()
        
        if not name:
            messagebox.showerror("Validation Error", "Product name is required!")
            return False
        try:
            if float(price_str) < 0: raise ValueError()
        except:
            messagebox.showerror("Validation Error", "Invalid price!")
            return False
        try:
            if int(stock_str) < 0: raise ValueError()
        except:
            messagebox.showerror("Validation Error", "Invalid stock quantity!")
            return False
        return True

    def submit(self):
        if not self.validate_inputs(): return
        self.result = {
            'name': self.name_entry.get().strip(),
            'barcode': self.barcode_entry.get().strip(),
            'category': self.category_entry.get().strip() or "General",
            'price': float(self.price_entry.get().strip()),
            'stock': int(self.stock_entry.get().strip())
        }
        self.destroy()


class AddProductDialog(ProductBaseDialog):
    def __init__(self, parent):
        super().__init__(parent, "Add New Product")

class EditProductDialog(ProductBaseDialog):
    def __init__(self, parent, product):
        super().__init__(parent, "Edit Product", product)


class UserBaseDialog(ModernDialog):
    """Base class for user add/edit dialogs"""
    def __init__(self, parent, title, user=None):
        super().__init__(parent, title, width=600, height=680)
        self.user = user
        self.init_ui()

    def init_ui(self):
        main_card = create_card_frame(self, fg_color=THEME_COLORS["background_light"])
        main_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header, text=f"{ICONS['user']} {self.title()}", font=(FONTS["primary"], 20, "bold")).pack(side="left")
        
        form = ctk.CTkFrame(main_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.name_entry, _ = self.create_input_field(form, "Full Name *")
        
        # Username with Suggest
        u_cont = ctk.CTkFrame(form, fg_color="transparent")
        u_cont.pack(fill="x", pady=8)
        u_head = ctk.CTkFrame(u_cont, fg_color="transparent")
        u_head.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(u_head, text="Username *", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(side="left")
        ctk.CTkButton(u_head, text="✨ Suggest", width=70, height=24, font=(FONTS["primary"], 11, "bold"),
                      fg_color=THEME_COLORS["gradient_accent"], command=self.suggest_username).pack(side="right")
        self.username_entry = ctk.CTkEntry(u_cont, height=45, fg_color=THEME_COLORS["surface"], border_color=THEME_COLORS["surface_light"], border_width=2)
        self.username_entry.pack(fill="x")
        self.username_entry.bind("<FocusIn>", lambda e: self.username_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.username_entry.bind("<FocusOut>", lambda e: self.username_entry.configure(border_color=THEME_COLORS["surface_light"]))

        self.pin_entry, _ = self.create_input_field(form, "4-Digit PIN *")
        
        # Role
        role_cont = ctk.CTkFrame(form, fg_color="transparent")
        role_cont.pack(fill="x", pady=8)
        ctk.CTkLabel(role_cont, text="Role *", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w", pady=(0, 5))
        self.role_var = ctk.StringVar(value="cashier")
        role_opts = ctk.CTkFrame(role_cont, fg_color=THEME_COLORS["surface"], corner_radius=RADIUS["md"])
        role_opts.pack(fill="x")
        for label, val in [("Admin", "admin"), ("Manager", "manager"), ("Cashier", "cashier"), ("Stocker", "stocker")]:
            ctk.CTkRadioButton(role_opts, text=label, variable=self.role_var, value=val, font=(FONTS["primary"], 14),
                               fg_color=THEME_COLORS["gradient_mid"]).pack(side="left", padx=10, pady=12)

        if self.user:
            self.name_entry.insert(0, self.user['name'])
            self.username_entry.insert(0, self.user.get('username', ''))
            self.pin_entry.insert(0, self.user['pin'])
            self.role_var.set(self.user['role'])

        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        ctk.CTkButton(btn_frame, text=f"{ICONS['close']} Cancel", fg_color="#334155", command=self.destroy).pack(side="right", padx=(10, 0))
        submit_txt = "Save Changes" if self.user else "Add User"
        ctk.CTkButton(btn_frame, text=f"{ICONS['check']} {submit_txt}", command=self.submit).pack(side="right")
        self.name_entry.focus()

    def suggest_username(self):
        name = self.name_entry.get().strip()
        if not name: return
        import random
        suggestion = f"{name.split()[0].lower()}{random.randint(100, 999)}"
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, suggestion)

    def submit(self):
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        pin = self.pin_entry.get().strip()
        if not name or not username or len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Error", "Please fill all fields correctly. PIN must be 4 digits.")
            return
        self.result = {'name': name, 'username': username, 'pin': pin, 'role': self.role_var.get()}
        self.destroy()


class AddUserDialog(UserBaseDialog):
    def __init__(self, parent):
        super().__init__(parent, "Add New User")

class EditUserDialog(UserBaseDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "Edit User", user)


class AddStockDialog(ModernDialog):
    """Modern dialog for adding stock to a product"""
    
    def __init__(self, parent, product_id, product_name):
        self.product_id = product_id
        self.product_name = product_name
        super().__init__(parent, "Add Stock", width=500, height=350)
        self.init_ui()
        
    def init_ui(self):
        # Main container card
        main_card = create_card_frame(
            self,
            fg_color=THEME_COLORS["background_light"],
            corner_radius=RADIUS["lg"]
        )
        main_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text=f"{ICONS['box']} Add Stock",
            font=(FONTS["primary"], 20, "bold"),
            text_color=THEME_COLORS["text"]
        ).pack(side="left")
        
        # Product info
        info_frame = ctk.CTkFrame(
            main_card,
            fg_color=THEME_COLORS["surface"],
            corner_radius=RADIUS["md"]
        )
        info_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Product: {self.product_name}",
            font=(FONTS["primary"], 15),
            text_color=THEME_COLORS["text_secondary"]
        ).pack(padx=15, pady=12)
        
        # Quantity input
        form = ctk.CTkFrame(main_card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            form,
            text="Quantity to Add *",
            font=(FONTS["primary"], 14),
            text_color=THEME_COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.quantity_entry = ctk.CTkEntry(
            form,
            height=50,
            font=(FONTS["primary"], 18),
            fg_color=THEME_COLORS["surface"],
            border_color=THEME_COLORS["surface_light"],
            border_width=2,
            corner_radius=RADIUS["md"],
            justify="center"
        )
        self.quantity_entry.pack(fill="x")
        self.quantity_entry.insert(0, "10")
        self.quantity_entry.bind("<FocusIn>", lambda e: self.quantity_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.quantity_entry.bind("<FocusOut>", lambda e: self.quantity_entry.configure(border_color=THEME_COLORS["surface_light"]))
        self.quantity_entry.bind("<Return>", lambda e: self.submit())
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(20, 20))
        
        ctk.CTkButton(
            btn_frame,
            text=f"{ICONS['close']} Cancel",
            width=120,
            height=45,
            fg_color=THEME_COLORS["surface"],
            hover_color=THEME_COLORS["surface_light"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 15, "bold"),
            command=self.cancel
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            btn_frame,
            text=f"{ICONS['check']} Add Stock",
            width=150,
            height=45,
            fg_color=THEME_COLORS["success"],
            hover_color=THEME_COLORS["success_hover"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 15, "bold"),
            command=self.submit
        ).pack(side="right")
        
        # Focus and select all
        self.quantity_entry.focus()
        self.quantity_entry.select_range(0, 'end')
        
    def validate_inputs(self):
        """Validate quantity input"""
        qty_str = self.quantity_entry.get().strip()
        
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError()
            if qty > 10000:
                messagebox.showerror("Validation Error", "Quantity cannot exceed 10,000!")
                return False
        except:
            messagebox.showerror("Validation Error", "Please enter a valid positive quantity!")
            self.quantity_entry.focus()
            return False
            
        return True
        
    def submit(self):
        """Handle form submission"""
        if not self.validate_inputs():
            return
            
        self.result = int(self.quantity_entry.get().strip())
        self.destroy()
        
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.destroy()


class BrowseProductsDialog(ModernDialog):
    """Modern dialog for browsing and selecting products"""
    
    def __init__(self, parent):
        super().__init__(parent, "Inventory Browser", width=800, height=600)
        self.init_ui()
        
    def init_ui(self):
        # Main Layout
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Search & Filter Header
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(
            header, 
            placeholder_text="🔍 Search name, category, or barcode...", 
            height=45,
            font=(FONTS["primary"], 15)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_products())
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.configure(border_color=THEME_COLORS["surface_light"]))
        
        # Scrollable area for products
        self.scroll_frame = ctk.CTkScrollableFrame(
            main_frame, 
            fg_color=THEME_COLORS["background_light"],
            border_width=1,
            border_color=THEME_COLORS["surface"]
        )
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_products()
        
    def load_products(self):
        from database import get_all_products
        self.products = get_all_products()
        self.display_products(self.products)
        
    def display_products(self, product_list):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        if not product_list:
            ctk.CTkLabel(self.scroll_frame, text="No matches found.", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_muted"]).pack(pady=40)
            return

        for p in product_list:
            item = ctk.CTkFrame(self.scroll_frame, fg_color=THEME_COLORS["surface"], height=60)
            item.pack(fill="x", pady=4, padx=5)
            item.pack_propagate(False)
            
            # Clickable area to select
            content = ctk.CTkFrame(item, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=15)
            
            ctk.CTkLabel(content, text=p['name'], font=(FONTS["primary"], 14, "bold"), anchor="w", width=250).pack(side="left")
            ctk.CTkLabel(content, text=p.get('category', 'General'), font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"], width=150).pack(side="left")
            ctk.CTkLabel(content, text=f"${p['price']:.2f}", font=(FONTS["primary"], 14), text_color=THEME_COLORS["gradient_accent"], width=100).pack(side="left")
            
            select_btn = ctk.CTkButton(
                content, text="Select", width=80, height=30,
                fg_color=THEME_COLORS["gradient_mid"],
                command=lambda x=p: self.select_product(x)
            )
            select_btn.pack(side="right")

    def filter_products(self):
        query = self.search_entry.get().lower()
        if not query:
            self.display_products(self.products)
            return
            
        filtered = [
            p for p in self.products 
            if query in p['name'].lower() or 
               query in p.get('category', '').lower() or 
               query in str(p.get('barcode', '')).lower()
        ]
        self.display_products(filtered)
        
    def select_product(self, product):
        self.result = product
        self.destroy()


class InvoiceDialog(ModernDialog):
    """Modern dialog for displaying generated invoices/receipts"""
    
    def __init__(self, parent, receipt_text):
        super().__init__(parent, "Transaction Receipt", width=400, height=650)
        self.receipt_text = receipt_text
        self.init_ui()
        
    def init_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Action Bar
        actions = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(
            actions, text=f"{ICONS['settings']} Print Copy", 
            width=120, height=35,
            command=self.print_simulated
        ).pack(side="left")
        
        ctk.CTkButton(
            actions, text=f"{ICONS['close']} Close", 
            fg_color=THEME_COLORS["surface"],
            width=100, height=35,
            command=self.destroy
        ).pack(side="right")
        
        # Receipt Text Area
        receipt_card = create_card_frame(main_frame, fg_color="#F1F5F9") # Paper White
        receipt_card.pack(fill="both", expand=True)
        
        # Monospaced font is critical for receipt alignment
        receipt_display = ctk.CTkTextbox(
            receipt_card, 
            fg_color="transparent", 
            text_color="#1E293B", # Dark Ink
            font=(FONTS["mono"], 14),
            padx=20, pady=20
        )
        receipt_display.pack(fill="both", expand=True)
        receipt_display.insert("1.0", self.receipt_text)
        receipt_display.configure(state="disabled") # Read only

    def print_simulated(self):
        messagebox.showinfo("Printer Status", "ESC/POS Command sent to thermal printer!")
        self.destroy()


class ManualEntryDialog(ModernDialog):
    """Modern dialog for manual item entry"""

    def __init__(self, parent):
        super().__init__(parent, "Manual Entry", width=500, height=450)
        self.init_ui()

    def init_ui(self):
        # Main container card
        main_card = create_card_frame(
            self,
            fg_color=THEME_COLORS["background_light"],
            corner_radius=RADIUS["lg"]
        )
        main_card.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=f"{ICONS['settings']} Manual Entry",
            font=(FONTS["primary"], 20, "bold"),
            text_color=THEME_COLORS["text"]
        ).pack(side="left")

        # Form
        form = ctk.CTkFrame(main_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(form, text="Item Name *", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(form, height=45, fg_color=THEME_COLORS["surface"])
        self.name_entry.pack(fill="x", pady=(0, 15))
        self.name_entry.insert(0, "Miscellaneous")
        self.name_entry.bind("<FocusIn>", lambda e: self.name_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.name_entry.bind("<FocusOut>", lambda e: self.name_entry.configure(border_color=THEME_COLORS["surface_light"]))

        ctk.CTkLabel(form, text="Price ($) *", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w", pady=(0, 5))
        self.price_entry = ctk.CTkEntry(form, height=45, fg_color=THEME_COLORS["surface"])
        self.price_entry.pack(fill="x", pady=(0, 20))
        self.price_entry.bind("<FocusIn>", lambda e: self.price_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.price_entry.bind("<FocusOut>", lambda e: self.price_entry.configure(border_color=THEME_COLORS["surface_light"]))

        # Buttons
        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=120, height=45,
            fg_color=THEME_COLORS["surface"],
            command=self.destroy
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Add to Cart",
            width=150, height=45,
            fg_color=THEME_COLORS["success"],
            hover_color=THEME_COLORS["success_hover"],
            font=(FONTS["primary"], 15, "bold"),
            command=self.submit
        ).pack(side="right", fill="x", expand=True)

        self.price_entry.focus()
        self.price_entry.bind("<Return>", lambda e: self.submit())
        self.name_entry.bind("<Return>", lambda e: self.submit())

    def submit(self):
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Item name is required!")
            self.name_entry.focus()
            return

        try:
            price = float(price_str)
            if price < 0: raise ValueError()
        except:
            messagebox.showerror("Validation Error", "Please enter a valid price!")
            self.price_entry.focus()
            return

        self.result = {
            "id": 0, # Virtual ID for manual entry
            "name": name,
            "price": price,
            "stock_quantity": 999999, # Unlimited for manual entry
            "category": "Manual"
        }
        self.destroy()
