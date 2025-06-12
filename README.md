# Apartment Rental System

This is a Django-based web application for managing apartment rentals. It includes modules for admin, tenants, and clients, with features such as user authentication, unit management, payment tracking, announcements, and messaging.

## Project Structure
- `manage.py`: Django project management script
- `rental/`: Project settings and configuration
- `core/`: Main application logic (models, views, admin, etc.)
- `static/`: Static files (CSS, JS, images)
- `templates/`: HTML templates for different user roles
- `media/`, `units/`, `receipts/`: File storage directories

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Start the server: `python manage.py runserver`

## License
MIT
