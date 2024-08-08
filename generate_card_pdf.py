import random
from fpdf import FPDF
import font_helper
import os


def generate_card_pdf(words:str, title: str, font:str):

    # are we using questions? If so, we'll do special formatting and handling later
    bQuestions = '?' in words

    # remove a line feed that is at the beginning of the list     
    words = words.replace(" \n", "")
    words = words.replace("\n", "")

    if bQuestions:
        # Sometimes the model separates the words in the questio nmark-separated list with a space behind the questionmark.  Remove that space.
        # Then split the question mark-separated string into an array
        words = words.replace("?, ", "?\r\n")
        words = words.replace("? ", "?\r\n")
        all_items = words.split("\r\n")
    else:
        # Sometimes the model separates the words in the comma-separated list with a space behind the comma.  Remove that space.
        # Then split the comma separated string into an array
        words = words.replace(", ", ",")
        all_items = words.split(",")

    print(f"Number of items: {len(all_items)}")

    # Function to generate a list of unique random items (words or questions)
    def extract_random_items(available_items, num):
        if len(available_items) < num:
            num = len(available_items)
        selected_items = random.sample(available_items, num)
        for item in selected_items:
            available_items.remove(item)
        return selected_items

    # Create instance of FPDF class
    pdf = FPDF('P', 'in', 'Letter')  # 'P' for portrait, 'in' for inches, 'Letter' for 8.5x11 in

    # Ensure the font is valid.  Default to Arial, if not.
    # Set regular font for list
    font_path:str = font_helper.find_font_path(font)
    if font_path:
        print(f"'{font}' font found.  Adding to PDF")

        #Add the font to the PDF.  See this URL for more details and future expansion: https://pyfpdf.readthedocs.io/en/latest/reference/add_font/index.html
        pdf.add_font(font, '', font_path, uni=True)
    else: 
        print(f"'{font}' font not found.  Substituted Arial")
        font = "Arial"  


    # Add custom font
    # TODO: add the ability to add_font from fonts directory
    # pdf.add_font('Inkfree', '', 'fonts/Inkfree.ttf')
    # pdf.add_font('InkfreeBold', '', 'fonts/Inkfree.ttf')  # Same as before, no style parameter

    # Dimensions
    section_width = 2.5
    section_height = 2.5
    margin = 0.5

    # Calculate positions
    x_positions = [margin + (section_width * i) for i in range(3)]
    y_positions = [margin + (section_height * j) for j in range(4)]

    # Create a copy of all_items to work with
    available_items = all_items.copy()

    # Function to add a new page and populate it with sections
    def add_page_with_sections(pdf, x_positions, y_positions, available_items):
        pdf.add_page()
        for y in y_positions:
            for x in x_positions:
                if not available_items:
                    return
                
                # Draw rectangle for the section
                pdf.rect(x, y, section_width, section_height)
                
                # Set bold font for title
                pdf.set_font(font, size=18)
                
                # Add title (centered within the section and underlined)
                title_width = pdf.get_string_width(title)
                pdf.set_xy(x + (section_width - title_width) / 2, y + 0.1)
                pdf.cell(title_width, 0.2, title, align='C', border='B')  # 'B' for bottom border (underline)
                
                # Generate unique random items
                random_items = extract_random_items(available_items,num=1 if bQuestions else 3) #3 words per card or 1 question
                
                # Set regular font for list
                pdf.set_font(font, size=12 if bQuestions else 16)
                
                # Set initial cursor position for items
                cursor_x = x + 0.1
                cursor_y = y + 0.45
                
                # Add text
                for item in random_items:
                    if bQuestions:
                        # For questions, use multi_cell to allow text wrapping
                        pdf.set_xy(cursor_x, cursor_y)
                        pdf.multi_cell(section_width - 0.2, 0.18, item, align='C')
                        cursor_y = pdf.get_y() + 0.1  # Add some space between questions
                    else:
                        # For single words, center them
                        pdf.set_xy(cursor_x + (section_width - 0.2) / 2 - pdf.get_string_width(item) / 2, cursor_y)
                        pdf.cell(0, 0.18, item)
                        cursor_y += 0.18  # Move cursor down

    # Add pages and populate sections until all items are used
    section_count = 0
    while available_items:
        add_page_with_sections(pdf, x_positions, y_positions, available_items)
        section_count += 1

    # Save the PDF
    pdf.output(title+".pdf")
    print(f"PDF generated successfully! Total sections created: {section_count * len(x_positions) * len(y_positions)}")