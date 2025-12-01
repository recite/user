// Test search functionality with badge generation
console.log('Testing badge generation...');

// Test the generateBadgeSVG function
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

function formatBadgeCount(count) {
    if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'k';
    }
    return count.toString();
}

// Test badge generation for numpy (rank 1, count 46750)
const testBadges = [
    generateBadgeSVG('Python Usage', '#1'),
    generateBadgeSVG('Imports', formatBadgeCount(46750)),
    generateBadgeSVG('Usage', '100%')
];

console.log('Generated badges:');
testBadges.forEach((badge, index) => {
    console.log(`Badge ${index + 1}:`, badge.includes('<svg') ? 'SVG Generated ✓' : 'Failed ✗');
});

// Verify the badges contain expected content
console.log('Badge content verification:');
console.log('Contains rank #1:', testBadges[0].includes('#1') ? '✓' : '✗');
console.log('Contains formatted count:', testBadges[1].includes('46.8k') ? '✓' : '✗');
console.log('Contains percentage:', testBadges[2].includes('100%') ? '✓' : '✗');