# ERP Management System (Backend)

A lightweight **ERP System** built with **Django REST Framework** and **SQLite**, designed to manage essential enterprise operations such as **multi-company management**, **invoicing**, and **financial tracking**.

---

## 📌 Features
- 🔐 **User Authentication & Role-Based Access**
- 🏢 **Multi-Company Support**
- 💰 **Invoicing with Tax & Discount Handling**
- 📦 **Stock Validation & Product Management**
- 📊 **Financial Dashboard with Cash/Bank Tracking**
- 🗄 **SQLite Database** (Easily switchable to PostgreSQL, MySQL, etc.)
---

## 🛠 Tech Stack
- **Backend:** Django
- **Database:** SQLite (can be replaced with PostgreSQL, MySQL, etc.)
- **API Framework:** Django REST Framework
- **Language:** Python

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
    git clone https://github.com/mruna18/ERP.git
    cd ERP
```
### 2️⃣ Create a Virtual Environment
```
  python -m venv env
```
 Windows
```
env\Scripts\activate
```
 Linux and MacOS
```
source env/bin/activate
```

### 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Run Migrations
```
python manage.py migrate
```
### 5️⃣ Start Development Server
```
python manage.py runserver
```

### Architecture Overview

Below is a high-level flow of how the ERP backend handles requests using Django REST Framework:

1. Client sends request (e.g., via Postman or frontend)
2. URL Routing → View/ViewSet
3. View handles logic → Serializer validation
4. Serializer interacts with Models → SQLite
5. Serialized response (JSON) returns to client


## 📌 Future Enhancements

- 📊 Dashboard with analytics
- 🌐 Frontend integration (React/Vue)
- 📧 Email notifications for leave requests
- 🔄 Multi-database support



