#!/usr/bin/env python3
"""
Generate optimized dashboard data files for fast loading
"""
import os
import json
import csv
import argparse
from datetime import datetime


def generate_dashboard_data(csv_file, processed_file, output_dir):
    """
    Generate optimized data files for the dashboard:
    1. dashboard.json - Essential stats + top 100 packages
    2. search_index.json - All package names for search autocomplete
    """
    # Read library counts
    libraries = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            libraries.append({
                'name': row['library'],
                'count': int(row['count'])
            })
    
    # Read processed repos count
    total_repos = 0
    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            total_repos = len([line for line in f if line.strip()])
    
    # Calculate statistics
    total_imports = sum(lib['count'] for lib in libraries)
    unique_packages = len(libraries)
    
    # Get actual file modification time for lastUpdated
    if os.path.exists(csv_file):
        csv_mod_time = os.path.getmtime(csv_file)
        last_updated = datetime.fromtimestamp(csv_mod_time).isoformat() + 'Z'
    else:
        last_updated = datetime.now().isoformat() + 'Z'
    
    # Generate dashboard.json (top 100 + stats)
    dashboard_data = {
        'stats': {
            'totalRepos': total_repos,
            'totalImports': total_imports,
            'uniquePackages': unique_packages,
            'lastUpdated': last_updated,
            'samplePercent': round((total_repos / 18_000_000) * 100, 3)
        },
        'topPackages': libraries[:100]  # Top 100 for charts
    }
    
    # Generate search_index.json (all package names)
    search_index = {
        'packages': [lib['name'] for lib in libraries],
        'count': unique_packages
    }
    
    # Write files
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'dashboard.json'), 'w') as f:
        json.dump(dashboard_data, f, separators=(',', ':'))  # Compact format
    
    with open(os.path.join(output_dir, 'search_index.json'), 'w') as f:
        json.dump(search_index, f, separators=(',', ':'))  # Compact format
    
    print(f"Generated dashboard.json: {len(json.dumps(dashboard_data))} bytes")
    print(f"Generated search_index.json: {len(json.dumps(search_index))} bytes")
    print(f"Total packages: {unique_packages}")
    print(f"Original CSV size: {os.path.getsize(csv_file)} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate optimized dashboard data")
    parser.add_argument("--csv", type=str, default="data/library_counts.csv", 
                        help="Path to library counts CSV")
    parser.add_argument("--processed", type=str, default="data/processed_repos.txt", 
                        help="Path to processed repos file")
    parser.add_argument("--output", type=str, default="data", 
                        help="Output directory")
    
    args = parser.parse_args()
    
    generate_dashboard_data(args.csv, args.processed, args.output)