#!/usr/bin/env python3
"""
Update README.md with top library counts

This script reads the library_counts.csv file and updates the README.md
with a table of the top libraries.
"""
import os
import csv
import re
import argparse
import logging
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_readme_with_library_stats(csv_file, readme_file, top_n=10):
    """
    Update the README.md file with a table of the top libraries from the CSV.
    This function preserves the structure and only updates the statistics table.
    
    Args:
        csv_file: Path to the library counts CSV file
        readme_file: Path to the README.md file
        top_n: Number of top libraries to include
    """
    if not os.path.exists(csv_file):
        logging.error(f"CSV file not found: {csv_file}")
        return False
    
    # Read the top N libraries from the CSV
    top_libraries = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header row
            next(reader, None)
            
            # Get top N rows
            for i, row in enumerate(reader):
                if i >= top_n:
                    break
                if len(row) >= 2:
                    top_libraries.append((row[0], row[1]))
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return False
    
    if not top_libraries:
        logging.warning("No library data found in CSV")
        return False

    # Get the last modified time of the CSV file as a UTC datetime string
    timestamp = datetime.datetime.utcfromtimestamp(os.path.getmtime(csv_file)).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Format the data as a markdown table
    table_content = "## Top Python Libraries\n\n"
    table_content += "| Rank | Library | Count |\n"
    table_content += "|------|---------|-------|\n"
    
    for i, (library, count) in enumerate(top_libraries, 1):
        table_content += f"| {i} | {library} | {count} |\n"
    
    table_content += f"\n*Last updated: {timestamp}*\n"
    
    # Create template for new README if it doesn't exist
    if not os.path.exists(readme_file):
        # Create new README with full structure
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write("""## user: estimate how often a Python library is used in a public GitHub repository

Estimate how frequently Python packages are imported across public GitHub repositories.

**📊 [View Live Dashboard](https://recite.github.io/user/)** | **[Methodology](https://recite.github.io/user/methodology.html)** | **[Download Data](https://github.com/recite/user/blob/main/data/library_counts.csv)**

## Overview

We determine package popularity by:
1. Randomly sampling GitHub repositories with Python as the main language
2. Analyzing Python import statements in these repositories
3. Extrapolating findings based on the total Python repository count ([~18M repositories]((https://github.com/recite/user/blob/main/scripts/total_python_repos.ipynb))

The system continually improves its accuracy by sampling additional repositories every 6 hours via [GitHub Actions](https://github.com/recite/user/blob/main/.github/workflows/count_imports.yml).

**Note:** We have stopped considering standard Python libraries but have not yet removed all the data.

## Why This Matters

Traditional package metrics like download counts are increasingly unreliable indicators of real-world usage. Every CI/CD run, dependency resolver cache miss, and mirror sync inflates these numbers without representing actual adoption. A package with millions of downloads might be used by only a handful of projects, while genuinely popular tools can be undercounted due to efficient caching.

This project provides a more meaningful metric: **actual usage in production code**. By analyzing import statements across a random sample of GitHub's ~18 million Python repositories, we capture how developers genuinely use packages in their projects. This approach offers package maintainers something download counts cannot—contextual understanding of their impact. Knowing your package appears in 2% of Python repositories, or has 70% of the adoption rate of an industry leader, provides actionable insights about market penetration and growth opportunities.

For the open source community, these metrics democratize impact measurement. Smaller, specialized packages can demonstrate their value within their niche, funding conversations become data-driven, and developers can make more informed decisions about dependencies based on actual adoption patterns rather than inflated download statistics.

### For Package Maintainers

- **Track Real Adoption**: See how many projects actually import your package
- **Benchmark Performance**: Compare your package's usage against similar tools
- **Identify Ecosystems**: Discover which packages are commonly used alongside yours
- **Measure Growth**: Monitor adoption trends over time as we continuously sample
- **Support Funding Applications**: Provide concrete usage data for grant proposals

### Scripts

| Script | Purpose |
|--------|---------|
| [find_repos.py](https://github.com/recite/user/blob/main/scripts/find_repos.py) | Queries GitHub API for random Python repositories |
| [analyze_imports.py](https://github.com/recite/user/blob/main/scripts/analyze_imports.py) | Extracts import statements from repository files |
| [count_libs.py](https://github.com/recite/user/blob/main/scripts/count_libs.py) | Aggregates and calculates package usage statistics |
| [update_readme.py](https://github.com/recite/user/blob/main/scripts/update_readme.py) | Refreshes this README with latest data |
| [total_python_repos.ipynb](https://github.com/recite/user/blob/main/scripts/total_python_repos.ipynb) | Estimates total Python repository count on GitHub |

### Data

| File | Description | Format |
|------|-------------|--------|
| [repos.jsonl](https://github.com/recite/user/blob/main/data/repos.jsonl) | Details of processed repositories | JSONL |
| [imports.jsonl](https://github.com/recite/user/blob/main/data/imports.jsonl) | Raw import statements extracted from repos | JSONL |
| [library_counts.csv](https://github.com/recite/user/blob/main/data/library_counts.csv) | Aggregated package usage statistics | CSV |

### Workflow

Our [GitHub Actions workflow](https://github.com/recite/user/blob/main/.github/workflows/count_imports.yml) orchestrates the entire process:
```
Find Random Repos → Analyze Imports → Count Package Usage → Update Statistics → Refresh README
```

""")
            f.write(table_content)
        logging.info(f"Created new README.md with full structure and library stats")
        return True
    
    # Read existing README
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace only the "## Top Python Libraries" section while preserving everything else
    # This regex matches from the header until the next header (starting with "##") or end-of-file.
    pattern = r"## Top Python Libraries[\s\S]*?(?=\n## |\Z)"
    
    # Check if the section exists
    if re.search(pattern, content):
        # Replace existing section
        new_content = re.sub(pattern, table_content.rstrip(), content, flags=re.DOTALL)
    else:
        # Append the section if it doesn't exist
        new_content = content.rstrip() + "\n\n" + table_content
    
    # Write updated content back to the README
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logging.info(f"Updated README.md with top {top_n} libraries")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update README with library statistics")
    parser.add_argument("--csv", type=str, default="data/library_counts.csv", 
                        help="Path to the library counts CSV file")
    parser.add_argument("--readme", type=str, default="README.md", 
                        help="Path to the README.md file")
    parser.add_argument("--top", type=int, default=10, 
                        help="Number of top libraries to include")
    
    args = parser.parse_args()
    
    update_readme_with_library_stats(args.csv, args.readme, args.top)
