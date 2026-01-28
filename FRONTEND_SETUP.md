# Frontend Setup Guide

## ✅ Backend Configuration Complete

The Django backend has been configured with CORS support to allow frontend requests.

### Backend Changes Made:
1. ✅ Added `django-cors-headers` to `requirements.txt`
2. ✅ Configured CORS in `settings.py` to allow requests from `localhost:3000` and `localhost:5173`
3. ✅ Added CORS middleware to handle cross-origin requests

## 🚀 Frontend Setup Instructions

### Step 1: Install Backend Dependencies

First, install the new CORS package:

```bash
pip install -r requirements.txt
```

### Step 2: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 3: Install Frontend Dependencies

```bash
npm install
```

### Step 4: Start Development Servers

You'll need to run both the Django backend and React frontend:

**Terminal 1 - Django Backend:**
```bash
# From project root
python manage.py runserver
```

**Terminal 2 - React Frontend:**
```bash
# From frontend directory
npm run dev
```

### Step 5: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000

## 📁 Frontend Structure

```
frontend/
├── src/
│   ├── components/        # Reusable components
│   │   └── ProtectedRoute.jsx
│   ├── contexts/          # React contexts
│   │   └── AuthContext.jsx
│   ├── pages/             # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Dashboard.jsx
│   ├── services/          # API services
│   │   ├── api.js         # Axios instance with interceptors
│   │   └── authService.js # Authentication API calls
│   ├── App.jsx            # Main app component
│   └── main.jsx           # Entry point
├── package.json
├── vite.config.js
└── .env
```

## 🔑 Key Features Implemented

1. **Authentication System**
   - Login/Register pages
   - JWT token management
   - Automatic token refresh
   - Protected routes

2. **API Integration**
   - Axios instance with interceptors
   - Automatic token injection
   - Company ID header management
   - Error handling

3. **User Context**
   - Global authentication state
   - Company selection
   - User information management

4. **UI Components**
   - Modern, responsive design
   - Toast notifications
   - Loading states

## 🔧 Next Steps

To extend the frontend, you can:

1. **Add More Pages:**
   - Create invoice management pages
   - Add item/product management
   - Build party management interface
   - Create payment tracking pages

2. **Enhance Dashboard:**
   - Add navigation menu
   - Show company statistics
   - Quick action buttons

3. **Add More Services:**
   - Create `invoiceService.js` for invoice operations
   - Create `itemService.js` for inventory management
   - Create `partyService.js` for party management

## 📝 API Integration Example

Here's how to add a new service:

```javascript
// src/services/invoiceService.js
import api from './api'

export const invoiceService = {
  getInvoices: async (companyId) => {
    const response = await api.post('/invoice/list/', { company: companyId })
    return response.data
  },
  
  createInvoice: async (invoiceData) => {
    const response = await api.post('/invoice/create/', invoiceData)
    return response.data
  },
}
```

## 🐛 Troubleshooting

### CORS Errors
- Make sure `django-cors-headers` is installed
- Verify CORS settings in `settings.py`
- Check that backend is running on port 8000

### Authentication Issues
- Verify JWT tokens are being stored in localStorage
- Check browser console for API errors
- Ensure backend token endpoint is working

### API Connection Issues
- Verify `VITE_API_BASE_URL` in `.env` file
- Check that Django server is running
- Review network tab in browser dev tools

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [Axios Documentation](https://axios-http.com/)
