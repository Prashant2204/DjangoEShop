# Django E-Commerce Project

A full-featured e-commerce platform built with Django and Stripe integration.

## Features

- User authentication and authorization
- Product catalog with categories
- Shopping cart functionality
- Secure checkout with Stripe
- Order management
- REST API endpoints
- Responsive design

## Tech Stack

- Django 5.1
- Django REST Framework
- Stripe Payment Integration
- SQLite (Development) / PostgreSQL (Production)
- Bootstrap for frontend

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Prashant2204/DjangoEShop.git
cd DjangoEShop
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

- `/api/products/` - Product listing and management
- `/api/cart/` - Cart operations
- `/api/orders/` - Order management
- `/api/users/` - User management

## Project Structure

```
djangoProject/
├── home/                 # Main app
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # URL routing
│   └── templates/       # HTML templates
├── static/              # Static files
├── media/               # User uploaded files
└── templates/           # Project templates
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.