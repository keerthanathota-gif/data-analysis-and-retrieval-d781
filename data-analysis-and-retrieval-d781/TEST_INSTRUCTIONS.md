# 🧪 Testing with Title-4 CFR Data

## 📋 Test URL

```
https://www.govinfo.gov/bulkdata/CFR/2024/title-4
```

This will download and process **Title 4 - Flag and Seal, Seat of Government, and the States** from the 2024 Code of Federal Regulations.

---

## 🚀 Step-by-Step Testing Guide

### **Prerequisites**

1. ✅ Dependencies installed
   ```powershell
   pip install -r requirements.txt
   ```

2. ✅ Server running
   ```powershell
   python run.py
   ```

3. ✅ Browser open
   ```
   http://localhost:8000/ui
   ```

---

## 📊 **Test 1: Data Pipeline**

### **Step 1: Open Pipeline Tab**

Click on the **"Pipeline"** tab in the web UI.

---

### **Step 2: Enter URL**

In the URL input field, enter:
```
https://www.govinfo.gov/bulkdata/CFR/2024/title-4
```

**What this downloads:**
- **Title:** 4 - Flag and Seal, Seat of Government, and the States
- **Year:** 2024
- **Format:** ZIP file containing XML data
- **Expected size:** ~500KB - 2MB

---

### **Step 3: Run Pipeline**

Click **"Run Complete Pipeline"** button.

---

### **Step 4: Watch Progress**

You should see a **real-time progress bar** updating:

```
Pipeline Started!
Processing 1 URL(s)

[████░░░░░░░░░░░░░░░░] 17%
Crawling data... (17%)

[████████░░░░░░░░░░░░] 33%
Parsing XML... (33%)

[████████████░░░░░░░░] 50%
Storing in database... (50%)

[████████████████░░░░] 67%
Generating embeddings... (67%)

[████████████████████] 83%
Calculating statistics... (83%)

[████████████████████] 100%
✅ Completed! (100%)
```

**Status updates every 2 seconds!**

---

### **Step 5: View Statistics**

After completion, statistics will **automatically display**:

```
✅ Pipeline Completed Successfully!

Statistics:
┌──────────┬─────────┬──────────────┬──────────┐
│ Chapters │ Parts   │ Subchapters  │ Sections │
├──────────┼─────────┼──────────────┼──────────┤
│    3     │   15    │      8       │   250    │
└──────────┴─────────┴──────────────┴──────────┘
```

*(Numbers will vary based on actual Title 4 content)*

---

### **Expected Timeline:**

| Step | Duration |
|------|----------|
| Download ZIP | 10-30 seconds |
| Extract XML | 5-10 seconds |
| Parse XML | 30-60 seconds |
| Store in DB | 20-40 seconds |
| Generate Embeddings | 1-3 minutes |
| Calculate Stats | 5-10 seconds |
| **Total** | **2-5 minutes** |

---

## 📊 **Test 2: Clustering**

After pipeline completes, test clustering:

### **Step 1: Go to Clustering Tab**

Click **"Clustering"** tab.

---

### **Step 2: Select Level**

Choose **"Section Level"** from dropdown.

---

### **Step 3: Set Clusters**

Set number of clusters: **3-5** (recommended for Title 4)

---

### **Step 4: Perform Clustering**

Click **"Perform Clustering"** button.

---

### **Step 5: Wait for LLM**

**First time:** 30-60 seconds (downloads FLAN-T5-base model ~900MB)  
**Subsequent:** 20-30 seconds

---

### **Step 6: View Results**

You should see **content-based summaries** like:

```
Cluster 1: "Flag Display and Protocol Standards"
[45 sections]

Summary: "This cluster encompasses regulations governing the 
display of the United States flag including proper protocols 
for raising and lowering, positioning relative to other flags, 
display during holidays and special occasions, flag dimensions 
and specifications, and penalties for improper flag usage."

Items: Section 1-45 with actual flag regulation content
```

```
Cluster 2: "Federal Property and Seal Usage"
[32 sections]

Summary: "Regulations covering the use of federal seals and 
emblems, proper display of governmental insignia, authorized 
reproductions of official symbols, restrictions on commercial 
use, and enforcement provisions for unauthorized usage."

Items: Section 46-77 with seal and emblem regulations
```

---

## 🔍 **Test 3: Analysis**

### **Step 1: Go to Analysis Tab**

Click **"Analysis"** tab.

---

### **Step 2: Select Level**

Choose **"Section Level"**.

---

### **Step 3: Run Analysis**

Click **"Run Analysis"** button.

Wait 20-40 seconds.

---

### **Step 4: View Results**

You'll see:
- **Similarity Score:** How similar sections are
- **Overlap Detection:** Sections with overlapping content
- **Redundancy Check:** Duplicate or highly similar sections
- **Parity Validation:** Structural consistency checks

---

### **Step 5: Click Results**

Click any result row to see:
- **Detailed similarity score**
- **Overlap data**
- **LLM justification** explaining why sections are similar

**Example:**
```
Section 1 vs Section 5
Similarity: 85%

Justification: "These sections are highly similar because 
both address flag display protocols during federal holidays. 
Section 1 establishes general holiday display requirements 
while Section 5 provides specific instructions for Memorial 
Day observances."
```

