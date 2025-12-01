// Global variables
let dashboardData = null;
let fullLibraryData = null;
let fuseSearch = null;
let chart = null;

// Constants
const TOTAL_PYTHON_REPOS = 18_000_000; // Estimated total Python repos on GitHub

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    await loadData();
    initializeFuseSearch();
    updateStatistics();
    createChart();
    populateTable();
    setupEventListeners();
});

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggle(savedTheme);
}

function updateThemeToggle(theme) {
    const toggle = document.getElementById('theme-toggle');
    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Load optimized dashboard data (fast initial load)
async function loadData() {
    try {
        // Load lightweight dashboard data first (~5KB)
        const dashboardResponse = await fetch('https://raw.githubusercontent.com/recite/user/refs/heads/main/data/dashboard.json');
        dashboardData = await dashboardResponse.json();
        
        console.log('Dashboard data loaded:', {
            topPackages: dashboardData.topPackages.length,
            stats: dashboardData.stats
        });
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Fallback to sample data
        dashboardData = {
            stats: {
                totalRepos: 5000,
                totalImports: 500000,
                uniquePackages: 8000,
                samplePercent: 0.028
            },
            topPackages: getSampleData()
        };
    }
}

// Initialize Fuse.js search with dashboard data (top packages only initially)
function initializeFuseSearch() {
    if (!dashboardData || !dashboardData.topPackages) return;
    
    // Initialize Fuse.js with the top packages from dashboard for immediate search
    const searchData = dashboardData.topPackages.map(pkg => ({
        name: pkg.name,
        count: pkg.count
    }));
    
    fuseSearch = new Fuse(searchData, {
        keys: ['name'],
        threshold: 0.3, // Allow some fuzzy matching
        ignoreLocation: true,
        includeScore: true,
        includeMatches: true
    });
    
    console.log('Fuse search initialized with', searchData.length, 'top packages');
}

// Load full search index (all packages) - called on first search
async function loadFullSearchIndex() {
    const CACHE_KEY = 'python_package_search_cache';
    const CACHE_VERSION_KEY = 'python_package_search_version';
    
    try {
        // Check if we have cached data
        const cachedData = localStorage.getItem(CACHE_KEY);
        const cachedVersion = localStorage.getItem(CACHE_VERSION_KEY);
        
        if (cachedData && cachedVersion) {
            console.log('Using cached search data');
            const searchData = JSON.parse(cachedData);
            updateFuseSearch(searchData);
            return;
        }
        
        // Download fresh data
        console.log('Downloading full search index...');
        const response = await fetch('https://raw.githubusercontent.com/recite/user/refs/heads/main/data/search_optimized.json');
        const searchIndex = await response.json();
        
        // Transform to search data format
        const searchData = searchIndex.packages.map(name => ({
            name: name,
            count: 0 // We don't need counts for search, just names
        }));
        
        // Cache the data
        localStorage.setItem(CACHE_KEY, JSON.stringify(searchData));
        localStorage.setItem(CACHE_VERSION_KEY, searchIndex.version);
        
        // Update Fuse.js with full data
        updateFuseSearch(searchData);
        
        console.log('Full search index loaded:', searchIndex.packages.length, 'packages');
        
    } catch (error) {
        console.error('Error loading full search index:', error);
        // Keep using the existing top packages search
    }
}

// Update Fuse.js with new search data
function updateFuseSearch(searchData) {
    fuseSearch = new Fuse(searchData, {
        keys: ['name'],
        threshold: 0.3,
        ignoreLocation: true,
        includeScore: true,
        includeMatches: true
    });
}

// Load full library data (lazy loaded when needed)
async function loadFullData() {
    if (fullLibraryData) return; // Already loaded
    
    try {
        const csvResponse = await fetch('https://raw.githubusercontent.com/recite/user/refs/heads/main/data/library_counts.csv');
        const csvText = await csvResponse.text();
        fullLibraryData = parseCSV(csvText);
        console.log('Full data loaded:', fullLibraryData.length, 'packages');
    } catch (error) {
        console.error('Error loading full data:', error);
        fullLibraryData = dashboardData.topPackages;
    }
}

// Parse CSV data
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',');
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        if (values.length === headers.length) {
            data.push({
                library: values[0],
                count: parseInt(values[1])
            });
        }
    }
    
    return data;
}

