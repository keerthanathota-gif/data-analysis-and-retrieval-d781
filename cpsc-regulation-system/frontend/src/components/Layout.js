import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Layout = ({ children }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  const isAuthPage = ['/login', '/signup', '/admin-login'].includes(location.pathname);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        // Keep transparent background to show gradient
        bgcolor: 'transparent',
      }}
    >
      {isAuthenticated && (
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            background: 'linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)',
            backdropFilter: 'blur(10px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
          }}
        >
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              CPSC Regulation System
            </Typography>
            <Button
              color="inherit"
              onClick={() => handleNavigation('/dashboard')}
              sx={{ mr: 2 }}
            >
              Dashboard
            </Button>
            {user?.role === 'admin' && (
              <Button
                color="inherit"
                onClick={() => handleNavigation('/admin-panel')}
                sx={{ mr: 2 }}
              >
                Admin
              </Button>
            )}
            <Typography variant="body2" sx={{ mr: 2 }}>
              Welcome, {user?.username}
            </Typography>
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          </Toolbar>
        </AppBar>
      )}
      <Box
        component="main"
        sx={{
          width: '100%',
          px: 0,
          // Remove vertical padding on auth pages to eliminate outside margins
          py: isAuthPage ? 0 : 3,
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;