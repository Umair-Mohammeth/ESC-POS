import customtkinter as ctk
from database import get_transactions, get_daily_sales
import json

class ManagerView(ctk.CTkFrame):
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
        ctk.CTkLabel(header, text="Manager Reports", font=("Segoe UI", 20, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header, text="Refresh", width=100, command=self.load_data).pack(side="right", padx=10)
        ctk.CTkButton(header, text="Logout", width=100, fg_color="#DC3545", command=self.logout_callback).pack(side="right", padx=10)

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("Recent Transactions")
        self.tabview.add("Daily Summary")

        # Scrollable area for transactions
        self.trans_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Recent Transactions"))
        self.trans_scroll.pack(fill="both", expand=True)

        self.summary_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Daily Summary"))
        self.summary_scroll.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self):
        # Transactions
        for w in self.trans_scroll.winfo_children(): w.destroy()
        trans = get_transactions()
        for t in trans:
            card = ctk.CTkFrame(self.trans_scroll)
            card.pack(fill="x", pady=5, padx=5)
            
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=f"Order #{t['id']}", font=("Segoe UI", 14, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(top, text=f"${t['total_amount']:.2f}", text_color="#28A745", font=("Segoe UI", 16, "bold")).pack(side="right", padx=5)
            
            mid = ctk.CTkFrame(card, fg_color="transparent")
            mid.pack(fill="x")
            ctk.CTkLabel(mid, text=f"By {t['cashier_name']} on {t['date']}", font=("Segoe UI", 10)).pack(side="left", padx=5)
            
            try:
                items = json.loads(t['items_json'])
                item_txt = ", ".join([f"{i['name']} (x{i['qty']})" for i in items])
                ctk.CTkLabel(card, text=item_txt, font=("Segoe UI", 10), wraplength=800).pack(fill="x", padx=10, pady=5)
            except: pass

        # Summary
        for w in self.summary_scroll.winfo_children(): w.destroy()
        sales = get_daily_sales()
        for s in sales:
            row = ctk.CTkFrame(self.summary_scroll)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=s['day'], width=300, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"${s['total']:.2f}", font=("Segoe UI", 16), text_color="#28A745").pack(side="right", padx=20)
