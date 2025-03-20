## user: estimate how often a library is used in a public GitHub repository

Count how often a Python package has been imported in scripts on public repos. in GitHub. We take a random sample of GitHub repositories with the main language as Python, tally the imports, and then pro-rate the number by the estimate of the total number of repositories with the main language as Python. 

We use GitHub Actions to incrementally sample and analyze a small set of repositories every 6 hours.

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | requests | 143 |
| 2 | numpy | 71 |
| 3 | pandas | 56 |
| 4 | pytest | 46 |
| 5 | os | 40 |
| 6 | sys | 32 |
| 7 | bs4 | 29 |
| 8 | torch | 29 |
| 9 | yaml | 27 |
| 10 | __future__ | 26 |

*Last updated: 2025-03-20 18:33:48 UTC*
