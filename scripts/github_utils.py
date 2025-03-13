# github_utils.py
import os
import logging
import time
import random
import json
import requests
from typing import Dict, Any, Optional, Tuple, List
from requests.exceptions import RequestException

# Constants
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# API rate limit tracking
api_requests_count = 0
api_request_reset_time = time.time() + 3600  # Start with assumption of 1 hour window

class RateLimitExceeded(Exception):
    """Exception raised when GitHub API rate limit is exceeded."""
    pass

def get_headers() -> Dict[str, str]:
    """Get headers for API requests with authentication if available."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def track_api_request():
    """
    Track API request count for GitHub Actions limits (1000/hour).
    Raises exception if approaching limit.
    """
    global api_requests_count, api_request_reset_time
    
    current_time = time.time()
    
    # Reset counter if hour has passed
    if current_time > api_request_reset_time:
        api_requests_count = 0
        api_request_reset_time = current_time + 3600
    
    api_requests_count += 1
    
    # GitHub Actions has a limit of 1000 API requests per hour
    # We'll be conservative and cap at 900 to leave room for other operations
    if api_requests_count >= 900:
        logging.error(f"Approaching GitHub Actions API request limit ({api_requests_count}/1000)")
        raise RateLimitExceeded("GitHub Actions API request limit reached")
    
    # Log every 100 requests
    if api_requests_count % 100 == 0:
        logging.info(f"API request count: {api_requests_count}/1000 for this hour")

def make_github_request(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make a request to GitHub API with GitHub Actions limits in mind.
    
    Args:
        url: The API URL to request
        params: Optional query parameters
        
    Returns:
        Parsed JSON response
        
    Raises:
        RateLimitExceeded: If limits are reached
        RequestException: For other request errors
    """
    # Track this request against our hourly quota
    track_api_request()
    
    try:
        response = requests.get(url, headers=get_headers(), params=params)
        
        # Handle rate limiting - no retry, just report the error
        if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
            remaining = int(response.headers['X-RateLimit-Remaining'])
            if remaining == 0:
                reset_time = int(response.headers['X-RateLimit-Reset'])
                wait_time = max(0, reset_time - time.time())
                logging.error(f"Rate limit exceeded. Would reset in {wait_time/60:.1f} minutes.")
                raise RateLimitExceeded("GitHub API rate limit exceeded")
        
        # Special handling for common error codes
        if response.status_code == 404:
            logging.warning(f"Resource not found: {url}")
        elif response.status_code == 451:
            logging.warning(f"Resource unavailable for legal reasons (451): {url}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        logging.warning(f"HTTP error for {url}: {e}")
        raise
    except json.JSONDecodeError as e:
        logging.warning(f"JSON decode error for {url}: {e}")
        raise
    except RequestException as e:
        logging.warning(f"Request error for {url}: {e}")
        raise

def is_runtime_expired(start_time: float, max_runtime_seconds: int = 21000) -> bool:
    """Check if we're approaching GitHub Actions runtime limit."""
    elapsed_time = time.time() - start_time
    return elapsed_time > max_runtime_seconds

def save_results(results: List[Tuple], output_file: str, format_json=True):
    """Save results to a file."""
    with open(output_file, 'a') as f:
        for result in results:
            if format_json:
                # Convert tuple to dictionary
                result_obj = {
                    "library": result[0],
                    "repo": result[1],
                    "file_path": result[2],
                    "fetch_date": result[3],
                    "last_updated": result[4]
                }
                f.write(json.dumps(result_obj) + '\n')
            else:
                # Write as CSV-like format
                f.write(','.join(str(item) for item in result) + '\n')