// No longer needed - we don't parse repos.jsonl for dashboard statistics

// Get sample data as fallback
function getSampleData() {
    return [
        { library: 'numpy', count: 5720 },
        { library: 'matplotlib', count: 1854 },
        { library: 'torch', count: 1775 },
        { library: 'pandas', count: 1660 },
        { library: 'django', count: 1236 },
        { library: 'cv2', count: 1116 },
        { library: 'requests', count: 1069 },
        { library: 'sklearn', count: 940 },
        { library: 'utils', count: 928 },
        { library: 'tensorflow', count: 867 }
    ];
}

// Update statistics cards
function updateStatistics() {
    if (!dashboardData) return;
    
    const stats = dashboardData.stats;
    
    // Repositories analyzed (actual sample size)
    document.getElementById('repo-count').textContent = stats.totalRepos.toLocaleString();
    
    // Total imports analyzed (the main metric)
    document.getElementById('import-count').textContent = stats.totalImports.toLocaleString();
    
    // Unique packages discovered
    document.getElementById('package-count').textContent = stats.uniquePackages.toLocaleString();
    
    // Last updated with proper date formatting
    const lastUpdated = new Date(stats.lastUpdated).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short', 
        day: 'numeric'
    });
    document.getElementById('last-updated').textContent = `Updated ${lastUpdated}`;
}

