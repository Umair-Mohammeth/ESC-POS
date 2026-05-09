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

    def create_input_field(self, parent, label, show=None):
        """Helper to create labeled input field with focus highlighting"""
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
            font=(FONTS["primary"], 15),
            fg_color=THEME_COLORS["surface"],
            border_color=THEME_COLORS["surface_light"],
            border_width=2,
            corner_radius=RADIUS["md"],
            show=show
        )
        entry.pack(fill="x")
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
        main_card = create_card_frame(self, fg_color=THEME_COLORS["background_light"], corner_radius=RADIUS["lg"])
        main_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        icon = ICONS['product'] if not self.product else ICONS['edit']
        ctk.CTkLabel(header, text=f"{icon} {self.title_text}", font=(FONTS["primary"], 20, "bold"), text_color=THEME_COLORS["text"]).pack(side="left")
        
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
        
        ctk.CTkButton(btn_frame, text=f"{ICONS['close']} Cancel", width=120, height=45, fg_color="#334155", hover_color="#475569", corner_radius=RADIUS["md"], font=(FONTS["primary"], 15, "bold"), command=self.destroy).pack(side="right", padx=(10, 0))
        
        submit_text = "Add Product" if not self.product else "Save Changes"
        submit_color = "#059669" if not self.product else THEME_COLORS["gradient_mid"]
        ctk.CTkButton(btn_frame, text=f"{ICONS['check']} {submit_text}", width=150, height=45, fg_color=submit_color, hover_color=THEME_COLORS["gradient_start"] if self.product else "#047857", corner_radius=RADIUS["md"], font=(FONTS["primary"], 15, "bold"), command=self.submit).pack(side="right")
        
        self.name_entry.focus()

    def submit(self):
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()
        stock_str = self.stock_entry.get().strip()
        
        if not name:
            messagebox.showerror("Validation Error", "Product name is required!")
            self.name_entry.focus()
            return
            
        try:
            price = float(price_str)
            if price < 0: raise ValueError()
        except:
            messagebox.showerror("Validation Error", "Please enter a valid price!")
            self.price_entry.focus()
            return
            
        try:
            stock = int(stock_str)
            if stock < 0: raise ValueError()
        except:
            messagebox.showerror("Validation Error", "Please enter a valid stock quantity!")
            self.stock_entry.focus()
            return
            
        self.result = {
            'name': name,
            'barcode': self.barcode_entry.get().strip(),
            'category': self.category_entry.get().strip() or "General",
            'price': price,
            'stock': stock
        }
        self.destroy()


class AddProductDialog(ProductBaseDialog):
    def __init__(self, parent):
        self.title_text = "Add New Product"
        super().__init__(parent, self.title_text)

class EditProductDialog(ProductBaseDialog):
    def __init__(self, parent, product):
        self.title_text = "Edit Product"
        super().__init__(parent, self.title_text, product)


