from fpdf import FPDF
from PIL import Image
import os
import font_helper  # Assuming this module exists with the find_font_path function

def create_image_grid(image_path, output_path="cardbacks.pdf", title="", font="", rows=4, cols=3, square_size=2.5):
    # Create a new PDF with portrait orientation
    pdf = FPDF(orientation='P', unit='in', format='Letter')
    pdf.add_page()

    # Add the font if provided and found
    if font:
        font_path = font_helper.find_font_path(font)
        if font_path:
            print(f"'{font}' font found.  Adding to PDF")
            #Add the font to the PDF.  See this URL for more details and future expansion: https://pyfpdf.readthedocs.io/en/latest/reference/add_font/index.html
            pdf.add_font(font, '', font_path, uni=True)
        else:
            print(f"Warning: Font '{font}' not found. Using default font.")
            font = "Arial"

    # Define grid parameters
    margin_left = (8.5 - (cols * square_size)) / 2
    margin_top = (11 - (rows * square_size)) / 2

    # Open and resize the image
    image = Image.open(image_path)
    image.thumbnail((square_size * 300, square_size * 300))  # Convert inches to points

    # Split the file name and extension
    # Create the new file name with "resized" as a suffix
    file_name, file_extension = os.path.splitext(image_path)
    resized_image_path = f"{file_name}_resized{file_extension}"
    image.save(resized_image_path)


    # Create the grid and insert images
    for row in range(rows):
        for col in range(cols):
            x = margin_left + (col * square_size)
            y = margin_top + (row * square_size)
            
            # Add the image to the PDF
            pdf.image(resized_image_path, x=x, y=y, w=square_size, h=square_size)
            
            # Draw a border around the square (optional)
            pdf.rect(x, y, square_size, square_size)

            # Add title in white text in the bottom half of each cell
            if title:
                pdf.add_font(font, '', font_path, uni=True)
                pdf.set_font(font if font else 'Arial', 'B', 16)
                pdf.set_text_color(255, 255, 255)  # White color
                pdf.set_xy(x, y + square_size / 2)
                pdf.cell(square_size, square_size / 2, title, 0, 0, 'C')

    # Save the PDF
    pdf.output(output_path)

# Example usage:
# create_image_grid("dog.png", "dog_grid.pdf", font="Arial", title="My Dog")