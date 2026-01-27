# 🚀 ESC-POS Modern POS System

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A state-of-the-art **Point of Sale (POS) System** built with Python and CustomTkinter. Experience a premium, glassmorphic UI designed for speed, efficiency, and aesthetics. Perfect for retail businesses looking for a modern checkout experience.

---

## ✨ Key Features

### 💎 Premium Modern UI
- **Gradients & Glassmorphism**: A sleek, high-end interface using a curated HSL color palette.
- **Micro-animations**: Smooth transitions and interactive elements for a superior user experience.
- **Responsive Layout**: Optimized for various screen sizes and terminal setups.

### 🛡️ Multi-Role Authentication
Secure access with PIN-based login for different staff levels:
- **Admin**: Full system control, user management, and detailed logs.
- **Manager**: Inventory control, sales reports, and discount management.
- **Cashier**: Streamlined checkout process and receipt generation.
- **Stocker**: Inventory tracking and stock updates.

### 📦 Dynamic Inventory Management
- **Barcode Integration**: Quick product lookups and additions.
- **Stock Tracking**: Real-time inventory updates with low-stock alerts.
- **Category Organization**: Easily group and find products.

### 💰 Smart Transaction & Checkout
- **Flexible Discounts**: Apply fixed amounts or percentage-based promo codes.
- **Cart Management**: Real-time subtotal calculation and item removal.
- **Change Calculation**: Automated math for cash payments.

### 🖨️ Thermal Receipt Generation
- **ESC/POS Optimized**: Generates formatted receipts ready for standard thermal printers.
- **Digital Records**: Automatically saves a text-based backup of every transaction.

---

## 🎨 Design System

Our system is built on a custom design framework defined in `styles.py`:
- **Primary Colors**: Vibrant Purple (`#8B5CF6`) to Bright Blue (`#3B82F6`) gradients.
- **Typography**: Clean, modern fonts (Segoe UI, Inter).
- **Visual Depth**: Utilizes a tiered shadow system and glassmorphic surfaces.

---

## 🛠️ Tech Stack

- **Frontend**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modernized Tkinter).
- **Backend**: Python 3.
- **Database**: SQLite3 (Lightweight, robust, and serverless).
- **Service**: Dedicated `PrinterService` for receipt logic.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Umair-Mohammeth/ESC-POS.git
   cd ESC-POS
   ```

2. **Install dependencies**:
   ```bash
   pip install customtkinter sqlite3
   ```
   *(Note: sqlite3 is included with most Python distributions)*

3. **Run the Application**:
   Simply run the batch file or the main script:
   ```bash
   python main.py
   ```

### Default Credentials
| Role | Username | PIN |
| :--- | :--- | :--- |
| Admin | `admin` | `1111` |
| Manager | `manager` | `2222` |
| Cashier | `cashier` | `3333` |
| Stocker | `stocker` | `4444` |

---

## 📁 Project Structure

```text
ESC-POS/
├── main.py              # Application entry point
├── database.py          # Database schema and migrations
├── printer_service.py   # Receipt generation and printing
├── styles.py            # Modern UI design system
├── ui/                  # UI View components
│   ├── login_view.py    # Staff authentication
│   ├── cashier_view.py  # Checkout interface
│   └── admin_view.py    # System administration
└── receipts/            # Generated transaction records
```

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---
*Built with ❤️ for modern businesses.*
