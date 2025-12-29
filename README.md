## user: estimate how often a Python library is used in a public GitHub repository

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
- **Add Usage Badges**: Display your package's real usage statistics in your README with our badges

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

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | numpy | 51879 |
| 2 | matplotlib | 16870 |
| 3 | torch | 16782 |
| 4 | pandas | 15491 |
| 5 | cv2 | 11264 |
| 6 | django | 10627 |
| 7 | sklearn | 8859 |
| 8 | utils | 8285 |
| 9 | requests | 8123 |
| 10 | tensorflow | 8091 |

*Last updated: 2025-12-29 06:49:04 UTC*