## user: estimate how often a library is used in a public GitHub repository

Count how often a Python package has been imported in scripts on public repos. in GitHub. We take a random sample of GitHub repositories with the main language as Python, tally the imports, and then pro-rate the number by the estimate of the total number of repositories with the main language as Python. 

We use GitHub Actions to incrementally sample and analyze a small set of repositories every 6 hours.

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | requests | 189 |
| 2 | numpy | 102 |
| 3 | pandas | 64 |
| 4 | pytest | 64 |
| 5 | yaml | 44 |
| 6 | torch | 41 |
| 7 | os | 40 |
| 8 | tqdm | 37 |
| 9 | utils | 37 |
| 10 | bs4 | 33 |

*Last updated: 2025-03-22 12:42:32 UTC*
