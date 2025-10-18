import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Chip,
  Divider
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { searchService } from '../services/searchService';

const UserDashboard = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLevel, setSearchLevel] = useState('all');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError('');

    try {
      const results = await searchService.searchRegulations(searchQuery, searchLevel, 20);
      setSearchResults(results.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'default';
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Search CPSC Regulations
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
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
          >
            <option value="all">All</option>
            <option value="chapter">Chapter</option>
            <option value="subchapter">Subchapter</option>
            <option value="section">Section</option>
          </TextField>
          <Button
            variant="contained"
            onClick={handleSearch}
            disabled={loading || !searchQuery.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
          >
            Search
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
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

      {searchResults.length === 0 && !loading && searchQuery && (
        <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary">
            No results found for "{searchQuery}"
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Try different keywords or check the spelling
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default UserDashboard;