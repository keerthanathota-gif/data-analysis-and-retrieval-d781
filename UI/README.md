# CFR Agentic AI - Authentication & UI Module

Complete authentication system with role-based access control for the CFR Agentic AI Application.

## Features

- **JWT-based Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Admin and User roles with different permissions
- **Audit Logging** - Track all authentication events and user actions
- **Secure Password Hashing** - bcrypt password hashing
- **Modern UI** - Clean, responsive web interface
- **RESTful API** - Well-documented API endpoints

## Quick Start

### 1. Install Dependencies

Ensure all required packages are installed:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `fastapi` - Web framework
- `python-jose[cryptography]` - JWT tokens
- `passlib[bcrypt]` - Password hashing
- `sqlalchemy` - Database ORM

### 2. Run Setup Script

Create authentication tables and default admin user:

```bash
cd C:\My_projects\data-analysis-and-retrieval-d781\data-analysis-and-retrieval-d781
python ..\UI\scripts\setup_auth.py
```

This will:
- Create `users` and `audit_logs` tables
- Create default admin user:
  - Username: `admin`
  - Password: `admin123`

### 3. Start the Application

```bash
py run.py
```

### 4. Access the UI

Open your browser to: **http://localhost:8000/ui**

Login with:
- **Username**: `admin`
- **Password**: `admin123`

**IMPORTANT**: Change the admin password immediately after first login!

## Folder Structure

```
UI/
├── README.md                          # This file
├── IMPLEMENTATION_GUIDE.md            # Detailed implementation guide
│
├── backend/                           # Backend authentication
│   ├── __init__.py
│   ├── auth_models.py                 # User & AuditLog models
│   ├── auth_service.py                # JWT & password utilities
│   ├── auth_schemas.py                # Pydantic schemas
│   ├── auth_router.py                 # API endpoints
│   └── integration_instructions.md    # Integration guide
│
├── frontend/                          # Frontend UI
│   ├── login.html                     # Login page
│   ├── dashboard.html                 # User dashboard
│   ├── admin.html                     # Admin panel
│   │
│   ├── js/                            # JavaScript modules
│   │   ├── auth.js                    # Authentication logic
│   │   ├── api.js                     # API wrapper
│   │   ├── dashboard.js               # User dashboard
│   │   └── admin.js                   # Admin panel
│   │
│   └── css/                           # Styling
│       └── styles.css                 # Complete UI styles
│
└── scripts/                           # Utility scripts
    └── setup_auth.py                  # Setup script
```

## User Roles

### Admin
Full access to all system operations:
- Run data pipeline
- Perform clustering
- Run analysis operations
- RAG search
- User management
- View audit logs
- Access all visualizations

