# ERP Mobile Application

This project contains both the backend API and mobile application for an ERP system.

## Project Structure

```
ERP_MOBILE/
├── backend/          # Flask backend API
│   ├── app/         # Application modules
│   ├── migrations/  # Database migrations
│   ├── config.py    # Configuration settings
│   ├── run.py       # Application entry point
│   └── requirements.txt
└── mobile_app/      # Mobile application
    └── erp_mobile/  # Mobile app source code
```

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   python run.py
   ```

## Mobile App Setup

1. Navigate to the mobile app directory:
   ```bash
   cd mobile_app/erp_mobile
   ```

2. Install dependencies and run the app according to your mobile framework (Flutter, React Native, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here]