# AI Game Card Generator

This project is an AI-powered tool for generating game cards with customizable content and layouts.

## Project Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-game-card-generator.git
   cd ai-game-card-generator
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Ensure you have the necessary folder structure:
   ```
   ai-game-card-generator/
   ├── output/
   ├── source/
   │   ├── card_designs/
   │   ├── fonts/
   │   ├── images/
   │   ├── pdf_layouts/
   │   └── test_content/
   ├── batch.cmd
   └── requirements.txt
   ```

## Running the Application

### Via GUI

1. Navigate to the project root directory.
2. Run the following command:
   ```
   python ./source/main.py
   ```
3. The GUI will open. Use the interface to:
   - Create a new configuration or open an existing one
   - Modify settings as needed
   - Click the "Generate PDF" button to create your cards

### Via Batch File

1. Open the `batch.cmd` file in a text editor.
2. Uncomment the lines for the configurations you want to run.
3. Save the file and run it by double-clicking `batch.cmd` or executing it from the command line:
   ```
   .\batch.cmd
   ```

This will generate PDFs based on the specified INI files in the `./source/card_designs/` directory.

### Running with Test Parameters

To run the application with test parameters, use the following command structure:

```
python ./source/main.py --config [path_to_ini_file] --testnumber [test_number]
```

Example:
```
python ./source/main.py --config ./source/card_designs/QuestionsandAnswers.ini --testnumber 1
```

Test numbers:
- 1: Uses a predefined list of questions (qa_list1)
- 2: Uses another predefined list of questions (qa_list2)

## Configuration Files

The `./source/card_designs/` directory contains INI files that define the content and layout of the cards. You can create new INI files or modify existing ones to customize your card generation.

Example INI file structure:
```ini
[General]
content length = 36
content type = QuestionsAndAnswers
content = Dragons and Unicorns
content title = Dragons & Unicorns
items per card = 1

[Fonts]
title font = Arial
title font size = 24
body font = Arial
body font size = 12

[Card Back]
title = Dragons & Unicorns
font = Arial
generate = FALSE
gen content = Dragon and Unicorn in classic beautiful water color style
image = ./source/images/DefaultCardBack.png

[PDF Layout]
layout file = ./source/pdf_layouts/pdf-layout-2.5x3.5cards-landscape.json
```

## Output

Generated PDFs will be saved in the `output/` directory.

## Troubleshooting

If you encounter any issues:
1. Ensure all dependencies are correctly installed
2. Check that file paths in your INI files are correct
3. Verify that the required directories exist and have the necessary permissions

For further assistance, please open an issue on the project's GitHub page.
