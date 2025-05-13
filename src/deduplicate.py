#!/usr/bin/env python3
"""
Deduplicate an aggregate markdown file that is already in lowercase and sorted by section.
Each section starts with a header line beginning with "## " and is followed by bullet items.
This script removes duplicate bullet lines within each section.
Future enhancements may include fuzzy matching.
Usage:
    python deduplicate.py <path_to_aggregate_file>
"""
import sys
import os

def deduplicate_aggregate_file(input_filepath):
    temp_filepath = input_filepath + ".tmp"
    with open(input_filepath, 'r', encoding='utf-8') as infile, open(temp_filepath, 'w', encoding='utf-8') as outfile:
        last_bullet = None
        for line in infile:
            stripped = line.rstrip("\n")
            if stripped.startswith("## "):
                # New section header; write header and reset last bullet
                outfile.write(line)
                last_bullet = None
            elif stripped.startswith("- "):
                # Bullet line: skip if it is a duplicate of the previous bullet in this section
                if stripped == last_bullet:
                    continue
                else:
                    outfile.write(line)
                    last_bullet = stripped
            else:
                outfile.write(line)
    # Overwrite the original file with the deduplicated version
    os.replace(temp_filepath, input_filepath)

def main():
    if len(sys.argv) < 2:
        print("Usage: deduplicate.py <path_to_aggregate_file>")
        sys.exit(1)
    input_filepath = sys.argv[1]
    if not os.path.isfile(input_filepath):
        print(f"File not found: {input_filepath}")
        sys.exit(1)
    deduplicate_aggregate_file(input_filepath)
    print(f"Deduplicated file saved: {input_filepath}")

if __name__ == "__main__":
    main()
