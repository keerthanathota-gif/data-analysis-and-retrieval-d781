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
  CircularProgress,
  IconButton,
  InputAdornment,
  Fade,
  Grow
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import { useAuth } from '../contexts/AuthContext';
import GoogleIcon from '@mui/icons-material/Google';
import FacebookIcon from '@mui/icons-material/Facebook';
import TwitterIcon from '@mui/icons-material/Twitter';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { authService } from '../services/authService';
import { getOAuthUrl } from '../config/oauth-config';

// Animations
const float = keyframes`
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
`;

const gradient = keyframes`
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
`;

const glow = keyframes`
  0%, 100% {
    box-shadow: 0 0 20px rgba(147, 51, 234, 0.3), 0 0 40px rgba(59, 130, 246, 0.1);
  }
  50% {
    box-shadow: 0 0 30px rgba(147, 51, 234, 0.5), 0 0 60px rgba(59, 130, 246, 0.3);
  }
`;

// Styled Components
const GradientContainer = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  background: 'linear-gradient(-45deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #fda085 100%)',
  backgroundSize: '400% 400%',
  animation: `${gradient} 15s ease infinite`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'radial-gradient(circle at 20% 80%, transparent 30%, rgba(255, 255, 255, 0.1) 100%)',
  },
  '&::after': {
    content: '""',
    position: 'absolute',
    top: '-50%',
    left: '-50%',
    width: '200%',
    height: '200%',
    background: 'radial-gradient(circle at 70% 40%, transparent 30%, rgba(147, 51, 234, 0.1) 100%)',
  }
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: '40px',
  width: '100%',
  maxWidth: '450px',
  backdropFilter: 'blur(20px)',
  background: 'rgba(255, 255, 255, 0.95)',
  borderRadius: '20px',
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  border: '1px solid rgba(255, 255, 255, 0.18)',
  animation: `${glow} 3s ease-in-out infinite`,
  position: 'relative',
  zIndex: 1,
  transition: 'transform 0.3s ease',
  '&:hover': {
    transform: 'scale(1.02)'
  }
}));

const LogoText = styled(Typography)(({ theme }) => ({
  background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
  backgroundClip: 'text',
  WebkitBackgroundClip: 'text',
  color: 'transparent',
  fontWeight: 'bold',
  letterSpacing: '2px',
  fontSize: '14px',
  animation: `${float} 3s ease-in-out infinite`,
  marginBottom: '8px'
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: '12px',
    background: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(10px)',
    transition: 'all 0.3s ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.95)',
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 12px rgba(147, 51, 234, 0.15)'
    },
    '&.Mui-focused': {
      background: 'white',
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 20px rgba(147, 51, 234, 0.25)'
    },
    '& fieldset': {
      borderColor: 'rgba(147, 51, 234, 0.2)',
      transition: 'all 0.3s ease'
    },
    '&:hover fieldset': {
      borderColor: 'rgba(147, 51, 234, 0.4)'
    },
    '&.Mui-focused fieldset': {
      borderColor: '#9333ea',
      borderWidth: '2px'
    }
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(0, 0, 0, 0.6)',
    '&.Mui-focused': {
      color: '#9333ea'
    }
  }
}));

const SignupButton = styled(Button)(({ theme }) => ({
  background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
  borderRadius: '12px',
  padding: '12px',
  fontSize: '16px',
  fontWeight: 'bold',
  textTransform: 'none',
  boxShadow: '0 3px 15px rgba(147, 51, 234, 0.3)',
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'linear-gradient(45deg, #764ba2 30%, #f093fb 90%)',
    transform: 'translateY(-3px)',
    boxShadow: '0 5px 25px rgba(147, 51, 234, 0.4)'
  },
  '&:active': {
    transform: 'translateY(0)'
  }
}));

