# Signup and Login Guide

## 📝 User Registration and Authentication

### How Signup Works

1. **Navigate to Signup:**
   - Go to `http://localhost:3000/login`
   - Click "Start your free trial" link
   - Or directly visit `http://localhost:3000/signup`

2. **Fill Signup Form:**
   - **Email:** Enter your email address
   - **Username:** Choose a unique username
   - **Password:** Create a strong password
   - **Confirm Password:** Re-enter your password

3. **Submit:**
   - Click "Create Account" button
   - System validates your information
   - Account is created in the database

4. **Success:**
   - Green success message appears
   - "Account created successfully! You can now login with username: [your-username]"
   - Form automatically switches to login after 3 seconds
   - Your username is pre-filled for easy login

5. **Login:**
   - Enter your password
   - Click "Sign in to Dashboard"
   - Redirected to the unified dashboard

---

## 🔐 Password Requirements

For security, passwords must meet these requirements:

- **Minimum length:** 8 characters
- **Complexity:** Mix of letters, numbers, and special characters recommended
- **No common words:** Avoid dictionary words
- **Unique:** Don't reuse passwords from other sites

If password doesn't meet requirements, you'll see an error message explaining what's needed.

---

## 👤 User Account Details

### What Gets Stored:

When you signup, the system stores:
- **Username:** Your chosen username (must be unique)
- **Email:** Your email address (must be unique)
- **Password:** Securely hashed using bcrypt (never stored in plain text)
- **Role:** Automatically set to "user" (full dashboard access)
- **Status:** Active by default
- **Created Date:** Timestamp of account creation

### Database:
- Stored in: `backend/auth.db`
- Table: `users`
- Encryption: bcrypt password hashing
- Security: JWT token-based authentication

---

## 🚀 Complete Signup to Login Flow

### Step-by-Step Example:

```
1. Open Browser
   └─→ http://localhost:3000

2. Click "Start your free trial"
   └─→ Signup form appears

3. Enter Details:
   ├─→ Email: john@example.com
   ├─→ Username: john_doe
   ├─→ Password: SecurePass123!
   └─→ Confirm Password: SecurePass123!

4. Click "Create Account"
   └─→ ✅ Success message appears
   └─→ Form switches to login mode (3 seconds)

5. Login Automatically Pre-filled:
   ├─→ Username: john_doe (already filled)
   └─→ Password: [enter your password]

6. Click "Sign in to Dashboard"
   └─→ Redirected to dashboard
   └─→ See all 5 tabs: Search, Pipeline, Analysis, Users, Activity
```

---

## 🎯 Quick Test

### Create a Test Account:

1. **Signup:**
   ```
   Email: test@example.com
   Username: testuser
   Password: TestPass123!
   Confirm: TestPass123!
   ```

2. **Wait for Success Message:**
   - Green alert appears
   - Shows "Account created successfully!"

3. **Login:**
   ```
   Username: testuser
   Password: TestPass123!
   ```

4. **Access Dashboard:**
   - See unified dashboard
   - All features available

---

## 📊 Verify Your Account

### Check if Account Was Created:

**Method 1: Try Logging In**
- Go to login page
- Enter your username and password
- If successful, account exists!

**Method 2: Database Check (Admin)**
```bash
cd backend
python3 -c "
from app.models.auth_database import get_auth_db, User
db = next(get_auth_db())
users = db.query(User).all()
for u in users:
    print(f'Username: {u.username}, Email: {u.email}')
"
```

**Method 3: Activity Logs**
- Login as any user
- Go to "Activity" tab
- Look for "signup" action in logs

---

## ⚠️ Common Signup Issues

### Issue: "Username already registered"
**Cause:** Someone already used that username  
**Solution:** Choose a different username

### Issue: "Email already registered"
**Cause:** That email is already in the system  
**Solution:** Use a different email or login with existing account

### Issue: "Passwords do not match"
**Cause:** Password and Confirm Password fields don't match  
**Solution:** Make sure both password fields are identical

