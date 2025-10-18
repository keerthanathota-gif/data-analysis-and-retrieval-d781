# OAuth Authentication Setup Guide

## Overview
The CPSC Regulation System supports OAuth authentication with Google, Microsoft, and Apple. This guide explains how to configure each provider.

## Environment Variables Required

### Google OAuth
```bash
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/oauth/google/callback
```

### Microsoft OAuth
```bash
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/oauth/microsoft/callback
```

### Apple OAuth
```bash
APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret-jwt
APPLE_REDIRECT_URI=http://localhost:8000/auth/oauth/apple/callback
```

### Frontend URL
```bash
FRONTEND_URL=http://localhost:3000
```

## Setting Up OAuth Providers

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Choose "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:8000/auth/oauth/google/callback`
   - `http://localhost:3000/oauth-callback` (for development)
7. Copy the Client ID and Client Secret

### Microsoft OAuth Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Set redirect URI to:
   - `http://localhost:8000/auth/oauth/microsoft/callback`
5. Under "Certificates & secrets", create a new client secret
6. Copy the Application (client) ID and the client secret value

### Apple OAuth Setup

1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Create an App ID with Sign in with Apple capability
3. Create a Service ID for web authentication
4. Configure the Service ID:
   - Add domain: `localhost`
   - Add return URL: `http://localhost:8000/auth/oauth/apple/callback`
5. Create a private key for Sign in with Apple
6. Generate a client secret JWT using the private key

## Running the Application

### Backend
```bash
cd backend
# Set environment variables (create .env file or export them)
export GOOGLE_CLIENT_ID=your-google-client-id
export GOOGLE_CLIENT_SECRET=your-google-client-secret
# ... other environment variables

python run.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Testing OAuth Flow

1. Navigate to http://localhost:3000/login
2. Click on one of the OAuth provider buttons (Google, Microsoft, or Apple)
3. You'll be redirected to the provider's login page
4. After successful authentication, you'll be redirected back and automatically logged in

## Troubleshooting

### "OAuth provider not configured" Error
- Ensure you have set the appropriate environment variables for the provider
- Restart the backend server after setting environment variables

### "Authentication failed" Error
- Check that the redirect URIs match exactly in both your provider configuration and the application
- Verify that the client ID and secret are correct
- Check the backend logs for more detailed error messages

### CORS Issues
- Ensure the CORS configuration in `backend/app/config.py` includes your frontend URL
- The default configuration includes `http://localhost:3000` and `http://localhost:8000`

## Production Deployment

For production deployment:

1. Update all redirect URIs to use your production domain
2. Set `FRONTEND_URL` to your production frontend URL
3. Use HTTPS for all URLs
4. Store secrets securely (use environment variables or secret management services)
5. Update CORS settings to include only your production domains

## Security Notes

- Never commit OAuth credentials to version control
- Always use HTTPS in production
- Implement rate limiting on OAuth endpoints
- Regularly rotate client secrets
- Monitor OAuth login attempts for suspicious activity