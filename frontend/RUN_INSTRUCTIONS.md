# How to Run the Frontend

## Step-by-Step Instructions

### 1. Install Dependencies (First Time Only)

Open a terminal/command prompt and navigate to the frontend directory:

```bash
cd d:\mrunali\ERP\ERP\frontend
```

Then install all required packages:

```bash
npm install
```

This will install React, Vite, and all other dependencies listed in `package.json`.

### 2. Start the Development Server

After dependencies are installed, run:

```bash
npm run dev
```

The frontend will start on **http://localhost:3000**

### 3. Access the Application

Open your browser and go to:
- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8002 (make sure Django server is running)

## Quick Commands

```bash
# Navigate to frontend directory
cd d:\mrunali\ERP\ERP\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

## Troubleshooting

### If npm install fails:
- Make sure Node.js is installed (check with `node --version`)
- Try clearing npm cache: `npm cache clean --force`
- Try using yarn instead: `yarn install`

### If port 3000 is already in use:
- The server will automatically try the next available port
- Or change the port in `vite.config.js`

### If you see CORS errors:
- Make sure the Django backend is running on port 8002
- Check that CORS is configured in `company/settings.py`

## Other Useful Commands

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```
