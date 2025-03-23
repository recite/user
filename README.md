## user: estimate how often a library is used in a public GitHub repository

Count how often a Python package has been imported in scripts on public repos in GitHub. We take a random sample of GitHub repositories with Python as the main language, tally the imports, and then pro-rate the number by the estimate of the total number of repositories with Python as the main language (still to be implemented). We have stopped considering standard Python libraries but have not yet removed all the data.

The repository is set up to analyze a small random sample of repositories each day, and we keep updating counts based on that.


We use GitHub Actions to incrementally sample and analyze a small set of repositories every 6 hours.

## Top Python Libraries

| Rank | Library | Count |
|------|---------|-------|
| 1 | requests | 211 |
| 2 | numpy | 110 |
| 3 | pandas | 67 |
| 4 | pytest | 66 |
| 5 | yaml | 46 |
| 6 | torch | 46 |
| 7 | os | 40 |
| 8 | tqdm | 40 |
| 9 | utils | 37 |
| 10 | bs4 | 35 |

*Last updated: 2025-03-23 06:31:39 UTC*
