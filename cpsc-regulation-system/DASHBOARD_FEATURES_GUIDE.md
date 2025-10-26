# Dashboard Features Guide

## Overview

After logging in, you'll see different features depending on your user role:

---

## 🔍 Regular User Dashboard

**Available to:** Users with `user` role  
**Access:** Login → Redirects to `/dashboard`

### Features:

### 1. **Search Regulations**
- Semantic AI-powered search through CPSC regulations
- Search box with query input
- Level filter dropdown:
  - All levels
  - Chapter
  - Subchapter  
  - Section
- Top 20 results returned

### 2. **View Search Results**
- Section numbers and subjects
- Similarity scores (color-coded):
  - Green: ≥80% match
  - Yellow: ≥60% match
  - Gray: <60% match
- Full text preview
- Citations
- Relevance ranking

---

## 🔧 Admin Dashboard

**Available to:** Users with `admin` role  
**Access:** Login → Redirects to `/dashboard` (admin sees admin panel)

The admin dashboard has **4 tabs**:

---

### Tab 1: 📈 Overview

Shows system statistics in card format:

| Metric | Description |
|--------|-------------|
| **Total Users** | Count of all registered users |
| **Active Users** | Count of active (non-deactivated) users |
| **Total Sections** | Number of regulation sections in database |
| **Total Chapters** | Number of chapters in database |

**Refresh:** Click any card to see updated stats

---

### Tab 2: 👥 Users Management

Manage all system users with a table view:

**Table Columns:**
- Username
- Email
- Role (Admin/User badge)
- Status (Active/Inactive badge)
- Actions (Activate/Deactivate button)

**Actions:**
- **Activate User:** Enable a deactivated user
- **Deactivate User:** Disable a user's access
- **Refresh:** Update the user list

**Note:** Cannot deactivate your own admin account

---

### Tab 3: 📋 Activity Logs

View all system activity in real-time:

**Log Information:**
- User ID
- Action performed (login, search, pipeline_run, etc.)
- Details (full description)
- IP Address
- Timestamp (local time format)

**Actions:**
- **Refresh:** Get latest activity logs
- **Filter by user:** (API supports filtering)

**Common Actions Logged:**
- `login` - User logged in
- `logout` - User logged out
- `search` - User performed a search
- `pipeline_run` - Admin started pipeline
- `pipeline_reset` - Admin reset database
- `user_activate` - Admin activated user
- `user_deactivate` - Admin deactivated user

---

### Tab 4: 🚀 Pipeline & Analysis ⭐

**This is the main data processing tab!**

#### **Pipeline Management Interface:**

```
┌─────────────────────────────────────────────────────┐
│ Pipeline URLs (one per line)                        │
│ ┌─────────────────────────────────────────────────┐ │
│ │ https://www.govinfo.gov/bulkdata/CFR/2025/...   │ │
│ │                                                 │ │
│ │                                                 │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ [Run Pipeline]  [Reset Pipeline]                   │
│                                                     │
│ Pipeline Status                                     │
│ ● running  Progress: 45%                           │
│ Current Step: Generating embeddings...             │
└─────────────────────────────────────────────────────┘
```

#### **Features:**

1. **URL Configuration**
   - Text area to input URLs (one per line)
   - Default URL: `https://www.govinfo.gov/bulkdata/CFR/2025/title-16/`
   - Can add multiple URLs for batch processing

2. **Run Pipeline Button**
   - Starts the full data processing pipeline
   - Shows loading indicator while running
   - Polls for status updates every 2 seconds
   - Processes:
     1. Crawl CFR data from URLs
     2. Parse XML documents
     3. Extract regulation structure
     4. Generate AI embeddings
     5. Store in database
     6. Create indexes

3. **Reset Pipeline Button**
   - **Warning:** Deletes all data!
   - Clears CFR database
   - Removes processed files
   - Requires confirmation
   - Use when starting fresh

4. **Pipeline Status Display**
   - **State badges:**
     - `idle` (gray) - Not running
     - `running` (yellow) - In progress
     - `completed` (green) - Finished successfully
     - `error` (red) - Failed
   
   - **Progress Information:**
     - Percentage complete (0-100%)
     - Current step description
     - Error messages (if failed)

#### **Pipeline Process Steps:**

The pipeline goes through 6 main steps:

```
Step 1: Starting → Initialize pipeline
Step 2: Crawling → Download CFR data
Step 3: Parsing → Extract XML content  
Step 4: Embedding → Generate AI vectors
Step 5: Storing → Save to database
Step 6: Indexing → Create search indexes
```

**Typical Duration:** 5-15 minutes depending on data size

---

## 📊 Additional Analysis Features (Backend API)

While not shown in the current UI tabs, these are available via the backend:

