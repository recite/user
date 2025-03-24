## user: estimate how often a Python library is used in a public GitHub repository

Estimate how frequently Python packages are imported across public GitHub repositories.

## Overview

We determine package popularity by:
1. Randomly sampling GitHub repositories with Python as the main language
2. Analyzing Python import statements in these repositories
3. Extrapolating findings based on the total Python repository count ([~18M repositories]((https://github.com/recite/user/blob/main/scripts/total_python_repos.ipynb))

The system continually improves its accuracy by sampling additional repositories every 6 hours via [GitHub Actions](https://github.com/recite/user/blob/main/.github/workflows/count_imports.yml).

**Note:** We have stopped considering standard Python libraries but have not yet removed all the data.

### Analysis Scripts

| Script | Purpose |
|--------|---------|
| [find_repos.py](https://github.com/recite/user/blob/main/scripts/find_repos.py) | Queries GitHub API for random Python repositories |
| [analyze_imports.py](https://github.com/recite/user/blob/main/scripts/analyze_imports.py) | Extracts import statements from repository files |
| [count_libs.py](https://github.com/recite/user/blob/main/scripts/count_libs.py) | Aggregates and calculates package usage statistics |
| [update_readme.py](https://github.com/recite/user/blob/main/scripts/update_readme.py) | Refreshes this README with latest data |
| [total_python_repos.ipynb](https://github.com/recite/user/blob/main/scripts/total_python_repos.ipynb) | Estimates total Python repository count on GitHub |

### Scripts

1. [Get Random Repos.](https://github.com/recite/user/blob/main/scripts/find_repos.py)
2. [Analyze Imports](https://github.com/recite/user/blob/main/scripts/analyze_imports.py)
3. [Count Imports](https://github.com/recite/user/blob/main/scripts/count_libs.py)
4. [Update Readme](https://github.com/recite/user/blob/main/scripts/update_readme.py)

### Data

1. [Processed Repos. (JSONL)](https://github.com/recite/user/blob/main/data/repos.jsonl)
2. [Imports (JSONL)](https://github.com/recite/user/blob/main/data/imports.jsonl)
3. [Counts (CSV)](https://github.com/recite/user/blob/main/data/library_counts.csv)

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | requests | 238 |
| 2 | numpy | 135 |
| 3 | pandas | 91 |
| 4 | pytest | 69 |
| 5 | torch | 63 |
| 6 | tqdm | 50 |
| 7 | yaml | 48 |
| 8 | os | 40 |
| 9 | utils | 40 |
| 10 | bs4 | 38 |

*Last updated: 2025-03-24 18:35:15 UTC*
