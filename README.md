## user: estimate how often a library is used in a public GitHub repository

Count how often a Python package has been imported in scripts on public repos. in GitHub. We take a random sample of GitHub repositories with the main language as Python, tally the imports, and then pro-rate the number by the estimate of the total number of repositories with the main language as Python. 

We use GitHub Actions to incrementally sample and analyze a small set of repositories every 6 hours.

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | requests | 151 |
| 2 | numpy | 75 |
| 3 | pandas | 56 |
| 4 | pytest | 51 |
| 5 | os | 40 |
| 6 | torch | 33 |
| 7 | sys | 32 |
| 8 | yaml | 32 |
| 9 | bs4 | 32 |
| 10 | utils | 29 |

*Last updated: 2025-03-21 01:54:00 UTC*
