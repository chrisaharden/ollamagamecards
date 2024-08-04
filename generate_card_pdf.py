import random
from fpdf import FPDF
from fontTools.ttLib import TTFont
import os

#TODO: Move this to its own file
def find_font_path(font_name, font_dir="C:\\Windows\\Fonts"):
    """
    Searches for the path of the specified font in the given directory.

    Args:
        font_name (str): The name of the font to search for.
        font_dir (str): The directory to search in (default is Windows Fonts directory).

    Returns:
        str: The full path to the font if found, otherwise None.
    """
    for root, _, files in os.walk(font_dir):
        for file in files:
            if file.lower().endswith(('.ttf', '.otf')):  # Common font file extensions
                try:
                    font_path = os.path.join(root, file)
                    font = TTFont(font_path)
                    name_records = font.get('name').names
                    for record in name_records:
                        try:
                            # Decode the font name based on the platform ID and encoding ID
                            platform_id = record.platformID
                            encoding_id = record.platEncID
                            name_id = record.nameID
                            if platform_id == 3 and encoding_id == 1:  # Windows Unicode
                                font_full_name = record.string.decode('utf-16-be')
                            elif platform_id == 1 and encoding_id == 0:  # Macintosh Roman
                                font_full_name = record.string.decode('mac_roman')
                            else:
                                font_full_name = record.string.decode('utf-8')  # Fallback to UTF-8

                            if font_name.lower() in font_full_name.lower():
                                return font_path
                        except UnicodeDecodeError:
                            try:
                                font_full_name = record.string.decode('latin1')
                                if font_name.lower() in font_full_name.lower():
                                    return font_path
                            except Exception as e:
                                print(f"Error decoding font name from {file}: {e}")
                except Exception as e:
                    print(f"Error reading font file {file}: {e}")
    return None

def generate_card_pdf(words:str,title: str, font:str):

    # Sometimes the model separates the words in the comma-separated list with a space behind the comma.  Remove that space.
    # Then split the comma separated string into an array
    words.replace(", ", ",")
    all_words = words.split(",")

    # Function to generate a list of unique random words
    def extract_random_words(available_words, num=3):
        if len(available_words) < num:
            num = len(available_words)
        selected_words = random.sample(available_words, num)
        for word in selected_words:
            available_words.remove(word)
        return selected_words

    # Create instance of FPDF class
    pdf = FPDF('P', 'in', 'Letter')  # 'P' for portrait, 'in' for inches, 'Letter' for 8.5x11 in

    # Ensure the font is valid.  Default to Arial, if not.
    # Set regular font for list
    font_path:str = find_font_path(font)
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

    # Create a copy of all_words to work with
    available_words = all_words.copy()

    # Function to add a new page and populate it with sections
    def add_page_with_sections(pdf, x_positions, y_positions, available_words):
        pdf.add_page()
        for y in y_positions:
            for x in x_positions:
                if not available_words:
                    return
                
                # Draw rectangle for the section
                pdf.rect(x, y, section_width, section_height)
                
                # Set bold font for title
                #pdf.set_font("InkfreeBold", size=18)
                pdf.set_font(font, size=18)
                
                # Add title (centered within the section and underlined)
                #title = "Choices"
                title_width = pdf.get_string_width(title)
                pdf.set_xy(x + (section_width - title_width) / 2, y + 0.1)
                pdf.cell(title_width, 0.2, title, align='C', border='B')  # 'B' for bottom border (underline)
                
                # Generate unique random words
                random_words = extract_random_words(available_words)
                
                # Set regular font for list
                pdf.set_font(font, size=16)
                
                # Set initial cursor position for words
                cursor_x = x + section_width / 2
                cursor_y = y + 0.35
                
                # Add text
                for word in random_words:
                    pdf.set_xy(cursor_x - pdf.get_string_width(word) / 2, cursor_y)
                    pdf.cell(0, 0.18, word)
                    cursor_y += 0.18  # Move cursor down

    # Add pages and populate sections until all words are used
    section_count = 0
    while available_words:
        add_page_with_sections(pdf, x_positions, y_positions, available_words)
        section_count += 1

    # Save the PDF
    pdf.output(title+"-"+font+".pdf")
    print(f"PDF generated successfully! Total sections created: {section_count * len(x_positions) * len(y_positions)}")
