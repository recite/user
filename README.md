## user: estimate how often a library is used in a public GitHub repository

Count how often a Python package has been imported in scripts on public repos. in GitHub. We take a random sample of GitHub repositories with the main language as Python, tally the imports, and then pro-rate the number by the estimate of the total number of repositories with the main language as Python. 

We use GitHub Actions to incrementally sample and analyze a small set of repositories every 6 hours.

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | requests | 162 |
| 2 | numpy | 90 |
| 3 | pandas | 63 |
| 4 | pytest | 62 |
| 5 | os | 40 |
| 6 | torch | 37 |
| 7 | yaml | 36 |
| 8 | tqdm | 34 |
| 9 | sys | 32 |
| 10 | bs4 | 32 |

*Last updated: 2025-03-21 18:32:54 UTC*
