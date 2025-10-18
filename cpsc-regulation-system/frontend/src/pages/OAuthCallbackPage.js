import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../services/authService';
import { Box, CircularProgress, Typography, Container } from '@mui/material';

const OAuthCallbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const finalizeLogin = async () => {
      const provider = searchParams.get('provider');
      const provider_account_id = searchParams.get('sub') || searchParams.get('id') || '';
      const email = searchParams.get('email');
      const name = searchParams.get('name');
      const access_token = searchParams.get('access_token');
      const refresh_token = searchParams.get('refresh_token');
      const expires_in = searchParams.get('expires_in');

      try {
        const response = await authService.oauthCallback({
          provider,
          provider_account_id,
          email,
          name,
          access_token,
          refresh_token,
          expires_in: expires_in ? parseInt(expires_in, 10) : undefined,
        });
        localStorage.setItem('token', response.access_token);
        // route by role
        const role = response?.user?.role;
        if (role === 'admin') {
          navigate('/admin-panel');
        } else {
          navigate('/dashboard');
        }
      } catch (e) {
        navigate('/login');
      }
    };

    finalizeLogin();
  }, [navigate, searchParams]);

  return (
    <Container maxWidth="sm">
      <Box display="flex" flexDirection="column" alignItems="center" mt={8}>
        <CircularProgress />
        <Typography variant="body1" mt={2}>Completing sign-in…</Typography>
      </Box>
    </Container>
  );
};

export default OAuthCallbackPage;
