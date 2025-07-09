# E-commerce Platform

## Overview
This is a simple e-commerce web app where users can:
- **Register** and **log in** with email/password (JWT authentication).
- **Browse** a catalog of products, view details and stock levels.
- **Add** products to a shopping cart and **place orders** with a shipping address.
- **Moderators** have an additional **Manage Users** panel to **ban** or **unban** other users.

## Key Features
1. **User Registration & Login**  
   - Sign up with username, email and password.  
   - Log in returns a JWT, stored in `localStorage` for authenticated requests.

2. **Product Catalog & Cart**  
   - Fetch product list via REST API.  
   - Add items to cart, view cart contents, and submit orders.

3. **User Management (Moderators Only)**  
   - After logging in as a moderator, a **Manage Users** button appears.  
   - View all registered users and toggle their banned status with a single click.
  
4. **Extra**
   -If you want to test the functioning of the moderator user, use the following credentials:
   email: joe@gmail.com
   password: joe12345

## Getting Started

### 1. Backend (Django)
```bash
git clone <repository-url>
cd ecommerce_project
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
