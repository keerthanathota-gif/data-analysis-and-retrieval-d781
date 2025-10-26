import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
  Grow,
  Checkbox,
  FormControlLabel
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
import BookIcon from '@mui/icons-material/Book';
import BoltIcon from '@mui/icons-material/Bolt';
import ShieldIcon from '@mui/icons-material/Shield';
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
  height: '100vh',
  display: 'flex',
  position: 'relative',
  overflow: 'hidden',
}));

const LeftPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '40px 60px',
  background: 'white',
  overflowY: 'auto',
  '@media (max-width: 960px)': {
    flex: 'unset',
    width: '100%',
    padding: '20px'
  },
  '@media (max-height: 800px)': {
    padding: '20px 60px'
  }
}));

const RightPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  padding: '80px 60px',
  color: 'white',
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
  '@media (max-width: 960px)': {
    display: 'none'
  }
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: '48px 40px',
  width: '100%',
  maxWidth: '500px',
  background: 'white',
  borderRadius: '0',
  boxShadow: 'none',
  position: 'relative',
  zIndex: 1,
  '@media (max-height: 800px)': {
    padding: '24px 40px'
  },
  '@media (max-width: 960px)': {
    padding: '24px 20px'
  }
}));

const LogoBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  marginBottom: '32px',
  '@media (max-height: 800px)': {
    marginBottom: '24px'
  }
}));

const LogoIcon = styled(Box)(({ theme }) => ({
  width: '48px',
  height: '48px',
  borderRadius: '12px',
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'white',
}));

const LogoText = styled(Typography)(({ theme }) => ({
  fontSize: '24px',
  fontWeight: 'bold',
  color: '#1a1a1a',
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: '8px',
    background: '#f8f9fa',
    transition: 'all 0.3s ease',
    '&:hover': {
      background: '#f1f3f5',
    },
    '&.Mui-focused': {
      background: 'white',
    },
    '& fieldset': {
      borderColor: '#e9ecef',
      transition: 'all 0.3s ease'
    },
    '&:hover fieldset': {
      borderColor: '#dee2e6'
    },
    '&.Mui-focused fieldset': {
      borderColor: '#667eea',
      borderWidth: '2px'
    }
  },
  '& .MuiInputLabel-root': {
    color: '#6c757d',
    '&.Mui-focused': {
      color: '#667eea'
    }
  }
}));

const PrimaryButton = styled(Button)(({ theme }) => ({
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  borderRadius: '8px',
  padding: '14px',
  fontSize: '16px',
  fontWeight: '600',
  textTransform: 'none',
  boxShadow: 'none',
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8e 100%)',
    transform: 'translateY(-2px)',
    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
  },
  '&:active': {
    transform: 'translateY(0)'
  }
}));

const SocialButton = styled(IconButton)(({ theme, color }) => ({
  width: '48px',
  height: '48px',
  borderRadius: '8px',
  border: '1px solid #e9ecef',
  transition: 'all 0.3s ease',
  backgroundColor: 'white',
  color: color || '#667eea',
  '&:hover': {
    borderColor: color || '#667eea',
    backgroundColor: color || '#667eea',
    color: 'white',
    transform: 'translateY(-2px)',
    boxShadow: `0 4px 12px ${color ? color + '40' : 'rgba(102, 126, 234, 0.25)'}`
  }
}));

const FeatureCard = styled(Box)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(10px)',
  borderRadius: '16px',
  padding: '24px',
  marginBottom: '20px',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateX(10px)',
    background: 'rgba(255, 255, 255, 0.15)',
  }
}));

