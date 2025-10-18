import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { adminService } from '../services/adminService';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pipelineUrls, setPipelineUrls] = useState(['https://www.govinfo.gov/bulkdata/CFR/2025/title-16/']);

  useEffect(() => {
    loadStats();
    loadUsers();
    loadActivityLogs();
    loadPipelineStatus();
  }, []);

  const loadStats = async () => {
    try {
      const data = await adminService.getStats();
      setStats(data);
    } catch (err) {
      setError('Failed to load statistics');
    }
  };

  const loadUsers = async () => {
    try {
      const data = await adminService.getUsers();
      setUsers(data);
    } catch (err) {
      setError('Failed to load users');
    }
  };

  const loadActivityLogs = async () => {
    try {
      const data = await adminService.getActivityLogs();
      setActivityLogs(data);
    } catch (err) {
      setError('Failed to load activity logs');
    }
  };

  const loadPipelineStatus = async () => {
    try {
      const data = await adminService.getPipelineStatus();
      setPipelineStatus(data);
    } catch (err) {
      setError('Failed to load pipeline status');
    }
  };

  const handleRunPipeline = async () => {
    setLoading(true);
    try {
      await adminService.runPipeline(pipelineUrls);
      setError('');
      // Poll for status updates
      const interval = setInterval(async () => {
        const status = await adminService.getPipelineStatus();
        setPipelineStatus(status);
        if (status.state === 'completed' || status.state === 'error') {
          clearInterval(interval);
          setLoading(false);
        }
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run pipeline');
      setLoading(false);
    }
  };

  const handleResetPipeline = async () => {
    if (window.confirm('Are you sure you want to reset the entire pipeline? This will delete all data.')) {
      setLoading(true);
      try {
        await adminService.resetPipeline();
        setError('');
        loadStats();
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to reset pipeline');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleUserAction = async (userId, action) => {
    try {
      if (action === 'activate') {
        await adminService.activateUser(userId);
      } else if (action === 'deactivate') {
        await adminService.deactivateUser(userId);
      }
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'warning';
      case 'completed': return 'success';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Admin Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Overview" />
          <Tab label="Users" />
          <Tab label="Activity Logs" />
          <Tab label="Pipeline" />
        </Tabs>
      </Paper>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <PersonIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Users
                    </Typography>
                    <Typography variant="h4">
                      {stats?.total_users || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <PersonIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Active Users
                    </Typography>
                    <Typography variant="h4">
                      {stats?.active_users || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <SearchIcon color="info" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Sections
                    </Typography>
                    <Typography variant="h4">
                      {stats?.total_sections || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <AssessmentIcon color="secondary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Chapters
                    </Typography>
                    <Typography variant="h4">
                      {stats?.total_chapters || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Users</Typography>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadUsers}
            >
              Refresh
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Username</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip
                        label={user.role}
                        color={user.role === 'admin' ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_active ? 'Active' : 'Inactive'}
                        color={user.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        onClick={() => handleUserAction(user.id, user.is_active ? 'deactivate' : 'activate')}
                        color={user.is_active ? 'error' : 'success'}
                      >
                        {user.is_active ? <StopIcon /> : <PlayIcon />}
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {activeTab === 2 && (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Activity Logs</Typography>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadActivityLogs}
            >
              Refresh
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Details</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>Timestamp</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {activityLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>{log.user_id}</TableCell>
                    <TableCell>
                      <Chip label={log.action} size="small" />
                    </TableCell>
                    <TableCell>{log.details}</TableCell>
                    <TableCell>{log.ip_address}</TableCell>
                    <TableCell>
                      {new Date(log.created_at).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {activeTab === 3 && (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Pipeline Management
          </Typography>
          
          <Box mb={3}>
            <TextField
              fullWidth
              label="Pipeline URLs (one per line)"
              multiline
              rows={3}
              value={pipelineUrls.join('\n')}
              onChange={(e) => setPipelineUrls(e.target.value.split('\n').filter(url => url.trim()))}
              sx={{ mb: 2 }}
            />
            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
                onClick={handleRunPipeline}
                disabled={loading}
              >
                Run Pipeline
              </Button>
              <Button
                variant="outlined"
                color="error"
                onClick={handleResetPipeline}
                disabled={loading}
              >
                Reset Pipeline
              </Button>
            </Box>
          </Box>

          {pipelineStatus && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Pipeline Status
              </Typography>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Chip
                  label={pipelineStatus.state}
                  color={getStatusColor(pipelineStatus.state)}
                />
                <Typography variant="body2">
                  Progress: {pipelineStatus.progress}%
                </Typography>
              </Box>
              {pipelineStatus.current_step && (
                <Typography variant="body2" color="textSecondary">
                  Current Step: {pipelineStatus.current_step}
                </Typography>
              )}
              {pipelineStatus.error_message && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {pipelineStatus.error_message}
                </Alert>
              )}
            </Box>
          )}
        </Paper>
      )}
    </Container>
  );
};

export default AdminDashboard;