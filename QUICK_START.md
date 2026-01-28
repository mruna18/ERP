# Quick Start Guide - ERP Frontend

## ✅ What's Been Done

1. **Backend CORS Configuration** ✅
   - Added `django-cors-headers` package
   - Configured CORS to allow frontend requests
   - Added company header support

2. **React Frontend Created** ✅
   - Complete React + Vite setup
   - Authentication system (Login/Register)
   - JWT token management
   - Protected routes
   - Company selection
   - Dashboard with basic UI

## 🚀 Getting Started

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start Backend Server

```bash
# From project root
python manage.py runserver
```

Backend will run on: `http://127.0.0.1:8000`

### 4. Start Frontend Server

```bash
# From frontend directory
npm run dev
```

Frontend will run on: `http://localhost:3000`

## 📱 Using the Application

1. **Register a New User**
   - Go to http://localhost:3000/register
   - Fill in the registration form
   - Submit to create account

2. **Login**
   - Go to http://localhost:3000/login
   - Use email and password to login
   - You'll be redirected to dashboard

3. **Select Company**
   - On dashboard, select a company
   - Company ID will be stored and sent with API requests

## 🔧 Project Structure

```
ERP/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── contexts/      # React contexts (Auth)
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   └── package.json
├── company/               # Django backend
│   └── settings.py        # CORS configured here
└── requirements.txt       # Includes django-cors-headers
```

## 🎨 Features Implemented

- ✅ User Registration
- ✅ User Login (with email)
- ✅ JWT Token Management
- ✅ Automatic Token Refresh
- ✅ Protected Routes
- ✅ Company Selection
- ✅ API Integration Layer
- ✅ Toast Notifications
- ✅ Responsive Design

## 📝 Next Steps

You can now extend the frontend by:

1. **Adding More Pages:**
   - Invoice management (`/invoice/list`, `/invoice/create`)
   - Item management (`/items/list`, `/items/create`)
   - Party management (`/parties/list`, `/parties/create`)
   - Payment tracking

2. **Creating Service Files:**
   ```javascript
   // Example: src/services/invoiceService.js
   import api from './api'
   
   export const invoiceService = {
     getInvoices: async (companyId) => {
       const response = await api.post('/invoice/list/', { company: companyId })
       return response.data
     }
   }
   ```

3. **Adding Navigation:**
   - Create a sidebar or top navigation
   - Add routing for new pages
   - Implement breadcrumbs

## 🐛 Troubleshooting

**CORS Errors:**
- Ensure `django-cors-headers` is installed
- Check `settings.py` has CORS configuration
- Verify backend is running on port 8000

**Login Issues:**
- Backend expects `email` (not username)
- Check browser console for errors
- Verify tokens are stored in localStorage

**API Connection:**
- Check `.env` file has correct `VITE_API_BASE_URL`
- Verify Django server is running
- Check network tab in browser dev tools

## 📚 Documentation

- See `FRONTEND_SETUP.md` for detailed setup instructions
- See `frontend/README.md` for frontend-specific docs