// Create Chart.js bar chart
function createChart() {
    if (!dashboardData) return;
    
    const ctx = document.getElementById('topPackagesChart').getContext('2d');
    const limit = parseInt(document.getElementById('chart-limit').value);
    const topPackages = dashboardData.topPackages.slice(0, Math.min(limit, dashboardData.topPackages.length));
    
    // Destroy existing chart if it exists
    if (chart) {
        chart.destroy();
    }
    
    // Decode HTML entities in library names
    function decodeHTMLEntities(text) {
        const textArea = document.createElement('textarea');
        textArea.innerHTML = text;
        return textArea.value;
    }
    
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topPackages.map(p => decodeHTMLEntities(p.name)),
            datasets: [{
                label: 'Import Count',
                data: topPackages.map(p => p.count),
                backgroundColor: 'rgba(88, 166, 255, 0.8)',
                borderColor: 'rgba(88, 166, 255, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(88, 166, 255, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Count: ${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    },
                    grid: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--border-color')
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Populate DataTables (lazy loaded)
async function populateTable() {
    // Load full data if not already loaded
    await loadFullData();
    
    const tbody = document.getElementById('packages-tbody');
    tbody.innerHTML = '';
    
    const totalImports = dashboardData.stats.totalImports;
    
    fullLibraryData.forEach((item, index) => {
        const row = tbody.insertRow();
        row.insertCell(0).textContent = index + 1;
        row.insertCell(1).textContent = item.library || item.name;
        row.insertCell(2).textContent = item.count.toLocaleString();
        row.insertCell(3).textContent = ((item.count / totalImports) * 100).toFixed(2) + '%';
    });
    
    // Initialize DataTable
    if ($.fn.DataTable.isDataTable('#packagesTable')) {
        $('#packagesTable').DataTable().destroy();
    }
    
    $('#packagesTable').DataTable({
        pageLength: 25,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        order: [[2, 'desc']],
        responsive: true
    });
}

// Setup event listeners
function setupEventListeners() {
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeToggle(newTheme);
    });
    
    // Chart limit selector
    document.getElementById('chart-limit').addEventListener('change', () => {
        createChart();
    });
    
    // Download CSV button
    document.getElementById('download-csv').addEventListener('click', () => {
        downloadCSV();
    });
    
    // Package search
    setupPackageSearch();
}

// Setup package search functionality
function setupPackageSearch() {
    const searchInput = document.getElementById('package-search');
    const searchBtn = document.getElementById('search-btn');
    const searchResults = document.getElementById('search-results');
    const searchSuggestions = document.getElementById('search-suggestions');
    
    let currentSuggestionIndex = -1;
    
    // Search on button click
    searchBtn.addEventListener('click', () => {
        performSearch(searchInput.value.trim());
    });
    
    // Search on Enter key
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch(searchInput.value.trim());
            hideSuggestions();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            navigateSuggestions(1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            navigateSuggestions(-1);
        } else if (e.key === 'Escape') {
            hideSuggestions();
        }
    });
    
    // Show suggestions on input
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (query.length >= 2) {
            showSuggestions(query);
        } else {
            hideSuggestions();
        }
    });
    
    // Hide suggestions on click outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    async function showSuggestions(query) {
        // Load full search index on first search (with caching)
        if (!fuseSearch || fuseSearch.getIndex().size < 1000) {
            await loadFullSearchIndex();
        }
        
        const fuseResults = fuseSearch.search(query);
        const matches = fuseResults.slice(0, 10).map(result => result.item.name);
        
        if (matches.length > 0) {
            searchSuggestions.innerHTML = matches
                .map(name => `<div class="suggestion-item" data-package="${name}">${name}</div>`)
                .join('');
            searchSuggestions.classList.add('active');
            currentSuggestionIndex = -1;
            
            // Add click handlers to suggestions
            searchSuggestions.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    searchInput.value = item.dataset.package;
                    performSearch(item.dataset.package);
                    hideSuggestions();
                });
            });
        } else {
            hideSuggestions();
        }
    }
    
    function hideSuggestions() {
        searchSuggestions.classList.remove('active');
        searchSuggestions.innerHTML = '';
        currentSuggestionIndex = -1;
    }
    
    function navigateSuggestions(direction) {
        const suggestions = searchSuggestions.querySelectorAll('.suggestion-item');
        if (suggestions.length === 0) return;
        
        // Remove previous selection
        if (currentSuggestionIndex >= 0) {
            suggestions[currentSuggestionIndex].classList.remove('selected');
        }
        
        // Update index
        currentSuggestionIndex += direction;
        if (currentSuggestionIndex >= suggestions.length) {
            currentSuggestionIndex = 0;
        } else if (currentSuggestionIndex < 0) {
            currentSuggestionIndex = suggestions.length - 1;
        }
        
        // Add new selection
        suggestions[currentSuggestionIndex].classList.add('selected');
        searchInput.value = suggestions[currentSuggestionIndex].dataset.package;
    }
    
    async function performSearch(query) {
        if (!query) return;
        
        // Load full data if not already loaded
        await loadFullData();
        
        const packageData = fullLibraryData.find(item => 
            (item.library || item.name).toLowerCase() === query.toLowerCase()
        );
        
        if (packageData) {
            const rank = fullLibraryData.indexOf(packageData) + 1;
            const totalRepos = dashboardData.stats.totalRepos;
            const usagePercent = ((packageData.count / totalRepos) * 100).toFixed(2);
            const estimatedTotalRepos = Math.round((packageData.count / totalRepos) * TOTAL_PYTHON_REPOS);
            const topPackage = fullLibraryData[0];
            const relativeUsage = ((packageData.count / topPackage.count) * 100).toFixed(1);
            const packageName = packageData.library || packageData.name;
            
            searchResults.innerHTML = `
                <div class="result-card">
                    <h3>📦 ${packageName}</h3>
                    <div class="result-stats">
                        <div class="result-stat">
                            <div class="result-stat-label">Popularity Rank</div>
                            <div class="result-stat-value">#${rank}</div>
                        </div>
                        <div class="result-stat">
                            <div class="result-stat-label">Usage Rate</div>
                            <div class="result-stat-value">${usagePercent}%</div>
                        </div>
                        <div class="result-stat">
                            <div class="result-stat-label">Estimated Total Usage</div>
                            <div class="result-stat-value">~${estimatedTotalRepos.toLocaleString()}</div>
                        </div>
                        <div class="result-stat">
                            <div class="result-stat-label">vs ${topPackage.library}</div>
                            <div class="result-stat-value">${relativeUsage}%</div>
                        </div>
                    </div>
                    <div class="extrapolation-note">
                        <small><strong>Based on random sample of ${totalRepos.toLocaleString()} repositories</strong><br>
                        Estimated ${estimatedTotalRepos.toLocaleString()} of ~18M Python repos (${usagePercent}%) use this package</small>
                    </div>
                    <div class="badge-section">
                        <h4>Add Badges to Your README</h4>
                        <div class="badge-examples">
                            ${generateBadgeSVG('Python Usage', '#' + rank)}
                            ${generateBadgeSVG('Imports', formatBadgeCount(packageData.count))}
                            ${generateBadgeSVG('Usage', relativeUsage + '%')}
                        </div>
                        <div class="badge-code" onclick="copyToClipboard(this)">
![Python Usage](https://recite.github.io/user/badges.html?package=${packageName}&type=rank)
                        </div>
                        <small style="display:block;margin-top:0.5rem;opacity:0.7;">Click to copy markdown</small>
                    </div>
                </div>
            `;
        } else {
            searchResults.innerHTML = `
                <div class="not-found-message">
                    <h3>Package "${query}" not found</h3>
                    <p>This package hasn't been detected in our sample of Python repositories yet.</p>
                    <p>As we continuously analyze more repositories, it may appear in future updates.</p>
                </div>
            `;
        }
        
        searchResults.classList.add('active');
    }
}

