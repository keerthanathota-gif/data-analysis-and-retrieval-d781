# Quick Start Guide - Updated UI

## Overview
The CFR Pipeline System UI has been updated to match the Figma design with horizontal centered tabs and a beautiful gradient background.

## What's New

### Visual Updates
✨ **Soft Pastel Gradient Background** - Beautiful purple-to-blue gradient (`#e0c3fc` → `#8ec5fc`)  
✨ **Horizontal Tab Navigation** - Clean, centered pill-shaped tabs (Pipeline, Analysis, RAG Query)  
✨ **Professional Header** - Logo, title, and Sign Out button in a dedicated header bar  
✨ **Modern Card Design** - Enhanced shadows, rounded corners, and smooth transitions  

## Quick Start

### 1. Install Frontend Dependencies
```bash
cd /workspace/cpsc-regulation-system/frontend
npm install
```

### 2. Start Backend Server
```bash
cd /workspace/cpsc-regulation-system/backend
source env/bin/activate
python run.py
```

### 3. Start Frontend Development Server
```bash
cd /workspace/cpsc-regulation-system/frontend
npm start
```

The application will open at `http://localhost:3000`

## UI Components

### Header Section
- **Logo**: Purple gradient cube icon
- **Title**: "CFR Pipeline System"
- **Sign Out**: Easy access logout button

### Tab Navigation
Three main tabs centered horizontally:
1. **Pipeline** - Data pipeline control and database statistics
2. **Analysis** - Advanced regulation analysis (Redundancy/Parity/Overlap)
3. **RAG Query** - AI-powered semantic search interface

### Content Area
Each tab displays its own content with:
- Clean card-based layout
- Gradient backgrounds matching the Figma design
- Smooth transitions and hover effects
- Fully responsive design

## Tab Functionality

### Pipeline Tab
- View database statistics (Chapters, Regulations, Embeddings)
- Run data pipeline on CFR URLs
- Reset database
- Track pipeline progress in real-time

### Analysis Tab
- Analyze regulation relationships
- View corpus health score
- Filter by category (Redundancy, Parity, Overlap)
- Compare regulation texts side-by-side

### RAG Query Tab
- Ask natural language questions
- Adjust query settings (Temperature, Max Tokens)
- Search by level (Chapter, Subchapter, Section)
- View semantic search results

## Design System

### Colors
```css
Primary: #6366f1 (Indigo)
Secondary: #8b5cf6 (Purple)
Success: #10b981 (Green)
Warning: #f59e0b (Amber)
Danger: #ef4444 (Red)
```

### Background Gradients
```css
Body: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)
Content: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%)
```

### Typography
- Headers: 700 weight (Bold)
- Body: 600 weight (Semi-bold)
- Labels: 600 weight (Semi-bold)

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Mobile Responsive
✅ Header adapts to smaller screens  
✅ Tabs wrap on mobile devices  
✅ Touch-friendly button sizes  
✅ Optimized padding and spacing  

## Troubleshooting

### Tabs not showing correctly?
- Clear browser cache
- Ensure Font Awesome CDN is loaded (check Network tab)
- Verify all CSS files are loaded

### Background gradient not appearing?
- Check browser compatibility
- Ensure CssBaseline from MUI is loaded
- Verify index.js theme configuration

### Sign Out button not working?
- Check browser console for errors
- Verify localStorage is accessible
- Check authentication token

## Support
For issues or questions, please refer to:
- `UI_UPDATE_SUMMARY.md` - Detailed technical changes
- `README.md` - General project documentation

## Next Steps
1. Login to the system
2. Navigate between tabs to explore features
3. Test the data pipeline functionality
4. Try the RAG query interface
5. Explore the advanced analysis tools

Enjoy the new UI! 🎉
