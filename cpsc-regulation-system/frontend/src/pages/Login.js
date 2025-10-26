import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Lottie from 'lottie-react';
import '../styles/auth.css';
import logoAnimation from '../animations/logo-animation.json';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const lottieRef = useRef();
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      if (response.data.access_token) {
        // Store token in localStorage
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify({
          email: email,
          role: response.data.role || 'user'
        }));

        // Play animation on success
        if (lottieRef.current) {
          lottieRef.current.play();
        }

        // Navigate based on role
        setTimeout(() => {
          if (response.data.role === 'admin') {
            navigate('/admin');
          } else {
            navigate('/cfr-dashboard');
          }
        }, 800);
      }
    } catch (err) {
      console.error('Login error:', err);

      // Handle different error response formats
      let errorMessage = 'Invalid credentials. Please try again.';

      if (err.response?.data) {
        const errorData = err.response.data;

        // Handle string error message
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        }
        // Handle validation error array
        else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(err => err.msg).join(', ');
        }
        // Handle object with message
        else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSSOLogin = (provider) => {
    setError(`${provider} authentication coming soon`);
  };

  const handleLogoClick = () => {
    if (lottieRef.current) {
      lottieRef.current.stop();
      lottieRef.current.play();
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <header className="auth-header">
          <div className="auth-logo-row">
            <div
              onClick={handleLogoClick}
              onMouseEnter={() => lottieRef.current?.play()}
              onMouseLeave={() => lottieRef.current?.stop()}
              style={{ cursor: 'pointer', width: '48px', height: '48px' }}
              aria-hidden="true"
            >
              <Lottie
                lottieRef={lottieRef}
                animationData={logoAnimation}
                loop={false}
                autoplay={false}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
            <div className="auth-title">Sign in</div>
          </div>
          <div className="auth-sub">Access CPSC CFR Regulation Database</div>
        </header>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={onSubmit}>
          <div className="field">
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              className="input"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              autoComplete="email"
            />
          </div>

          <div className="field">
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              className="input"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          <button className="btn" type="submit" disabled={loading}>
            {loading ? (
              <span className="ring" aria-label="loading" />
            ) : (
              'Continue'
            )}
          </button>

          <div className="divider">or</div>

          <div className="row">
            <button
              className="btn btn-secondary"
              type="button"
              onClick={() => handleSSOLogin('Google')}
            >
              <span className="icon" aria-hidden="true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
              </span>
              Continue with Google
            </button>
            <button
              className="btn btn-secondary"
              type="button"
              onClick={() => handleSSOLogin('Microsoft')}
            >
              <span className="icon" aria-hidden="true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.4 11.4H2V2h9.4v9.4zm10.6 0h-9.4V2H22v9.4zM11.4 22H2v-9.4h9.4V22zm10.6 0h-9.4v-9.4H22V22z" fill="#00A4EF"/>
                </svg>
              </span>
              Continue with Microsoft
            </button>
          </div>

          <div className="help">
            By continuing, you agree to the Terms of Service and acknowledge the Privacy Policy.
          </div>
        </form>
      </div>
    </div>
  );
}