---

## 🔎 **Test 4: RAG Query**

### **Step 1: Go to RAG Query Tab**

Click **"RAG Query"** tab.

---

### **Step 2: Enter Query**

Try these example queries:

```
"flag display requirements"
```

```
"federal seal usage"
```

```
"state government protocols"
```

---

### **Step 3: Search**

Click **"Search"** button.

---

### **Step 4: View Results**

You'll see **top-10 most relevant sections** with:
- Section number
- Subject/title
- Similarity score
- Snippet of content

---

### **Step 5: Click Section**

Click any section to see:
- **Full text**
- **Citation**
- **Section label**
- **Hierarchy** (Chapter → Subchapter → Part → Section)

---

## 📈 **Test 5: Visualizations**

### **Step 1: Go to Visualizations Tab**

Click **"Visualizations"** tab.

---

### **Step 2: View Available Visualizations**

You should see charts like:
- **Cluster scatter plots** (t-SNE, PCA)
- **Similarity heatmaps**
- **Interactive Plotly charts**

---

### **Step 3: Click to View**

Click any visualization to see full-screen interactive chart.

---

## ✅ **Expected Results**

### **Pipeline:**
- ✅ Progress bar updates smoothly
- ✅ Stats display automatically
- ✅ Files created in `cfr_data/` folder
- ✅ Database file `cfr_data.db` created
- ✅ JSON/CSV files in `output/` folder

### **Clustering:**
- ✅ 3-5 clusters generated
- ✅ Each cluster has meaningful name
- ✅ Summaries mention actual flag/seal topics
- ✅ Summaries are detailed (50+ words)

### **Analysis:**
- ✅ Results show similarity scores
- ✅ LLM justifications present
- ✅ Can identify overlapping sections

### **RAG:**
- ✅ Search returns relevant results
- ✅ Similarity scores accurate
- ✅ Section details complete

### **Visualizations:**
- ✅ Charts generated
- ✅ Files in `visualizations/` folder
- ✅ Interactive and zoomable

---

## 📂 **Files Generated**

After running the pipeline with title-4:

```
cfr_data/
├── CFR-2024-title-4.zip          # Downloaded ZIP
└── CFR-2024-title4-vol1.xml      # Extracted XML

output/
├── title4_parsed.json            # Parsed JSON
└── title4_parsed.csv             # Parsed CSV

visualizations/
├── cluster_tsne_section.png      # t-SNE plot
├── cluster_pca_section.png       # PCA plot
└── cluster_plotly_section.html   # Interactive chart

cfr_data.db                       # SQLite database
```

---

## 🐛 **Troubleshooting**

### **Issue: "Download failed"**

**Check:**
- Internet connection
- URL is correct
- govinfo.gov is accessible

**Try:**
- Different URL: `https://www.govinfo.gov/bulkdata/CFR/2024/title-16`

---

### **Issue: "Slow embeddings"**

**Normal:** First time generates embeddings for all sections (~2-3 minutes for Title 4)

**Speed up:**
- Use GPU if available
- Reduce sections by using smaller title

---

### **Issue: "LLM download slow"**

**Normal:** First clustering downloads FLAN-T5-base (~900MB)

**Wait:** 1-2 minutes for download

**Subsequent:** Much faster (model cached)

---

### **Issue: "Out of memory"**

**Reduce clusters:**
```python
# Edit app/config.py:
DEFAULT_N_CLUSTERS = 3  # Instead of 5
```

**Or use smaller title:**
```
https://www.govinfo.gov/bulkdata/CFR/2024/title-4  # Smaller
Instead of:
https://www.govinfo.gov/bulkdata/CFR/2024/title-16 # Larger
```

---

## 📊 **Title 4 Content Overview**

**Title 4: Flag and Seal, Seat of Government, and the States**

**Typical structure:**
- **3-5 Chapters**
- **8-12 Subchapters**
- **15-25 Parts**
- **200-300 Sections**

**Topics covered:**
- Flag of the United States
- Seal of the United States
- Seat of government (District of Columbia)
- The States (admission procedures)

**Good for testing because:**
- ✅ Moderate size (not too large)
- ✅ Clear topics (easy to verify clustering)
- ✅ Well-structured content
- ✅ Fast download (~1-2 MB)

---

## 🎯 **Success Criteria**

After testing with Title 4, you should have:

- [x] Pipeline completed successfully
- [x] ~200-300 sections in database
- [x] 3-5 meaningful clusters
- [x] Cluster summaries mention flag/seal topics
- [x] RAG search finds relevant sections
- [x] Visualizations generated
- [x] No errors in console

---

## 🚀 **Next Steps**

After successfully testing Title 4:

1. **Try other titles:**
   - Title 16 (larger dataset)
   - Title 1 (very small, fast)
   - Title 12 (banking regulations)

2. **Explore features:**
   - Test different cluster numbers
   - Try various search queries
   - Compare similarity results

3. **Customize:**
   - Adjust thresholds in `app/config.py`
   - Modify clustering algorithm
   - Add custom analysis

---

**Ready to test! Just run `python run.py` and enter the URL!** 🎉
