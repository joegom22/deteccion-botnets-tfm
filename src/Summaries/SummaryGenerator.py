import os
import pandas as pd
from fpdf import FPDF
import logging

class SummaryGenerator:
    def __init__(self, output_path: str, title: str) -> None:
        """
        Initialize the SummaryGenerator object.

        This constructor sets up the initial state of the SummaryGenerator,
        including the output path for the PDF report and a configured logger.

        Args:
            - output_path (str): The path to the PDF file where the report will be saved.
            - title (str): The title for the PDF report.
        """
        self.output_path = output_path
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=16, style="B")
        self.pdf.cell(200, 10, txt=title, ln=True, align='C')
        self.pdf.ln(2)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def add_text(self, text, font="Arial", size=12, color="black") -> None:
        """
        Add a text to the PDF report.

        This method adds the specified text to the PDF report, using the
        provided font, size, and color.

        Args:
            - text (str): The text to be added to the report.
            - font (str, optional): The font family for the text. Defaults to "Arial".
            - size (int, optional): The font size for the text. Defaults to 12.
            - color (str, optional): The color of the text. Defaults to "black".
        """
        self.pdf.set_font(font, size=size, style='')
        self.pdf.multi_cell(0, 10, text)
        self.pdf.ln(2)
    
    def add_section_header(self, title: str) -> None:
        """
        Add a section header to the PDF report.

        This method adds a header with the specified title to the PDF report,
        formatted in bold.

        Args:
            - title (str): The title for the section header.
        """
        self.pdf.set_font("Arial", size=18, style="B")
        self.pdf.cell(0, 10, title, ln=True, align="L")
        self.pdf.ln(2)

    def add_image(self, image_path: str, caption: str = None) -> None:
        """
        Add an image to the PDF report, centered with a caption.

        Args:
            - image_path (str): Path to the image file.
            - caption (str, optional): Caption to display below the image.
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            return
        
        page_width = self.pdf.w - 20
        max_height = 100
        
        self.pdf.image(image_path, x=10, w=page_width, h=max_height)
        self.pdf.ln(5)
        
        if caption:
            self.pdf.set_font("Arial", size=10, style="I")
            self.pdf.multi_cell(0, 8, caption, align="C")
            self.pdf.ln(5)

    def save_pdf(self) -> None:
        """
        Save the PDF report to the specified output path.

        This method saves the PDF report to the specified output path.
        If the output path already exists, it will overwrite the existing file.
        """
        try:
            self.pdf.output(self.output_path)
            self.logger.info(f"PDF report saved successfully to {self.output_path}")
        except Exception as e:
            self.logger.error(f"Error saving PDF report: {str(e)}")