### 1. **Semantic Analysis**
- Endpoint: `POST /admin/analysis/run`
- Parameters: `level` (chapter/subchapter/section)
- Returns: Similarity analysis between items
- Can be added to UI in future

### 2. **Clustering Analysis**
- Endpoint: `POST /admin/clustering/run`
- Parameters: 
  - `level` (chapter/subchapter/section)
  - `n_clusters` (number of groups)
- Returns: K-means clustering results
- Groups similar regulations together

---

## 🔐 Access Control

| Feature | Regular User | Admin |
|---------|--------------|-------|
| Search Regulations | ✅ Yes | ✅ Yes |
| View Results | ✅ Yes | ✅ Yes |
| View Statistics | ❌ No | ✅ Yes |
| Manage Users | ❌ No | ✅ Yes |
| View Activity Logs | ❌ No | ✅ Yes |
| Run Pipeline | ❌ No | ✅ Yes |
| Reset Database | ❌ No | ✅ Yes |
| Run Analysis | ❌ No | ✅ Yes |

---

## 🎯 Common Workflows

### For Regular Users:

1. **Login** → Enter credentials
2. **Search** → Type query (e.g., "toy safety requirements")
3. **Review** → Check similarity scores and results
4. **Explore** → Click sections for full details

### For Admins:

#### First Time Setup:
1. **Login** as admin
2. **Go to Pipeline tab** (Tab 4)
3. **Check URL** is correct
4. **Click "Run Pipeline"**
5. **Wait** for completion (watch progress)
6. **Verify** data loaded (check Overview stats)

#### Regular Administration:
1. **Monitor Overview** - Check system health
2. **Manage Users** - Activate/deactivate as needed
3. **Review Logs** - Track system usage
4. **Re-run Pipeline** - Update data periodically

#### Troubleshooting:
1. **Check Activity Logs** for errors
2. **View Pipeline Status** for processing issues
3. **Reset Pipeline** if data is corrupted
4. **Re-run Pipeline** to refresh data

---

## 📸 UI Elements

### Dashboard Layout:

```
┌─────────────────────────────────────────────────────────────┐
│  CPSC Regulation System                     [Logout] [User] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Admin Dashboard                                            │
│                                                             │
│  [Overview] [Users] [Activity Logs] [Pipeline]  ← Tabs     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━             │
│                                                             │
│  [Content based on selected tab]                           │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Button States:

- **Enabled:** Full color, clickable
- **Disabled:** Gray, shows loading spinner if processing
- **Success:** Green confirmation message
- **Error:** Red error alert with message

---

## 🚀 Quick Reference

### To Run Pipeline:
1. Login as admin
2. Click "Pipeline" tab
3. Click "Run Pipeline"
4. Wait for completion

### To View Data:
1. Check "Overview" for counts
2. Use search (as regular user would)
3. Verify results appear

### To Manage Users:
1. Click "Users" tab
2. See all registered users
3. Activate/Deactivate as needed

### To Monitor System:
1. Click "Activity Logs" tab
2. Review recent actions
3. Look for errors or unusual activity

---

## 🔔 Status Indicators

### Pipeline States:

| State | Badge Color | Meaning | Action |
|-------|-------------|---------|--------|
| `idle` | Gray | Ready to run | Can start pipeline |
| `running` | Yellow | Processing | Wait for completion |
| `completed` | Green | Finished | Data ready to use |
| `error` | Red | Failed | Check logs, try again |

### User States:

| State | Badge Color | Can Login? |
|-------|-------------|------------|
| Active | Green | ✅ Yes |
| Inactive | Gray | ❌ No |

---

## 💡 Tips

1. **First Time:** Run pipeline immediately after setup to populate data
2. **Regular Updates:** Re-run pipeline monthly to get latest CFR data
3. **Before Reset:** Export important data (pipeline reset deletes everything)
4. **Monitor Progress:** Pipeline shows real-time updates every 2 seconds
5. **Check Logs:** Activity logs help diagnose issues
6. **User Management:** Deactivate users instead of deleting (preserves history)

---

## 🐛 Troubleshooting

### Pipeline Won't Start:
- Check if already running (only one instance at a time)
- Verify URL is accessible
- Check backend logs for errors

### No Search Results:
- Ensure pipeline has completed successfully
- Check Overview tab for section count (should be > 0)
- Try different search terms

### Can't See Admin Features:
- Verify logged in as admin (not regular user)
- Check role in Users tab
- Logout and login again

---

## 📚 Related Documentation

- **Backend API:** http://localhost:8000/api/docs
- **Configuration:** BACKEND_FRONTEND_CONFIG_REPORT.md
- **Quick Start:** QUICK_START_GUIDE.md
- **Login Help:** LOGIN_ISSUES_RESOLVED.md

---

**Last Updated:** October 26, 2025  
**Version:** 2.0.0
