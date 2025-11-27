# FEMS - FAST EATERY MANAGEMENT SYSTEM
FEMS is a Full-Stack Eatery Management Platform designed for university cafeterias. It helps students and teachers preorder food to avoid queues and enables vendors to manage digital orders with live tracking and analytics. Built with Flask (Python) backend and React (TypeScript) frontend.

## Features

### For Vendors
- Register as a vendor and manage your profile
- Create and manage menus with items (name, description, price, prep time)
- View and manage incoming orders
- Update order status (pending → accepted → preparing → ready → completed)
- View vendor statistics and analytics

### For Customers
- Browse all available vendors on campus
- View vendor menus and add items to cart
- Place orders with pickup time
- View order history and track order status
- Cancel orders before they're prepared

## Tech Stack

**Backend:** Flask, PostgreSQL, SQLAlchemy, JWT Authentication  
**Frontend:** React, TypeScript, Tailwind CSS, shadcn/ui

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get current user profile

### Customer Routes
- `GET /api/customer/vendors` - Get all vendors
- `GET /api/customer/vendors/:id/menu` - Get vendor menu
- `POST /api/customer/orders` - Place new order
- `GET /api/customer/orders` - Get customer order history
- `GET /api/customer/orders/:id` - Get order details
- `PUT /api/customer/orders/:id/cancel` - Cancel order
- `GET /api/customer/stats` - Get customer statistics

### Vendor Routes
- `GET /api/vendors/:id` - Get vendor profile & menu
- `PUT /api/vendors/:id` - Update vendor profile
- `POST /api/vendors/:id/menus` - Create menu
- `POST /api/vendors/:id/menus/:menuId/items` - Add menu item
- `PUT /api/vendors/:id/menus/:menuId/items/:itemId` - Update menu item
- `DELETE /api/vendors/:id/menus/:menuId/items/:itemId` - Delete menu item
- `GET /api/vendors/:id/orders` - Get vendor orders
- `PUT /api/vendors/:id/orders/:orderId/status` - Update order status
- `GET /api/vendors/:id/stats` - Get vendor statistics

## Database Schema

### Key Tables
- **users** - User accounts (customers & vendors)
- **vendors** - Vendor profiles and business information
- **menus** - Vendor menus (one per vendor)
- **menu_items** - Items in menus with pricing and availability
- **orders** - Customer orders with status tracking
- **order_items** - Items in each order with quantity
- **email_verifications** - Email verification codes
- **notifications** - User notifications
- **vendor_analytics_events** - Vendor analytics tracking

### Database Views
- **active_menu_items_view** - Active menu items with vendor information
- **customer_order_summary_view** - Customer order statistics
- **vendor_orders_view** - Vendor's orders with customer details
- **vendor_menu_items_stats** - Menu items with sales statistics
- **vendor_revenue_analytics** - Vendor revenue and order analytics

### Stored Functions
- **calculate_order_total()** - Calculate total amount for an order
- **get_customer_order_count()** - Get number of orders for a customer
- **is_item_available()** - Check if menu item is available
- **vendor_owns_menu()** - Verify vendor ownership of menu
- **vendor_owns_item()** - Verify vendor ownership of menu item
- **get_vendor_order_count()** - Get vendor's order count by status

### Stored Procedures
- **place_customer_order()** - Handles order placement with validation and transaction management
- **cancel_customer_order()** - Handles order cancellation with status validation
- **create_vendor_menu()** - Creates a new menu for vendor
- **add_menu_item()** - Adds item to vendor's menu
- **update_menu_item()** - Updates existing menu item
- **delete_menu_item()** - Deletes menu item
- **update_order_status()** - Updates order status with validation
- **get_vendor_orders()** - Retrieves vendor orders with filters


## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL database (or Supabase account)

## Quick Setup

### 1. Clone Repository

```bash
git clone https://github.com/MahamMohsin/FEMS.git
cd FEMS
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `.env` file:**

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://username:password@host:port/database
JWT_EXPIRES_DAYS=7
```

**Get PostgreSQL Database (Supabase - Free):**

1. Go to [supabase.com](https://supabase.com) → New Project
2. Project Settings → Database → Copy "Connection Pooling" string
3. Use as `DATABASE_URL` in `.env`

**Initialize Database:**

1. Run backend to create tables:
```bash
python app.py
```

2. In Supabase SQL Editor, run these SQL files:
   - `backend/sql/customer_routes.sql`
   - `backend/sql/vendor_routes.sql`

**Start Backend:**

```bash
python app.py
```

Backend runs on **http://localhost:5000**

### 3. Frontend Setup

Open new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on **http://localhost:5173**

## Usage

1. **Register** as Customer or Vendor at http://localhost:5173
2. **Vendors:** Add menu items in "Menu" section
3. **Customers:** Browse vendors, add to cart, place orders
4. **Track orders** in real-time

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Get profile

### Customer
- `GET /api/customer/vendors` - List vendors
- `GET /api/customer/vendors/:id/menu` - Get menu
- `POST /api/customer/orders` - Place order
- `GET /api/customer/orders` - Order history

### Vendor
- `POST /api/vendors/:id/menus/:menuId/items` - Add menu item
- `PUT /api/vendors/:id/menus/:menuId/items/:itemId` - Update item
- `GET /api/vendors/:id/orders` - Get orders
- `PUT /api/vendors/:id/orders/:orderId/status` - Update order status

## Troubleshooting

**Port already in use:**

```bash
# macOS/Linux
lsof -ti:5000 | xargs kill  # Backend
lsof -ti:5173 | xargs kill  # Frontend

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**Module not found:**

```bash
pip install psycopg2-binary
```

**API calls failing:**
- Ensure backend is running on port 5000
- Check `DATABASE_URL` in `.env`
- Verify connection in browser: http://localhost:5000/api/auth/profile

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Built with Flask, React, and PostgreSQL | UI by shadcn/ui
