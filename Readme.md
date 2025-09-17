# 🚀 Task Management System  

A **FastAPI-based Task Management System** with secure JWT authentication, PostgreSQL database integration, role-based access (Admin, Manager, Employee), and Alembic-powered database migrations.  

---

## 📌 Table of Contents  

- [✨ Features](#-features)  
- [🛠 Tech Stack](#-tech-stack)  
- [✅ Prerequisites](#-prerequisites)  
- [⚙️ Setup Instructions](#️-setup-instructions)  
- [🔑 Environment Configuration](#-environment-configuration)  
- [🗄️ Database Migrations](#️-database-migrations)  
- [👑 Superadmin Setup](#-superadmin-setup)  
- [🚀 Run the Application](#-run-the-application)  
- [📜 API Documentation](#-api-documentation)  
- [📂 .gitignore](#-gitignore)  
- [🙌 Contributing](#-contributing)  

---

## ✨ Features  

- ✅ **Role-Based Access Control** (Admin, Manager, Employee)  
- 🔑 **JWT Authentication** for secure login and token handling  
- 📋 **Task Management** – create, assign, and track tasks  
- 🗄️ **PostgreSQL Database** with SQLAlchemy ORM  
- 🔄 **Alembic Migrations** for version-controlled schema changes  
- ⚡ **FastAPI Backend** with automatic interactive API documentation  

---

## 🛠 Tech Stack  

- **Backend:** FastAPI (Python)  
- **Database:** PostgreSQL  
- **Authentication:** JWT (JSON Web Tokens)  
- **ORM:** SQLAlchemy  
- **Migrations:** Alembic  
- **Server:** Uvicorn  

---

## ✅ Prerequisites  

Make sure you have:  
- Python **3.8+**  
- PostgreSQL installed & running  
- Git  

---

## ⚙️ Setup Instructions  

1️⃣ **Clone the Repository**  
```bash
git clone https://github.com/sunilkumawat123/task-management-system.git
cd task-management-system


2️⃣ Create & Activate Virtual Environment


python3 -m venv venv
source venv/bin/activate      # macOS / Linux
# OR
venv\Scripts\activate         # Windows
3️⃣ Install Dependencies




pip install --upgrade pip
pip install -r requirements.txt
🔑 Environment Configuration


Create a .env file in the root folder with the following content:

ini
Copy code
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your password
POSTGRES_DB= your database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# JWT
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
⚠ Security Tip: Use a strong, random SECRET_KEY for production and never commit .env to version control.



🗄️ Database Migrations
This project uses Alembic for schema migrations.

1️⃣ Initialize Alembic (only once per project)



alembic init alembic

2️⃣ Create a New Migration

bash
Copy code
alembic revision --autogenerate -m "initial migration"


3️⃣ Apply Migrations


alembic upgrade head

4️⃣ Check Current Migration


alembic current

5️⃣ Downgrade (if needed)


alembic downgrade -1
Tip: Run migrations every time you change your models so your database schema stays in sync.

👑 Superadmin Setup
Before running the server, create the superadmin account:


python create_superadmin.py
If needed, modify create_superadmin.py to update credentials.

Username --> superadmin	 
Password --> admin123
                   

🚀 Run the Application
Start the server with live reload:


uvicorn main:app --reload
Your app will be available at: http://127.0.0.1:8000

📜 API Documentation
Once the app is running, explore the API docs:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

📂 .gitignore
Recommended .gitignore for this project:

gitignore
Copy code
# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environment
venv/
.env

# IDE & Editor
.vscode/
.idea/

# Alembic cache
alembic/__pycache__/

# OS files
.DS_Store
Thumbs.db
🙌 Contributing
Contributions are welcome!

Fork the repository

Create a feature branch (git checkout -b feature/your-feature)

Commit your changes (git commit -m "Add feature")

Push to your branch (git push origin feature/your-feature)

Open a Pull Request 🎉
