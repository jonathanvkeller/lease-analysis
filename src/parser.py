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
                # Skip the STATUS section
                if header.upper() == "## STATUS":
                    continue
                # Initialize list for the section if not already present
                if header not in sections:
                    sections[header] = []
                # Append this file's section content if it exists
                if body:
                    sections[header].append(body)

    # Build aggregated markdown content
    output_lines = []
    for header, items in sections.items():
        output_lines.append(header)
        output_lines.append("")  # blank line
        for item in items:
            # Append each aggregated item as an unordered list bullet
            output_lines.append(f"- {item}")
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
    
    # List clause folders: all directories in "output" excluding "processed", "summaries", and "aggregate"
    for entry in os.listdir(base_output):
        path = os.path.join(base_output, entry)
        if os.path.isdir(path) and entry.lower() not in ["processed", "summaries", "aggregate"]:
            print(f"Processing clause folder: {path}")
            aggregate_clause_folder(path, aggregate_output)

if __name__ == "__main__":
    main()
