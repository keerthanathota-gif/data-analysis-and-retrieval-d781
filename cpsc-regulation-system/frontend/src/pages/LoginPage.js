import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import GoogleIcon from '@mui/icons-material/Google';
import AppleIcon from '@mui/icons-material/Apple';
import MicrosoftIcon from '@mui/icons-material/Microsoft';
import { authService } from '../services/authService';
import { getOAuthUrl } from '../config/oauth-config';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData.username, formData.password);
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Sign in failed. Please check your credentials and try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider) => {
    setError('');
    setLoading(true);
    try {
      // Get state token from backend for CSRF protection
      const { state, client_id } = await authService.oauthStart(provider);
      
      // Store state in sessionStorage for verification
      sessionStorage.setItem('oauth_state', state);
      sessionStorage.setItem('oauth_provider', provider);
      
      // If we have a client_id from backend, use real OAuth flow
      if (client_id) {
        const authUrl = getOAuthUrl(provider, state, client_id);
        window.location.href = authUrl;
      } else {
        // Fallback for development/testing without OAuth credentials
        setError(`OAuth provider ${provider} is not configured. Please set ${provider.toUpperCase()}_CLIENT_ID environment variable.`);
        setLoading(false);
      }
    } catch (error) {
      console.error('OAuth start error:', error);
      setError('Unable to start OAuth flow. Please try again.');
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            CPSC Regulation System
          </Typography>
          <Typography component="h2" variant="h6" align="center" color="textSecondary" gutterBottom>
            Sign In
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={formData.username}
              onChange={handleChange}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>

            <Typography align="center" variant="body2" color="textSecondary" sx={{ my: 1 }}>
              Or continue with
            </Typography>
            <Box display="flex" gap={2}>
              <Button fullWidth variant="outlined" startIcon={<GoogleIcon />} onClick={() => handleOAuth('google')}>Google</Button>
              <Button fullWidth variant="outlined" startIcon={<MicrosoftIcon />} onClick={() => handleOAuth('microsoft')}>Microsoft</Button>
              <Button fullWidth variant="outlined" startIcon={<AppleIcon />} onClick={() => handleOAuth('apple')}>Apple</Button>
            </Box>
            <Box textAlign="center">
              <Link to="/signup" style={{ textDecoration: 'none' }}>
                <Typography variant="body2" color="primary">
                  Don't have an account? Sign Up
                </Typography>
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;