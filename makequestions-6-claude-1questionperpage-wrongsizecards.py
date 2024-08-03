import random
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import sys
import traceback

# Extended list of "How Do I..." questions
how_do_i_questions = [
    "How do I change a flat tire?",
    "How do I unclog a drain?",
    "How do I jump-start a car?",
    "How do I fix a leaky faucet?",
    "How do I clean gutters safely?",
    "How do I organize my study space?",
    "How do I remove a stain from carpet?",
    "How do I change an air filter?",
    "How do I repair a hole in drywall?",
    "How do I sharpen kitchen knives?",
    "How do I create a study schedule?",
    "How do I change windshield wipers?",
    "How do I fix a running toilet?",
    "How do I clean a microwave oven?",
    "How do I organize a school locker?",
    "How do I check tire pressure?",
    "How do I fix a squeaky door hinge?",
    "How do I remove scratches from wood?",
    "How do I clean a computer keyboard?",
    "How do I replace a light switch?",
    "How do I clean a washing machine?",
    "How do I organize digital files?",
    "How do I fix a slow computer?",
    "How do I clean air conditioning vents?",
    "How do I remove permanent marker?",
    "How do I clean a ceiling fan?",
    "How do I fix a loose doorknob?",
    "How do I remove candle wax from carpet?",
    "How do I clean a coffee maker?",
    "How do I organize a backpack?",
    "How do I fix a clogged printer?",
    "How do I remove water stains from wood?",
    "How do I clean a dishwasher?",
    "How do I organize a garage?",
    "How do I fix a sticky lock?",
    "How do I remove ink stains from clothing?",
    "How do I clean a refrigerator coil?",
    "How do I organize a desk drawer?",
    "How do I fix a wobbly chair?",
    "How do I remove pet hair from furniture?",
    "How do I clean a bathroom exhaust fan?",
    "How do I organize digital photos?",
    "How do I fix a drafty window?",
    "How do I remove rust from metal?",
    "How do I clean a stovetop?",
    "How do I organize a closet?",
    "How do I fix a dripping shower head?",
    "How do I remove gum from clothing?",
    "How do I clean oven racks?",
    "How do I organize school supplies?",
    "How do I fix a garbage disposal?",
    "How do I remove mold from bathroom tiles?",
    "How do I clean window tracks?",
    "How do I organize a pantry?",
    "How do I fix a broken zipper?",
    "How do I remove grease stains from clothing?",
    "How do I clean a dryer vent?",
    "How do I organize a medicine cabinet?",
    "How do I fix a slow drain?",
    "How do I remove crayon marks from walls?",
    "How do I change a furnace filter?",
    "How do I organize a linen closet?",
    "How do I fix a loose tile?",
    "How do I remove hard water stains?",
    "How do I clean a gas stovetop?",
    "How do I organize a junk drawer?",
    "How do I fix a leaky showerhead?",
    "How do I remove oil stains from concrete?",
    "How do I clean a front-loading washer?",
    "How do I organize a home office?",
    "How do I fix a stuck window?",
    "How do I remove paint from clothing?",
]

print(f"Total number of questions in the array: {len(how_do_i_questions)}")

def generate_unique_random_question(available_questions):
    try:
        if not available_questions:
            return None
        question = random.choice(available_questions)
        available_questions.remove(question)
        return question
    except Exception as e:
        print(f"Error in generate_unique_random_question: {str(e)}")
        traceback.print_exc()
        return None

try:
    # Create instance of FPDF class
    pdf = FPDF('P', 'in', 'Letter')  # 'P' for portrait, 'in' for inches, 'Letter' for 8.5x11 in

    # Add custom font
    pdf.add_font('Inkfree', '', 'fonts/Inkfree.ttf')
    pdf.add_font('InkfreeBold', '', 'fonts/Inkfree.ttf')

    # Dimensions
    section_width = 1.75  # Reduced width to fit 4 columns
    section_height = 1.75  # Reduced height to fit 5 rows
    margin = 0.25  # Reduced margin

    # Calculate positions
    x_positions = [margin + (section_width * i) for i in range(4)]
    y_positions = [margin + (section_height * j) for j in range(5)]

    # Create a copy of all questions to work with
    available_questions = how_do_i_questions.copy()

    # Generate six pages (twice as many as before)
    for page in range(6):
        pdf.add_page()

        # Populate sections with unique random questions
        for y in y_positions:
            for x in x_positions:
                try:
                    # Draw rectangle for the section
                    pdf.rect(x, y, section_width, section_height)
                    
                    # Set bold font for title
                    pdf.set_font("InkfreeBold", size=10)
                    
                    # Add title (centered within the section and underlined)
                    title = "How Do I..."
                    title_width = pdf.get_string_width(title)
                    pdf.set_xy(x + (section_width - title_width) / 2, y + 0.1)
                    pdf.cell(title_width, 0.15, title, align='C', border='B')
                    
                    # Generate unique random question
                    random_question = generate_unique_random_question(available_questions)
                    
                    if random_question:
                        # Set regular font for question
                        pdf.set_font("Inkfree", size=16)
                        
                        # Set initial cursor position for question
                        cursor_x = x + 0.1
                        cursor_y = y + 0.35
                        
                        # Add text
                        pdf.set_xy(cursor_x, cursor_y)
                        lines = pdf.multi_cell(section_width - 0.2, 0.15, random_question, align='L', dry_run=True, output="LINES")
                        for line in lines:
                            if cursor_y + 0.15 > y + section_height - 0.1:  # Check if we're about to overflow
                                break
                            pdf.set_xy(cursor_x, cursor_y)
                            pdf.cell(section_width - 0.2, 0.15, line)
                            cursor_y += 0.15
                except Exception as e:
                    print(f"Error in section generation at x={x}, y={y}: {str(e)}")
                    traceback.print_exc()

    # Save the PDF
    pdf.output("how_do_i_questions.pdf")
    print("PDF generated successfully!")

except Exception as e:
    print(f"An error occurred during PDF generation: {str(e)}")
    traceback.print_exc()

print("Script execution completed.")