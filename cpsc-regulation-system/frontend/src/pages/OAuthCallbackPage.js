import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../services/authService';
import { Box, CircularProgress, Typography, Container, Alert } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const OAuthCallbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleOAuthCallback = async () => {
      // Check if this is a redirect from the backend with a token
      const token = searchParams.get('token');
      const provider = searchParams.get('provider');
      
      if (token) {
        // Direct token from backend OAuth flow
        try {
          localStorage.setItem('token', token);
          
          // Get user info to complete login
          const userInfo = await authService.getCurrentUser();
          
          // Navigate based on user role
          if (userInfo.role === 'admin') {
            navigate('/admin-panel');
          } else {
            navigate('/dashboard');
          }
          return;
        } catch (error) {
          console.error('Error completing OAuth login:', error);
          setError('Failed to complete sign-in. Please try again.');
          setTimeout(() => navigate('/login'), 3000);
          return;
        }
      }

      // Handle OAuth callback from provider (authorization code flow)
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      if (error) {
        setError(`Authentication failed: ${errorDescription || error}`);
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      if (!code || !state) {
        setError('Invalid OAuth callback parameters');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      // Verify state to prevent CSRF attacks
      const savedState = sessionStorage.getItem('oauth_state');
      const savedProvider = sessionStorage.getItem('oauth_provider');
      
      if (!state.includes(savedState)) {
        setError('Invalid OAuth state. Please try signing in again.');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      // Clear stored OAuth state
      sessionStorage.removeItem('oauth_state');
      sessionStorage.removeItem('oauth_provider');

      // The backend should handle the code exchange
      // For now, redirect to backend OAuth callback endpoint
      const backendCallbackUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/auth/oauth/${savedProvider}/callback?code=${code}&state=${state}`;
      window.location.href = backendCallbackUrl;
    };

    handleOAuthCallback();
  }, [navigate, searchParams]);

  return (
    <Container maxWidth="sm">
      <Box display="flex" flexDirection="column" alignItems="center" mt={8}>
        {error ? (
          <>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
            <Typography variant="body2">Redirecting to login...</Typography>
          </>
        ) : (
          <>
            <CircularProgress />
            <Typography variant="body1" mt={2}>Completing sign-in…</Typography>
          </>
        )}
      </Box>
    </Container>
  );
};

export default OAuthCallbackPage;
