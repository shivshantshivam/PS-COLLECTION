# AI-Powered E-Commerce Website

A full-stack e-commerce web application built with Flask, MySQL, HTML, CSS, and JavaScript. The project includes complete shopping functionality along with AI-powered customer support and product recommendations.

## 🚀 Live Project

**Live Website:** Add your Render URL here

**GitHub Repository:** Add your GitHub repository URL here

---

## 📌 About The Project

This project is a full-stack e-commerce website developed using Python Flask and MySQL.

It provides a complete online shopping experience where users can browse products, add items to their cart, manage their wishlist, place orders, write reviews, and manage their account.

The application also includes AI-powered features such as an AI chatbot for customer support and a product recommendation system.

---

## ✨ Features

### 🛍️ E-Commerce

- Product listing
- Product details
- Product categories
- Add to cart
- Cart quantity management
- Wishlist
- Product reviews and ratings
- Checkout
- Address management
- Order placement
- Order history
- Order tracking

### 👤 User Authentication

- User registration
- Email OTP verification
- Secure password hashing
- User login and logout
- Forgot password
- Password reset using OTP
- User profile management
- Mobile number support

### 🤖 AI Features

- AI-powered customer support chatbot
- Product recommendation system
- AI-assisted shopping experience

### 🛠️ Admin Panel

- Admin dashboard
- User management
- Product management
- Product editing
- Order management
- Admin order tracking

### 📱 UI & Responsive Design

- Responsive website design
- Desktop and mobile support
- Organized product layout
- Interactive JavaScript components
- Clean and consistent styling

---

## 🧰 Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

### Backend

- Python
- Flask

### Database

- MySQL
- mysql-connector-python

### AI

- Google Gemini API

### Email & Authentication

- Brevo API
- Email OTP verification
- Werkzeug password hashing
- Flask Sessions

### Deployment

- Git
- GitHub
- Render
- Railway

### Development Tools

- Visual Studio Code
- Terminal
- Python Virtual Environment

---

## 🏗️ Project Structure

```text
E-Commerce/
│
├── app.py
├── add_products.py
├── assign_images.py
├── requirements.txt
├── .gitignore
│
├── static/
│   ├── css/
│   │   ├── header.css
│   │   ├── footer.css
│   │   ├── home.css
│   │   ├── product.css
│   │   ├── cart.css
│   │   ├── checkout.css
│   │   ├── account.css
│   │   ├── wishlist.css
│   │   ├── order.css
│   │   ├── recommendations.css
│   │   ├── chatbot.css
│   │   └── ...
│   │
│   ├── j-Script/
│   │   ├── home.js
│   │   ├── product.js
│   │   └── chatbot.js
│   │
│   └── images/
│
└── templates/
    ├── base.html
    ├── home.html
    ├── product.html
    ├── cart.html
    ├── checkout.html
    ├── login.html
    ├── register.html
    ├── verify_otp.html
    ├── forgot_password.html
    ├── reset_password.html
    ├── wishlist.html
    ├── account.html
    ├── order.html
    ├── recommendations.html
    ├── chatbot.html
    └── .....
