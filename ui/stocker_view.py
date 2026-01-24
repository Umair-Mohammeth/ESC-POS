import customtkinter as ctk
from database import get_all_products, update_product_stock
from tkinter import messagebox
from ui.custom_dialogs import AddStockDialog
from styles import (
    THEME_COLORS, RADIUS, SPACING, FONTS, ICONS,
    create_card_frame
)

class StockerView(ctk.CTkFrame):
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
            text=f"{ICONS['box']} Inventory Management",
            font=(FONTS["primary"], 20, "bold"),
            text_color=THEME_COLORS["text"]
        ).pack(side="left")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            width=110,
            height=40,
            fg_color=THEME_COLORS["gradient_mid"],
            hover_color=THEME_COLORS["gradient_start"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 14, "bold"),
            command=self.load_products
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text=f"{ICONS['logout']} Logout",
            width=110,
            height=40,
            fg_color=THEME_COLORS["danger"],
            hover_color=THEME_COLORS["danger_hover"],
            corner_radius=RADIUS["md"],
            font=(FONTS["primary"], 14, "bold"),
            command=self.logout_callback
        ).pack(side="left")

        # Product List Container
        list_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        list_container.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        # Title
        ctk.CTkLabel(
            list_container,
            text="Product Stock Levels",
            font=(FONTS["primary"], 18, "bold"),
            text_color=THEME_COLORS["text"]
        ).pack(anchor="w", padx=5, pady=(0, 10))
        
        # Scrollable product list
        self.scroll_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_products()

    def load_products(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        products = get_all_products()
        
        if not products:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No products in inventory.",
                font=(FONTS["primary"], 14),
                text_color=THEME_COLORS["text_muted"]
            ).pack(pady=30)
            return

        for p in products:
            # Modern product card
            card = create_card_frame(
                self.scroll_frame,
                fg_color=THEME_COLORS["background_light"],
                corner_radius=RADIUS["lg"]
            )
            card.pack(fill="x", pady=8, padx=5)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=20, pady=15)
            
            # Top row: Product info
            top_row = ctk.CTkFrame(content, fg_color="transparent")
            top_row.pack(fill="x")
            
            # Left: Product name and barcode
            info_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                info_frame,
                text=f"{ICONS['product']} {p['name']}",
                font=(FONTS["primary"], 16, "bold"),
                text_color=THEME_COLORS["text"],
                anchor="w"
            ).pack(anchor="w")
            
            if p['barcode']:
                ctk.CTkLabel(
                    info_frame,
                    text=f"Barcode: {p['barcode']}",
                    font=(FONTS["primary"], 12),
                    text_color=THEME_COLORS["text_secondary"],
                    anchor="w"
                ).pack(anchor="w", pady=(3, 0))
            
            # Right: Add Stock button
            ctk.CTkButton(
                top_row,
                text=f"{ICONS['add']} Add Stock",
                width=130,
                height=40,
                fg_color=THEME_COLORS["success"],
                hover_color=THEME_COLORS["success_hover"],
                corner_radius=RADIUS["md"],
                font=(FONTS["primary"], 14, "bold"),
                command=lambda pid=p['id'], name=p['name']: self.add_stock(pid, name)
            ).pack(side="right")
            
            # Bottom row: Stock status
            bottom_row = ctk.CTkFrame(content, fg_color="transparent")
            bottom_row.pack(fill="x", pady=(12, 0))
            
            stock = p['stock_quantity']
            
            # Determine status and color
            if stock > 20:
                status, color = "In Stock", THEME_COLORS["success"]
            elif stock > 5:
                status, color = "Low Stock", THEME_COLORS["warning"]
            elif stock > 0:
                status, color = "Critical", THEME_COLORS["danger"]
            else:
                status, color = "Out of Stock", THEME_COLORS["text_muted"]
            
            # Stock badge
            stock_badge = ctk.CTkFrame(
                bottom_row,
                fg_color=color,
                corner_radius=RADIUS["md"]
            )
            stock_badge.pack(side="left")
            
            ctk.CTkLabel(
                stock_badge,
                text=f"{stock} units in stock",
                font=(FONTS["primary"], 14, "bold"),
                text_color=THEME_COLORS["text"]
            ).pack(padx=15, pady=8)
            
            # Status label
            ctk.CTkLabel(
                bottom_row,
                text=f"• {status}",
                font=(FONTS["primary"], 14, "bold"),
                text_color=color
            ).pack(side="left", padx=(10, 0))

    def add_stock(self, pid, name):
        """Show modern add stock dialog"""
        dialog = AddStockDialog(self, pid, name)
        qty = dialog.get_result()
        
        if qty:
            update_product_stock(pid, qty)
            messagebox.showinfo("Success", f"Added {qty} units to {name}!")
            self.load_products()
