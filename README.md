# Chodavaram Retail AI – WhatsApp Retail Assistant

An AI-powered WhatsApp assistant built with Django to help customers check product availability and interact with a retail store. The project also includes an owner dashboard for monitoring inventory and viewing customer conversations.

## 🚀 Live Demo

- **Owner Dashboard:** https://chodavaram-retail-bot.onrender.com/owner/
- **Django Admin:** https://chodavaram-retail-bot.onrender.com/admin/

## ✨ Features

- **WhatsApp Integration:** Communicates with customers through the WhatsApp Cloud API.
- **AI-Powered Responses:** Uses Groq AI to help generate responses to customer queries.
- **Product Management:** Stores product details, prices, categories, descriptions, and stock quantities.
- **Inventory Monitoring:** Displays the total number of products in the owner dashboard.
- **Low-Stock Alerts:** Identifies products with stock quantities between 1 and 5.
- **Out-of-Stock Alerts:** Identifies products whose stock quantity is zero.
- **Customer Conversation History:** Allows the owner to view customer leads and chat messages.
- **Database Integration:** Uses PostgreSQL in the deployed environment to store application data.
- **Django Admin:** Provides an interface for managing products and other application records.

## 🛠️ Technologies Used

- Python
- Django
- PostgreSQL
- SQLite (local development fallback when `DATABASE_URL` is not configured)
- WhatsApp Cloud API
- Groq AI API
- HTML and CSS
- Render
- Git and GitHub

## 🏗️ Project Overview

The application receives customer messages through the WhatsApp integration, processes supported queries using the application's AI logic, and sends responses back to customers.

Product information and stock quantities are stored in the database. The owner dashboard displays inventory summaries and customer conversations, helping the store owner monitor stock and review customer interactions.

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/chdeepthisree/chodavaram-retail-bot.git
cd chodavaram-retail-bot
```

### 2. Create and activate a virtual environment

**Windows Command Prompt:**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install dependencies

If a `requirements.txt` file exists in the repository, run:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Configure the environment variables required by your application, such as the Django secret key, database connection URL, Groq API key, and WhatsApp Cloud API credentials.

**Never commit API keys, passwords, or production secrets to GitHub.**

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open the following URLs in your browser:

- Owner dashboard: http://127.0.0.1:8000/owner/
- Django admin: http://127.0.0.1:8000/admin/

## 🔐 Security Notes

- Store API credentials and database connection details in environment variables.
- Keep production secrets out of source control.
- Use secure Django settings when deploying to production.

## 🎯 Project Goal

This project demonstrates the development of a retail assistant that combines AI-powered customer interactions, WhatsApp integration, database-backed product management, and inventory monitoring in a web application.

## 👩‍💻 Author

**Deepthi Sree**

GitHub: [chdeepthisree](https://github.com/chdeepthisree)
