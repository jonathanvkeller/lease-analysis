# Lease Analysis Tool

## Overview
Lease Analysis Tool is a Python-based project designed to parse, process, and analyze lease data. The tool reads documents stored in the data/leases folder, processes them using custom scripts in the src/ directory, and produces organized reports in various output folders.

## Features
- **Data Parsing:** Extracts key lease information.
- **Data Processing:** Analyzes lease data to generate insights.
- **Reporting:** Outputs summary and detailed reports.
- **Logging & Error Handling:** Built-in logging and exception management.

## Installation
1. Clone the repository:
   ```
   git clone [REPOSITORY_URL]
   ```
2. Navigate into the project directory.
3. Create and activate a virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`
4. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Follow these steps to use the Lease Analysis Tool:
1. Ensure that your lease files are saved in the `data/leases` folder.
2. Ensure that you have at least one prompt file in the `data/prompts` folder.
   - A corresponding folder will be created in the `output` directory for each prompt.
   - the prompt file should contain the exact text to send to the API
3. Review and, if necessary, update the configuration settings in `src/config.py` to match your environment or preferences.
4. Run the project by executing the main script from the root directory:
   ```
   python src/main.py
   ```
   This will trigger the parsing and processing of the lease data.
5. Monitor progress and check for any errors via the log files stored in the `logs/` directory.
6. Once processing is complete, review the generated reports located in the following directories:
   - `output/aggregate/` – Aggregated data reports.
   - `output/processed/` – Processed lease details.
   - `output/summaries/` – Summary reports.
7. For troubleshooting or further customization, consult the documentation comments within the source code in `src/`.

## Project Structure
- **data/** – Contains input lease documents. Lease files are stored in `data/leases`.
- **src/** – Contains the source code including `main.py`, `parser.py`, `processor.py`, `config.py`, and `utils.py`.
- **output/** – Contains generated reports in subdirectories (`aggregate`, `paid-up`, `processed`, `summaries`).
- **logs/** – Contains log files with runtime information.
- **exceptions/** – Contains custom exception handling modules.

## License
This project is licensed under the MIT License. Refer to the LICENSE file for details.

## Contributing
To contribute to this project:
- Fork the repository.
- Create a feature branch.
- Commit changes with descriptive messages.
- Submit a pull request for review.
