import sys
import logging
import argparse
from EDA.DataProcessor import DataProcessor
from Summaries.SummaryGenerator import SummaryGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main(args) -> None:
    logging.info("Starting Exploratory Data Analysis...")
    file_path = args.get("file_path")

    # Initialize DataProcessor and SummaryGenerator objects
    logging.info(f"Initializing DataProcessor and SummaryGenerator objects...")
    data_processor = DataProcessor(file_path)
    summary_generator = SummaryGenerator(args.get("output_path"), title="Exploratory Data Analysis Report")

    # Load dataset from CSV file
    logging.info("Loading dataset from file...")
    data_processor.load_dataset("csv")

    # Clean dataset by removing null values and duplicate entries
    logging.info("Cleaning dataset...")
    data_processor.clean_dataset()

    # Detect outliers in the dataset
    data_processor.detect_outliers()

    # Detect columns correlation
    data_processor.detect_correlation()

    # Generate summary report
    #summary_generator.add_section_header("Dataset Information")
    #summary_generator.add_text(f"Number of rows: {data_processor.df.shape[0]}")
    #summary_generator.add_text(f"Number of columns: {data_processor.df.shape[1]}")
    #summary_generator.add_section_header("Outlier Analysis")
    #summary_generator.add_text(data_processor.outliers_text)
    #summary_generator.add_section_header("Correlation Analysis")
    #summary_generator.add_text(data_processor.correlation_text)
    #summary_generator.add_image("./src/EDA/assets/correl_matrix.png", "Correlation matrix of the dataset")    
    #summary_generator.save_pdf()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform exploratory data analysis on a CSV file.")
    parser.add_argument("--file_path", required=True, help="Path to the CSV file to be analyzed.")
    parser.add_argument("--output_path", default="eda_report.pdf", help="Path to the PDF file where the report will be saved. (default: eda_report.pdf)")
    args = vars(parser.parse_args())
    main(args)