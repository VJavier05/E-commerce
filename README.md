<p align="center">
  <img src="mobile_app/erp_mobile/assets/logos/splash_logo_black.png" alt="ERP Mobile Logo" width="250">
</p>

# 👗 SheWear - E-commerce Platform

The **SheWear E-commerce Platform** is a **comprehensive fashion marketplace** designed to provide **seamless shopping experiences for women's fashion**.  
It combines a powerful Flask backend API with an intuitive Flutter mobile application for modern fashion retail.

---

## 🖼️ Preview

![Main Interface](backend/app/static/img/banner1.png)

| Mobile App | Backend Dashboard |
|-----------|-------------------|
| ![Mobile](mobile_app/erp_mobile/assets/images/on_boarding_images/sammy-line-shopping.gif) | ![Dashboard](backend/app/static/img/banner2.png) |

---

## 🚀 Features

- 👗 **Fashion E-Commerce Platform**  
  Complete women's fashion shopping experience with curated product collections.

- 📱 **Cross-Platform Mobile App**  
  Flutter-based mobile application for iOS and Android platforms.

- 🔐 **Multi-Role Authentication**  
  Secure login system with role-based access (Admin, Seller, Courier, Customer).

- 💳 **Secure Payment Processing**  
  Integrated payment gateway with multiple payment options.

- 📦 **Smart Order Management**  
  Complete order lifecycle from placement to delivery with status tracking.

- 💬 **Real-time Communication**  
  Chat system between customers, sellers, and delivery partners.

- 📊 **Business Analytics**  
  Comprehensive dashboard for sales insights and performance metrics.

- 🚚 **Delivery Management**  
  Real-time order tracking and courier assignment system.

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|------------|
| Mobile Frontend | Flutter, Dart |
| Backend API | Flask, Python |
| Database | SQLite/PostgreSQL |
| Authentication | JWT Tokens |
| Real-time | WebSocket |
| Architecture | REST API + Mobile Client |

---

## 📁 Project Structure

```
SheWear-E-commerce/
├── backend/          # Flask backend API
│   ├── app/         # Application modules
│   ├── migrations/  # Database migrations
│   ├── static/      # CSS, JS, images
│   ├── templates/   # HTML templates
│   ├── config.py    # Configuration settings
│   ├── run.py       # Application entry point
│   └── requirements.txt
└── mobile_app/      # Flutter mobile application
    └── erp_mobile/  # SheWear mobile app
        ├── lib/     # Dart source files
        ├── assets/  # Images, fonts, icons
        └── pubspec.yaml
```

---

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

### Mobile App Setup

1. **Navigate to mobile app directory:**
   ```bash
   cd mobile_app/erp_mobile
   ```

2. **Install Flutter dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run the mobile app:**
   ```bash
   flutter run
   ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for modern fashion retail
</p>