<p align="center">
  <img src="mobile_app/erp_mobile/assets/logos/splash_logo_white.png" alt="ERP Mobile Logo" width="250">
</p>


# 📱 SheWear E-commerce Website

The **SheWear E-commerce Website** is a **comprehensive e-commerce platform** designed to streamline **business operations and customer interactions**.  
It combines a powerful Flask backend API with an intuitive Flutter mobile application for seamless shopping experiences.

---

## 🖼️ Preview

![Main Interface](backend/app/static/img/banner1.png)

| Mobile App | Backend Dashboard |
|-----------|-------------------|
| ![Mobile](mobile_app/erp_mobile/assets/images/on_boarding_images/sammy-line-shopping.gif) | ![Dashboard](backend/app/static/img/banner2.png) |

---

## 🚀 Features

- 🛒 **E-Commerce Platform**  
  Complete online shopping experience with product catalog and cart functionality.

- 📱 **Cross-Platform Mobile App**  
  Flutter-based mobile application for iOS and Android platforms.

- 🔐 **User Authentication & Authorization**  
  Secure login system with role-based access (Admin, Seller, Courier, Customer).

- 💳 **Payment Integration**  
  Secure payment processing and order management system.

- 📦 **Order Management**  
  Complete order lifecycle from placement to delivery tracking.

- 💬 **Real-time Messaging**  
  Chat system between customers, sellers, and couriers.

- 📊 **Analytics Dashboard**  
  Comprehensive reporting and analytics for business insights.

- 🚚 **Delivery Tracking**  
  Real-time order tracking and courier management.

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
ERP_MOBILE/
├── backend/          # Flask backend API
│   ├── app/         # Application modules
│   ├── migrations/  # Database migrations
│   ├── static/      # CSS, JS, images
│   ├── templates/   # HTML templates
│   ├── config.py    # Configuration settings
│   ├── run.py       # Application entry point
│   └── requirements.txt
└── mobile_app/      # Flutter mobile application
    └── erp_mobile/  # Mobile app source code
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

<p align="center">
  Made with ❤️ for modern e-commerce solutions
</p>