class UserBaseDialog(ModernDialog):
    """Base class for user add/edit dialogs"""
    def __init__(self, parent, title, user=None):
        super().__init__(parent, title, width=600, height=680)
        self.user = user
        self.init_ui()

    def init_ui(self):
        main_card = create_card_frame(self, fg_color=THEME_COLORS["background_light"], corner_radius=RADIUS["lg"])
        main_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        icon = ICONS['user'] if not self.user else ICONS['edit']
        ctk.CTkLabel(header, text=f"{icon} {self.title_text}", font=(FONTS["primary"], 20, "bold"), text_color=THEME_COLORS["text"]).pack(side="left")
        
        form = ctk.CTkFrame(main_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.name_entry, _ = self.create_input_field(form, "Full Name *")
        
        # Username field with Suggest button
        username_container = ctk.CTkFrame(form, fg_color="transparent")
        username_container.pack(fill="x", pady=8)
        header_frame = ctk.CTkFrame(username_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(header_frame, text="Username *", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(side="left")
        ctk.CTkButton(header_frame, text="✨ Suggest", width=70, height=24, font=(FONTS["primary"], 11, "bold"), fg_color=THEME_COLORS["gradient_accent"], command=self.suggest_username).pack(side="right")
        self.username_entry = ctk.CTkEntry(username_container, height=45, font=(FONTS["primary"], 15), fg_color=THEME_COLORS["surface"], border_color=THEME_COLORS["surface_light"], border_width=2, corner_radius=RADIUS["md"])
        self.username_entry.pack(fill="x")
        self.username_entry.bind("<FocusIn>", lambda e: self.username_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.username_entry.bind("<FocusOut>", lambda e: self.username_entry.configure(border_color=THEME_COLORS["surface_light"]))

        self.pin_entry, _ = self.create_input_field(form, "4-Digit PIN *")
        
        role_container = ctk.CTkFrame(form, fg_color="transparent")
        role_container.pack(fill="x", pady=8)
        ctk.CTkLabel(role_container, text="Role *", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"], anchor="w").pack(anchor="w", pady=(0, 5))
        self.role_var = ctk.StringVar(value="cashier")
        role_options = ctk.CTkFrame(role_container, fg_color=THEME_COLORS["surface"], corner_radius=RADIUS["md"])
        role_options.pack(fill="x")
        for label, value in [("Admin", "admin"), ("Manager", "manager"), ("Cashier", "cashier"), ("Stocker", "stocker")]:
            ctk.CTkRadioButton(role_options, text=label, variable=self.role_var, value=value, font=(FONTS["primary"], 14), fg_color=THEME_COLORS["gradient_mid"], hover_color=THEME_COLORS["gradient_start"]).pack(side="left", padx=10, pady=12)

        if self.user:
            self.name_entry.insert(0, self.user['name'])
            self.username_entry.insert(0, self.user.get('username', ''))
            self.pin_entry.insert(0, self.user['pin'])
            self.role_var.set(self.user['role'])

        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text=f"{ICONS['close']} Cancel", width=120, height=45, fg_color="#334155", hover_color="#475569", corner_radius=RADIUS["md"], font=(FONTS["primary"], 15, "bold"), command=self.destroy).pack(side="right", padx=(10, 0))
        
        submit_text = "Add User" if not self.user else "Save Changes"
        ctk.CTkButton(btn_frame, text=f"{ICONS['check']} {submit_text}", width=150, height=45, fg_color="#059669", hover_color="#047857", corner_radius=RADIUS["md"], font=(FONTS["primary"], 15, "bold"), command=self.submit).pack(side="right")
        
        self.name_entry.focus()

    def suggest_username(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showinfo("Tip", "Enter a name first to get a suggestion!")
            return
        import random
        first_name = name.split()[0].lower()
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, f"{first_name}{random.randint(100, 999)}")

    def submit(self):
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        pin = self.pin_entry.get().strip()
        
        if not name:
            messagebox.showerror("Validation Error", "Full name is required!")
            self.name_entry.focus()
            return
            
        if not username:
            messagebox.showerror("Validation Error", "Username is required!")
            self.username_entry.focus()
            return

        if not pin or len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Validation Error", "PIN must be exactly 4 digits!")
            self.pin_entry.focus()
            return
            
        self.result = {'name': name, 'username': username, 'pin': pin, 'role': self.role_var.get()}
        self.destroy()

class AddUserDialog(UserBaseDialog):
    def __init__(self, parent):
        self.title_text = "Add New User"
        super().__init__(parent, self.title_text)

class EditUserDialog(UserBaseDialog):
    def __init__(self, parent, user):
        self.title_text = "Edit User"
        super().__init__(parent, self.title_text, user)


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
            command=self.destroy
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
            font=("Consolas", 14),
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

        self.name_entry, _ = self.create_input_field(form, "Item Name *")
        self.name_entry.insert(0, "Miscellaneous")

        self.price_entry, _ = self.create_input_field(form, "Price ($) *")

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
