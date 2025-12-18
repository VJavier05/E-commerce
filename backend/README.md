# ERP Mobile Backend

Flask-based backend for the ERP Mobile application.

## Setup

### 1. Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual configuration values:

- `SECRET_KEY`: Generate a secure secret key for Flask sessions
- `JWT_SECRET_KEY`: Generate a secure JWT secret key
- `MAIL_USERNAME`: Your email address for sending emails
- `MAIL_PASSWORD`: Your email app password (not your regular password)
- `DATABASE_URL`: Your database connection string

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Run the Application

```bash
python run.py
```

## Environment Configuration

The application supports multiple environments:

- **Development**: Default configuration with debug enabled
- **Production**: Optimized for production deployment
- **Testing**: Configuration for running tests

Set the `FLASK_ENV` environment variable to switch between configurations:

```bash
export FLASK_ENV=production  # Linux/Mac
set FLASK_ENV=production     # Windows
```

## Security Notes

- Never commit `.env` files to version control
- Use strong, unique secret keys for production
- Enable HTTPS in production by setting `SESSION_COOKIE_SECURE=True`
- Configure proper CORS origins for production

## Email Configuration

For Gmail, you need to:
1. Enable 2-factor authentication
2. Generate an app password
3. Use the app password in `MAIL_PASSWORD`