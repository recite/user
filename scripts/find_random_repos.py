# find_repos.py
import os
import logging
import time
import random
import json
import argparse
from typing import List, Tuple, Optional
from github_utils import make_github_request, RateLimitExceeded, GITHUB_API_URL

def get_random_repo(
    min_stars: int = 5, 
    language: str = "python",
    min_size_kb: int = 100
) -> Optional[Tuple[str, str, str]]:
    """
    Find a random GitHub repository meeting the criteria.
    
    Args:
        min_stars: Minimum number of stars
        language: Programming language filter
        min_size_kb: Minimum repository size in KB
        
    Returns:
        Tuple of (repo_name, repo_url, last_updated) or None if not found
    """
    try:
        # Generate a random page number (GitHub search has a limit of 1000 results)
        page = random.randint(1, 10)
        
        # Create a query with the specified criteria
        query = f"language:{language} stars:>={min_stars} size:>={min_size_kb}"
        
        # Search for repositories
        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 100,
            "page": page
        }
        
        result = make_github_request(f"{GITHUB_API_URL}/search/repositories", params)
        
        if not result or "items" not in result or not result["items"]:
            logging.warning(f"No repositories found matching criteria: {query}")
            return None
        
        # Select a random repository from the results
        repo = random.choice(result["items"])
        repo_name = repo["full_name"]
        repo_url = repo["html_url"]
        last_updated = repo["updated_at"]
        
        logging.info(f"Selected random repository: {repo_name} (last updated: {last_updated})")
        return (repo_name, repo_url, last_updated)
    
    except RateLimitExceeded as e:
        logging.error(f"Rate limit exceeded while finding random repo: {e}")
        raise
    except Exception as e:
        logging.error(f"Error finding random repository: {e}")
        return None

def find_random_repos(
    count: int = 10,
    min_stars: int = 5,
    language: str = "python",
    min_size_kb: int = 100,
    output_file: str = "repos.jsonl"
) -> List[Tuple[str, str, str]]:
    """
    Find multiple random repositories and save them to a file.
    
    Args:
        count: Number of repositories to find
        min_stars: Minimum number of stars
        language: Programming language filter
        min_size_kb: Minimum repository size in KB
        output_file: File to save results to
        
    Returns:
        List of found repositories as (repo_name, repo_url, last_updated)
    """
    start_time = time.time()
    found_repos = []
    
    with open(output_file, 'a') as f:
        for i in range(count):
            try:
                repo_info = get_random_repo(min_stars, language, min_size_kb)
                
                if repo_info:
                    # Save immediately to preserve progress
                    result_obj = {
                        "repo_name": repo_info[0],
                        "repo_url": repo_info[1],
                        "last_updated": repo_info[2]
                    }
                    f.write(json.dumps(result_obj) + '\n')
                    found_repos.append(repo_info)
                    
                    logging.info(f"Found {len(found_repos)}/{count} repositories")
                
                # Add a small delay to avoid hitting rate limits
                time.sleep(1)
                
            except RateLimitExceeded:
                logging.error("API rate limit reached. Stopping repository search.")
                break
            except Exception as e:
                logging.error(f"Error during repository search: {e}")
    
    elapsed_time = time.time() - start_time
    logging.info(f"Found {len(found_repos)} repositories in {elapsed_time:.2f} seconds")
    return found_repos

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find random GitHub repositories")
    parser.add_argument("--count", type=int, default=10, help="Number of repositories to find")
    parser.add_argument("--min-stars", type=int, default=5, help="Minimum number of stars")
    parser.add_argument("--language", type=str, default="python", help="Programming language filter")
    parser.add_argument("--min-size", type=int, default=100, help="Minimum repository size in KB")
    parser.add_argument("--output", type=str, default="repos.jsonl", help="Output file")
    
    args = parser.parse_args()
    
    repos = find_random_repos(
        count=args.count,
        min_stars=args.min_stars,
        language=args.language,
        min_size_kb=args.min_size,
        output_file=args.output
    )
    
    print(f"Found {len(repos)} repositories. Results saved to {args.output}")