const AuthPage = () => {
  const location = useLocation();
  const [isSignup, setIsSignup] = useState(location.pathname === '/signup');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    rememberMe: false,
    role: 'user'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (isSignup) {
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }
        const signupResponse = await signup({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          role: formData.role
        });
        
        // Show success message with username from response
        const signupUsername = signupResponse.username || formData.username;
        setSuccess(`Account created successfully! You can now login with username: ${signupUsername}`);
        
        // Switch to login mode after 3 seconds
        setTimeout(() => {
          setIsSignup(false);
          setSuccess('');
        }, 3000);
        
        // Clear form but keep username for easy login
        setFormData({
          username: signupUsername,
          email: '',
          password: '',
          confirmPassword: '',
          rememberMe: false,
          role: 'user'
        });
      } else {
        // Login and wait for state to update
        const loginResponse = await login(formData.username, formData.password);
        
        // Ensure the token and user are set before navigating
        if (loginResponse && loginResponse.access_token) {
          // Small delay to ensure state is fully updated
          setTimeout(() => {
            navigate('/dashboard');
          }, 100);
        }
      }
    } catch (err) {
      console.error('Auth error:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          `${isSignup ? 'Sign up' : 'Sign in'} failed. Please try again.`;
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider) => {
    setError('');
    setLoading(true);
    try {
      const { state, client_id } = await authService.oauthStart(provider);
      
      sessionStorage.setItem('oauth_state', state);
      sessionStorage.setItem('oauth_provider', provider);
      if (isSignup) {
        sessionStorage.setItem('oauth_signup', 'true');
      }
      
      if (client_id) {
        const authUrl = getOAuthUrl(provider, state, client_id);
        window.location.href = authUrl;
      } else {
        setError(`OAuth provider ${provider} is not configured.`);
        setLoading(false);
      }
    } catch (error) {
      console.error('OAuth start error:', error);
      setError('Unable to start OAuth flow. Please try again.');
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsSignup(!isSignup);
    setError('');
    setSuccess('');
    setFormData({
      username: formData.username,
      email: '',
      password: '',
      confirmPassword: '',
      rememberMe: false,
      role: 'user'
    });
  };

  return (
    <GradientContainer>
      <LeftPanel>
        <Container maxWidth="sm">
          <StyledPaper elevation={0}>
            <LogoBox>
              <LogoIcon>
                <BookIcon />
              </LogoIcon>
              <Box>
                <LogoText>CFR Pipeline</LogoText>
                <Typography variant="caption" sx={{ color: '#6c757d' }}>
                  Regulatory Intelligence Platform
                </Typography>
              </Box>
            </LogoBox>

            <Box sx={{ mb: 4 }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1a1a1a', mb: 1 }}>
                {isSignup ? 'Create Account' : 'Welcome back'}
              </Typography>
              <Typography variant="body2" sx={{ color: '#6c757d' }}>
                {isSignup ? 'Start your free trial today' : 'Access your regulatory intelligence dashboard'}
              </Typography>
            </Box>
            
            {error && (
              <Fade in={true}>
                <Alert 
                  severity="error" 
                  sx={{ 
                    mb: 3, 
                    borderRadius: '8px',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)'
                  }} 
                  onClose={() => setError('')}
                >
                  {error}
                </Alert>
              </Fade>
            )}

            {success && (
              <Fade in={true}>
                <Alert 
                  severity="success" 
                  sx={{ 
                    mb: 3, 
                    borderRadius: '8px',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    border: '1px solid rgba(34, 197, 94, 0.3)'
                  }} 
                  onClose={() => setSuccess('')}
                >
                  {success}
                </Alert>
              </Fade>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              {isSignup && (
                <StyledTextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  placeholder="your.email@company.com"
                  label="Email address"
                  name="email"
                  autoComplete="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailOutlinedIcon sx={{ color: '#adb5bd' }} />
                      </InputAdornment>
                    ),
                  }}
                />
              )}
              
              <StyledTextField
                margin="normal"
                required
                fullWidth
                id="username"
                placeholder={isSignup ? "Choose a username" : "your.email@company.com"}
                label={isSignup ? "Username" : "Email address"}
                name="username"
                autoComplete="username"
                autoFocus
                value={formData.username}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      {isSignup ? (
                        <PersonOutlineIcon sx={{ color: '#adb5bd' }} />
                      ) : (
                        <EmailOutlinedIcon sx={{ color: '#adb5bd' }} />
                      )}
                    </InputAdornment>
                  ),
                }}
              />
              
              <StyledTextField
                margin="normal"
                required
                fullWidth
                name="password"
                placeholder="Enter your password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete={isSignup ? "new-password" : "current-password"}
                value={formData.password}
                onChange={handleChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockOutlinedIcon sx={{ color: '#adb5bd' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        sx={{ color: '#adb5bd' }}
                      >
                        {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              {isSignup && (
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
                        <LockOutlinedIcon sx={{ color: '#adb5bd' }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          edge="end"
                          sx={{ color: '#adb5bd' }}
                        >
                          {showConfirmPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              )}
              
              {!isSignup && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, mb: 2 }}>
                  <FormControlLabel
                    control={
                      <Checkbox 
                        name="rememberMe"
                        checked={formData.rememberMe}
                        onChange={handleChange}
                        sx={{
                          color: '#667eea',
                          '&.Mui-checked': {
                            color: '#667eea',
                          },
                        }}
                      />
                    }
                    label={<Typography variant="body2" sx={{ color: '#6c757d' }}>Keep me signed in for 30 days</Typography>}
                  />
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      color: '#667eea', 
                      cursor: 'pointer',
                      '&:hover': { textDecoration: 'underline' }
                    }}
                  >
                    Forgot password?
                  </Typography>
                </Box>
              )}

              <PrimaryButton
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{ mt: isSignup ? 3 : 2, mb: 3 }}
              >
                {loading ? (
                  <CircularProgress size={24} sx={{ color: 'white' }} />
                ) : (
                  isSignup ? 'Create Account' : 'Sign in to Dashboard →'
                )}
              </PrimaryButton>

              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Typography variant="body2" sx={{ color: '#adb5bd', mb: 2 }}>
                  {isSignup ? 'Or sign up with' : 'Or sign in with'}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
                  <SocialButton color="#4267B2" onClick={() => handleOAuth('facebook')} disabled={loading}>
                    <FacebookIcon />
                  </SocialButton>
                  <SocialButton color="#1DA1F2" onClick={() => handleOAuth('twitter')} disabled={loading}>
                    <TwitterIcon />
                  </SocialButton>
                  <SocialButton color="#DB4437" onClick={() => handleOAuth('google')} disabled={loading}>
                    <GoogleIcon />
                  </SocialButton>
                </Box>
              </Box>

              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: '#6c757d', display: 'inline' }}>
                  {isSignup ? "Already have an account?" : "Don't have an account?"}{' '}
                </Typography>
                <Typography 
                  variant="body2" 
                  component="span"
                  onClick={toggleMode}
                  sx={{ 
                    color: '#667eea', 
                    fontWeight: '600',
                    cursor: 'pointer',
                    '&:hover': {
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {isSignup ? 'Sign in' : 'Start your free trial'}
                </Typography>
              </Box>
            </Box>
          </StyledPaper>
        </Container>
      </LeftPanel>

      <RightPanel>
        <Box sx={{ maxWidth: '550px', position: 'relative', zIndex: 1, mt: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
            <BoltIcon sx={{ fontSize: '28px' }} />
            <Typography variant="h6" sx={{ fontWeight: 'bold', letterSpacing: '0.5px', fontSize: '1.1rem' }}>
              AI-Powered Regulatory Intelligence
            </Typography>
          </Box>
          
          <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 3, lineHeight: 1.3, fontSize: '2.2rem' }}>
            Transform how you navigate federal regulations
          </Typography>
          
          <Typography variant="h6" sx={{ mb: 5, opacity: 0.9, fontWeight: 400 }}>
            Harness the power of AI to search, analyze, and understand the Code of Federal Regulations instantly.
          </Typography>

          <FeatureCard>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <BookIcon sx={{ fontSize: '32px', mt: 0.5 }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                  1,176+ Regulations
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Access comprehensive CFR database with AI-powered search
                </Typography>
              </Box>
            </Box>
          </FeatureCard>

          <FeatureCard>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <BoltIcon sx={{ fontSize: '32px', mt: 0.5 }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Instant Analysis
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Process regulatory documents in seconds, not hours
                </Typography>
              </Box>
            </Box>
          </FeatureCard>

          <FeatureCard>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <ShieldIcon sx={{ fontSize: '32px', mt: 0.5 }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Compliance Ready
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Stay updated with real-time regulatory changes
                </Typography>
              </Box>
            </Box>
          </FeatureCard>


          <Box sx={{ mt: 5, pt: 4, borderTop: '1px solid rgba(255,255,255,0.2)' }}>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block', mb: 1 }}>
              Trusted by compliance teams at
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Fortune 500 • Legal Firms • Gov Agencies
            </Typography>
          </Box>
        </Box>
      </RightPanel>
    </GradientContainer>
  );
};

export default AuthPage;
