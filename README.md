## user: estimate how often a library is used in a public GitHub repository

Count how often a Python package has been imported in scripts on public repos. in GitHub. We take a random sample of GitHub repositories with the main language as Python, tally the imports, and then pro-rate the number by the estimate of the total number of repositories with the main language as Python. 

We use GitHub Actions to incrementally sample and analyze a small set of repositories every 6 hours.

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | requests | 174 |
| 2 | numpy | 90 |
| 3 | pandas | 63 |
| 4 | pytest | 62 |
| 5 | yaml | 41 |
| 6 | os | 40 |
| 7 | torch | 37 |
| 8 | tqdm | 34 |
| 9 | utils | 34 |
| 10 | sys | 32 |

*Last updated: 2025-03-22 01:50:46 UTC*
