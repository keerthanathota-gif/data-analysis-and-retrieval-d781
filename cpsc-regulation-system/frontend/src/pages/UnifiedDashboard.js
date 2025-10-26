import React, { useState, useEffect } from 'react';
import {
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
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Assessment as AssessmentIcon,
  Science as ScienceIcon
} from '@mui/icons-material';
import { adminService } from '../services/adminService';
import { searchService } from '../services/searchService';

const UnifiedDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pipelineUrls, setPipelineUrls] = useState(['https://www.govinfo.gov/bulkdata/CFR/2025/title-16/']);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLevel, setSearchLevel] = useState('all');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

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
      console.error('Failed to load stats:', err);
    }
  };

  const loadUsers = async () => {
    try {
      const data = await adminService.getUsers();
      setUsers(data);
    } catch (err) {
      console.error('Failed to load users:', err);
    }
  };

  const loadActivityLogs = async () => {
    try {
      const data = await adminService.getActivityLogs();
      setActivityLogs(data);
    } catch (err) {
      console.error('Failed to load activity logs:', err);
    }
  };

  const loadPipelineStatus = async () => {
    try {
      const data = await adminService.getPipelineStatus();
      setPipelineStatus(data);
    } catch (err) {
      console.error('Failed to load pipeline status:', err);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setError('');

    try {
      const results = await searchService.searchRegulations(searchQuery, searchLevel, 20);
      setSearchResults(results.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
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
          loadStats(); // Refresh stats after pipeline completes
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

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'default';
  };

  return (
    <Box sx={{ width: '100%', p: { xs: 2, md: 3 } }}>
      <Typography variant="h4" component="h1" gutterBottom>
        CFR Regulation System Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab icon={<SearchIcon />} label="Search" />
          <Tab icon={<PlayIcon />} label="Pipeline" />
          <Tab icon={<ScienceIcon />} label="Analysis" />
          <Tab icon={<PersonIcon />} label="Users" />
          <Tab icon={<AssessmentIcon />} label="Activity" />
        </Tabs>
      </Paper>

      {/* Tab 0: Search */}
      {activeTab === 0 && (
        <Box>
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              Search CFR Regulations
            </Typography>
            <Box display="flex" gap={2} alignItems="center" mb={2}>
              <TextField
                fullWidth
                label="Search regulations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your search query (e.g., 'safety requirements for toys')"
              />
              <TextField
                select
                label="Level"
                value={searchLevel}
                onChange={(e) => setSearchLevel(e.target.value)}
                sx={{ minWidth: 120 }}
                SelectProps={{ native: true }}
              >
                <option value="all">All</option>
                <option value="chapter">Chapter</option>
                <option value="subchapter">Subchapter</option>
                <option value="section">Section</option>
              </TextField>
              <Button
                variant="contained"
                onClick={handleSearch}
                disabled={searchLoading || !searchQuery.trim()}
                startIcon={searchLoading ? <CircularProgress size={20} /> : <SearchIcon />}
              >
                Search
              </Button>
            </Box>
          </Paper>

          {searchResults.length > 0 && (
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Search Results ({searchResults.length} found)
              </Typography>
              <List>
                {searchResults.map((result, index) => (
                  <React.Fragment key={index}>
                    <ListItem alignItems="flex-start">
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle1" component="span">
                              {result.section_number || result.name}
                            </Typography>
                            {result.similarity_score && (
                              <Chip
                                label={`${(result.similarity_score * 100).toFixed(1)}%`}
                                color={getSimilarityColor(result.similarity_score)}
                                size="small"
                              />
                            )}
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                              {result.subject || result.text?.substring(0, 200) + '...'}
                            </Typography>
                            {result.citation && (
                              <Typography variant="caption" color="textSecondary">
                                Citation: {result.citation}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < searchResults.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          )}
        </Box>
      )}

      {/* Tab 1: Pipeline */}
      {activeTab === 1 && (
        <Box>
          <Grid container spacing={3} mb={3}>
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
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <ScienceIcon color="success" sx={{ mr: 1 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Subchapters
                      </Typography>
                      <Typography variant="h4">
                        {stats?.total_subchapters || 0}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Paper elevation={2} sx={{ p: 3 }}>
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
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={loadPipelineStatus}
                >
                  Refresh Status
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
        </Box>
      )}

      {/* Tab 2: Analysis */}
      {activeTab === 2 && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Analysis & Clustering
          </Typography>
          <Typography variant="body1" color="textSecondary" paragraph>
            Run semantic analysis and clustering on regulations.
          </Typography>
          <Box display="flex" gap={2}>
            <Button
              variant="contained"
              onClick={() => alert('Analysis feature - Coming soon! Use API: POST /admin/analysis/run')}
            >
              Run Analysis
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={() => alert('Clustering feature - Coming soon! Use API: POST /admin/clustering/run')}
            >
              Run Clustering
            </Button>
          </Box>
        </Paper>
      )}

      {/* Tab 3: Users */}
      {activeTab === 3 && (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Users Management</Typography>
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
                        size="small"
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

      {/* Tab 4: Activity */}
      {activeTab === 4 && (
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
    </Box>
  );
};

export default UnifiedDashboard;