### User (Regular)
Read-only access:
- RAG search
- View clustering results
- View analysis reports
- View visualizations
- Browse statistics

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | Login with username/password | No |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/logout` | Logout (logs action) | Yes |
| POST | `/api/auth/register` | Create new user | Admin |
| GET | `/api/auth/users` | List all users | Admin |
| GET | `/api/auth/audit-logs` | View audit logs | Admin |

### Frontend Routes

| Route | Description | Access |
|-------|-------------|--------|
| `/ui` | Login page | Public |
| `/ui/dashboard` | User dashboard | Authenticated users |
| `/ui/admin` | Admin panel | Admins only |

## Security Features

### Password Security
- Passwords hashed using bcrypt
- Minimum password length: 6 characters
- Passwords never stored in plain text

### Token Security
- JWT tokens with 1-hour expiration
- Tokens signed with SECRET_KEY
- Automatic token validation on requests

### Audit Logging
All authentication events are logged:
- Login attempts (success/failure)
- Logout events
- User creation
- All API access

### Role-Based Access
- Endpoints protected by role requirements
- Admin-only operations enforced
- Inactive users cannot authenticate

## Configuration

### Change Secret Key (Production)

Edit `UI/backend/auth_service.py`:

```python
SECRET_KEY = "your-secure-random-key-here"
```

Generate a secure key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Change Token Expiration

Edit `UI/backend/auth_service.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Change to desired minutes
```

### CORS Settings

CORS is configured in `app/main.py`. For production, restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Customization

### Styling

Edit `UI/frontend/css/styles.css` to customize:
- Colors and themes
- Layout and spacing
- Component styles
- Responsive breakpoints

CSS variables for easy theming:
```css
:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --success-color: #10b981;
    --error-color: #ef4444;
    /* ... more variables */
}
```

### API Endpoints

Edit `UI/frontend/js/api.js` to add/modify API calls:

```javascript
const MyAPI = {
    async myCustomEndpoint(param) {
        const response = await fetch(`${API_BASE_URL}/api/my-endpoint`, {
            headers: getAuthHeaders(),
            // ...
        });
        return handleResponse(response);
    }
};
```

### UI Pages

Modify HTML files in `UI/frontend/` to add features:
- `login.html` - Login page layout
- `dashboard.html` - User interface
- `admin.html` - Admin interface

## Troubleshooting

### Issue: "Could not import authentication router"
**Cause**: Python path issue
**Solution**: Ensure you're running from the correct directory:
```bash
cd C:\My_projects\data-analysis-and-retrieval-d781\data-analysis-and-retrieval-d781
python run.py
```

### Issue: "UI not found"
**Cause**: UI files not in correct location
**Solution**: Verify folder structure matches the layout shown above

### Issue: Database errors
**Cause**: Tables not created
**Solution**: Run setup script:
```bash
python ..\UI\scripts\setup_auth.py
```

### Issue: Login fails with valid credentials
**Cause**: Database or token issue
**Solution**:
1. Check if users table has data: `python -c "from app.database import *; from UI.backend.auth_models import *; init_db(); db = next(get_db()); print(db.query(User).all())"`
2. Verify SECRET_KEY hasn't changed
3. Check browser console for errors

### Issue: CORS errors
**Cause**: Frontend/backend origin mismatch
**Solution**: CORS is already enabled for all origins in main.py. Check browser console for specific error.

### Issue: Token expired
**Cause**: Token lifetime exceeded
**Solution**: Login again. Tokens expire after 1 hour by default.

## Development

### Adding New User Roles

1. Edit `UI/backend/auth_models.py`:
```python
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"  # Add new role
```

2. Update role checks in `UI/backend/auth_router.py`

3. Update frontend role handling in `UI/frontend/js/auth.js`

### Adding Protected Endpoints

Use the `get_current_user` dependency:

```python
from UI.backend.auth_router import get_current_user, require_admin

@app.get("/api/my-endpoint")
async def my_endpoint(current_user: User = Depends(get_current_user)):
    # Accessible to all authenticated users
    pass

@app.get("/api/admin-endpoint")
async def admin_endpoint(current_user: User = Depends(require_admin)):
    # Admin only
    pass
```

## Testing

### Manual Testing Checklist

- [ ] Can access login page at /ui
- [ ] Can login with admin credentials
- [ ] Token is stored in localStorage
- [ ] Admin redirects to /ui/admin
- [ ] Regular user redirects to /ui/dashboard
- [ ] Logout clears token and redirects to login
- [ ] Cannot access /ui/admin as regular user
- [ ] Cannot access protected endpoints without token
- [ ] Audit logs record events
- [ ] Can create new users (admin only)
- [ ] New users can login successfully

### API Testing

Use curl or Postman:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=admin123"

# Get current user (use token from login)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Change SECRET_KEY to secure random value
- [ ] Change default admin password
- [ ] Restrict CORS to your domain
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Test all authentication flows
- [ ] Review audit logs
- [ ] Add rate limiting for login endpoint
- [ ] Configure firewall rules
- [ ] Set up SSL certificates

### Environment Variables (Recommended)

Create `.env` file:
```
SECRET_KEY=your-secure-key
DATABASE_URL=your-database-url
API_HOST=0.0.0.0
API_PORT=8000
TOKEN_EXPIRE_MINUTES=60
```

Update auth_service.py to read from environment:
```python
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "default-key-for-dev")
```

## Support

For issues or questions:
1. Check this README
2. Review `IMPLEMENTATION_GUIDE.md`
3. Check `backend/integration_instructions.md`
4. Review browser console for errors
5. Check server logs for backend errors

## License

Part of the CFR Agentic AI Application project.

## Credits

Built with:
- FastAPI
- SQLAlchemy
- python-jose
- passlib
- Vanilla JavaScript
- CSS3
