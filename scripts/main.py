#!/usr/bin/env python3
# scripts/main.py
import os
import argparse
import logging
import time
from typing import Optional

# Import functionality from other modules
from github_utils import is_runtime_expired
from find_repos import find_random_repos
from analyze_imports import process_repo_from_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def enough_unprocessed_repos(repos_file: str, processed_file: str, buffer: int = 5) -> bool:
    """
    Check if there are enough unprocessed repositories.
    
    Args:
        repos_file: File containing repository information
        processed_file: File containing processed repository names
        buffer: Minimum number of unprocessed repositories required
        
    Returns:
        True if there are enough unprocessed repositories, False otherwise
    """
    import json
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(repos_file) if os.path.dirname(repos_file) else '.', exist_ok=True)
    os.makedirs(os.path.dirname(processed_file) if os.path.dirname(processed_file) else '.', exist_ok=True)
    
    # Load processed repositories
    processed_repos = set()
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            processed_repos = {line.strip() for line in f}
    
    # Count unprocessed repositories
    unprocessed_count = 0
    if os.path.exists(repos_file):
        with open(repos_file, 'r') as f:
            for line in f:
                try:
                    repo_data = json.loads(line.strip())
                    repo_name = repo_data.get("repo_name")
                    
                    if repo_name and repo_name not in processed_repos:
                        unprocessed_count += 1
                        
                        # Early exit if we have enough
                        if unprocessed_count >= buffer:
                            return True
                except json.JSONDecodeError:
                    continue
    
    return unprocessed_count >= buffer

def run_incremental_process(
    repos_file: str = "repos.jsonl",
    imports_file: str = "imports.jsonl",
    processed_file: str = "processed_repos.txt",
    repos_to_find: int = 5,
    repos_to_process: int = 1,
    min_stars: int = 5,
    language: str = "python",
    max_files: int = 10,
    max_runtime: int = 21000  # ~6 hours minus buffer
) -> None:
    """
    Run the incremental process:
    1. Find repos if needed
    2. Process a batch of repos
    
    Args:
        repos_file: File to store repository information
        imports_file: File to store import information
        processed_file: File to track processed repositories
        repos_to_find: Number of new repositories to find if needed
        repos_to_process: Number of repositories to process in this run
        min_stars: Minimum stars for random repo search
        language: Programming language filter
        max_files: Maximum number of Python files to analyze per repository
        max_runtime: Maximum runtime in seconds
    """
    start_time = time.time()
    logging.info("Starting incremental process")
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(repos_file) if os.path.dirname(repos_file) else '.', exist_ok=True)
    os.makedirs(os.path.dirname(imports_file) if os.path.dirname(imports_file) else '.', exist_ok=True)
    os.makedirs(os.path.dirname(processed_file) if os.path.dirname(processed_file) else '.', exist_ok=True)
    
    # Step 1: Find repositories if needed
    if not enough_unprocessed_repos(repos_file, processed_file):
        logging.info(f"Finding {repos_to_find} new repositories")
        find_random_repos(
            count=repos_to_find,
            min_stars=min_stars,
            language=language,
            output_file=repos_file
        )
    
    # Step 2: Process repositories
    processed_count = 0
    for i in range(repos_to_process):
        # Check if we're approaching runtime limits
        elapsed_time = time.time() - start_time
        if elapsed_time > max_runtime:
            logging.warning("Approaching runtime limit, stopping early")
            break
        
        logging.info(f"Processing repository {i+1}/{repos_to_process}")
        if process_repo_from_file(
            repo_file=repos_file,
            output_file=imports_file,
            processed_file=processed_file,
            max_files=max_files
        ):
            processed_count += 1
        
        # Small delay between repositories
        time.sleep(1)
    
    elapsed_time = time.time() - start_time
    logging.info(f"Processed {processed_count}/{repos_to_process} repositories in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Incremental GitHub repository analysis")
    parser.add_argument("--repos-file", type=str, required=True, help="Repository information file")
    parser.add_argument("--imports-file", type=str, required=True, help="Output file for imports")
    parser.add_argument("--processed-file", type=str, required=True, help="File to track processed repositories")
    parser.add_argument("--repos-to-find", type=int, default=5, help="Number of new repositories to find if needed")
    parser.add_argument("--repos-to-process", type=int, default=1, help="Number of repositories to process in this run")
    parser.add_argument("--min-stars", type=int, default=5, help="Minimum stars for random repo search")
    parser.add_argument("--language", type=str, default="python", help="Programming language filter")
    parser.add_argument("--max-files", type=int, default=10, help="Maximum number of Python files to analyze per repository")
    
    args = parser.parse_args()
    
    run_incremental_process(
        repos_file=args.repos_file,
        imports_file=args.imports_file,
        processed_file=args.processed_file,
        repos_to_find=args.repos_to_find,
        repos_to_process=args.repos_to_process,
        min_stars=args.min_stars,
        language=args.language,
        max_files=args.max_files
    )