import os
from datetime import datetime

class PrinterService:
    @staticmethod
    def generate_receipt_text(user_name, items, subtotal, discount, total, cash_received, change_due):
        """Generates a formatted text receipt suitable for thermal printers (32/42 chars)"""
        width = 32
        receipt = []
        
        # Header
        receipt.append("=" * width)
        receipt.append("    MODERN POS SYSTEM    ".center(width))
        receipt.append("    123 Business Street    ".center(width))
        receipt.append("    Tel: 555-0199    ".center(width))
        receipt.append("-" * width)
        
        # Details
        receipt.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        receipt.append(f"Cashier: {user_name}")
        receipt.append(f"Terminal: 01")
        receipt.append("-" * width)
        
        # Items Header
        receipt.append("ITEM             QTY    PRICE")
        
        # Items List
        for item in items:
            name = item['name'][:15].ljust(15)
            qty = str(item['qty']).rjust(4)
            price = f"{item['subtotal']:.2f}".rjust(9)
            receipt.append(f"{name}{qty} {price}")
            
        receipt.append("-" * width)
        
        # Totals
        receipt.append(f"Subtotal:       ${subtotal:14.2f}")
        if discount > 0:
            receipt.append(f"Discount:      -${discount:14.2f}")
        receipt.append("-" * width)
        receipt.append(f"TOTAL:          ${total:14.2f}")
        receipt.append(f"Cash RCVD:      ${cash_received:14.2f}")
        receipt.append(f"Change:         ${change_due:14.2f}")
        
        # Footer
        receipt.append("-" * width)
        receipt.append("   THANK YOU FOR YOUR   ".center(width))
        receipt.append("      VISIT TODAY!      ".center(width))
        receipt.append("=" * width)
        receipt.append("\n\n\n\n") # Feed lines
        
        return "\n".join(receipt)

    @staticmethod
    def print_to_file(receipt_text, transaction_id):
        """Simulates printing by saving to a receipts folder"""
        if not os.path.exists("receipts"):
            os.makedirs("receipts")
            
        filename = f"receipts/receipt_{transaction_id}_{datetime.now().strftime('%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(receipt_text)
        return filename
