# main.py
import os
import argparse
import logging
from datetime import datetime
from . import config
from .processor import LeaseProcessor

def setup_logging():
    """Set up logging configuration"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"processing_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def setup_folders():
    """Create necessary folders if they don't exist"""
    os.makedirs(config.LEASE_FOLDER, exist_ok=True)
    os.makedirs(config.PROMPT_FOLDER, exist_ok=True)
    os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(config.EXCEPTIONS_FOLDER, exist_ok=True)

def main():
    """Main entry point for the lease analysis script"""
    parser = argparse.ArgumentParser(description="Process lease documents with OpenAI")
    parser.add_argument("--max-cost", type=float, default=config.MAX_COST,
                        help=f"Maximum cost in USD (default: ${config.MAX_COST})")
    parser.add_argument("--model", default=config.MODEL,
                        help=f"OpenAI model to use (default: {config.MODEL})")
    args = parser.parse_args()
    
    # Setup environment
    setup_logging()
    setup_folders()
    
    # Log startup information
    logging.info("Starting lease analysis process")
    logging.info(f"Using model: {args.model}")
    logging.info(f"Maximum cost: ${args.max_cost}")
    logging.info(f"Lease folder: {config.LEASE_FOLDER}")
    logging.info(f"Prompt folder: {config.PROMPT_FOLDER}")
    
    # Initialize and run processor
    processor = LeaseProcessor(
        lease_folder=config.LEASE_FOLDER,
        prompt_folder=config.PROMPT_FOLDER,
        output_folder=config.OUTPUT_FOLDER,
        exceptions_folder=config.EXCEPTIONS_FOLDER,
        model=args.model,
        max_cost=args.max_cost
    )
    
    try:
        processor.process()
        processor.generate_report()
    except Exception as e:
        logging.error(f"Process failed: {e}")
        raise

if __name__ == "__main__":
    main()