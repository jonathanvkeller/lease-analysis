import os
import re

def aggregate_clause_folder(clause_folder_path, aggregate_output_path):
    """
    Process a clause folder by aggregating markdown content from each file,
    excluding files that contain "I'm sorry, I can't assist with that."
    and ignoring the "## STATUS" section.
    The aggregated content for each section is appended as an unordered list.
    """
    # Dictionary to store aggregated content for each section header (e.g., "## CLAUSE")
    sections = {}

    # List all markdown files in the clause folder
    for filename in os.listdir(clause_folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(clause_folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Skip file if it contains the disallowed phrase
            if "I'm sorry, I can't assist with that." in content:
                continue

            # Split content into sections using headers that start with "##"
            parts = re.split(r'(^##\s+.*$)', content, flags=re.MULTILINE)

            # If the content does not start with a header, skip the preamble
            if parts and not parts[0].startswith("##"):
                parts = parts[1:]

            # Process sections in pairs: header and its content
            for i in range(0, len(parts), 2):
                header = parts[i].strip()
                body = parts[i+1].strip() if i+1 < len(parts) else ""
                # Skip the STATUS and ASSESSMENT sections
                if header.upper() in ["## STATUS", "## ASSESSMENT"]:
                    continue
                # Initialize list for the section if not already present
                if header not in sections:
                    sections[header] = []
                # Append this file's section content if it exists
                if body:
                    sections[header].append(body)

    # Build aggregated markdown content in lowercase and sorted by section
    output_lines = []
    for header in sorted(sections.keys(), key=lambda h: h[3:].strip().lower() if h.startswith("## ") else h.lower()):
        lower_header = header.lower()
        output_lines.append(lower_header)
        output_lines.append("")  # blank line
        if header.lower() == "## chunk size":
            # Calculate average chunk size
            total_tokens = 0
            total_overlap = 0
            count = 0
            for item in sections[header]:
                match = re.search(r'(\d+)\s+tokens\s+with\s+a\s+(\d+)-token\s+overlap', item)
                if match:
                    total_tokens += int(match.group(1))
                    total_overlap += int(match.group(2))
                    count += 1
            if count > 0:
                avg_tokens = total_tokens // count
                avg_overlap = total_overlap // count
                output_lines.append(f"recommend a chunk size of {avg_tokens} tokens with a {avg_overlap}-token overlap")
        else:
            for item in sorted(sections[header], key=lambda i: i.lower()):
                sanitized_item = item.lower().strip()
                sanitized_item = re.sub(r'^[-\s]+', '', sanitized_item)
                sanitized_item = re.sub(r'^"+|"+$', '', sanitized_item).strip()
                if "n/a" in sanitized_item:
                    continue
                output_lines.append(f"- {sanitized_item}")
        output_lines.append("")  # blank line after each section

    aggregated_content = "\n".join(output_lines)
    # Determine output file path based on the clause folder name
    aggregated_filename = os.path.basename(clause_folder_path) + ".md"
    aggregated_filepath = os.path.join(aggregate_output_path, aggregated_filename)

    # Ensure the aggregate output folder exists
    os.makedirs(aggregate_output_path, exist_ok=True)
    try:
        with open(aggregated_filepath, 'w', encoding='utf-8') as f:
            f.write(aggregated_content)
        print(f"Aggregated file created: {aggregated_filepath}")
    except Exception as e:
        print(f"Error writing aggregated file {aggregated_filepath}: {e}")

def main():
    base_output = os.path.join("output")
    aggregate_output = os.path.join(base_output, "aggregate")
    processed_output = os.path.join(base_output, "processed")
    os.makedirs(processed_output, exist_ok=True)
    
    # List clause folders: all directories in "output" excluding "processed", "summaries", and "aggregate"
    for entry in os.listdir(base_output):
        path = os.path.join(base_output, entry)
        if os.path.isdir(path) and entry.lower() not in ["processed", "summaries", "aggregate"]:
            print(f"Processing clause folder: {path}")
            aggregate_clause_folder(path, aggregate_output)

if __name__ == "__main__":
    main()
