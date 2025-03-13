# analyze_imports.py
import os
import logging
import tempfile
import subprocess
import time
from datetime import datetime
import ast
import re
import json
import argparse
from typing import List, Tuple, Set, Optional
from github_utils import save_results, is_runtime_expired

def extract_imports(content: str) -> Set[str]:
    """
    Extract imported libraries from Python content using AST parsing
    and regex as a fallback for edge cases.
    """
    libraries = set()
    
    # AST parsing for reliable import extraction
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    libraries.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    libraries.add(node.module.split('.')[0])
    except SyntaxError:
        # Fallback to regex for files with syntax errors
        import_pattern = r'^import\s+([\w\.]+)|^from\s+([\w\.]+)\s+import'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            lib = match.group(1) or match.group(2)
            if lib:
                libraries.add(lib.split('.')[0])
                
    return libraries

def analyze_repo(repo_info: Tuple[str, str, str], max_files: int = 10) -> List[Tuple[str, str, str, str, str]]:
    """
    Analyze a GitHub repository for Python library usage by cloning it once.
    
    Args:
        repo_info: Tuple of (repo_name, repo_url, last_updated)
        max_files: Maximum number of Python files to analyze
        
    Returns:
        List of tuples (library_name, repo_name, file_path, fetch_date, last_updated)
    """
    repo_name, repo_url, last_updated = repo_info
    logging.info(f"Processing repo: {repo_name}")
    
    repo_results = []
    fetch_date = datetime.utcnow().isoformat()
    
    # Create a temporary directory for the cloned repo
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository with minimal depth
            clone_cmd = f"git clone --depth 1 --single-branch https://github.com/{repo_name}.git {temp_dir}"
            process = subprocess.run(
                clone_cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout for cloning
            )
            
            if process.returncode != 0:
                logging.error(f"Failed to clone repository: {process.stderr}")
                return []
            
            # Find Python files in the repository (limit search time to 2 minutes)
            search_start = time.time()
            python_files = []
            max_search_time = 120  # 2 minutes
            
            for root, _, files in os.walk(temp_dir):
                # Check if we're exceeding our search time budget
                if time.time() - search_start > max_search_time:
                    logging.warning(f"Search time limit reached after finding {len(python_files)} Python files")
                    break
                    
                for file in files:
                    if file.endswith('.py'):
                        relative_path = os.path.relpath(os.path.join(root, file), temp_dir)
                        python_files.append(relative_path)
                
                # Limit the number of files to analyze
                if len(python_files) >= max_files:
                    python_files = python_files[:max_files]
                    break
            
            # Process each Python file with a per-file timeout
            for file_path in python_files:
                try:
                    # Skip files larger than 1MB to avoid processing huge files
                    full_path = os.path.join(temp_dir, file_path)
                    if os.path.getsize(full_path) > 1_000_000:
                        logging.info(f"Skipping large file {file_path} ({os.path.getsize(full_path)/1_000_000:.2f} MB)")
                        continue
                        
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extract imports
                    imports = extract_imports(content)
                    
                    for library in imports:
                        repo_results.append((
                            library, 
                            repo_name, 
                            file_path, 
                            fetch_date, 
                            last_updated
                        ))
                except Exception as e:
                    logging.warning(f"Error processing file {file_path} in {repo_name}: {e}")
            
            return repo_results
        
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout while processing {repo_name}")
            return []
        except Exception as e:
            logging.error(f"Failed to analyze repo {repo_name}: {e}")
            return []

def process_repo_from_file(
    repo_file: str,
    output_file: str = "imports.jsonl", 
    processed_file: str = "processed_repos.txt",
    max_files: int = 10
) -> bool:
    """
    Process a single repository from a file containing repository information.
    
    Args:
        repo_file: Path to file containing repository information (JSONL)
        output_file: Path to output file for imports
        processed_file: Path to file containing processed repository names
        max_files: Maximum number of Python files to analyze per repository
        
    Returns:
        True if successful, False otherwise
    """
    # Load already processed repositories
    processed_repos = set()
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            processed_repos = {line.strip() for line in f}
    
    # Find next repository to process
    next_repo = None
    with open(repo_file, 'r') as f:
        for line in f:
            try:
                repo_data = json.loads(line.strip())
                repo_name = repo_data.get("repo_name")
                
                if repo_name and repo_name not in processed_repos:
                    next_repo = (
                        repo_name,
                        repo_data.get("repo_url", f"https://github.com/{repo_name}"),
                        repo_data.get("last_updated", datetime.utcnow().isoformat())
                    )
                    break
            except json.JSONDecodeError:
                continue
    
    if not next_repo:
        logging.info("No unprocessed repositories found")
        return False
    
    # Process the repository
    logging.info(f"Processing repository: {next_repo[0]}")
    try:
        results = analyze_repo(next_repo, max_files)
        
        if results:
            # Save results
            save_results(results, output_file)
            logging.info(f"Found {len(results)} imported libraries in {next_repo[0]}")
        
        # Mark as processed
        with open(processed_file, 'a') as f:
            f.write(f"{next_repo[0]}\n")
        
        return True
    
    except Exception as e:
        logging.error(f"Error processing repository {next_repo[0]}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python imports in repositories")
    parser.add_argument("--repos", type=str, default="repos.jsonl", help="Repository information file")
    parser.add_argument("--output", type=str, default="imports.jsonl", help="Output file for imports")
    parser.add_argument("--processed", type=str, default="processed_repos.txt", help="File to track processed repositories")
    parser.add_argument("--max-files", type=int, default=10, help="Maximum number of Python files to analyze per repository")
    parser.add_argument("--count", type=int, default=1, help="Number of repositories to process in this run")
    
    args = parser.parse_args()
    
    start_time = time.time()
    successful = 0
    
    for i in range(args.count):
        # Check if we're approaching runtime limits
        if is_runtime_expired(start_time):
            logging.warning("Approaching runtime limit, stopping early")
            break
        
        if process_repo_from_file(
            repo_file=args.repos,
            output_file=args.output,
            processed_file=args.processed,
            max_files=args.max_files
        ):
            successful += 1
        
        # Small delay between repositories
        time.sleep(1)
    
    elapsed_time = time.time() - start_time
    logging.info(f"Processed {successful}/{args.count} repositories in {elapsed_time:.2f} seconds")
    print(f"Processed {successful} repositories. Results saved to {args.output}")