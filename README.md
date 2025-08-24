Safe Haven is a **Django-based hall rental application** that allows visitors to:

- Browse available halls with images, descriptions, and pricing
- Check real-time availability for specific dates
- Book halls online
- Pay securely via **PayPal**, **Stripe**, or **Paystack**
- Receive booking confirmation instantly

The system includes a **beautiful, responsive front-end** with modals for hall details, booking, checkout, and success messages.

---

## ✨ Features

- **Hall Management**: Add, edit, and delete halls via Django Admin
- **Availability Checking**: Prevents double-booking for overlapping dates
- **Booking Workflow**: Collects customer details and booking dates
- **Payment Integration**:
  - **PayPal** (Sandbox & Live)
  - **Stripe Checkout** (Test & Live)
  - **Paystack Inline** (Test & Live)
- **Responsive UI**:
  - Dark blue → yellow gradient header
  - Search bar for halls
  - Hero section with full-width background image
  - Card grid for hall listings
  - Stylish, animated modals
- **Security**:
  - CSRF protection
  - Webhook endpoints for payment providers
  - Environment-based configuration

---
## 🛠 Installation

### 1. Clone the repository
```bash
git clone https://github.com/ugtf/safe-haven.git
cd safe-haven
2. Create and activate a virtual environment
bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
3. Install dependencies
bash
pip install -r requirements.txt
