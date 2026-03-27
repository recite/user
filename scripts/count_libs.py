#!/usr/bin/env python3
"""
Library Import Counter

This script processes a JSON Lines file with GitHub repository import data
and produces a CSV file with library name and occurrence counts.
"""
import json
import csv
import argparse
import tarfile
import os
import tempfile
from collections import Counter

def count_libraries(input_file, output_file):
    """
    Count library occurrences from JSON Lines input file and write results to CSV.

    Args:
        input_file (str): Path to input JSON Lines file (or .tar.gz archive)
        output_file (str): Path to output CSV file
    """
    library_counter = Counter()
    temp_file = None

    if input_file.endswith('.tar.gz'):
        with tarfile.open(input_file, 'r:gz') as tar:
            members = tar.getnames()
            jsonl_name = members[0] if members else 'imports.jsonl'
            temp_dir = tempfile.mkdtemp()
            tar.extractall(path=temp_dir)
            actual_file = os.path.join(temp_dir, jsonl_name)
            temp_file = temp_dir
    else:
        actual_file = input_file

    try:
        with open(actual_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if 'library' in data:
                        library_counter[data['library']] += 1
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON line: {line[:50]}...")
                    continue
    finally:
        if temp_file:
            import shutil
            shutil.rmtree(temp_file)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['library', 'count'])
        for library, count in library_counter.most_common():
            writer.writerow([library, count])

    print(f"Processing complete: Found {len(library_counter)} unique libraries.")
    print(f"Results written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count library imports from GitHub repository data")
    parser.add_argument("input_file", help="Path to the input JSON Lines file")
    parser.add_argument("-o", "--output", default="library_counts.csv", 
                        help="Path to the output CSV file (default: library_counts.csv)")
    
    args = parser.parse_args()
    
    count_libraries(args.input_file, args.output)
