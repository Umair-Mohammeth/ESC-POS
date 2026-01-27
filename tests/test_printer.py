import unittest
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from printer_service import PrinterService

class TestPrinter(unittest.TestCase):
    def test_generate_receipt_text(self):
        items = [{
            'id': 1,
            'name': 'Apple',
            'price': 1.50,
            'qty': 2,
            'subtotal': 3.00
        }]
        receipt = PrinterService.generate_receipt_text(
            "Test Cashier", items, 3.00, 0, 3.00, 5.00, 2.00
        )

        self.assertIn("Apple", receipt)
        self.assertIn("1.50", receipt)
        self.assertIn("3.00", receipt)
        self.assertIn("Test Cashier", receipt)

        # Check header
        self.assertIn("ITEM         QTY  PRICE    TOTAL", receipt)

        # Check item line format (12 + 4 + 7 + 9 = 32)
        # "Apple       " (12) + "   2" (4) + "   1.50" (7) + "     3.00" (9)
        expected_line = "Apple          2   1.50     3.00"
        self.assertIn(expected_line, receipt)

if __name__ == '__main__':
    unittest.main()
