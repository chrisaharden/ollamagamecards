import ollama
import generate_card_pdf
import generate_cardbacks_pdf
import generate_image_withSD
import sys
from ollama import chat
import configparser
import tkinter as tk
from ConfigEditor import ConfigEditor

def run_card_generation(config):
    # use the Content Type to choose the right prompt
    content_type = config.get('General', 'Content Type', fallback='').lower()
    bQuestions = "question" in content_type

    if bQuestions:
        systemPrompt = "Output questions as list with question marks at the end of each question. " \
                       "Do not include any carriage returns. " \
                       "Do not include any line feeds. " \
                       "Example: How are you? What are you doing? What is that?"
    else:
        systemPrompt = "Output a comma separated list. " \
                       "Do not include any carriage returns. " \
                       "Do not include any line feeds. " \
                       "Example: boy, girl, dog"

    # Build a sentence that uses all the key value pairs in the Content description.
    content_length = config.get('General', 'Content Length', fallback='10')
    content = config.get('General', 'Content', fallback='')
    userPrompt = f"List {content_length} unique {content}. no yapping."
    print(f"userPrompt: {userPrompt}")

    print(f"systemPrompt: {systemPrompt}")

    messages = [
        {
            'role': 'system',
            'content': systemPrompt
        },
        {
            'role': 'user',
            'content': userPrompt,
        },
        {
            'role':'assistant',
            'content': 'Here is the list:',
        }
    ]

    response = chat('llama3.1', messages=messages)
    print(response['message']['content'])

    # get some params
    imagePath = config.get('Card Back', 'Image', fallback='')
    contentTitle = config.get('General', 'Content Title', fallback='Default Title')
    contentFont = config.get('Fonts', 'Title Font', fallback='Arial')
    cardBackTitle = config.get("Card Back", "Title", fallback='Back Title')
    cardBackFont = config.get("Card Back", "Font", fallback='Arial')
    cardBackGenerate = config.get("Card Back", "Generate", fallback='FALSE')
    cardBackImageGenContent = config.get("Card Back", "Gen Content", fallback='')

    # generate the card image, or use the one specified?
    if cardBackGenerate.upper() == 'TRUE':
        imagePath = generate_image_withSD.gen_image(cardBackImageGenContent, cardBackTitle)

    # generate the cards
    generate_card_pdf.generate_card_pdf(response['message']['content'], contentTitle, contentFont) 
    generate_cardbacks_pdf.create_image_grid(imagePath, contentTitle+"-Backs.pdf", cardBackTitle, cardBackFont)

class MainApp(ConfigEditor):
    def __init__(self, master):
        super().__init__(master)
        
    def run_callback(self):
        if not self.current_file:
            tk.messagebox.showerror("Error", "Please open or save a configuration file first.")
            return

        print(f"Starting PDF generation.")
             
        # Save current changes
        self.save_file()
        print(f"Saved config file and starting PDF generation.")

        # Run the card generation process
        run_card_generation(self.config)
        print("Card generation complete!")
        tk.messagebox.showinfo("Success", "Card generation completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()