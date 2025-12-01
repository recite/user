// Badge generation logic
let libraryData = [];

// Load data and generate badge
async function generateBadge(packageName, badgeType) {
    // Try to load library data
    try {
        const response = await fetch('../data/library_counts.csv');
        const csvText = await response.text();
        libraryData = parseCSV(csvText);
    } catch (error) {
        console.error('Error loading data:', error);
        // Use fallback data if loading fails
        libraryData = getFallbackData();
    }
    
    // Find package in data
    const packageData = libraryData.find(item => 
        item.library.toLowerCase() === packageName.toLowerCase()
    );
    
    if (packageData) {
        const rank = libraryData.indexOf(packageData) + 1;
        const count = packageData.count;
        const topPackage = libraryData[0];
        const relativeUsage = Math.round((count / topPackage.count) * 100);
        
        switch (badgeType) {
            case 'rank':
                return createBadgeSVG('Python Usage', `#${rank}`, '#3776ab');
            case 'count':
                return createBadgeSVG('Imports', formatCount(count), '#3776ab');
            case 'relative':
                return createBadgeSVG('Usage', `${relativeUsage}% of ${topPackage.library}`, '#3776ab');
            default:
                return createBadgeSVG('Python Usage', `#${rank}`, '#3776ab');
        }
    } else {
        return createBadgeSVG('Python Usage', 'not found', '#999999');
    }
}

// Create SVG badge (shields.io style)
function createBadgeSVG(label, value, color) {
    const labelWidth = label.length * 6 + 12;
    const valueWidth = value.length * 6 + 12;
    const totalWidth = labelWidth + valueWidth;
    
    return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${totalWidth}" height="20">
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

// Format count for display
function formatCount(count) {
    if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'k';
    }
    return count.toString();
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

// Fallback data if CSV loading fails
function getFallbackData() {
    return [
        { library: 'numpy', count: 46641 },
        { library: 'matplotlib', count: 15206 },
        { library: 'torch', count: 14969 },
        { library: 'pandas', count: 13945 },
        { library: 'cv2', count: 10091 },
        { library: 'django', count: 9624 },
        { library: 'sklearn', count: 8052 },
        { library: 'utils', count: 7389 },
        { library: 'requests', count: 7345 },
        { library: 'tensorflow', count: 7237 }
    ];
}