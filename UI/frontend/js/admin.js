/**
 * Admin Panel JavaScript
 * Handles all admin-specific functionality
 */

// ============================================
// SECTION NAVIGATION
// ============================================

function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Remove active class from all nav links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Add active class to clicked nav link
    const activeLink = document.querySelector(`.nav-links a[onclick="showSection('${sectionName}')"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }

    // Load data for specific sections
    if (sectionName === 'users') {
        loadUsers();
    } else if (sectionName === 'logs') {
        loadAuditLogs();
    }
}

// ============================================
// STATISTICS
// ============================================

async function loadAdminStats() {
    try {
        const stats = await StatsAPI.getOverview();
        const users = await AuthAPI.listUsers();

        document.getElementById('statChapters').textContent = stats.chapters || 0;
        document.getElementById('statSubchapters').textContent = stats.subchapters || 0;
        document.getElementById('statSections').textContent = stats.sections || 0;
        document.getElementById('statUsers').textContent = users.length || 0;
    } catch (error) {
        console.error('Failed to load admin stats:', error);
    }
}

// ============================================
// PIPELINE OPERATIONS
// ============================================

async function runPipeline() {
    const url = document.getElementById('pipelineUrl').value.trim();
    const pipelineMessage = document.getElementById('pipelineMessage');
    const pipelineProgress = document.getElementById('pipelineProgress');

    if (!url) {
        pipelineMessage.textContent = 'Please enter a valid URL';
        pipelineMessage.style.color = 'red';
        return;
    }

    pipelineMessage.textContent = 'Starting pipeline...';
    pipelineMessage.style.color = 'blue';
    pipelineProgress.style.display = 'block';

    try {
        const result = await PipelineAPI.runPipeline(url);
        pipelineMessage.textContent = result.message || 'Pipeline completed successfully';
        pipelineMessage.style.color = 'green';
        setTimeout(() => {
            pipelineProgress.style.display = 'none';
        }, 2000);
    } catch (error) {
        pipelineMessage.textContent = `Pipeline failed: ${error.message}`;
        pipelineMessage.style.color = 'red';
        pipelineProgress.style.display = 'none';
        console.error('Pipeline error:', error);
    }
}

// ============================================
// CLUSTERING OPERATIONS
// ============================================

async function performClustering() {
    const level = document.getElementById('clusterLevel').value;
    const numClusters = parseInt(document.getElementById('clusterCount').value);
    const resultsBox = document.getElementById('clusteringResults');

    resultsBox.innerHTML = '<p>Performing clustering...</p>';

    try {
        const result = await ClusteringAPI.performClustering(level, numClusters);

        let html = '<div class="success-message">Clustering completed successfully</div>';
        html += '<div class="clustering-summary">';
        html += `<p><strong>Level:</strong> ${level}</p>`;
        html += `<p><strong>Number of Clusters:</strong> ${numClusters}</p>`;
        html += `<p><strong>Items Clustered:</strong> ${result.items_clustered || 0}</p>`;
        html += '</div>';

        resultsBox.innerHTML = html;
    } catch (error) {
        resultsBox.innerHTML = `<p class="error">Clustering failed: ${error.message}</p>`;
        console.error('Clustering error:', error);
    }
}

// ============================================
// ANALYSIS OPERATIONS
// ============================================

async function runSimilarityAnalysis() {
    const level = document.getElementById('analysisLevel').value;
    const resultsBox = document.getElementById('analysisResults');

    resultsBox.innerHTML = '<p>Running similarity analysis...</p>';

    try {
        const result = await AnalysisAPI.runSimilarity(level);
        resultsBox.innerHTML = `<div class="success-message">${result.message || 'Similarity analysis completed'}</div>`;
    } catch (error) {
        resultsBox.innerHTML = `<p class="error">Analysis failed: ${error.message}</p>`;
        console.error('Analysis error:', error);
    }
}

async function checkOverlaps() {
    const level = document.getElementById('analysisLevel').value;
    const resultsBox = document.getElementById('analysisResults');

    resultsBox.innerHTML = '<p>Checking for overlaps...</p>';

    try {
        const result = await AnalysisAPI.checkOverlaps(level);
        resultsBox.innerHTML = `<div class="success-message">${result.message || 'Overlap check completed'}</div>`;
    } catch (error) {
        resultsBox.innerHTML = `<p class="error">Overlap check failed: ${error.message}</p>`;
        console.error('Overlap check error:', error);
    }
}

async function checkRedundancy() {
    const level = document.getElementById('analysisLevel').value;
    const resultsBox = document.getElementById('analysisResults');

    resultsBox.innerHTML = '<p>Checking for redundancy...</p>';

    try {
        const result = await AnalysisAPI.checkRedundancy(level);
        resultsBox.innerHTML = `<div class="success-message">${result.message || 'Redundancy check completed'}</div>`;
    } catch (error) {
        resultsBox.innerHTML = `<p class="error">Redundancy check failed: ${error.message}</p>`;
        console.error('Redundancy check error:', error);
    }
}

// ============================================
// RAG SEARCH
// ============================================

async function performSearch() {
    const query = document.getElementById('ragQuery').value.trim();
    const searchResults = document.getElementById('searchResults');

    if (!query) {
        searchResults.innerHTML = '<p class="error">Please enter a search query</p>';
        return;
    }

    searchResults.innerHTML = '<p>Searching...</p>';

    try {
        const results = await RAGAPI.search(query, 5);

        if (results.results && results.results.length > 0) {
            let html = '<div class="search-results-list">';
            results.results.forEach((result, index) => {
                html += `
                    <div class="search-result-item">
                        <h4>${index + 1}. ${result.title || 'Untitled'}</h4>
                        <p class="result-score">Relevance: ${(result.score * 100).toFixed(1)}%</p>
                        <p class="result-content">${result.content || result.text || 'No content available'}</p>
                    </div>
                `;
            });
            html += '</div>';
            searchResults.innerHTML = html;
        } else {
            searchResults.innerHTML = '<p>No results found</p>';
        }
    } catch (error) {
        searchResults.innerHTML = '<p class="error">Search failed. Please try again.</p>';
        console.error('Search error:', error);
    }
}

// ============================================
// USER MANAGEMENT
// ============================================

async function loadUsers() {
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = '<tr><td colspan="6">Loading users...</td></tr>';

    try {
        const users = await AuthAPI.listUsers();

        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No users found</td></tr>';
            return;
        }

        let html = '';
        users.forEach(user => {
            html += `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td><span class="badge-${user.role}">${user.role}</span></td>
                    <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                    <td>${new Date(user.created_at).toLocaleDateString()}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" class="error">Failed to load users</td></tr>';
        console.error('Failed to load users:', error);
    }
}

