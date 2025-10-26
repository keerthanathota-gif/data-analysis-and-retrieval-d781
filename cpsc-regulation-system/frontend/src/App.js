import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import AuthPage from './pages/AuthPage';
import OAuthCallbackPage from './pages/OAuthCallbackPage';
import CFRDashboard_85063ac from './pages/CFRDashboard_85063ac';
import Layout from './components/Layout';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route path="/signup" element={<AuthPage />} />
        <Route path="/oauth-callback" element={<OAuthCallbackPage />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <CFRDashboard_85063ac />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;