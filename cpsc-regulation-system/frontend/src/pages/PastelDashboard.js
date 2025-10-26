import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/PastelDashboard.css';

const PastelDashboard = () => {
  const { user, logout } = useAuth();
  const [activeNav, setActiveNav] = useState('dashboard');
  const [users, setUsers] = useState([
    { name: "Emma Wilson", email: "emma.wilson@example.com", role: "Admin", status: "Active" },
    { name: "Sophia Lee", email: "sophia.lee@example.com", role: "Editor", status: "Pending" },
    { name: "Ava Johnson", email: "ava.johnson@example.com", role: "Viewer", status: "Inactive" },
    { name: "Olivia Brown", email: "olivia.brown@example.com", role: "Editor", status: "Active" },
    { name: "Mia Davis", email: "mia.davis@example.com", role: "Viewer", status: "Active" },
    { name: "Isabella Miller", email: "isabella.miller@example.com", role: "Admin", status: "Active" },
    { name: "Charlotte Wilson", email: "charlotte.wilson@example.com", role: "Viewer", status: "Pending" },
    { name: "Amelia Taylor", email: "amelia.taylor@example.com", role: "Editor", status: "Inactive" }
  ]);

  const sparkUsersRef = useRef(null);
  const sparkSessionsRef = useRef(null);
  const sparkPerformanceRef = useRef(null);

  useEffect(() => {
    initSparklines();
    window.addEventListener('resize', initSparklines);
    return () => window.removeEventListener('resize', initSparklines);
  }, []);

  const drawSparkline = (canvas, data, options = {}) => {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.clientWidth || canvas.width;
    const height = canvas.height;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, width, height);

    const paddingX = 6;
    const paddingY = 6;
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);
    const range = Math.max(maxVal - minVal, 1);

    const stepX = (width - paddingX * 2) / (data.length - 1);

    const grad = ctx.createLinearGradient(0, 0, width, 0);
    grad.addColorStop(0, '#F9C2D8');
    grad.addColorStop(1, '#C7B3F6');

    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.strokeStyle = grad;

    const areaGrad = ctx.createLinearGradient(0, 0, 0, height);
    areaGrad.addColorStop(0, 'rgba(249,194,216,0.35)');
    areaGrad.addColorStop(1, 'rgba(199,179,246,0.05)');

    ctx.beginPath();
    data.forEach((v, i) => {
      const x = paddingX + i * stepX;
      const y = paddingY + (1 - (v - minVal) / range) * (height - paddingY * 2);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.lineTo(width - paddingX, height - paddingY);
    ctx.lineTo(paddingX, height - paddingY);
    ctx.closePath();
    ctx.fillStyle = areaGrad;
    ctx.fill();
  };

  const initSparklines = () => {
    if (sparkUsersRef.current) {
      drawSparkline(sparkUsersRef.current, [12, 14, 11, 16, 18, 17, 21, 20, 22, 24, 23, 25]);
    }
    if (sparkSessionsRef.current) {
      drawSparkline(sparkSessionsRef.current, [6, 7, 9, 8, 11, 13, 12, 14, 13, 15, 16, 18]);
    }
    if (sparkPerformanceRef.current) {
      drawSparkline(sparkPerformanceRef.current, [92, 93, 94, 95, 94, 96, 97, 98, 97, 98, 99, 98]);
    }
  };

  const createStatusBadge = (status) => {
    const normalized = status.toLowerCase();
    if (normalized === 'active') return <span className="badge success">Active</span>;
    if (normalized === 'pending') return <span className="badge pending">Pending</span>;
    return <span className="badge inactive">Inactive</span>;
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="pastel-app" role="application">
      {/* Sidebar */}
      <aside className="pastel-sidebar" aria-label="Primary">
        <div className="pastel-brand">
          <div className="pastel-brand-mark" aria-hidden="true">✦</div>
          <div className="pastel-brand-name">CFR Lumine</div>
        </div>
        <nav className="pastel-nav">
          <a 
            className={`pastel-nav-item ${activeNav === 'dashboard' ? 'active' : ''}`} 
            href="#"
            onClick={(e) => { e.preventDefault(); setActiveNav('dashboard'); }}
          >
            <span className="pastel-icon duotone" aria-hidden="true">
              <span className="i i-dashboard"></span>
            </span>
            <span>Dashboard</span>
          </a>
          <a 
            className={`pastel-nav-item ${activeNav === 'users' ? 'active' : ''}`} 
            href="#users"
            onClick={(e) => { e.preventDefault(); setActiveNav('users'); }}
          >
            <span className="pastel-icon duotone" aria-hidden="true">
              <span className="i i-users"></span>
            </span>
            <span>Users</span>
          </a>
          <a 
            className={`pastel-nav-item ${activeNav === 'analytics' ? 'active' : ''}`} 
            href="#analytics"
            onClick={(e) => { e.preventDefault(); setActiveNav('analytics'); }}
          >
            <span className="pastel-icon duotone" aria-hidden="true">
              <span className="i i-analytics"></span>
            </span>
            <span>Analytics</span>
          </a>
          <a 
            className={`pastel-nav-item ${activeNav === 'settings' ? 'active' : ''}`} 
            href="#settings"
            onClick={(e) => { e.preventDefault(); setActiveNav('settings'); }}
          >
            <span className="pastel-icon duotone" aria-hidden="true">
              <span className="i i-settings"></span>
            </span>
            <span>Settings</span>
          </a>
          <div className="pastel-spacer"></div>
          <a 
            className="pastel-nav-item" 
            href="#logout"
            onClick={(e) => { e.preventDefault(); handleLogout(); }}
          >
            <span className="pastel-icon duotone" aria-hidden="true">
              <span className="i i-logout"></span>
            </span>
            <span>Logout</span>
          </a>
        </nav>
      </aside>

      {/* Main */}
      <main className="pastel-main">
        {/* Topbar */}
        <header className="pastel-topbar" aria-label="Secondary">
          <div className="pastel-search">
            <span className="pastel-icon duotone sm" aria-hidden="true">
              <span className="i i-search"></span>
            </span>
            <input aria-label="Search" className="pastel-search-input" placeholder="Search..." />
          </div>
          <div className="pastel-topbar-actions">
            <button className="pastel-icon-btn" aria-label="Notifications">
              <span className="pastel-icon duotone" aria-hidden="true">
                <span className="i i-bell"></span>
              </span>
            </button>
            <button className="pastel-avatar" aria-label="Profile">
              <div className="pastel-avatar-placeholder">{user?.username?.charAt(0).toUpperCase() || 'U'}</div>
            </button>
          </div>
        </header>

        {/* Content */}
        <section className="pastel-content">
          {/* Summary Cards */}
          <div className="pastel-cards">
            <article className="pastel-card">
              <div className="pastel-card-head">
                <div className="pastel-title">Total Users</div>
                <div className="pastel-value">24,582</div>
              </div>
              <canvas className="pastel-spark" ref={sparkUsersRef} height="40"></canvas>
            </article>
            <article className="pastel-card">
              <div className="pastel-card-head">
                <div className="pastel-title">Active Sessions</div>
                <div className="pastel-value">1,284</div>
              </div>
              <canvas className="pastel-spark" ref={sparkSessionsRef} height="40"></canvas>
            </article>
            <article className="pastel-card">
              <div className="pastel-card-head">
                <div className="pastel-title">Performance Analytics</div>
                <div className="pastel-value">98.6%</div>
              </div>
              <canvas className="pastel-spark" ref={sparkPerformanceRef} height="40"></canvas>
            </article>
          </div>

          {/* Users Table */}
          <div className="pastel-panel">
            <div className="pastel-panel-head">
              <h2 className="pastel-panel-title">Users</h2>
              <div className="pastel-panel-actions">
                <button className="pastel-btn primary">Add User</button>
              </div>
            </div>
            <div className="pastel-table-wrap">
              <table className="pastel-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th className="right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u, index) => (
                    <tr key={index}>
                      <td>{u.name}</td>
                      <td>{u.email}</td>
                      <td>{u.role}</td>
                      <td>{createStatusBadge(u.status)}</td>
                      <td className="right">
                        <div className="pastel-actions">
                          <button className="pastel-action-btn edit">Edit</button>
                          <button className="pastel-action-btn delete">Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default PastelDashboard;
