// Global variables
let libraryData = [];
let totalReposAnalyzed = 0;
let chart = null;

// Constants
const TOTAL_PYTHON_REPOS = 18_000_000; // Estimated total Python repos on GitHub

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    await loadData();
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

// Load data from CSV and processed repos files
async function loadData() {
    try {
        // Load library counts CSV
        const csvResponse = await fetch('https://raw.githubusercontent.com/recite/user/refs/heads/main/data/library_counts.csv');
        const csvText = await csvResponse.text();
        console.log('CSV loaded from raw GitHub, first line:', csvText.split('\n')[0]);
        libraryData = parseCSV(csvText);

        // Load processed repos count for accurate sampling statistics
        const processedResponse = await fetch('https://raw.githubusercontent.com/recite/user/refs/heads/main/data/processed_repos.txt');
        const processedText = await processedResponse.text();
        const processedRepos = processedText.trim().split('\n').filter(line => line.trim());
        totalReposAnalyzed = processedRepos.length;
        
        console.log('Data loaded successfully:', {
            libraries: libraryData.length,
            totalImports: libraryData.reduce((sum, item) => sum + item.count, 0),
            totalReposAnalyzed: totalReposAnalyzed
        });
        
    } catch (error) {
        console.error('Error loading data:', error);
        // Fallback to sample data if files not found
        libraryData = getSampleData();
        totalReposAnalyzed = 5000; // Fallback estimate
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
    // Repositories analyzed (actual sample size)
    document.getElementById('repo-count').textContent = totalReposAnalyzed.toLocaleString();
    
    // Total imports analyzed (the main metric)
    const totalImports = libraryData.reduce((sum, item) => sum + item.count, 0);
    document.getElementById('import-count').textContent = totalImports.toLocaleString();
    
    // Unique packages discovered
    document.getElementById('package-count').textContent = libraryData.length.toLocaleString();
    
    // Sample percentage
    const samplePercent = ((totalReposAnalyzed / TOTAL_PYTHON_REPOS) * 100).toFixed(3);
    document.getElementById('last-updated').textContent = `${samplePercent}% of all Python repos`;
}

// Create Chart.js bar chart
function createChart() {
    const ctx = document.getElementById('topPackagesChart').getContext('2d');
    const limit = parseInt(document.getElementById('chart-limit').value);
    const topPackages = libraryData.slice(0, limit);
    
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
            labels: topPackages.map(p => decodeHTMLEntities(p.library)),
            datasets: [{
                label: 'Import Count',
                data: topPackages.map(p => p.count),
                backgroundColor: 'rgba(55, 118, 171, 0.8)',
                borderColor: 'rgba(55, 118, 171, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(55, 118, 171, 1)'
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

// Populate DataTables
function populateTable() {
    const tbody = document.getElementById('packages-tbody');
    tbody.innerHTML = '';
    
    const totalImports = libraryData.reduce((sum, item) => sum + item.count, 0);
    
    libraryData.forEach((item, index) => {
        const row = tbody.insertRow();
        row.insertCell(0).textContent = index + 1;
        row.insertCell(1).textContent = item.library;
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
    
    function showSuggestions(query) {
        const matches = libraryData
            .filter(item => item.library.toLowerCase().includes(query))
            .slice(0, 10);
        
        if (matches.length > 0) {
            searchSuggestions.innerHTML = matches
                .map(item => `<div class="suggestion-item" data-package="${item.library}">${item.library}</div>`)
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
    
    function performSearch(query) {
        if (!query) return;
        
        const packageData = libraryData.find(item => 
            item.library.toLowerCase() === query.toLowerCase()
        );
        
        if (packageData) {
            const rank = libraryData.indexOf(packageData) + 1;
            const usagePercent = ((packageData.count / totalReposAnalyzed) * 100).toFixed(2);
            const estimatedTotalRepos = Math.round((packageData.count / totalReposAnalyzed) * TOTAL_PYTHON_REPOS);
            const topPackage = libraryData[0];
            const relativeUsage = ((packageData.count / topPackage.count) * 100).toFixed(1);
            
            searchResults.innerHTML = `
                <div class="result-card">
                    <h3>📦 ${packageData.library}</h3>
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
                        <small><strong>Based on random sample of ${totalReposAnalyzed.toLocaleString()} repositories</strong><br>
                        Estimated ${estimatedTotalRepos.toLocaleString()} of ~18M Python repos (${usagePercent}%) use this package</small>
                    </div>
                    <div class="badge-section">
                        <h4>🏷️ Add Badges to Your README</h4>
                        <div class="badge-examples">
                            <img src="badges.html?package=${packageData.library}&type=rank" alt="Rank Badge">
                            <img src="badges.html?package=${packageData.library}&type=count" alt="Count Badge">
                            <img src="badges.html?package=${packageData.library}&type=relative" alt="Relative Badge">
                        </div>
                        <div class="badge-code" onclick="copyToClipboard(this)">
![Python Usage](https://recite.github.io/user/badges.html?package=${packageData.library}&type=rank)
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