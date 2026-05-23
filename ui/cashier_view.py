import customtkinter as ctk
from database import (
    get_product_by_barcode, get_product_by_id, search_products,
    create_transaction, get_discount
)
from tkinter import messagebox
from styles import (
    THEME_COLORS, RADIUS, SPACING, FONTS, ICONS,
    create_card_frame
)
from printer_service import PrinterService
from ui.custom_dialogs import (
    BrowseProductsDialog, ManualEntryDialog, InvoiceDialog
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
            top = self.winfo_toplevel()
            top.unbind("<space>")
            top.unbind("<Return>")
        except:
            pass
        super().destroy()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Modern Header
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

        # 1. Action Controls
        controls_card = create_card_frame(left_area, fg_color=THEME_COLORS["background_light"])
        controls_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        controls_box = ctk.CTkFrame(controls_card, fg_color="transparent")
        controls_box.pack(fill="x", padx=15, pady=15)

        # Barcode Entry
        barcode_box = ctk.CTkFrame(controls_box, fg_color="transparent")
        barcode_box.pack(side="left", padx=(0, 20), fill="x", expand=True)
        ctk.CTkLabel(barcode_box, text="Scan Barcode", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w")
        self.barcode_entry = ctk.CTkEntry(barcode_box, height=45, font=(FONTS["primary"], 16), placeholder_text="Enter Barcode...")
        self.barcode_entry.pack(fill="x", pady=(5, 0))
        self.barcode_entry.bind("<Return>", self.handle_barcode_scan)
        self.barcode_entry.bind("<FocusIn>", lambda e: self.barcode_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.barcode_entry.bind("<FocusOut>", lambda e: self.barcode_entry.configure(border_color=THEME_COLORS["surface_light"]))

        # Multiplier field
        qty_box = ctk.CTkFrame(controls_box, fg_color="transparent")
        qty_box.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(qty_box, text="Qty", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w")
        self.qty_multiply = ctk.CTkEntry(qty_box, width=60, height=45, font=(FONTS["primary"], 18, "bold"), justify="center")
        self.qty_multiply.pack(pady=(5, 0))
        self.qty_multiply.insert(0, "1")
        self.qty_multiply.bind("<FocusIn>", lambda e: self.qty_multiply.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.qty_multiply.bind("<FocusOut>", lambda e: self.qty_multiply.configure(border_color=THEME_COLORS["surface_light"]))

        # Action Buttons
        btn_area = ctk.CTkFrame(controls_box, fg_color="transparent")
        btn_area.pack(side="left")
        ctk.CTkLabel(btn_area, text="Actions", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"]).pack(anchor="w")
        btn_row = ctk.CTkFrame(btn_area, fg_color="transparent")
        btn_row.pack(fill="x", pady=(5, 0))
        ctk.CTkButton(btn_row, text=f"{ICONS['box']}", width=45, height=45, command=self.browse_products).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_row, text=f"{ICONS['settings']}", width=45, height=45, command=self.manual_entry).pack(side="left")

        # 2. Shopping Cart
        cart_card = create_card_frame(left_area)
        cart_card.grid(row=1, column=0, sticky="nsew")
        cart_title_bar = ctk.CTkFrame(cart_card, fg_color=THEME_COLORS["surface"], corner_radius=0)
        cart_title_bar.pack(fill="x")
        self.cart_title = ctk.CTkLabel(cart_title_bar, text=f"{ICONS['cart']} Current Order (0 Items)", font=(FONTS["primary"], 16, "bold"))
        self.cart_title.pack(side="left", padx=20, pady=12)
        self.cart_frame = ctk.CTkScrollableFrame(cart_card, fg_color="transparent")
        self.cart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # RIGHT PANEL: Summary & Checkout
        right_area = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_area.grid(row=0, column=1, sticky="nsew")
        
        summary_card = create_card_frame(right_area, fg_color=THEME_COLORS["background_light"])
        summary_card.pack(fill="x", pady=(0, 20))
        summary_content = ctk.CTkFrame(summary_card, fg_color="transparent")
        summary_content.pack(fill="x", padx=20, pady=20)
        
        self.count_label = ctk.CTkLabel(summary_content, text="0 Items Selected", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_muted"])
        self.count_label.pack(anchor="w")

        sub_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        sub_row.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(sub_row, text="Subtotal", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(side="left")
        self.subtotal_label = ctk.CTkLabel(sub_row, text="$0.00", font=(FONTS["primary"], 14, "bold"))
        self.subtotal_label.pack(side="right")

        disc_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        disc_row.pack(fill="x", pady=5)
        ctk.CTkLabel(disc_row, text="Discount", font=(FONTS["primary"], 14), text_color=THEME_COLORS["text_secondary"]).pack(side="left")
        self.discount_label = ctk.CTkLabel(disc_row, text="-$0.00", font=(FONTS["primary"], 14, "bold"), text_color=THEME_COLORS["success"])
        self.discount_label.pack(side="right")
        
        ctk.CTkFrame(summary_content, height=2, fg_color=THEME_COLORS["surface"]).pack(fill="x", pady=15)
        
        total_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        total_row.pack(fill="x")
        ctk.CTkLabel(total_row, text="PAYABLE", font=(FONTS["primary"], 18, "bold")).pack(side="left")
        self.total_label = ctk.CTkLabel(total_row, text="$0.00", font=(FONTS["primary"], 40, "bold"), text_color=THEME_COLORS["gradient_start"])
        self.total_label.pack(side="right")

        ctk.CTkFrame(summary_content, height=1, fg_color=THEME_COLORS["surface"]).pack(fill="x", pady=15)
        
        paid_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        paid_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(paid_row, text="Cash RCVD", font=(FONTS["primary"], 14)).pack(side="left")
        self.paid_entry = ctk.CTkEntry(paid_row, width=120, height=40, font=(FONTS["primary"], 18, "bold"), justify="right")
        self.paid_entry.pack(side="right")
        self.paid_entry.bind("<KeyRelease>", lambda e: self.update_change_due())
        self.paid_entry.bind("<FocusIn>", lambda e: self.paid_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.paid_entry.bind("<FocusOut>", lambda e: self.paid_entry.configure(border_color=THEME_COLORS["surface_light"]))
        
        change_row = ctk.CTkFrame(summary_content, fg_color="transparent")
        change_row.pack(fill="x")
        ctk.CTkLabel(change_row, text="Change Due", font=(FONTS["primary"], 14)).pack(side="left")
        self.change_label = ctk.CTkLabel(change_row, text="$0.00", font=(FONTS["primary"], 22, "bold"), text_color=THEME_COLORS["info"])
        self.change_label.pack(side="right")

        right_actions = ctk.CTkFrame(right_area, fg_color="transparent")
        right_actions.pack(fill="both", expand=True)
        
        promo_card = create_card_frame(right_actions, fg_color=THEME_COLORS["surface"])
        promo_card.pack(fill="x", pady=(0, 20))
        promo_box = ctk.CTkFrame(promo_card, fg_color="transparent")
        promo_box.pack(fill="x", padx=15, pady=10)
        self.promo_entry = ctk.CTkEntry(promo_box, placeholder_text="Promo Code", height=40)
        self.promo_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.promo_entry.bind("<FocusIn>", lambda e: self.promo_entry.configure(border_color=THEME_COLORS["gradient_accent"]))
        self.promo_entry.bind("<FocusOut>", lambda e: self.promo_entry.configure(border_color=THEME_COLORS["surface_light"]))
        ctk.CTkButton(promo_box, text="Apply", width=70, height=40, fg_color=THEME_COLORS["info"], command=self.handle_discount).pack(side="right")

        self.pay_btn = ctk.CTkButton(right_actions, text=f"{ICONS['money']} COMPLETE PAYMENT\n(Enter/Space)", height=100, font=(FONTS["primary"], 20, "bold"), fg_color=THEME_COLORS["success"], command=self.process_payment)
        self.pay_btn.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(right_actions, text=f"{ICONS['close']} CANCEL", height=55, fg_color="#1e293b", text_color="#f87171", border_width=2, border_color="#991b1b", command=self.clear_cart).pack(fill="x")

        self.barcode_entry.focus_set()
        self.after(100, self.bind_shortcuts)

    def bind_shortcuts(self):
        try:
            top = self.winfo_toplevel()
            top.bind("<space>", self.on_shortcut_press)
            top.bind("<Return>", self.on_shortcut_press)
        except: pass

    def on_shortcut_press(self, event):
        focused = str(self.focus_get())
        # If focused on barcode_entry and Return is pressed, handle_barcode_scan will trigger.
        # We only want to trigger process_payment if NOT focused on specific entries.
        entries = [str(self.barcode_entry), str(self.qty_multiply), str(self.promo_entry), str(self.paid_entry)]

        if event.keysym == "Return":
            if focused == str(self.barcode_entry):
                return # Let handle_barcode_scan handle it
            if focused in entries:
                return

        if self.cart and focused not in entries:
            self.process_payment()

    def handle_barcode_scan(self, event=None):
        barcode = self.barcode_entry.get().strip()
        if not barcode: return

        product = get_product_by_barcode(barcode)
        if product:
            self.add_to_cart(product)
            self.barcode_entry.delete(0, 'end')
        else:
            messagebox.showerror("Not Found", f"Product with barcode {barcode} not found.")
            self.barcode_entry.select_range(0, 'end')

    def update_change_due(self):
        try:
            total = float(self.total_label.cget("text").replace("$", ""))
            paid = float(self.paid_entry.get().strip() or "0")
            change = paid - total
            if change < 0:
                self.change_label.configure(text=f"-${abs(change):.2f}", text_color=THEME_COLORS["danger"])
            else:
                self.change_label.configure(text=f"${change:.2f}", text_color=THEME_COLORS["info"])
        except:
            self.change_label.configure(text="ERR", text_color=THEME_COLORS["danger"])

    def handle_discount(self):
        code = self.promo_entry.get().strip()
        if not code: return
        discount = get_discount(code)
        if not discount:
            messagebox.showerror("Invalid", "Code not found/expired.")
            return
        subtotal = sum(i['subtotal'] for i in self.cart)
        if subtotal < discount['min_amount']:
            messagebox.showwarning("Min Amount", f"Requires ${discount['min_amount']:.2f}")
            return
        self.applied_discount = discount
        messagebox.showinfo("Applied", f"Code {discount['code']} applied!")
        self.update_cart_display()

    def browse_products(self):
        dialog = BrowseProductsDialog(self)
        res = dialog.get_result()
        if res: self.add_to_cart(res)

    def manual_entry(self):
        dialog = ManualEntryDialog(self)
        res = dialog.get_result()
        if res: self.add_to_cart(res)

    def add_to_cart(self, product):
        try:
            multiplier = int(self.qty_multiply.get().strip() or "1")
            if multiplier <= 0: multiplier = 1
        except: multiplier = 1

        # Re-fetch product to get latest stock
        if product['id'] > 0:
            product = get_product_by_id(product['id'])
            if not product: return

        if product['stock_quantity'] < multiplier:
            messagebox.showwarning("Stock Alert", f"Insufficient stock for {product['name']}!")
            return

        for item in self.cart:
            if (item['id'] == product['id'] and item['id'] > 0) or \
               (item['id'] == 0 and product['id'] == 0 and item['name'] == product['name'] and item['price'] == product['price']):
                if item['qty'] + multiplier > product['stock_quantity']:
                    messagebox.showwarning("Stock Alert", "Insufficient stock!")
                    return
                item['qty'] += multiplier
                item['subtotal'] = item['qty'] * item['price']
                self.update_cart_display()
                self.qty_multiply.delete(0, 'end'); self.qty_multiply.insert(0, "1")
                return

        self.cart.append({
            'id': product['id'], 'name': product['name'], 'price': product['price'],
            'qty': multiplier, 'subtotal': product['price'] * multiplier,
            'category': product.get('category', 'General')
        })
        self.update_cart_display()
        self.qty_multiply.delete(0, 'end'); self.qty_multiply.insert(0, "1")

    def update_cart_display(self):
        for w in self.cart_frame.winfo_children(): w.destroy()

        subtotal = sum(i['subtotal'] for i in self.cart)

        # Check discount eligibility
        if self.applied_discount and subtotal < self.applied_discount['min_amount']:
            messagebox.showinfo("Discount Removed", f"Subtotal dropped below ${self.applied_discount['min_amount']:.2f}")
            self.applied_discount = None

        if not self.cart:
            ctk.CTkLabel(self.cart_frame, text="Cart is empty", font=(FONTS["primary"], 16), text_color=THEME_COLORS["text_muted"]).pack(pady=60)
            self.subtotal_label.configure(text="$0.00")
            self.discount_label.configure(text="-$0.00")
            self.total_label.configure(text="$0.00")
            self.cart_title.configure(text=f"{ICONS['cart']} Current Order (0 Items)")
            self.count_label.configure(text="0 Items Selected")
            self.applied_discount = None
            self.update_change_due()
            return

        total_items = 0
        for i, item in enumerate(self.cart):
            total_items += item['qty']
            card = ctk.CTkFrame(self.cart_frame, fg_color=THEME_COLORS["surface"], corner_radius=RADIUS["sm"])
            card.pack(fill="x", pady=2, padx=5)
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)
            info = ctk.CTkFrame(content, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(info, text=item['name'], font=(FONTS["primary"], 15, "bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"{item['category']} • ${item['price']:.2f}/ea", font=(FONTS["primary"], 12), text_color=THEME_COLORS["text_secondary"], anchor="w").pack(anchor="w")
            pricing = ctk.CTkFrame(content, fg_color="transparent")
            pricing.pack(side="right")
            ctk.CTkLabel(pricing, text=f"x{item['qty']}", font=(FONTS["primary"], 14, "bold"), width=40).pack(side="left", padx=10)
            ctk.CTkLabel(pricing, text=f"${item['subtotal']:.2f}", font=(FONTS["primary"], 16, "bold"), text_color=THEME_COLORS["gradient_accent"]).pack(side="left", padx=10)
            ctk.CTkButton(pricing, text=ICONS['delete'], width=30, height=30, fg_color="transparent", hover_color=THEME_COLORS["danger_hover"], text_color="#9ca3af", command=lambda x=i: self.remove_item(x)).pack(side="left")

        self.cart_title.configure(text=f"{ICONS['cart']} Current Order ({total_items} Items)")
        self.count_label.configure(text=f"{total_items} Items Selected")

        discount_amt = 0
        if self.applied_discount:
            if self.applied_discount['type'] == 'percentage': discount_amt = subtotal * (self.applied_discount['value'] / 100)
            else: discount_amt = self.applied_discount['value']

        total = max(0, subtotal - discount_amt)
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.discount_label.configure(text=f"-${discount_amt:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
        self.update_change_due()

    def remove_item(self, index):
        del self.cart[index]
        self.update_cart_display()

    def clear_cart(self):
        if self.cart and messagebox.askyesno("Void Order", "Void this transaction?"):
            self.cart = []; self.applied_discount = None
            self.promo_entry.delete(0, 'end'); self.paid_entry.delete(0, 'end')
            self.update_cart_display()

    def process_payment(self):
        if not self.cart: return
        subtotal = sum(i['subtotal'] for i in self.cart)
        discount_amt = 0
        if self.applied_discount:
            if self.applied_discount['type'] == 'percentage': discount_amt = subtotal * (self.applied_discount['value'] / 100)
            else: discount_amt = self.applied_discount['value']
        total = max(0, subtotal - discount_amt)
        
        try:
            paid = float(self.paid_entry.get().strip() or "0")
            if paid < total:
                messagebox.showwarning("Error", f"Customer needs to pay ${total:.2f}")
                self.paid_entry.focus(); return
        except:
            messagebox.showwarning("Error", "Invalid payment amount")
            return

        try:
            tid = create_transaction(self.user['id'], self.cart, subtotal, discount_amt, total)
            receipt_text = PrinterService.generate_receipt_text(self.user['name'], self.cart, subtotal, discount_amt, total, paid, paid - total)
            PrinterService.print_to_file(receipt_text, tid)
            InvoiceDialog(self, receipt_text)
            self.cart = []; self.applied_discount = None
            self.promo_entry.delete(0, 'end'); self.paid_entry.delete(0, 'end')
            self.barcode_entry.delete(0, 'end')
            self.update_cart_display()
            self.barcode_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Transaction failed: {e}")
