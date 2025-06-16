# 🏟️ Sports Booking System

A web-based application to streamline the booking of sports facilities (like football grounds, badminton courts, etc.) by students and staff in an institution. Built with Django.

---

## 🚀 Features

* 🔐 User Registration, Login, Logout
* 📅 Facility Browsing & Slot Booking
* ✅ Booking Confirmation with QR Code
* 🗓️ View & Cancel Bookings
* 🧾 Attendance via QR Code Scanner
* 👤 User Profile Management
* 🛠️ Admin Panel for Facility & Booking Control

---

## 🧱 Tech Stack

* **Backend**: Python, Django
* **Frontend**: HTML, CSS, Bootstrap, JS
* **Database**: SQLite (default), can be switched to PostgreSQL
* **Authentication**: Django User Model with Custom Profile
* **QR Scanner**: JavaScript-based scanner for booking attendance

---

## 📂 Project Structure

```bash
sports_booking_system/
├── bookings/               # Booking app (views, models, urls)
├── facilities/             # Sports facility info
├── users/                  # Auth and profiles
├── templates/              # Shared HTML templates
├── static/                 # CSS, JS, and images
├── media/                  # Uploaded files (e.g., profile pics)
├── manage.py
└── booking_system/         # Project settings
```

---

## 📸 QR Code Attendance Scanner

A built-in QR scanner allows sports admins or faculty to verify attendance by scanning the user's booking confirmation QR.

### 🔧 How It Works:

1. Upon successful booking, a QR code is generated with the booking ID.
2. Admin opens the **QR Attendance Scanner** page (secured route).
3. The scanner reads the QR and marks the booking as **attended** in the database.

### 📦 Dependencies:

* [**instascan**](https://github.com/schmich/instascan) or [**html5-qrcode**](https://github.com/mebjas/html5-qrcode) JS library
* Django endpoint to verify and update attendance on scan

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/v1gneshkum4r21/sports_booking_system.git
cd sports_booking_system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Server

```bash
python manage.py runserver
```

---

## 🧠 Future Enhancements

* 📲 Mobile App for booking and scanning
* 📧 Email/Push notifications
* 🔍 Filtering and analytics dashboard
* 📆 Weekly booking limit logic
* ⏰ Real-time slot availability


