/**
 * User Dashboard JavaScript
 * Handles dashboard interactions and data display for regular users
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
    if (sectionName === 'stats') {
        loadDetailedStats();
    }
}

// ============================================
// LOAD STATISTICS
// ============================================

async function loadQuickStats() {
    try {
        const stats = await StatsAPI.getOverview();

        document.getElementById('statChapters').textContent = stats.chapters || 0;
        document.getElementById('statSubchapters').textContent = stats.subchapters || 0;
        document.getElementById('statSections').textContent = stats.sections || 0;
    } catch (error) {
        console.error('Failed to load quick stats:', error);
    }
}

async function loadDetailedStats() {
    const detailedStats = document.getElementById('detailedStats');
    detailedStats.innerHTML = '<p>Loading statistics...</p>';

    try {
        const stats = await StatsAPI.getDetailed('all');

        let html = '<div class="stats-details">';
        html += `<h3>Database Statistics</h3>`;
        html += `<p><strong>Total Chapters:</strong> ${stats.total_chapters || 0}</p>`;
        html += `<p><strong>Total Subchapters:</strong> ${stats.total_subchapters || 0}</p>`;
        html += `<p><strong>Total Sections:</strong> ${stats.total_sections || 0}</p>`;
        html += `<p><strong>Total Documents:</strong> ${stats.total_documents || 0}</p>`;
        html += `<p><strong>Last Updated:</strong> ${stats.last_updated || 'N/A'}</p>`;
        html += '</div>';

        detailedStats.innerHTML = html;
    } catch (error) {
        detailedStats.innerHTML = '<p class="error">Failed to load statistics</p>';
        console.error('Failed to load detailed stats:', error);
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
                        ${result.metadata ? `<p class="result-metadata"><small>${JSON.stringify(result.metadata)}</small></p>` : ''}
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
// RESULTS VIEWING
// ============================================

async function showResults(resultType) {
    const resultsContent = document.getElementById('resultsContent');
    const tabs = document.querySelectorAll('.tab-btn');

    // Update active tab
    tabs.forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');

    resultsContent.innerHTML = '<p>Loading results...</p>';

    try {
        if (resultType === 'clustering') {
            const results = await ClusteringAPI.getResults('all');
            displayClusteringResults(results);
        } else if (resultType === 'similarity') {
            const results = await AnalysisAPI.getResults('similarity', 'all');
            displaySimilarityResults(results);
        }
    } catch (error) {
        resultsContent.innerHTML = '<p class="error">Failed to load results</p>';
        console.error('Failed to load results:', error);
    }
}

function displayClusteringResults(results) {
    const resultsContent = document.getElementById('resultsContent');

    if (!results || !results.clusters) {
        resultsContent.innerHTML = '<p>No clustering results available</p>';
        return;
    }

    let html = '<div class="clustering-results">';
    results.clusters.forEach((cluster, index) => {
        html += `
            <div class="cluster-item">
                <h4>Cluster ${index + 1}</h4>
                <p><strong>Size:</strong> ${cluster.size || 0} items</p>
                <p><strong>Summary:</strong> ${cluster.summary || 'No summary available'}</p>
            </div>
        `;
    });
    html += '</div>';

    resultsContent.innerHTML = html;
}

function displaySimilarityResults(results) {
    const resultsContent = document.getElementById('resultsContent');

    if (!results || !results.pairs) {
        resultsContent.innerHTML = '<p>No similarity results available</p>';
        return;
    }

    let html = '<div class="similarity-results">';
    html += '<h4>Similar Document Pairs</h4>';
    results.pairs.forEach((pair, index) => {
        html += `
            <div class="similarity-item">
                <p><strong>Pair ${index + 1}:</strong></p>
                <p>Document A: ${pair.doc1 || 'Unknown'}</p>
                <p>Document B: ${pair.doc2 || 'Unknown'}</p>
                <p>Similarity: ${(pair.similarity * 100).toFixed(1)}%</p>
            </div>
        `;
    });
    html += '</div>';

    resultsContent.innerHTML = html;
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Load quick stats on page load
    loadQuickStats();
});
