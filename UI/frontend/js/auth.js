/**
 * Authentication Module
 * Handles login, logout, token management, and auth state
 */

const API_BASE = window.location.origin; // Use current server URL

// ============================================
// TOKEN MANAGEMENT
// ============================================

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function clearToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
}

function getUserInfo() {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
}

function setUserInfo(userInfo) {
    localStorage.setItem('user_info', JSON.stringify(userInfo));
}

// ============================================
// LOGIN HANDLER
// ============================================

if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('errorMessage');
        const loginBtn = document.getElementById('loginBtn');
        const loadingSpinner = document.getElementById('loadingSpinner');

        // Hide error, show loading
        errorMessage.style.display = 'none';
        loginBtn.style.display = 'none';
        loadingSpinner.style.display = 'flex';

        try {
            // Create form data for OAuth2 format
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                // Save token
                setToken(data.access_token);

                // Get user info
                const userResponse = await fetch(`${API_BASE}/api/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`
                    }
                });

                if (userResponse.ok) {
                    const userInfo = await userResponse.json();
                    setUserInfo(userInfo);

                    // Redirect based on role
                    if (userInfo.role === 'admin') {
                        window.location.href = 'admin.html';
                    } else {
                        window.location.href = 'dashboard.html';
                    }
                } else {
                    throw new Error('Failed to get user information');
                }
            } else {
                // Show error
                errorMessage.textContent = data.detail || 'Login failed';
                errorMessage.style.display = 'block';
                loginBtn.style.display = 'block';
                loadingSpinner.style.display = 'none';
            }
        } catch (error) {
            errorMessage.textContent = 'An error occurred. Please try again.';
            errorMessage.style.display = 'block';
            loginBtn.style.display = 'block';
            loadingSpinner.style.display = 'none';
            console.error('Login error:', error);
        }
    });
}

// ============================================
// LOGOUT HANDLER
// ============================================

async function logout() {
    const token = getToken();

    if (token) {
        try {
            await fetch(`${API_BASE}/api/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    clearToken();
    window.location.href = 'login.html';
}

// ============================================
// AUTH CHECK ON PAGE LOAD
// ============================================

function checkAuth() {
    const token = getToken();
    const userInfo = getUserInfo();
    const currentPage = window.location.pathname.split('/').pop();

    // If on login page and already logged in, redirect
    if (currentPage === 'login.html' && token && userInfo) {
        if (userInfo.role === 'admin') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'dashboard.html';
        }
        return;
    }

    // If on protected page and not logged in, redirect to login
    if ((currentPage === 'dashboard.html' || currentPage === 'admin.html') && (!token || !userInfo)) {
        window.location.href = 'login.html';
        return;
    }

    // If on admin page but not admin, redirect to dashboard
    if (currentPage === 'admin.html' && userInfo && userInfo.role !== 'admin') {
        window.location.href = 'dashboard.html';
        return;
    }

    // Display user name if element exists
    const userDisplayName = document.getElementById('userDisplayName');
    if (userDisplayName && userInfo) {
        userDisplayName.textContent = userInfo.username;
    }
}

// Run auth check on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuth);
} else {
    checkAuth();
}
