import random
from fpdf import FPDF

def generate_card_pdf(words:str):

    # Sometimes the model separates the words in the comma-separated list with a space behind the comma.  Remove that space.
    # Then split the comma separated string into an array
    words.replace(", ", ",")
    all_words = words.split(",")

    # Function to generate a list of unique random words
    def extract_random_words(available_words, num=3):
        if len(available_words) < num:
            num = len(available_words)
        selected_words = random.sample(available_words, num)
        for noun in selected_words:
            available_words.remove(noun)
        return selected_words

    # Create instance of FPDF class
    pdf = FPDF('P', 'in', 'Letter')  # 'P' for portrait, 'in' for inches, 'Letter' for 8.5x11 in

    # Add custom font
    pdf.add_font('Inkfree', '', 'fonts/Inkfree.ttf')
    pdf.add_font('InkfreeBold', '', 'fonts/Inkfree.ttf')  # Same as before, no style parameter

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
                pdf.set_font("InkfreeBold", size=18)
                
                # Add title (centered within the section and underlined)
                title = "Choices"
                title_width = pdf.get_string_width(title)
                pdf.set_xy(x + (section_width - title_width) / 2, y + 0.1)
                pdf.cell(title_width, 0.2, title, align='C', border='B')  # 'B' for bottom border (underline)
                
                # Generate unique random words
                random_words = extract_random_words(available_words)
                
                # Set regular font for list
                pdf.set_font("Inkfree", size=16)
                
                # Set initial cursor position for words
                cursor_x = x + section_width / 2
                cursor_y = y + 0.35
                
                # Add text
                for noun in random_words:
                    pdf.set_xy(cursor_x - pdf.get_string_width(noun) / 2, cursor_y)
                    pdf.cell(0, 0.18, noun)
                    cursor_y += 0.18  # Move cursor down

    # Add pages and populate sections until all words are used
    section_count = 0
    while available_words:
        add_page_with_sections(pdf, x_positions, y_positions, available_words)
        section_count += 1

    # Save the PDF
    pdf.output("game.pdf")
    print(f"PDF generated successfully! Total sections created: {section_count * len(x_positions) * len(y_positions)}")
