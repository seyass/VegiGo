# VegiGo

VegiGo is a comprehensive e-commerce platform built using Python, Django, PostgreSQL, and template engines. It provides a robust set of features to manage products, orders, users, and more.

## Features

### Admin
- Manage products, categories, and inventory.
- View and process orders.
- Manage users and their permissions.
- Handle coupons, offers, and discounts.
- Review return requests and manage returns.

### User
- User registration and authentication.
- Profile management.
- View and browse products.
- Add products to the cart and proceed to checkout.
- Apply coupons and avail offers.
- Track orders and request returns.

### Cart
- Add, update, and remove products in the cart.
- View cart summary with applied discounts and total price.
- Proceed to checkout with a secure payment gateway.

### Wallet and Online Payment Gateway
- Users can add money to their wallet.
- Wallet balance can be used for seamless payments.
- Secure online payment gateway integration for credit/debit cards and other payment methods.

### Coupon and Offer Management
- Create and manage coupons and promotional offers.
- Apply coupons at checkout to avail discounts.

### Order Management
- View order history and details.
- Track order status from processing to delivery.
- Request returns and refunds.

### Return Management
- Admin can review return requests.
- Manage the return process and refunds.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/sreyasnamboothiris/python-django-ecommerce.git
    cd vegigo
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv env
    source env/bin/activate   # On Windows, use `env\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the PostgreSQL database and update the database settings in `settings.py`:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'your_db_name',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

5. Apply migrations:
    ```sh
    python manage.py migrate
    ```

6. Create a superuser to access the Django admin:
    ```sh
    python manage.py createsuperuser
    ```

7. Collect static files:
    ```sh
    python manage.py collectstatic
    ```

8. Run the development server:
    ```sh
    python manage.py runserver
    ```

## Usage

1. Access the admin panel at `http://127.0.0.1:8000/vgadmin/` and log in with the superuser credentials.
2. Add products, categories, coupons, and manage users through the admin interface.
3. Visit `http://127.0.0.1:8000/` to explore the user-facing e-commerce platform.

## Contributing

Contributions are welcome! Please create a pull request with your changes.


## Acknowledgements

- Django: https://www.djangoproject.com/
- PostgreSQL: https://www.postgresql.org/

