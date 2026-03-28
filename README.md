# Dailykart - E-Commerce Web Application

A Django-based e-commerce web application for browsing and purchasing products online with category-based organization and shopping cart functionality.

## Features

- 🛍️ **Product Catalog** - Browse products organized by categories
- 🛒 **Shopping Cart** - Add and manage products in your cart
- 👤 **User Accounts** - Create accounts and manage user profiles
- 🏷️ **Category Management** - Products organized by categories with descriptions
- 🖼️ **Product Images** - Support for product and category images
- 📝 **Product Details** - Comprehensive product information including price, stock, and description
- 🔍 **Search Functionality** - Find products by categories

## Tech Stack

- **Backend**: Django 5.2.11
- **Database**: SQLite3
- **Frontend**: HTML, CSS, Bootstrap, jQuery
- **Image Processing**: Pillow
- **Python**: 3.x

## Project Structure

```
Dailykart/
├── accounts/              # User authentication and account management
│   ├── models.py         # Custom user model
│   ├── views.py          # Account views
│   └── migrations/
├── category/              # Product categories
│   ├── models.py         # Category model
│   ├── views.py
│   └── migrations/
├── store/                 # Product store
│   ├── models.py         # Product model
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── carts/                 # Shopping cart functionality
│   ├── models.py         # Cart and CartItem models
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── Dailykart/             # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL routing
│   ├── views.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── media/                 # User-uploaded content
├── manage.py             # Django management script
└── env/                  # Python virtual environment
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd E-Commerece
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv env
   
   # Activate virtual environment (Windows)
   env\Scripts\Activate.ps1
   
   # Activate virtual environment (macOS/Linux)
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   If `requirements.txt` doesn't exist, install manually:
   ```bash
   pip install Django==5.2.11
   pip install Pillow
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

## Running the Application

### Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Access Admin Panel

Navigate to `http://127.0.0.1:8000/admin/` and log in with your superuser credentials to manage:
- Products
- Categories
- User accounts
- Shopping cart data

## Usage

### Homepage
- Access the main store at `/`
- View all categories and featured products

### Browse Products
- Navigate to `/store/` to view all products
- Filter products by category
- View product details including price, stock, and description

### Shopping Cart
- Add products to cart from product details page
- Manage cart at `/cart/`
- View item quantities and subtotals

### User Accounts
- Register a new account
- Log in to your account
- Manage profile information

## Database Models

### Product
- `product_name` - Product name
- `slug` - URL-friendly identifier
- `description` - Product description
- `price` - Product price
- `images` - Product image
- `stock` - Available quantity
- `is_available` - Availability status
- `category` - Associated category (Foreign Key)
- `created_date` - Creation timestamp
- `modified_date` - Last modification timestamp

### Category
- `category_name` - Category name
- `slug` - URL-friendly identifier
- `description` - Category description
- `cat_image` - Category image

### Account (Custom User Model)
- `email` - User email (login identifier)
- `user_name` - Username
- `first_name` - First name
- `last_name` - Last name
- `phone_number` - Phone number
- `is_active` - Account status
- `is_admin` - Admin privileges
- `is_staff` - Staff status

### Cart
- `cart_id` - Unique cart identifier
- `date_added` - Creation date

### CartItem
- `product` - Associated product (Foreign Key)
- `cart` - Associated cart (Foreign Key)
- `quantity` - Item quantity
- `is_active` - Item status

## Key URLs

| URL | Purpose |
|-----|---------|
| `/` | Homepage |
| `/store/` | Product store |
| `/cart/` | Shopping cart |
| `/admin/` | Admin panel |

## Configuration

### Static Files
- CSS files located in `static/css/`
- JavaScript files located in `static/js/`
- Images located in `static/images/`

### Media Files
- User-uploaded product images in `media/photos/product/`
- Category images in `media/photos/category/`

### Settings
Main Django settings are in `Dailykart/settings.py`. Key settings:
- `DEBUG = True` (Development mode)
- `ALLOWED_HOSTS` - Add your domain in production
- `INSTALLED_APPS` - Registered Django apps
- `DATABASES` - Database configuration (SQLite)

## Development Notes

### Important Security Notes
⚠️ **These settings should NOT be used in production:**
- `DEBUG = True`
- `SECRET_KEY` - Change this value before deployment
- `ALLOWED_HOSTS = []` - Configure for your domain

### For Production Deployment
1. Set `DEBUG = False`
2. Generate a new `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` with your domain
4. Use a production database (PostgreSQL recommended)
5. Configure proper static file serving
6. Set up HTTPS
7. Use environment variables for sensitive settings

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```bash
python manage.py runserver 8001
```

### Migration Errors
Reset migrations (development only):
```bash
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please check existing documentation or contact the development team.

---

**Last Updated**: March 28, 2026
**Django Version**: 5.2.11
**Python Version**: 3.x
