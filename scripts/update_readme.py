#!/usr/bin/env python3
"""
Update README.md with top library counts

This script reads the library_counts.csv file and updates the README.md
with a table of the top libraries.
"""
import os
import csv
import re
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_readme_with_library_stats(csv_file, readme_file, top_n=10):
    """
    Update the README.md file with a table of the top libraries from the CSV.
    
    Args:
        csv_file: Path to the library counts CSV file
        readme_file: Path to the README.md file
        top_n: Number of top libraries to include
    """
    if not os.path.exists(csv_file):
        logging.error(f"CSV file not found: {csv_file}")
        return False
    
    # Read the top N libraries from the CSV
    top_libraries = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header row
            next(reader, None)
            
            # Get top N rows
            for i, row in enumerate(reader):
                if i >= top_n:
                    break
                if len(row) >= 2:
                    top_libraries.append((row[0], row[1]))
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return False
    
    if not top_libraries:
        logging.warning("No library data found in CSV")
        return False
    
    # Format the data as a markdown table
    table_content = "## Top Python Libraries\n\n"
    table_content += "| Rank | Library | Count |\n"
    table_content += "|------|---------|-------|\n"
    
    for i, (library, count) in enumerate(top_libraries, 1):
        table_content += f"| {i} | {library} | {count} |\n"
    
    table_content += f"\n*Last updated: {os.path.getmtime(csv_file)}*\n"
    
    # Check if README exists
    if not os.path.exists(readme_file):
        # Create new README with the table
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write("# GitHub Repository Python Library Analysis\n\n")
            f.write("Analysis of Python libraries used in GitHub repositories.\n\n")
            f.write(table_content)
        logging.info(f"Created new README.md with library stats")
        return True
    
    # Read existing README
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define regex pattern to find the existing table section
    pattern = r"## Top Python Libraries\n\n\|.*?\n\n"
    
    if re.search(pattern, content, re.DOTALL):
        # Replace existing table
        new_content = re.sub(pattern, table_content, content, flags=re.DOTALL)
    else:
        # Append the table to the end of the README
        new_content = content + "\n\n" + table_content
    
    # Write updated content
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logging.info(f"Updated README.md with top {top_n} libraries")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update README with library statistics")
    parser.add_argument("--csv", type=str, default="data/library_counts.csv", 
                        help="Path to the library counts CSV file")
    parser.add_argument("--readme", type=str, default="README.md", 
                        help="Path to the README.md file")
    parser.add_argument("--top", type=int, default=10, 
                        help="Number of top libraries to include")
    
    args = parser.parse_args()
    
    update_readme_with_library_stats(args.csv, args.readme, args.top)