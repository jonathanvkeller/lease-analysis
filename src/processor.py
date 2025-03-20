# processor.py
import os
import logging
import time
import json
import shutil
from datetime import datetime
from openai import OpenAI
from . import config
from .utils import is_pdf, convert_pdf_to_images
import base64

class LeaseProcessor:
    def __init__(self, lease_folder, prompt_folder, output_folder, exceptions_folder, 
                 model="o3-mini", max_cost=500.0):
        """
        Initialize the lease processor.
        
        Args:
            lease_folder: Path to folder containing lease PDFs
            prompt_folder: Path to folder containing prompt files
            output_folder: Path to folder where results will be saved
            exceptions_folder: Path to folder where error files will be moved
            model: OpenAI model to use
            max_cost: Maximum cost allowed for API calls (in USD)
        """
        self.lease_folder = lease_folder
        self.prompt_folder = prompt_folder
        self.output_folder = output_folder
        self.exceptions_folder = exceptions_folder
        self.model = model
        self.max_cost = max_cost
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Stats tracking
        self.stats = {
            "total_leases": 0,
            "total_prompts": 0,
            "processed_combinations": 0,
            "successful": 0,
            "errors": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "estimated_cost": 0.0,
            "error_details": []
        }
    
    def get_lease_files(self):
        """Get all PDF files from the lease folder."""
        return [f for f in os.listdir(self.lease_folder) 
                if f.lower().endswith('.pdf')]
    
    def get_prompt_files(self):
        """Get all prompt files from the prompt folder."""
        return [f for f in os.listdir(self.prompt_folder) 
                if f.lower().endswith(('.txt', '.md'))]
    
    def read_prompt_file(self, file_name):
        """
        Read the content of a prompt file and extract the output name if available.
        
        Returns:
            tuple: (prompt_content, output_name)
        """
        file_path = os.path.join(self.prompt_folder, file_name)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        
        # Extract output name from the first line if it starts with "# NAME:"
        lines = content.split('\n')
        output_name = None
        
        if lines and lines[0].startswith("# NAME:"):
            output_name = lines[0][7:].strip()
            content = '\n'.join(lines[1:]).strip()
        else:
            # Use the file name without extension as the output name
            output_name = os.path.splitext(file_name)[0]
            
        return content, output_name
    
    def call_openai_api(self, prompt, lease_path):
        """
        Make an API call to OpenAI with the prompt and lease file.
        
        Returns:
            dict: API response or error information
        """
        try:
            lease_full_path = os.path.join(self.lease_folder, lease_path)
            if is_pdf(lease_full_path):
                images = convert_pdf_to_images(lease_full_path)
                image_messages = []
                for image_bytes in images:
                    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                    image_messages.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    })
                user_content = image_messages
            else:
                with open(lease_full_path, "rb") as file:
                    pdf_b64 = base64.b64encode(file.read()).decode('utf-8')
                user_content = [{
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:application/pdf;base64,{pdf_b64}"
                    }
                }]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                temperature=0.2  # Lower temperature for more deterministic outputs
            )

            # Update token usage
            usage = response.usage
            self.stats["total_tokens_input"] += usage.prompt_tokens
            self.stats["total_tokens_output"] += usage.completion_tokens

            # Calculate estimated cost
            token_costs = config.TOKEN_COSTS.get(self.model, config.TOKEN_COSTS["gpt-4o"])
            input_cost = usage.prompt_tokens * token_costs["input"]
            output_cost = usage.completion_tokens * token_costs["output"]
            current_cost = input_cost + output_cost

            self.stats["estimated_cost"] += current_cost

            if self.stats["estimated_cost"] > self.max_cost:
                raise Exception(f"Cost limit exceeded: ${self.stats['estimated_cost']:.2f} > ${self.max_cost:.2f}")

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }
        except Exception as e:
            logging.error(f"API call failed for {lease_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_output(self, prompt_name, lease_name, response):
        """
        Save the API response to a markdown file.
        
        Returns:
            str: Path to the saved file or None if failed
        """
        # Create output folder for this prompt if it doesn't exist
        prompt_output_folder = os.path.join(self.output_folder, prompt_name)
        # prompt_output_folder = os.path.join(self.output_folder, "summaries", prompt_name)
        os.makedirs(prompt_output_folder, exist_ok=True)
        
        # Create the output filename
        output_filename = f"{lease_name}.md"
        output_path = os.path.join(prompt_output_folder, output_filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                # If successful, write the content directly
                if response["success"]:
                    file.write(response["content"])
                # If failed, write error information
                else:
                    file.write("# Error Processing Lease\n\n")
                    file.write(f"**Error Message:** {response['error']}\n\n")
                    file.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return output_path
            
        except Exception as e:
            logging.error(f"Error saving output to {output_path}: {e}")
            return None
    
    def move_to_exceptions(self, lease_file):
        """Move a problematic lease file to the exceptions folder."""
        source_path = os.path.join(self.lease_folder, lease_file)
        dest_path = os.path.join(self.exceptions_folder, lease_file)
        
        try:
            shutil.move(source_path, dest_path)
            logging.info(f"Moved {lease_file} to exceptions folder")
            return True
        except Exception as e:
            logging.error(f"Failed to move {lease_file} to exceptions folder: {e}")
            return False

    def move_to_processed(self, lease_file):
        """Move a processed lease file to the processed folder inside the output folder."""
        source_path = os.path.join(self.lease_folder, lease_file)
        dest_path = os.path.join(self.output_folder, "processed", lease_file)
        try:
            shutil.move(source_path, dest_path)
            logging.info(f"Moved {lease_file} to processed folder")
            return True
        except Exception as e:
            logging.error(f"Failed to move {lease_file} to processed folder: {e}")
            return False
    
    def process(self):
        """Process all lease files with all prompts."""
        self.processing_start_time = datetime.now()
        lease_files = self.get_lease_files()
        prompt_files = self.get_prompt_files()
        
        self.stats["total_leases"] = len(lease_files)
        self.stats["total_prompts"] = len(prompt_files)
        
        if not lease_files:
            logging.error(f"No lease files found in {self.lease_folder}")
            return
        
        if not prompt_files:
            logging.error(f"No prompt files found in {self.prompt_folder}")
            return
        
        logging.info(f"Found {len(lease_files)} lease files and {len(prompt_files)} prompt files")
        
        total_combinations = len(lease_files) * len(prompt_files)
        processed = 0
        
        for lease_file in lease_files:
            lease_name = os.path.splitext(lease_file)[0]
            lease_success = True
            for prompt_file in prompt_files:
                prompt_content, prompt_name = self.read_prompt_file(prompt_file)
                logging.info(f"Processing lease '{lease_file}' with prompt '{prompt_file}' (Output name: {prompt_name})")
                response = self.call_openai_api(prompt_content, lease_file)
                self.stats["processed_combinations"] += 1
                if response["success"]:
                    output_path = self.save_output(prompt_name, lease_name, response)
                    if output_path:
                        logging.info(f"Saved output to {output_path}")
                        self.stats["successful"] += 1
                else:
                    self.stats["errors"] += 1
                    self.stats["error_details"].append({
                        "lease": lease_file,
                        "prompt": prompt_file,
                        "error": response["error"]
                    })
                    self.save_output(prompt_name, lease_name, response)
                    self.move_to_exceptions(lease_file)
                    lease_success = False
                    break

                logging.info(f"Current estimated cost: ${self.stats['estimated_cost']:.4f}")

                if self.stats["estimated_cost"] > self.max_cost:
                    logging.warning(f"Cost limit reached (${self.stats['estimated_cost']:.2f}). Stopping processing.")
                    return

            if lease_success:
                self.move_to_processed(lease_file)
                logging.info(f"Completed processing for {lease_file}, moved to processed folder")
    
    def generate_report(self):
        """Generate a summary report of the processing."""
        processing_end = datetime.now()
        total_time_delta = processing_end - self.processing_start_time
        total_seconds = int(total_time_delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        total_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_stats": {
                "total_leases": self.stats["total_leases"],
                "total_prompts": self.stats["total_prompts"],
                "total_combinations": self.stats["total_leases"] * self.stats["total_prompts"],
                "processed_combinations": self.stats["processed_combinations"],
                "successful": self.stats["successful"],
                "errors": self.stats["errors"],
                "total_processing_time": total_time_str
            },
            "usage_stats": {
                "total_tokens_input": self.stats["total_tokens_input"],
                "total_tokens_output": self.stats["total_tokens_output"],
                "total_tokens": self.stats["total_tokens_input"] + self.stats["total_tokens_output"],
                "estimated_cost": f"${self.stats['estimated_cost']:.4f}"
            },
            "errors": self.stats["error_details"] if self.stats["errors"] > 0 else []
        }
        
        # Save to JSON file
        report_path = os.path.join(self.output_folder, "summaries", f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Also create a markdown version
        md_report_path = os.path.join(self.output_folder, "summaries", f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        with open(md_report_path, 'w', encoding='utf-8') as f:
            f.write("# Lease Analysis Summary Report\n\n")
            f.write(f"Generated: {report['timestamp']}\n\n")
            
            f.write("## Execution Statistics\n\n")
            f.write(f"- Total lease documents: {report['execution_stats']['total_leases']}\n")
            f.write(f"- Total prompts: {report['execution_stats']['total_prompts']}\n")
            f.write(f"- Total combinations: {report['execution_stats']['total_combinations']}\n")
            f.write(f"- Processed combinations: {report['execution_stats']['processed_combinations']}\n")
            f.write(f"- Successful: {report['execution_stats']['successful']}\n")
            f.write(f"- Errors: {report['execution_stats']['errors']}\n")
            f.write(f"- Total processing time: {report['execution_stats']['total_processing_time']}\n\n")
            
            f.write("## Usage Statistics\n\n")
            f.write(f"- Total input tokens: {report['usage_stats']['total_tokens_input']:,}\n")
            f.write(f"- Total output tokens: {report['usage_stats']['total_tokens_output']:,}\n")
            f.write(f"- Total tokens: {report['usage_stats']['total_tokens']:,}\n")
            f.write(f"- Estimated cost: {report['usage_stats']['estimated_cost']}\n\n")
            
            if report['errors']:
                f.write("## Errors\n\n")
                for i, error in enumerate(report['errors']):
                    f.write(f"### Error {i+1}\n\n")
                    f.write(f"- Lease file: `{error['lease']}`\n")
                    f.write(f"- Prompt file: `{error['prompt']}`\n")
                    f.write(f"- Error message: `{error['error']}`\n\n")
        
        logging.info(f"Generated summary report: {md_report_path}")
        
        return report
