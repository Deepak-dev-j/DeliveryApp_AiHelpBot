<!-- Food delivery website with Help & Support chatbot -->

Django REST API + MySQL (or SQLite) + chatbot website.

## 1. Setup (VS Code terminal)
```
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```
Quick start without MySQL: if you don't want mysqlclient yet, run `pip install django djangorestframework`.

## 2. Create database tables + demo orders
```
python manage.py makemigrations support
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser      # for the admin panel (support agents)
```

## 3. Run
```
python manage.py runserver
```
- Website + chatbot: http://127.0.0.1:8000/
- Admin (orders, tickets, chat history): http://127.0.0.1:8000/admin/
- Try order IDs FD1001 to FD1006.

## 4. Use MySQL (optional)
Create the database: `CREATE DATABASE forkful CHARACTER SET utf8mb4;`
Then set environment variables before running:
```
set DB_ENGINE=mysql
set DB_NAME=forkful
set DB_USER=root
set DB_PASSWORD=yourpassword
set DB_HOST=127.0.0.1
```
(Mac/Linux: use `export` instead of `set`.) Run migrate and seed_demo again.

## API
| Method | URL | Purpose |
|---|---|---|
| POST | /api/chat/ | Save customer message, return detected intent |
| GET | /api/order/<order_id>/ | Order details/status |
| POST | /api/cancel-order/ | Cancel request `{order_id, reason}` |
| GET | /api/refund/<order_id>/ | Refund status |
| POST | /api/support-ticket/ | Create ticket (with chat transcript) |
| GET | /api/chat-history/?session_id= | Chat history for agents |

## Structure
```
manage.py
foodsite/     settings.py, urls.py
support/      models.py, views.py, serializers.py, urls.py, admin.py, seed_demo command
frontend/     index.html  (website + chatbot)
```
