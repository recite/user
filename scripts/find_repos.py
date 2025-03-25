#!/usr/bin/env python3
"""
GitHub Repository Sampler - CLI tool to sample random Python repositories from GitHub

This script samples random GitHub repositories by randomly selecting hours
across a specified time period and finding repositories updated during those hours.

Usage:
    python github_repo_sampler.py --count 10 --min-stars 5 --language python --output repos.jsonl
"""

import os
import time
import random
import json
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Import functions from github_utils
from github_utils import make_github_request, RateLimitExceeded, GITHUB_API_URL

# Default output file
DEFAULT_OUTPUT_FILE = "repos.jsonl"

def get_random_date_hour(years_back: int = 10) -> datetime:
    """
    Generate a random date and hour from the past X years
    
    Args:
        years_back: How many years back to sample from
    
    Returns:
        Datetime object for a random hour
    """
    now = datetime.now()
    start_date = now - timedelta(days=365 * years_back)
    random_days = random.randint(0, (now - start_date).days)
    random_date = start_date + timedelta(days=random_days)
    random_hour = random.randint(0, 23)
    
    return random_date.replace(hour=random_hour, minute=0, second=0, microsecond=0)

def get_repos_from_hour(
    date_hour: datetime, 
    language: str = "python", 
    min_stars: int = 0,
    min_size_kb: int = 0
) -> List[Dict]:
    """
    Get repositories updated in a specific hour with optional filtering
    
    Args:
        date_hour: Datetime object representing the hour to sample
        language: Programming language to filter for
        min_stars: Minimum number of stars (0 for no filtering)
        min_size_kb: Minimum repository size in KB (0 for no filtering)
        
    Returns:
        List of repository dictionaries
    """
    # Format timestamps for GitHub Search API
    start_time = date_hour.isoformat() + "Z"  # GitHub needs the Z suffix for UTC
    end_time = (date_hour + timedelta(hours=1)).isoformat() + "Z"
    
    # Construct GitHub Search API query
    query_parts = [f"language:{language}", f"pushed:{start_time}..{end_time}"]
    
    # Add optional criteria
    if min_stars > 0:
        query_parts.append(f"stars:>={min_stars}")
    if min_size_kb > 0:
        query_parts.append(f"size:>={min_size_kb}")
    
    query = " ".join(query_parts)
    
    # Make API request using the utility function
    try:
        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 10  # Fixed at 10 repos per hour
        }
        
        data = make_github_request(f"{GITHUB_API_URL}/search/repositories", params)
        
        # Check if we got any results
        if "items" in data:
            repos = data["items"]
            
            # Extract relevant fields to match expected format
            cleaned_repos = []
            for repo in repos:
                cleaned_repos.append({
                    "repo_name": repo.get("full_name"),
                    "repo_url": repo.get("html_url"),
                    "last_updated": repo.get("updated_at")
                })
            
            return cleaned_repos
        else:
            logging.info(f"No results found for {start_time}")
            return []
            
    except Exception as e:
        logging.error(f"Error querying GitHub API: {e}")
        return []

def find_random_repos(
    count: int = 10,
    min_stars: int = 5,
    language: str = "python",
    min_size_kb: int = 100,
    output_file: str = DEFAULT_OUTPUT_FILE,
    years_back: int = 10
) -> List[Dict]:
    """
    Find multiple random repositories and save them to a file.
    
    Args:
        count: Number of repositories to find
        min_stars: Minimum number of stars
        language: Programming language filter
        min_size_kb: Minimum repository size in KB
        output_file: File to save results to
        years_back: How many years back to sample from
        
    Returns:
        List of found repositories
    """
    start_time = time.time()
    found_repos = []
    attempts = 0
    max_attempts = count * 3  # Allow more attempts than needed
    
    # Open output file for immediate writing (to preserve progress)
    with open(output_file, 'w') as f:
        while len(found_repos) < count and attempts < max_attempts:
            try:
                attempts += 1
                
                # Generate a random hour
                random_hour = get_random_date_hour(years_back)
                hour_str = random_hour.strftime("%Y-%m-%d %H:00")
                logging.info(f"Sampling hour {attempts}/{max_attempts}: {hour_str}")
                
                # Get repositories for this hour
                repos = get_repos_from_hour(
                    random_hour, 
                    language,
                    min_stars=min_stars,
                    min_size_kb=min_size_kb
                )
                
                if repos:
                    # Select one random repo from the results for this hour
                    repo = random.choice(repos)
                    
                    # Check if we already have this repo (avoid duplicates)
                    if repo["repo_name"] not in [r["repo_name"] for r in found_repos]:
                        found_repos.append(repo)
                        
                        # Write to file immediately to preserve progress
                        f.write(json.dumps(repo) + '\n')
                        f.flush()  # Ensure it's written to disk
                        
                        logging.info(f"Found {len(found_repos)}/{count} repositories: {repo['repo_name']}")
                        
                        # If we have enough repos, we can stop
                        if len(found_repos) >= count:
                            break
                
                # Add a small delay
                time.sleep(1)
                
            except RateLimitExceeded:
                logging.error("API rate limit reached. Stopping repository search.")
                break
            except Exception as e:
                logging.error(f"Error during repository search: {e}")
    
    elapsed_time = time.time() - start_time
    logging.info(f"Found {len(found_repos)} repositories in {elapsed_time:.2f} seconds")
    
    return found_repos

def main():
    """Main function to parse arguments and run the repository sampling"""
    parser = argparse.ArgumentParser(
        description="Sample random GitHub repositories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--count", type=int, default=10, help="Number of repositories to find")
    parser.add_argument("--min-stars", type=int, default=5, help="Minimum number of stars")
    parser.add_argument("--language", type=str, default="python", help="Programming language filter")
    parser.add_argument("--min-size", type=int, default=100, help="Minimum repository size in KB") 
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILE, help="Output file")
    parser.add_argument("--years-back", type=int, default=10, help="How many years back to sample from")
    
    args = parser.parse_args()
    
    try:
        repos = find_random_repos(
            count=args.count,
            min_stars=args.min_stars,
            language=args.language,
            min_size_kb=args.min_size,
            output_file=args.output,
            years_back=args.years_back
        )
        
        print(f"Found {len(repos)} repositories. Results saved to {args.output}")
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        
    except RateLimitExceeded:
        print("\nError: GitHub API rate limit exceeded.")
        print("Consider using a GitHub token or reducing the number of repositories.")
        
    except Exception as e:
        print(f"\nError: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
