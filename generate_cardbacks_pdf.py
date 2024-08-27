from fpdf import FPDF
from PIL import Image
import os
import json
import font_helper  # Assuming this module exists with the find_font_path function

def create_image_grid(image_path, output_path="cardbacks.pdf", title="", font="", layout_file="./pdf_layouts/pdf-layout-2.5x2.5cards.json"):
    # Load layout information from JSON file
    with open(layout_file, 'r') as f:
        layout = json.load(f)

    # Extract layout information
    page_info = layout['page_info']
    orientation = page_info.get('orientation', 'portrait')
    horizontal_sections = page_info['horizontal_sections']
    vertical_sections = page_info['vertical_sections']
    section_width = page_info['section_width']
    section_height = page_info['section_height']
    page_margin = page_info['page_margin']

    # Create a new PDF with the specified orientation
    pdf = FPDF(orientation=orientation[0].upper(), unit='in', format='Letter')
    pdf.add_page()

    # Add the font if provided and found
    if font:
        font_path = font_helper.find_font_path(font)
        if font_path:
            print(f"'{font}' font found. Adding to PDF")
            pdf.add_font(font, '', font_path, uni=True)
        else:
            print(f"Warning: Font '{font}' not found. Using default font.")
            font = "Arial"

    # Open and resize the image
    image = Image.open(image_path)
    image.thumbnail((section_width * 300, section_height * 300))  # Convert inches to points

    # Create a new file name with "resized" as a suffix
    file_name, file_extension = os.path.splitext(image_path)
    resized_image_path = f"{file_name}_resized{file_extension}"
    image.save(resized_image_path)

    # Calculate positions
    x_positions = [page_margin + (section_width * i) for i in range(horizontal_sections)]
    y_positions = [page_margin + (section_height * j) for j in range(vertical_sections)]

    # Create the grid and insert images
    for y in y_positions:
        for x in x_positions:
            # Add the image to the PDF
            pdf.image(resized_image_path, x=x, y=y, w=section_width, h=section_height)
            
            # Draw a border around the square (optional)
            pdf.rect(x, y, section_width, section_height)

            # Add title with black bar behind it
            if title:
                pdf.set_font(font if font else 'Arial', 'B', 16)
                
                # Calculate text height and position
                text_height = pdf.font_size
                bar_height = text_height * 1.2  # Slightly taller than the text
                text_y = y + section_height - (section_height / 4) - (bar_height / 2)
                
                # Draw black bar behind the text
                pdf.set_fill_color(0, 0, 0)  # Black color
                pdf.rect(x, text_y, section_width, bar_height, 'F')
                
                # Add white text on the black bar
                pdf.set_text_color(255, 255, 255)  # White color
                pdf.set_xy(x, text_y + (bar_height - text_height) / 2)  # Center text vertically in the bar
                pdf.cell(section_width, text_height, title, 0, 0, 'C')

    # Create the output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Update the output path to use the output directory
    output_path = os.path.join(output_dir, output_path)

    # Save the PDF
    pdf.output(output_path)
    print(f"{output_path} generated successfully!")

# Example usage:
# create_image_grid("dog.png", "dog_grid.pdf", font="Arial", title="My Dog", layout_file="./pdf_layouts/pdf-layout-2.5x2.5cards.json")
