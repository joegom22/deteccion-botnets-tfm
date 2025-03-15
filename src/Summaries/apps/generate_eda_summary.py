import sys
import logging
import argparse
from DataProcessor import DataProcessor
from SummaryGenerator import SummaryGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main(args) -> None:
    file_path = args.get("file_path")

    # Initialize DataProcessor and SummaryGenerator objects
    data_processor = DataProcessor(file_path)
    summary_generator = SummaryGenerator(args.get("output_path"), title="Exploratory Data Analysis Report")

    # Load dataset from CSV file
    data_processor.load_dataset(file_path)

    # Clean dataset by removing null values and duplicate entries
    data_processor.clean_dataset()

    # Detect outliers in the dataset
    data_processor.detect_outliers()

    # Detect columns correlation
    data_processor.detect_correlation()

    # Generate summary report
    summary_generator.add_text("Data Summary")
    summary_generator.add_section_header("Dataset Information")
    summary_generator.add_text(f"Number of rows: {data_processor.df.shape[0]}")
    summary_generator.add_text(f"Number of columns: {data_processor.df.shape[1]}")