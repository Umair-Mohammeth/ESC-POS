import customtkinter as ctk
from database import get_transactions, get_daily_sales
import json
from styles import (
    THEME_COLORS, RADIUS, SPACING, FONTS, ICONS,
    create_card_frame
)

class ManagerView(ctk.CTkFrame):
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
            text=f"{ICONS['report']} Manager Reports",
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
            command=self.load_data
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
        
        self.tabview.add("Recent Transactions")
        self.tabview.add("Daily Summary")

        # Transaction tab
        self.trans_scroll = ctk.CTkScrollableFrame(
            self.tabview.tab("Recent Transactions"),
            fg_color="transparent"
        )
        self.trans_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        # Summary tab
        self.summary_scroll = ctk.CTkScrollableFrame(
            self.tabview.tab("Daily Summary"),
            fg_color="transparent"
        )
        self.summary_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        self.load_data()

    def load_data(self):
        # Load Transactions
        for w in self.trans_scroll.winfo_children():
            w.destroy()
            
        trans = get_transactions()
        
        if not trans:
            ctk.CTkLabel(
                self.trans_scroll,
                text="No transactions yet.",
                font=(FONTS["primary"], 14),
                text_color=THEME_COLORS["text_muted"]
            ).pack(pady=30)
        else:
            for t in trans:
                # Modern transaction card
                card = create_card_frame(
                    self.trans_scroll,
                    fg_color=THEME_COLORS["background_light"],
                    corner_radius=RADIUS["lg"]
                )
                card.pack(fill="x", pady=8, padx=5)
                
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="x", padx=20, pady=15)
                
                # Top row: Order ID and Amount
                top_row = ctk.CTkFrame(content, fg_color="transparent")
                top_row.pack(fill="x")
                
                ctk.CTkLabel(
                    top_row,
                    text=f"{ICONS['money']} Order #{t['id']}",
                    font=(FONTS["primary"], 16, "bold"),
                    text_color=THEME_COLORS["text"]
                ).pack(side="left")
                
                amount_badge = ctk.CTkFrame(
                    top_row,
                    fg_color=THEME_COLORS["success"],
                    corner_radius=RADIUS["sm"]
                )
                amount_badge.pack(side="right")
                
                ctk.CTkLabel(
                    amount_badge,
                    text=f"${t['total_amount']:.2f}",
                    font=(FONTS["primary"], 16, "bold"),
                    text_color=THEME_COLORS["text"]
                ).pack(padx=15, pady=6)
                
                # Middle row: Cashier and Date
                mid_row = ctk.CTkFrame(content, fg_color="transparent")
                mid_row.pack(fill="x", pady=(8, 0))
                
                ctk.CTkLabel(
                    mid_row,
                    text=f"By {t['cashier_name']} • {t['date']}",
                    font=(FONTS["primary"], 13),
                    text_color=THEME_COLORS["text_secondary"]
                ).pack(side="left")
                
                # Items detail
                try:
                    items = json.loads(t['items_json'])
                    item_txt = ", ".join([f"{i['name']} (×{i['qty']})" for i in items])
                    
                    items_label = ctk.CTkLabel(
                        content,
                        text=item_txt,
                        font=(FONTS["primary"], 12),
                        text_color=THEME_COLORS["text_muted"],
                        wraplength=700,
                        anchor="w",
                        justify="left"
                    )
                    items_label.pack(fill="x", pady=(8, 0))
                except:
                    pass

        # Load Daily Summary
        for w in self.summary_scroll.winfo_children():
            w.destroy()
            
        sales = get_daily_sales()
        
        if not sales:
            ctk.CTkLabel(
                self.summary_scroll,
                text="No sales data available.",
                font=(FONTS["primary"], 14),
                text_color=THEME_COLORS["text_muted"]
            ).pack(pady=30)
        else:
            for s in sales:
                # Daily sales card
                card = create_card_frame(
                    self.summary_scroll,
                    fg_color=THEME_COLORS["background_light"],
                    corner_radius=RADIUS["lg"]
                )
                card.pack(fill="x", pady=8, padx=5)
                
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="x", padx=20, pady=15)
                
                ctk.CTkLabel(
                    content,
                    text=f"📅 {s['day']}",
                    font=(FONTS["primary"], 15, "bold"),
                    text_color=THEME_COLORS["text"]
                ).pack(side="left")
                
                ctk.CTkLabel(
                    content,
                    text=f"${s['total']:.2f}",
                    font=(FONTS["primary"], 20, "bold"),
                    text_color=THEME_COLORS["gradient_accent"]
                ).pack(side="right")
