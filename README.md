## user: estimate how often a Python library is used in a public GitHub repository

Estimate how frequently Python packages are imported across public GitHub repositories.

## Overview

We determine package popularity by:
1. Randomly sampling GitHub repositories with Python as the main language
2. Analyzing Python import statements in these repositories
3. Extrapolating findings based on the total Python repository count ([~18M repositories]((https://github.com/recite/user/blob/main/scripts/total_python_repos.ipynb))

The system continually improves its accuracy by sampling additional repositories every 6 hours via [GitHub Actions](https://github.com/recite/user/blob/main/.github/workflows/count_imports.yml).

**Note:** We have stopped considering standard Python libraries but have not yet removed all the data.

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
| 1 | numpy | 489 |
| 2 | requests | 289 |
| 3 | pandas | 197 |
| 4 | torch | 169 |
| 5 | matplotlib | 157 |
| 6 | django | 121 |
| 7 | utils | 103 |
| 8 | cv2 | 101 |
| 9 | pytest | 94 |
| 10 | scipy | 81 |

*Last updated: 2025-03-26 18:36:48 UTC*
