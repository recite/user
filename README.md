## user: estimate how often a library is used in a public GitHub repository

Count how often a Python package has been imported in scripts on public repos in GitHub. We take a random sample of GitHub repositories with Python as the main language, tally the imports, and then pro-rate the number by the estimate of [the total number of repositories with Python as the main language (~ 18M)](https://github.com/recite/user/blob/main/scripts/total_python_repos.ipynb). 

*We have stopped considering standard Python libraries but have not yet removed all the data.

We use [GitHub Actions](https://github.com/recite/user/blob/main/.github/workflows/count_imports.yml) to incrementally sample and analyze a small set of repositories every 6 hours, and we keep updating counts based on that.

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
