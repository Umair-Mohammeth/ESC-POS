import customtkinter as ctk
from database import get_product_by_barcode, get_product_by_id, search_products, create_transaction, get_discount
from printer_service import PrinterService
from ui.custom_dialogs import BrowseProductsDialog, ManualEntryDialog, InvoiceDialog
from tkinter import messagebox
from styles import (
    THEME_COLORS, RADIUS, SPACING, FONTS, ICONS,
    create_card_frame
)

class CashierView(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master, fg_color=THEME_COLORS["background"])
        self.user = user
        self.logout_callback = logout_callback
        self.cart = []
        self.applied_discount = None
        self.init_ui()

    def destroy(self):
        """Clean up bindings before destruction"""
        try:
            self.winfo_toplevel().unbind("<space>")
            self.winfo_toplevel().unbind("<Return>")
        except:
            pass
        super().destroy()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Modern Header with Gradient-like effect
        header = ctk.CTkFrame(self, fg_color=THEME_COLORS["background_light"], corner_radius=0, height=80)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24)
        
        # Left side: User Profile
        user_info = ctk.CTkFrame(header_content, fg_color="transparent")
        user_info.pack(side="left", pady=15)
        
        ctk.CTkLabel(
            user_info, 
            text=f"{ICONS['user']} {self.user['name']}",
            font=(FONTS["primary"], 20, "bold"),
            text_color=THEME_COLORS["text"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            user_info, 
            text=f" • Terminal 01", 
            font=(FONTS["primary"], 14), 
            text_color=THEME_COLORS["text_muted"]
        ).pack(side="left", padx=10, pady=(4, 0))

        # Right side: System Controls
        ctrl_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        ctrl_frame.pack(side="right", pady=15)

        ctk.CTkButton(
            ctrl_frame,
            text=f"{ICONS['report']} Reports",
            width=100, height=40,
            fg_color="transparent",
            hover_color=THEME_COLORS["surface"],
            font=(FONTS["primary"], 14),
            command=lambda: messagebox.showinfo("Info", "Reporting module coming soon!")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            ctrl_frame,
            text=f"{ICONS['logout']} Logout",
            width=120, height=40,
            fg_color=THEME_COLORS["danger"],
            hover_color=THEME_COLORS["danger_hover"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 14, "bold"),
            command=self.logout_callback
        ).pack(side="left")

        # Main Layout
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # LEFT PANEL: Select & Order
        left_area = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_area.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        left_area.grid_rowconfigure(1, weight=1)
        left_area.grid_columnconfigure(0, weight=1)

        # 1. Action Controls (Browse & Quantity)
        controls_card = create_card_frame(left_area, fg_color=THEME_COLORS["background_light"])
        controls_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        controls_box = ctk.CTkFrame(controls_card, fg_color="transparent")
        controls_box.pack(fill="x", padx=15, pady=15)

        # Multiplier field (Add amount of item)
        qty_box = ctk.CTkFrame(controls_box, fg_color="transparent")
        qty_box.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(qty_box, text="Quantity Multiplier", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w")
        self.qty_multiply = ctk.CTkEntry(
            qty_box, width=120, height=45, 
            font=(FONTS["primary"], 18, "bold"), 
            justify="center",
            fg_color=THEME_COLORS["surface"]
        )
        self.qty_multiply.pack(pady=(5, 0))
        self.qty_multiply.insert(0, "1")

        # Action Buttons
        btn_area = ctk.CTkFrame(controls_box, fg_color="transparent")
        btn_area.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(btn_area, text="Product Selection", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w")
        btn_row = ctk.CTkFrame(btn_area, fg_color="transparent")
        btn_row.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(
            btn_row,
            text=f"{ICONS['box']} Browse Inventory",
            font=(FONTS["primary"], 15, "bold"),
            fg_color=THEME_COLORS["gradient_mid"],
            hover_color=THEME_COLORS["gradient_start"],
            height=45,
            command=self.browse_products
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text=f"{ICONS['settings']} Custom Entry",
            font=(FONTS["primary"], 15),
            fg_color=THEME_COLORS["surface"],
            hover_color=THEME_COLORS["surface_light"],
            width=140, height=45,
            command=self.manual_entry
        ).pack(side="left")

        # 2. Shopping Cart Card
        cart_card = create_card_frame(left_area)
        cart_card.grid(row=1, column=0, sticky="nsew")
        
        cart_title_bar = ctk.CTkFrame(cart_card, fg_color=THEME_COLORS["surface"], corner_radius=0)
        cart_title_bar.pack(fill="x")
        
        self.cart_title = ctk.CTkLabel(
            cart_title_bar, 
            text=f"{ICONS['cart']} Current Order (0 Items)", 
            font=(FONTS["primary"], 16, "bold")
        )
        self.cart_title.pack(side="left", padx=20, pady=12)
        
        self.cart_frame = ctk.CTkScrollableFrame(cart_card, fg_color="transparent")
        self.cart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # RIGHT PANEL: Summary & Checkout
        right_area = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_area.grid(row=0, column=1, sticky="nsew")
        
        # 1. Comprehensive Summary Card
        summary_card = create_card_frame(right_area, fg_color=THEME_COLORS["background_light"])
        summary_card.pack(fill="x", pady=(0, 20))
        
        summary_content = ctk.CTkFrame(summary_card, fg_color="transparent")
        summary_content.pack(fill="x", padx=20, pady=20)
        
        # Items Count
        self.count_label = ctk.CTkLabel(summary_content, text="0 Items Selected", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_muted"])
        self.count_label.pack(anchor="w")

        # Subtotal
        sub_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        sub_row.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(sub_row, text="Order Subtotal", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(side="left")
        self.subtotal_label = ctk.CTkLabel(sub_row, text="$0.00", font=(FONTS["primary"], 14, "bold"))
        self.subtotal_label.pack(side="right")

        # Discount Row
        disc_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        disc_row.pack(fill="x", pady=5)
        ctk.CTkLabel(disc_row, text="Coupon Discount", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(side="left")
        self.discount_label = ctk.CTkLabel(disc_row, text="-$0.00", font=(FONTS["primary"], 14, "bold"), text_color=THEME_COLORS["success"])
        self.discount_label.pack(side="right")
        
        ctk.CTkFrame(summary_content, height=2, fg_color=THEME_COLORS["surface"]).pack(fill="x", pady=15)
        
        # Grand Total
        total_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        total_row.pack(fill="x")
        ctk.CTkLabel(total_row, text="PAYABLE", font=(FONTS["primary"], 18, "bold")).pack(side="left")
        self.total_label = ctk.CTkLabel(total_row, text="$0.00", font=(FONTS["primary"], 40, "bold"), text_color=THEME_COLORS["gradient_start"])
        self.total_label.pack(side="right")

        # Paid & Change (Add amount of item logic)
        ctk.CTkFrame(summary_content, height=1, fg_color=THEME_COLORS["surface"]).pack(fill="x", pady=15)
        
        paid_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        paid_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(paid_row, text="Cash Received", font=(FONTS["primary"], 14)).pack(side="left")
        self.paid_entry = ctk.CTkEntry(paid_row, width=120, height=40, font=(FONTS["primary"], 18, "bold"), justify="right", fg_color=THEME_COLORS["background"], border_width=1)
        self.paid_entry.pack(side="right")
        self.paid_entry.bind("<KeyRelease>", lambda e: self.update_change_due())
        self.paid_entry.bind("<FocusIn>", lambda e: self.paid_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.paid_entry.bind("<FocusOut>", lambda e: self.paid_entry.configure(border_color=THEME_COLORS["surface_light"]))
        
        change_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        change_row.pack(fill="x")
        ctk.CTkLabel(change_row, text="Change Due", font=(FONTS["primary"], 14)).pack(side="left")
        self.change_label = ctk.CTkLabel(change_row, text="$0.00", font=(FONTS["primary"], 22, "bold"), text_color=THEME_COLORS["info"])
        self.change_label.pack(side="right")

        # 2. Promo & Actions
        right_actions = ctk.CTkFrame(right_area, fg_color="transparent")
        right_actions.pack(fill="both", expand=True)
        
        promo_card = create_card_frame(right_actions, fg_color=THEME_COLORS["surface"])
        promo_card.pack(fill="x", pady=(0, 20))
        
        promo_box = ctk.CTkFrame(promo_card, fg_color="transparent")
        promo_box.pack(fill="x", padx=15, pady=10)
        
        self.promo_entry = ctk.CTkEntry(promo_box, placeholder_text="Discount Code", font=(FONTS["primary"], 13), height=40, fg_color=THEME_COLORS["background"], border_width=0)
        self.promo_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.promo_entry.bind("<FocusIn>", lambda e: self.promo_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.promo_entry.bind("<FocusOut>", lambda e: self.promo_entry.configure(border_color=THEME_COLORS["surface_light"]))
        
        ctk.CTkButton(promo_box, text="Apply", width=70, height=40, fg_color=THEME_COLORS["info"], font=(FONTS["primary"], 12, "bold"), command=self.handle_discount).pack(side="right")

        # 3. Checkout Buttons
        self.pay_btn = ctk.CTkButton(
            right_actions,
            text=f"{ICONS['money']} COMPLETE PAYMENT\n(Spacebar)",
            height=100,
            font=(FONTS["primary"], 22, "bold"),
            fg_color=THEME_COLORS["success"],
            hover_color=THEME_COLORS["success_hover"],
            corner_radius=RADIUS["lg"],
            command=self.process_payment
        )
        self.pay_btn.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            right_actions,
            text=f"{ICONS['close']} CANCEL",
            height=55,
            font=(FONTS["primary"], 14, "bold"),
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#f87171",
            border_width=2,
            border_color="#991b1b",
            command=self.clear_cart
        ).pack(fill="x")

        self.qty_multiply.focus_set()
        self.qty_multiply.bind("<FocusIn>", lambda e: self.qty_multiply.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.qty_multiply.bind("<FocusOut>", lambda e: self.qty_multiply.configure(border_color=THEME_COLORS["surface_light"]))
        self.after(10, lambda: self.winfo_toplevel().bind("<space>", self.on_payment_shortcut))
        self.after(10, lambda: self.winfo_toplevel().bind("<Return>", self.on_payment_shortcut))

    def update_change_due(self):
        """Calculate and display change based on cash received"""
        try:
            total_text = self.total_label.cget("text").replace("$", "")
            grand_total = float(total_text)
            paid_text = self.paid_entry.get().strip()
            
            if not paid_text:
                self.change_label.configure(text="$0.00", text_color=THEME_COLORS["info"])
                return
                
            paid_amount = float(paid_text)
            change = paid_amount - grand_total
            
            if change < 0:
                self.change_label.configure(text=f"-${abs(change):.2f}", text_color=THEME_COLORS["danger"])
            else:
                self.change_label.configure(text=f"${change:.2f}", text_color=THEME_COLORS["info"])
        except ValueError:
            self.change_label.configure(text="ERR", text_color=THEME_COLORS["danger"])

    def handle_discount(self):
        code = self.promo_entry.get().strip()
        if not code:
            return
            
        discount = get_discount(code)
        
        if not discount:
            messagebox.showerror("Invalid Code", "This promotion code does not exist or is expired.")
            return
            
        subtotal = sum(i['subtotal'] for i in self.cart)
        if subtotal < discount['min_amount']:
            messagebox.showwarning("Minimum Reached", f"This code requires a minimum purchase of ${discount['min_amount']:.2f}")
            return
            
        self.applied_discount = discount
        messagebox.showinfo("Success", f"Discount applied: {discount['code']}")
        self.update_cart_display()

    def browse_products(self):
        """Show a quick inventory browser dialog"""
        dialog = BrowseProductsDialog(self)
        product = dialog.get_result()
        if product:
            self.add_to_cart(product)

    def manual_entry(self):
        """Show manual entry dialog"""
        dialog = ManualEntryDialog(self)
        product = dialog.get_result()
        if product:
            self.add_to_cart(product)

    def on_payment_shortcut(self, event):
        # Trigger payment if cart is not empty and not typing in entry fields
        focused = str(self.focus_get())
        # Check if focus is on any entry
        if self.cart and not any(isinstance(self.focus_get(), ctk.CTkEntry) for _ in [1]):
             # CustomTkinter entries might have internal widgets, let's be more specific
             pass

        # Simpler check using the strings we have
        if self.cart and focused not in [str(self.qty_multiply), str(self.promo_entry), str(self.paid_entry)]:
            self.process_payment()

    def handle_search(self):
        # Entry removed - this is a fallback or for barcode scan bypass if needed
        pass

    def add_to_cart(self, product):
        # Re-fetch product data for accurate stock levels
        if product['id'] > 0:
            latest_product = get_product_by_id(product['id'])
            if latest_product:
                product = latest_product

        # Get multiplier
        try:
            multiplier = int(self.qty_multiply.get().strip() or "1")
            if multiplier <= 0: multiplier = 1
        except:
            multiplier = 1

        if product['stock_quantity'] < multiplier:
            messagebox.showwarning("Stock Alert", f"Insufficient stock for {product['name']}!\nAvailable: {product['stock_quantity']}")
            return

        for item in self.cart:
            # Merge if same product ID (>0) OR if it's a manual entry (ID=0) with same name and price
            is_same_product = (item['id'] == product['id'] and item['id'] > 0)
            is_same_manual = (item['id'] == 0 and product.get('id') == 0 and
                             item['name'] == product['name'] and
                             item['price'] == product['price'])

            if is_same_product or is_same_manual:
                if item['qty'] + multiplier > product['stock_quantity']:
                    messagebox.showwarning("Stock Alert", f"Insufficient stock for {product['name']}!\nAvailable: {product['stock_quantity']}\nIn Cart: {item['qty']}")
                    return
                item['qty'] += multiplier
                item['subtotal'] = item['qty'] * item['price']
                self.update_cart_display()
                self.qty_multiply.delete(0, 'end')
                self.qty_multiply.insert(0, "1")
                return

        self.cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'qty': multiplier,
            'subtotal': product['price'] * multiplier,
            'category': product.get('category', 'General')
        })
        self.update_cart_display()
        self.qty_multiply.delete(0, 'end')
        self.qty_multiply.insert(0, "1")

    def update_cart_display(self, notify_discount_removal=False):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        if not self.cart:
            ctk.CTkLabel(self.cart_frame, text="Select items to begin transaction...", font=(FONTS["primary"], 16), text_color=THEME_COLORS["text_muted"]).pack(pady=60)
            self.subtotal_label.configure(text="$0.00")
            self.discount_label.configure(text="-$0.00")
            self.total_label.configure(text="$0.00")
            self.cart_title.configure(text=f"{ICONS['cart']} Current Order (0 Items)")
            self.count_label.configure(text="0 Items Selected")
            self.applied_discount = None
            self.update_change_due()
            return

        subtotal = 0
        total_items = 0
        for i, item in enumerate(self.cart):
            subtotal += item['subtotal']

        # Re-verify discount eligibility
        if self.applied_discount and subtotal < self.applied_discount['min_amount']:
            self.applied_discount = None
            if notify_discount_removal:
                messagebox.showinfo("Discount Removed", "Cart total no longer meets minimum requirement for the applied discount.")

        subtotal = 0 # reset for loop
        for i, item in enumerate(self.cart):
            total_items += item['qty']
            # Dynamic Cart Item
            card = ctk.CTkFrame(self.cart_frame, fg_color=THEME_COLORS["surface"], corner_radius=RADIUS["sm"])
            card.pack(fill="x", pady=2, padx=5)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)
            
            # Left: Info
            info = ctk.CTkFrame(content, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(info, text=item['name'], font=(FONTS["primary"], 15, "bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"{item['category']} • ${item['price']:.2f}/ea", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"], anchor="w").pack(anchor="w")
            
            # Right: Qty & Price
            pricing = ctk.CTkFrame(content, fg_color="transparent")
            pricing.pack(side="right")
            
            ctk.CTkLabel(pricing, text=f"x{item['qty']}", font=(FONTS["primary"], 14, "bold"), width=40).pack(side="left", padx=10)
            ctk.CTkLabel(pricing, text=f"${item['subtotal']:.2f}", font=(FONTS["primary"], 16, "bold"), text_color=THEME_COLORS["gradient_accent"]).pack(side="left", padx=10)
            
            ctk.CTkButton(
                pricing, text=ICONS['delete'], width=30, height=30, 
                fg_color="transparent", hover_color=THEME_COLORS["danger_hover"], 
                text_color="#9ca3af",
                command=lambda x=i: self.remove_item(x)
            ).pack(side="left")
            
            subtotal += item['subtotal']

        # Update Headers
        self.cart_title.configure(text=f"{ICONS['cart']} Current Order ({total_items} Items)")
        self.count_label.configure(text=f"{total_items} Items Selected")

        # Calculation
        discount_amt = 0
        if self.applied_discount:
            if self.applied_discount['type'] == 'percentage':
                discount_amt = subtotal * (self.applied_discount['value'] / 100)
            else:
                discount_amt = self.applied_discount['value']

        total = max(0, subtotal - discount_amt)
        
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.discount_label.configure(text=f"-${discount_amt:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
        self.update_change_due()

    def remove_item(self, index):
        del self.cart[index]
        if not self.cart: self.applied_discount = None
        self.update_cart_display(notify_discount_removal=True)

    def clear_cart(self):
        if self.cart and messagebox.askyesno("Confirm Void", "Are you sure you want to void this transaction?"):
            self.cart = []
            self.applied_discount = None
            self.promo_entry.delete(0, 'end')
            self.paid_entry.delete(0, 'end')
            self.update_cart_display()

    def process_payment(self):
        if not self.cart:
            return
            
        subtotal = sum(i['subtotal'] for i in self.cart)
        discount_amt = 0
        if self.applied_discount:
            if self.applied_discount['type'] == 'percentage':
                discount_amt = subtotal * (self.applied_discount['value'] / 100)
            else:
                discount_amt = self.applied_discount['value']
        
        total = max(0, subtotal - discount_amt)
        
        # Check if paid amount is sufficient
        try:
            paid = float(self.paid_entry.get().strip() or "0")
            if paid < total:
                messagebox.showwarning("Insufficient Funds", f"Customer needs to pay at least ${total:.2f}")
                self.paid_entry.focus()
                return
        except:
            messagebox.showwarning("Validation Error", "Please enter a valid amount in Cash Received.")
            return

        try:
            tid = create_transaction(self.user['id'], self.cart, subtotal, discount_amt, total)
            
            # Generate receipt
            change_due = paid - total
            receipt_text = PrinterService.generate_receipt_text(
                self.user['name'], self.cart, subtotal, discount_amt, total, paid, change_due
            )
            
            # Save to disk (Audit log)
            PrinterService.print_to_file(receipt_text, tid)
            
            # Show receipt dialog
            InvoiceDialog(self, receipt_text)
            
            # Clear for next customer
            self.cart = []
            self.applied_discount = None
            self.promo_entry.delete(0, 'end')
            self.paid_entry.delete(0, 'end')
            self.update_cart_display()
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save transaction: {e}")

