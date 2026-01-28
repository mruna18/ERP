# ERP Frontend

React frontend for the ERP Management System.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Routing
- **Axios** - HTTP client
- **React Toastify** - Notifications

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Environment Variables

Create a `.env` file (or copy from `.env.example`):
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Project Structure

```
src/
  ├── components/     # Reusable components
  ├── contexts/       # React contexts (Auth, etc.)
  ├── pages/          # Page components
  ├── services/       # API services
  └── App.jsx         # Main app component
```

## Features

- ✅ User authentication (Login/Register)
- ✅ JWT token management
- ✅ Protected routes
- ✅ Company selection
- ✅ API integration with Django backend
- ✅ Toast notifications

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.
