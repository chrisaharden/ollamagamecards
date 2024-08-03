import random
from fpdf import FPDF

def generate_game_pdf(words):

    # Copy the nouns
    all_nouns = words.copy()
    """
    # Hardcoded list of sample nouns (120+ nouns)
    all_nouns = [
        "apple", "banana", "cat", "dog", "elephant", "flower", "giraffe", "hat", "ice", "jacket",
        "kite", "lemon", "monkey", "notebook", "orange", "piano", "queen", "rose", "sun", "table",
        "umbrella", "violin", "whale", "xylophone", "yogurt", "zebra", "airplane", "ball", "car",
        "dolphin", "eagle", "frog", "guitar", "horse", "igloo", "jelly", "kangaroo", "lion",
        "mushroom", "nest", "octopus", "penguin", "quilt", "rabbit", "snake", "tiger", "unicorn",
        "vase", "wolf", "yak", "zucchini", "anchor", "book", "candle", "drum", "egg", "feather",
        "glasses", "hammer", "island", "juice", "key", "leaf", "moon", "needle", "owl", "pencil",
        "quail", "rainbow", "star", "tree", "umbrella", "volcano", "window", "yarn", "zipper",
        "acorn", "butterfly", "cactus", "daisy", "elephant", "fox", "grapes", "helicopter", "iguana",
        "jellyfish", "koala", "lighthouse", "mountain", "nest", "octopus", "peacock", "quokka",
        "raccoon", "seashell", "tortoise", "unicycle", "violin", "watermelon", "x-ray", "yeti",
        "zebra", "astronaut", "balloon", "crayons", "dinosaur", "envelope", "fireworks", "globe",
        "hamburger", "ice cream", "jigsaw", "kiwi", "ladybug", "magnet", "newspaper", "ostrich",
        "popcorn", "quarter", "robot", "scissors", "telescope", "umbrella", "volcano", "wagon",
        "xylophone", "yo-yo", "zeppelin", "ant", "beach", "cloud", "desert", "engine", "forest",
        "garden", "hill", "iceberg", "jungle", "kettle", "lantern", "mountain", "net", "ocean",
        "pond", "quarry", "river", "stream", "tower", "universe", "valley", "waterfall", "xenon",
        "yard", "zipline", "arch", "bridge", "cave", "door", "exit", "fountain", "gate", "house",
        "island", "junction", "kiosk", "lake", "meadow", "nook", "orchard", "path", "quicksand",
        "road", "shore", "trail", "underpass", "village", "wall", "xylophone", "yurt", "zenith",
        "avenue", "building", "castle", "dome", "elevator", "farm", "gallery", "hotel", "igloo",
        "jetty", "kingdom", "library", "market", "nursery", "office", "palace", "quay", "resort",
        "station", "temple", "underground", "villa", "warehouse", "yard", "zoo", "arena", "block",
        "church", "diner", "estate", "field", "garage", "hall", "inn", "jail", "kitchen", "lab",
        "museum", "nursery", "observatory", "park", "quarter", "restaurant", "stadium", "theater",
        "university", "vineyard", "windmill", "yacht", "zone"
    ]
    """

    # Function to generate a list of unique random nouns
    def generate_unique_random_nouns(available_nouns, num=3):
        if len(available_nouns) < num:
            num = len(available_nouns)
        selected_nouns = random.sample(available_nouns, num)
        for noun in selected_nouns:
            available_nouns.remove(noun)
        return selected_nouns

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

    # Create a copy of all_nouns to work with
    available_nouns = all_nouns.copy()

    # Function to add a new page and populate it with sections
    def add_page_with_sections(pdf, x_positions, y_positions, available_nouns):
        pdf.add_page()
        for y in y_positions:
            for x in x_positions:
                if not available_nouns:
                    return
                
                # Draw rectangle for the section
                pdf.rect(x, y, section_width, section_height)
                
                # Set bold font for title
                pdf.set_font("InkfreeBold", size=12)
                
                # Add title (centered within the section and underlined)
                title = "Nouns"
                title_width = pdf.get_string_width(title)
                pdf.set_xy(x + (section_width - title_width) / 2, y + 0.1)
                pdf.cell(title_width, 0.2, title, align='C', border='B')  # 'B' for bottom border (underline)
                
                # Generate unique random nouns
                random_nouns = generate_unique_random_nouns(available_nouns)
                
                # Set regular font for list
                pdf.set_font("Inkfree", size=16)
                
                # Set initial cursor position for nouns
                cursor_x = x + section_width / 2
                cursor_y = y + 0.35
                
                # Add text
                for noun in random_nouns:
                    pdf.set_xy(cursor_x - pdf.get_string_width(noun) / 2, cursor_y)
                    pdf.cell(0, 0.18, noun)
                    cursor_y += 0.18  # Move cursor down

    # Add pages and populate sections until all nouns are used
    section_count = 0
    while available_nouns:
        add_page_with_sections(pdf, x_positions, y_positions, available_nouns)
        section_count += 1

    # Save the PDF
    pdf.output("sections_with_unique_nouns_centered_and_titled_underlined.pdf")
    print(f"PDF generated successfully! Total sections created: {section_count * len(x_positions) * len(y_positions)}")