const SocialButton = styled(IconButton)(({ theme, color }) => ({
  width: '50px',
  height: '50px',
  borderRadius: '50%',
  border: '2px solid rgba(147, 51, 234, 0.2)',
  transition: 'all 0.3s ease',
  backgroundColor: 'white',
  color: color || '#667eea',
  '&:hover': {
    transform: 'translateY(-3px) scale(1.1)',
    borderColor: color || '#667eea',
    backgroundColor: color || '#667eea',
    color: 'white',
    boxShadow: `0 5px 15px ${color ? color + '40' : 'rgba(102, 126, 234, 0.4)'}`
  }
}));

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'user'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { signup } = useAuth();
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

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await signup({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: formData.role
      });
      navigate('/login');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Signup failed. Please check your information and try again.';
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
      sessionStorage.setItem('oauth_signup', 'true'); // Mark as signup flow
      
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
    <GradientContainer>
      <Container maxWidth="sm">
        <Grow in={true} timeout={800}>
          <StyledPaper elevation={0}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <LogoText variant="subtitle1">CPSC</LogoText>
              <Fade in={true} timeout={1000}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1a1a1a', mb: 1 }}>
                  Sign Up
                </Typography>
              </Fade>
              <Typography variant="body2" sx={{ color: 'rgba(0, 0, 0, 0.6)' }}>
                Create your account to get started
              </Typography>
            </Box>

            {error && (
              <Fade in={true}>
                <Alert
                  severity="error"
                  sx={{
                    mb: 2,
                    borderRadius: '12px',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)'
                  }}
                  onClose={() => setError('')}
                >
                  {error}
                </Alert>
              </Fade>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <StyledTextField
                margin="normal"
                required
                fullWidth
                id="username"
                placeholder="Type your username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={formData.username}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonOutlineIcon sx={{ color: 'rgba(147, 51, 234, 0.5)' }} />
                    </InputAdornment>
                  ),
                }}
              />
              <StyledTextField
                margin="normal"
                required
                fullWidth
                id="email"
                placeholder="Type your email"
                label="Email Address"
                name="email"
                autoComplete="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailOutlinedIcon sx={{ color: 'rgba(147, 51, 234, 0.5)' }} />
                    </InputAdornment>
                  ),
                }}
              />
              <StyledTextField
                margin="normal"
                required
                fullWidth
                name="password"
                placeholder="Type your password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockOutlinedIcon sx={{ color: 'rgba(147, 51, 234, 0.5)' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        sx={{ color: 'rgba(147, 51, 234, 0.5)' }}
                      >
                        {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <StyledTextField
                margin="normal"
                required
                fullWidth
                name="confirmPassword"
                placeholder="Confirm your password"
                label="Confirm Password"
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockOutlinedIcon sx={{ color: 'rgba(147, 51, 234, 0.5)' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        edge="end"
                        sx={{ color: 'rgba(147, 51, 234, 0.5)' }}
                      >
                        {showConfirmPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <SignupButton
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{ mt: 3, mb: 3 }}
              >
                {loading ? (
                  <CircularProgress size={24} sx={{ color: 'white' }} />
                ) : (
                  'SIGN UP'
                )}
              </SignupButton>

              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Typography variant="body2" sx={{ color: 'rgba(0, 0, 0, 0.5)', mb: 2 }}>
                  Or Sign Up Using
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
                  <SocialButton color="#4267B2" onClick={() => handleOAuth('facebook')}>
                    <FacebookIcon />
                  </SocialButton>
                  <SocialButton color="#1DA1F2" onClick={() => handleOAuth('twitter')}>
                    <TwitterIcon />
                  </SocialButton>
                  <SocialButton color="#DB4437" onClick={() => handleOAuth('google')}>
                    <GoogleIcon />
                  </SocialButton>
                </Box>
              </Box>

              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: 'rgba(0, 0, 0, 0.5)', mb: 1 }}>
                  Already have an account?
                </Typography>
                <Link to="/login" style={{ textDecoration: 'none' }}>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#9333ea',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        textDecoration: 'underline'
                      }
                    }}
                  >
                    SIGN IN
                  </Typography>
                </Link>
              </Box>
            </Box>
          </StyledPaper>
        </Grow>
      </Container>
    </GradientContainer>
  );
};

export default SignupPage;