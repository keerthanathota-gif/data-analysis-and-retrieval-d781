/**
 * API Wrapper Module
 * Provides convenient methods for making authenticated API calls
 */

const API_BASE_URL = window.location.origin; // Use current server URL

// ============================================
// HELPER FUNCTIONS
// ============================================

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

async function handleResponse(response) {
    if (response.status === 401) {
        // Token expired or invalid
        clearToken();
        window.location.href = 'login.html';
        throw new Error('Authentication required');
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }

    return data;
}

// ============================================
// AUTH API
// ============================================

const AuthAPI = {
    async getCurrentUser() {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    },

    async listUsers() {
        const response = await fetch(`${API_BASE_URL}/api/auth/users`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    },

    async createUser(userData) {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(userData)
        });
        return handleResponse(response);
    },

    async getAuditLogs(limit = 100) {
        const response = await fetch(`${API_BASE_URL}/api/auth/audit-logs?limit=${limit}`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    }
};

// ============================================
// PIPELINE API
// ============================================

const PipelineAPI = {
    async runPipeline(url) {
        const response = await fetch(`${API_BASE_URL}/api/pipeline/run`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ url })
        });
        return handleResponse(response);
    },

    async getStatus() {
        const response = await fetch(`${API_BASE_URL}/api/pipeline/status`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    }
};

// ============================================
// CLUSTERING API
// ============================================

const ClusteringAPI = {
    async performClustering(level, numClusters) {
        const response = await fetch(`${API_BASE_URL}/api/clustering/cluster`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                level: level,
                num_clusters: numClusters
            })
        });
        return handleResponse(response);
    },

    async getResults(level) {
        const response = await fetch(`${API_BASE_URL}/api/clustering/results/${level}`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    }
};

// ============================================
// ANALYSIS API
// ============================================

const AnalysisAPI = {
    async runSimilarity(level) {
        const response = await fetch(`${API_BASE_URL}/api/analysis/similarity`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ level })
        });
        return handleResponse(response);
    },

    async checkOverlaps(level) {
        const response = await fetch(`${API_BASE_URL}/api/analysis/overlaps`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ level })
        });
        return handleResponse(response);
    },

    async checkRedundancy(level) {
        const response = await fetch(`${API_BASE_URL}/api/analysis/redundancy`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ level })
        });
        return handleResponse(response);
    },

    async getResults(analysisType, level) {
        const response = await fetch(`${API_BASE_URL}/api/analysis/results/${analysisType}/${level}`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    }
};

// ============================================
// RAG API
// ============================================

const RAGAPI = {
    async search(query, topK = 5) {
        const response = await fetch(`${API_BASE_URL}/api/rag/search`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                query: query,
                top_k: topK
            })
        });
        return handleResponse(response);
    }
};

// ============================================
// STATISTICS API
// ============================================

const StatsAPI = {
    async getOverview() {
        const response = await fetch(`${API_BASE_URL}/api/stats/overview`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    },

    async getDetailed(level) {
        const response = await fetch(`${API_BASE_URL}/api/stats/detailed/${level}`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    }
};

// ============================================
// VISUALIZATION API
// ============================================

const VisualizationAPI = {
    async getClusterVisualization(level) {
        const response = await fetch(`${API_BASE_URL}/api/visualization/clusters/${level}`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    },

    async getSimilarityMatrix(level) {
        const response = await fetch(`${API_BASE_URL}/api/visualization/similarity/${level}`, {
            headers: getAuthHeaders()
        });
        return handleResponse(response);
    }
};
