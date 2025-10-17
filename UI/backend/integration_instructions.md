# Integration Instructions for Authentication System

## Overview
This document provides instructions for integrating the authentication system with the main FastAPI application.

## Step 1: Update `app/main.py`

Add the following imports near the top of the file (after existing imports):

```python
# Add these imports
from fastapi.responses import RedirectResponse
from UI.backend.auth_router import router as auth_router
```

Add the authentication router to the app (after the existing middleware setup, around line 40):

```python
# Include authentication router
app.include_router(auth_router)
```

## Step 2: Mount Frontend Static Files

Replace or update the existing UI serving section (around line 688-694) with:

```python
# Mount UI frontend files
UI_FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "..", "UI", "frontend")
if os.path.exists(UI_FRONTEND_PATH):
    app.mount("/ui/css", StaticFiles(directory=os.path.join(UI_FRONTEND_PATH, "css")), name="ui_css")
    app.mount("/ui/js", StaticFiles(directory=os.path.join(UI_FRONTEND_PATH, "js")), name="ui_js")

# Serve the login page at /ui
@app.get("/ui")
async def serve_ui():
    """Serve the login page"""
    login_path = os.path.join(UI_FRONTEND_PATH, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"message": "UI not found. Please check UI folder structure."}

# Serve dashboard
@app.get("/ui/dashboard")
async def serve_dashboard():
    """Serve the user dashboard"""
    dashboard_path = os.path.join(UI_FRONTEND_PATH, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return RedirectResponse(url="/ui")

# Serve admin panel
@app.get("/ui/admin")
async def serve_admin():
    """Serve the admin panel"""
    admin_path = os.path.join(UI_FRONTEND_PATH, "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path)
    return RedirectResponse(url="/ui")
```

## Step 3: Update the Root Endpoint

Optionally update the root endpoint to redirect to the UI:

```python
@app.get("/")
async def root():
    # Redirect to UI login page
    return RedirectResponse(url="/ui")
```

## Step 4: Run the Setup Script

Before running the application for the first time, execute the setup script to create authentication tables and the default admin user:

```bash
cd C:\My_projects\data-analysis-and-retrieval-d781
python UI/scripts/setup_auth.py
```

## Step 5: Start the Application

Start the application as normal:

```bash
python run.py
```

Or from the project root:

```bash
python data-analysis-and-retrieval-d781/run.py
```

## Step 6: Access the UI

1. Open your browser to: `http://localhost:8000/ui`
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. **IMPORTANT**: Change the admin password immediately after first login!

## API Endpoints Added

The authentication system adds the following endpoints:

### Public Endpoints
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info (requires auth)
- `POST /api/auth/logout` - Logout (requires auth)

### Admin-Only Endpoints
- `POST /api/auth/register` - Create new user
- `GET /api/auth/users` - List all users
- `GET /api/auth/audit-logs` - View audit logs

## Frontend Routes

- `/ui` - Login page
- `/ui/dashboard` - User dashboard (requires user authentication)
- `/ui/admin` - Admin panel (requires admin authentication)

## Security Notes

1. The default admin password (`admin123`) should be changed immediately
2. The SECRET_KEY in `UI/backend/auth_service.py` should be changed for production
3. JWT tokens expire after 1 hour by default
4. All authentication attempts are logged in the `audit_logs` table
5. CORS is currently set to allow all origins - restrict this in production

## Database Tables

The authentication system creates these tables:

- `users` - Stores user accounts with hashed passwords
- `audit_logs` - Tracks all authentication events

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Ensure the `UI` folder is in the Python path. The auth files already add the parent directory to sys.path.

### Issue: Database errors
**Solution**: Run the setup script first: `python UI/scripts/setup_auth.py`

### Issue: Cannot access UI files
**Solution**: Verify the UI frontend folder structure matches:
```
UI/
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── auth.js
│       ├── api.js
│       ├── dashboard.js
│       └── admin.js
```

### Issue: CORS errors
**Solution**: The main app already has CORS middleware enabled for all origins. If you still get errors, check browser console for specific details.

## Next Steps

After integration:

1. Test login functionality
2. Create additional users via admin panel
3. Test role-based access control
4. Review audit logs
5. Customize styling in `UI/frontend/css/styles.css`
6. Update API endpoints in `UI/frontend/js/api.js` if your backend uses different routes

## Production Checklist

Before deploying to production:

- [ ] Change SECRET_KEY in `UI/backend/auth_service.py`
- [ ] Change default admin password
- [ ] Restrict CORS origins to your domain
- [ ] Enable HTTPS
- [ ] Set up proper database backups
- [ ] Review and test all security controls
- [ ] Set appropriate token expiration times
- [ ] Add rate limiting for login endpoints
- [ ] Configure logging and monitoring
