# How to Run the Backend

## Step-by-Step Instructions

### 1. Create Virtual Environment (First Time Only)

Open a terminal/command prompt and navigate to the project root:

```bash
cd d:\mrunali\ERP\ERP
```

Create a virtual environment:

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**Linux/MacOS:**
```bash
python -m venv env
source env/bin/activate
```

### 2. Install Dependencies (First Time Only)

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install Django, Django REST Framework, JWT authentication, CORS headers, and all other dependencies.

### 3. Run Database Migrations (First Time Only)

Set up the database schema:

```bash
python manage.py migrate
```

This creates the SQLite database (`db.sqlite3`) and applies all migrations.

### 4. Start the Development Server

Run the Django development server:

```bash
python manage.py runserver 8002
```

The backend will start on **http://127.0.0.1:8002**

**Note:** The frontend is configured to connect to port 8002. If you use a different port, update the frontend configuration.

### 5. Access the Application

- **Backend API:** http://127.0.0.1:8002
- **Django Admin:** http://127.0.0.1:8002/admin (if admin is configured)
- **API Endpoints:** http://127.0.0.1:8002/api/...

## Quick Commands

```bash
# Navigate to project root
cd d:\mrunali\ERP\ERP

# Activate virtual environment (Windows)
env\Scripts\activate

# Activate virtual environment (Linux/MacOS)
source env/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run migrations (first time only)
python manage.py migrate

# Start development server
python manage.py runserver 8002
```

## Troubleshooting

### If pip install fails:
- Make sure Python is installed (check with `python --version` or `python3 --version`)
- Make sure you're in the virtual environment (you should see `(env)` in your terminal prompt)
- Try upgrading pip: `python -m pip install --upgrade pip`

### If port 8002 is already in use:
- Find and stop the process using port 8002
- Or use a different port: `python manage.py runserver 8003` (then update frontend config)

### If migrations fail:
- Make sure the database file (`db.sqlite3`) is not locked by another process
- Try deleting `db.sqlite3` and running migrations again (⚠️ This will delete all data)

### If you see import errors:
- Make sure the virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### If you see CORS errors from frontend:
- Make sure the backend is running on port 8002
- Check that `django-cors-headers` is installed and configured in `company/settings.py`
- Verify CORS_ALLOWED_ORIGINS includes the frontend URL

## Other Useful Commands

```bash
# Create a superuser (for Django admin)
python manage.py createsuperuser

# Make migrations (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run Django shell
python manage.py shell

# Check for issues
python manage.py check

# Collect static files (for production)
python manage.py collectstatic
```

## Database

The project uses **SQLite** by default. The database file is `db.sqlite3` in the project root.

- No additional database setup required
- Database is created automatically on first migration
- Can be easily switched to PostgreSQL, MySQL, etc. by updating `company/settings.py`

## API Authentication

The backend uses **JWT (JSON Web Tokens)** for authentication:

- Access tokens expire after 12 hours
- Refresh tokens expire after 7 days
- Include token in requests: `Authorization: Bearer <token>`
- Include company ID in requests: `Company: <company_id>` header

## Project Structure

```
ERP/
├── company/           # Django project settings
│   ├── settings.py    # Main configuration (CORS, JWT, etc.)
│   ├── urls.py        # URL routing
│   └── wsgi.py        # WSGI configuration
├── companies/         # Company management app
├── customer/          # Customer/User management app
├── items/             # Product/Item management app
├── invoice/           # Invoice management app
├── parties/           # Party management app
├── payments/          # Payment management app
├── staff/             # Staff management app
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── db.sqlite3         # SQLite database (created after migrations)
```