### Issue: "Password does not meet requirements"
**Cause:** Password is too weak  
**Solution:** Use at least 8 characters with mix of letters, numbers, symbols

### Issue: Signup succeeds but can't login
**Cause:** Rare - possible database issue  
**Solution:** 
1. Check backend logs
2. Verify database exists: `ls backend/auth.db`
3. Restart backend server

---

## 🔄 Existing Users

### Default Admin Account:
```
Username: admin
Password: admin123
Email: admin@cpsc.gov
```

This account is created automatically when the system starts.

### Your Custom Accounts:
After signup, you can create as many accounts as needed:
- Each needs unique username
- Each needs unique email
- All get full dashboard access
- No role restrictions

---

## 💡 Tips

1. **Remember Your Credentials:**
   - Write down username and password
   - Use a password manager
   - Email is NOT used for login (only username)

2. **Username vs Email:**
   - Login with USERNAME (not email)
   - Email is just for records
   - Both must be unique

3. **After Signup:**
   - Success message shows your username
   - Username pre-filled in login form
   - Just enter password and login

4. **Lost Password:**
   - Currently no password recovery (coming soon)
   - Remember your password or create new account
   - Admin can reset passwords via database

---

## 🎨 UI Features

### Signup Page Features:

- **Auto-switch:** Automatically switches to login after successful signup
- **Pre-fill:** Username pre-filled for easy login
- **Validation:** Real-time password match checking
- **Feedback:** Clear success/error messages
- **Toggle:** Easy switch between signup and login modes

### Visual Indicators:

- 🟢 **Green Alert:** Signup successful
- 🔴 **Red Alert:** Error occurred
- 🔵 **Loading:** Processing signup/login
- 👁️ **Password Toggle:** Show/hide password

---

## 🔒 Security Features

### Password Security:
- **Hashing:** bcrypt with salt
- **No Plain Text:** Never stored unencrypted
- **Strong Requirements:** Enforced password strength

### Token Security:
- **JWT Tokens:** Secure authentication
- **30-min Expiry:** Automatic logout for security
- **HTTP-only:** Cannot be accessed by JavaScript

### Account Security:
- **Active/Inactive:** Accounts can be deactivated
- **Activity Logging:** All actions tracked
- **IP Tracking:** Login locations recorded

---

## 📝 Example Accounts You Can Create

```
Account 1:
  Email: sarah@company.com
  Username: sarah_smith
  Password: SarahPass123!

Account 2:
  Email: mike@company.com
  Username: mike_jones
  Password: MikeSecure456!

Account 3:
  Email: admin@company.com
  Username: company_admin
  Password: AdminPass789!
```

All will have full dashboard access with all features!

---

## 🛠️ For Developers

### Signup API:
```
POST /auth/signup
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "user"
}

Response: 200 OK
{
  "id": 2,
  "username": "newuser",
  "email": "user@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2025-10-26T..."
}
```

### Login API:
```
POST /auth/login
Content-Type: application/json

{
  "username": "newuser",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "newuser",
    ...
  }
}
```

---

## ✅ Checklist

Before using signup, verify:

- [ ] Backend is running (`http://localhost:8000/health`)
- [ ] Frontend is running (`http://localhost:3000`)
- [ ] Database exists (`backend/auth.db`)
- [ ] Network connection is working
- [ ] No browser cache issues (Ctrl+Shift+R to refresh)

---

## 🎉 Summary

**Signup Process:**
1. Fill form with email, username, password
2. Click "Create Account"
3. See success message
4. Automatically switched to login
5. Enter password and login
6. Access full dashboard

**What You Get:**
- Personal account
- Secure password storage
- Full dashboard access
- All features available
- Activity tracking

**Remember:**
- Login with USERNAME (not email)
- Password is case-sensitive
- Keep credentials secure
- All users have same access level

---

**Last Updated:** October 26, 2025  
**Status:** Fully Functional  
**Support:** Check error messages for troubleshooting
