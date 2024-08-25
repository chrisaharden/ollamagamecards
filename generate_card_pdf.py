import random
from fpdf import FPDF
import font_helper
import os
import json

def generate_card_pdf(content_type:str, contentList:list, title: str, font:str, items_per_card:int=1, pdftemplate:str=''):
    # Read dimensions from the template file
    with open(pdftemplate, 'r') as f:
        template = json.load(f)

    # Page Info
    horizontal_sections = template['page_info']['horizontal_sections']
    vertical_sections = template['page_info']['vertical_sections']
    section_width = template['page_info']['section_width']
    section_height = template['page_info']['section_height']
    page_margin = template['page_info']['page_margin']
    page_bottom_margin = template['page_info']['page_bottom_margin']

    # Title Info
    title_font_size = template['title_info']['font_size']
    title_height = template['title_info']['height']

    # Body Info
    #body_height = template['body_info']['height']
    body_font_size = template['body_info']['font_size']
    line_height = template['body_info']['line_height']
    answer_font_size = template['body_info']['answer_font_size']
    answer_line_height = template['body_info']['answer_line_height']
    cell_margin = template['body_info']['cell_margin']
    body_height = section_height - title_height - cell_margin #calculate the body height

    #we are using all_items as the name.  TODO: later change to just using contentList
    all_items = contentList
    print(f"Number of items: {len(all_items)}")

    # Function to extract a list of unique items (words or questions)
    def extract_items(available_items, num):
        if len(available_items) < num:
            num = len(available_items)
        selected_items = available_items[:num]
        del available_items[:num]
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

    # Calculate positions
    x_positions = [page_margin + (section_width * i) for i in range(horizontal_sections)]
    y_positions = [page_margin + (section_height * j) for j in range(vertical_sections)]

    # Create a copy of all_items to work with
    available_items = all_items.copy()

    # Function to add a new page and populate it with sections
    def add_page_with_sections(pdf, x_positions, y_positions, available_items):
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=page_bottom_margin)

        #debug
        #card_number:int=0
        for y in y_positions:
            for x in x_positions:
                if not available_items:
                    return
                
                # Track the card number for debugging purposes
                #card_number+=1 

                # Draw rectangle for the section
                pdf.rect(x, y, section_width, section_height)
                
                # Set bold font for title
                pdf.set_font(font, size=title_font_size)
                
                # Add title (centered within the section and underlined)
                title_width = pdf.get_string_width(title)
                pdf.set_xy(x + (section_width - title_width) / 2, y + 0.1)
                pdf.cell(title_width, title_height, title, align='C', border='B')  # 'B' for bottom border (underline)
                
                # Extract one or more items for the next card / section
                extracted_items = extract_items(available_items, items_per_card) 
                
                # Set regular font for list
                pdf.set_font(font, size=body_font_size)
                
                # Set initial cursor position for items
                cursor_x = x + 0.1
                cursor_y = y + 0.45

                # Add text to body
                for index, item in enumerate(extracted_items):
                    
                    #debug
                    #item = f"{card_number}: "+item

                    if content_type == 'questions':
                        # For questions, use multi_cell to allow text wrapping
                        pdf.set_xy(cursor_x, cursor_y)
                        pdf.multi_cell(section_width - cell_margin, line_height, item, align='C')
                        
                    elif content_type == 'questionsandanswers':
                        # extract_items() grabs two lines at once for questions and answers 
                        if index % 2 == 0: #even entries are questions
                            if "?" not in item:
                                print(f"WARNING: index:{index},x:{x},y:{y}: Question is missing a question mark, or array is off by one.  Cards may have questions and answers swapped.")

                            pdf.set_xy(cursor_x, cursor_y)
                            pdf.set_font(font, size=11)
                            pdf.multi_cell(section_width - cell_margin, line_height, item, align='C')
                        else: #odd entries are answers.  move them down.
                            #print(f"{x},{y}: {item}")
                            
                            # Calculate the number of lines, then calculate the total height of the multi-cell, 
                            # so you can move the answer box location up that amount.
                            text_width = pdf.get_string_width(item)
                            number_of_lines = int(text_width / (section_width-cell_margin)) + 1
                            answer_height = number_of_lines * answer_line_height
                            #print(f"height in: {answer_height}, number of lines: {number_of_lines}")
                            answer_cursor_y=cursor_y+body_height-answer_height-cell_margin
                            pdf.set_xy(cursor_x,answer_cursor_y)
                            pdf.set_font(font, size=answer_font_size)

                            # Print the answer 
                            ybefore = pdf.get_y()
                            pdf.multi_cell(section_width-cell_margin, answer_line_height, item, align='C',border=0)
                            yafter = pdf.get_y()
                            #print(f"height out: {yafter - ybefore}, number of lines: {number_of_lines}")

                    else: #assuming "words"
                        # For single words, center them
                        pdf.set_xy(cursor_x + (section_width - cell_margin) / 2 - pdf.get_string_width(item) / 2, cursor_y)
                        pdf.cell(0, line_height, item)
                        cursor_y += line_height  # Move cursor down

    # Add pages and populate sections until all items are used
    section_count = 0
    while available_items:
        add_page_with_sections(pdf, x_positions, y_positions, available_items)
        section_count += 1

    # Create the output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Save the PDF in the output directory
    output_path = os.path.join(output_dir, f"{title}.pdf")
    pdf.output(output_path)
    print(f"{output_path} generated successfully! Total sections created: {section_count * len(x_positions) * len(y_positions)}")