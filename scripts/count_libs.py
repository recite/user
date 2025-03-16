#!/usr/bin/env python3
"""
Library Import Counter

This script processes a JSON Lines file with GitHub repository import data
and produces a CSV file with library name and occurrence counts.
"""
import json
import csv
import argparse
from collections import Counter

def count_libraries(input_file, output_file):
    """
    Count library occurrences from JSON Lines input file and write results to CSV.
    
    Args:
        input_file (str): Path to input JSON Lines file
        output_file (str): Path to output CSV file
    """
    # Initialize counter for libraries
    library_counter = Counter()
    
    # Read and process the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                # Parse each JSON line
                data = json.loads(line.strip())
                
                # Extract and count the library
                if 'library' in data:
                    library_counter[data['library']] += 1
            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON line: {line[:50]}...")
                continue
    
    # Write the results to CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['library', 'count'])
        
        # Write data rows (sorted by count in descending order)
        for library, count in library_counter.most_common():
            writer.writerow([library, count])
    
    print(f"Processing complete: Found {len(library_counter)} unique libraries.")
    print(f"Results written to {output_file}")
    