// Generate badge SVG directly
function generateBadgeSVG(label, value, color = '#007aff') {
    const labelWidth = label.length * 6 + 12;
    const valueWidth = value.toString().length * 6 + 12;
    const totalWidth = labelWidth + valueWidth;
    
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="20">
        <linearGradient id="b" x2="0" y2="100%">
            <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
            <stop offset="1" stop-opacity=".1"/>
        </linearGradient>
        <clipPath id="a">
            <rect width="${totalWidth}" height="20" rx="3" fill="#fff"/>
        </clipPath>
        <g clip-path="url(#a)">
            <path fill="#555" d="M0 0h${labelWidth}v20H0z"/>
            <path fill="${color}" d="M${labelWidth} 0h${valueWidth}v20H${labelWidth}z"/>
            <path fill="url(#b)" d="M0 0h${totalWidth}v20H0z"/>
        </g>
        <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
            <text x="${labelWidth / 2}" y="15" fill="#010101" fill-opacity=".3">${label}</text>
            <text x="${labelWidth / 2}" y="14">${label}</text>
            <text x="${labelWidth + valueWidth / 2}" y="15" fill="#010101" fill-opacity=".3">${value}</text>
            <text x="${labelWidth + valueWidth / 2}" y="14">${value}</text>
        </g>
    </svg>`;
}

// Format count for badge display
function formatBadgeCount(count) {
    if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'k';
    }
    return count.toString();
}

// Copy text to clipboard
function copyToClipboard(element) {
    const text = element.textContent.trim();
    navigator.clipboard.writeText(text).then(() => {
        const originalText = element.innerHTML;
        element.innerHTML = '✅ Copied to clipboard!';
        setTimeout(() => {
            element.innerHTML = originalText;
        }, 2000);
    });
}

// Download data as CSV
function downloadCSV() {
    let csv = 'library,count\n';
    libraryData.forEach(item => {
        csv += `${item.library},${item.count}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'python_package_usage.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}