// Create User Form Handler
if (document.getElementById('createUserForm')) {
    document.getElementById('createUserForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const userData = {
            username: document.getElementById('newUsername').value,
            email: document.getElementById('newEmail').value,
            password: document.getElementById('newPassword').value,
            role: document.getElementById('newRole').value
        };

        try {
            await AuthAPI.createUser(userData);
            alert('User created successfully');
            document.getElementById('createUserForm').reset();
            loadUsers();  // Refresh user list
        } catch (error) {
            alert(`Failed to create user: ${error.message}`);
            console.error('User creation error:', error);
        }
    });
}

// ============================================
// AUDIT LOGS
// ============================================

async function loadAuditLogs() {
    const tbody = document.querySelector('#logsTable tbody');
    tbody.innerHTML = '<tr><td colspan="5">Loading audit logs...</td></tr>';

    try {
        const logs = await AuthAPI.getAuditLogs(100);

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No logs found</td></tr>';
            return;
        }

        let html = '';
        logs.forEach(log => {
            html += `
                <tr>
                    <td>${new Date(log.timestamp).toLocaleString()}</td>
                    <td>${log.username}</td>
                    <td>${log.action}</td>
                    <td>${log.endpoint || 'N/A'}</td>
                    <td>${log.details || 'N/A'}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="5" class="error">Failed to load audit logs</td></tr>';
        console.error('Failed to load audit logs:', error);
    }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Load admin stats on page load
    loadAdminStats();
});
