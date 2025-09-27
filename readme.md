# Lenme - Peer-to-Peer Lending Platform

A Django REST-based peer-to-peer lending platform where borrowers can request loans, lenders can make offers, and the system manages funding and repayments. Includes **Celery** tasks for automated repayment management.

---

## Features

### User Management

* User registration and authentication
* Role-based access (Borrower / Lender)
* User profile endpoint

### Borrower Actions

* Create a loan request
* Accept lender offers
* Pay loan installments
* View all loans and repayment schedules
* View offers for a loan

### Lender Actions

* List open loans
* Make offers on loans
* View own offers

### Automated Tasks

* Celery task to check overdue repayments every hour
* Mark overdue loans and repayments
* Extendable for notifications or late fee calculation

---

## Tech Stack

* Django REST Framework
* Celery + Redis (task queue)
* PostgreSQL (or SQLite for testing)
* Python 3.11+

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/lenme.git
cd lenme
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
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

## Celery Setup

### 1. Install Redis

Make sure Redis is installed and running locally on default port `6379`.

```bash
# Linux
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### 2. Start Celery Worker

```bash
celery -A lending_platform worker --loglevel=info
```
OR  for windows
```celery -A lending_platform worker --loglevel=info --pool=solo -l info```

### 3. Start Celery Beat (Scheduler)

```bash
celery -A lending_platform beat --loglevel=info
```




The task `check_due_repayments` will run **every hour**, checking unpaid or overdue repayments and updating loan statuses.

---

## API Endpoints

### User

| Endpoint     | Method | Description              |
| ------------ | ------ | ------------------------ |
| `/register/` | POST   | Register new user        |
| `/me/`       | GET    | Get current user profile |

### Borrower

| Endpoint                          | Method | Description                |
| --------------------------------- | ------ | -------------------------- |
| `/loans/create/`                  | POST   | Create loan request        |
| `/loans/<loan_id>/offers/`        | GET    | List offers for a loan     |
| `/offers/<offer_id>/accept/`      | POST   | Accept offer               |
| `/repayments/<repayment_id>/pay/` | POST   | Pay an installment         |
| `/loans/`                         | GET    | List borrower loans        |
| `/loans/<loan_id>/repayments/`    | GET    | List repayments for a loan |

### Lender

| Endpoint                  | Method | Description             |
| ------------------------- | ------ | ----------------------- |
| `/loans/open/`            | GET    | List open loans         |
| `/loans/<loan_id>/offer/` | POST   | Make an offer on a loan |
| `/offers/`                | GET    | List lender offers      |

---

## Models Overview

* **User / Profile**: Stores user info and balance
* **Loan**: Borrower loan request, status, interest rate, lender
* **Offer**: Lender offer for a loan
* **Repayment**: Tracks installments, due date, paid status, overdue

---

## Running Tests

```bash
python manage.py test
```

---

## Notes

* Ensure **Celery worker** and **Celery beat** are always running in production.
* Modify `CELERY_BEAT_SCHEDULE` in `settings.py` to change task frequency.
