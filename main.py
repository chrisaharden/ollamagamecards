import ollama
import generate_card_pdf
import generate_cardbacks_pdf
import generate_image_withSD
import sys
import os
import argparse
from ollama import chat
import configparser
import tkinter as tk
from ConfigEditor import ConfigEditor
import threading
from PIL import Image, ImageTk
from qa_list import qa_list1, qa_list2

# Define constants
TEST_SEND_LIST1_TO_PDF = 1
TEST_SEND_LIST2_TO_PDF = 2

class CardGenerator:
    def __init__(self, config, testnumber=None):
        self.config = config
        self.testnumber = testnumber

    def run_card_generation(self, log_func=print):
        try:
            log_func("Prepping prompts...\n")

            content_type = self.config.get('General', 'Content Type', fallback='').lower()

            content_type_prompts = {
                'words': {
                    'system_prompt': "Output words in an unnumbered list. no yapping. Example:\n"
                                     "cat\ndog\ngoat",
                    'output_format': "words in an unnumbered list"
                },
                'questions': {
                    'system_prompt': "Output questions as an unnumbered list with question marks at the end of each question. no yapping. Example:\n"
                                     "Is this a question 1?\nIs this a question 2?\nIs this a question 3?\n",
                    'output_format': "unnumbered list of questions"
                },
                'questionsandanswers': {
                    'system_prompt': "Output questions and answers in an unnumbered list. no yapping. Example:\n"
                                     "Is this a question 1?\nThis is the answer 1.\n"
                                     "Is this a question 2?\nThis is the answer to 2.\n"
                                     "Is this a question 3?\nThis is the answer to 3.",
                    'output_format': "alternating list of questions and answers in an unnumbered list."
                }
            }

            selected_prompt = content_type_prompts.get(content_type, content_type_prompts['words'])
            system_prompt = selected_prompt['system_prompt']
            output_format = selected_prompt['output_format']

            content_length = self.config.get('General', 'Content Length', fallback='10')
            content = self.config.get('General', 'Content', fallback='')
            user_prompt = f"List {content_length} unique {content} in the format of a {output_format}. No yapping."

            log_func(f"userPrompt: {user_prompt}\n")
            log_func(f"systemPrompt: {system_prompt}\n")

            messages = [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_prompt,
                },
                {
                    'role':'assistant',
                    'content': 'Here is the list:',
                }
            ]

            # Basic testing framework - in this case to test our strings still visually look correct as things change.
            if self.testnumber == TEST_SEND_LIST1_TO_PDF:
                contentList = qa_list1
            elif self.testnumber == TEST_SEND_LIST2_TO_PDF:
                contentList = qa_list2
            else: #Normal code path
                modelName:str = 'llama3.1'
                log_func(f"Sending chat to {modelName}...\n")
                response = chat('llama3.1', messages=messages)
                log_func('Model Response:\r\n'+response['message']['content'] + '\n')

                #clean/standardize the model output string and then convert to a list
                response_content = response['message']['content']
                response_content = response_content.replace(" \n\n", "\n") 
                response_content = response_content.replace(" \n", "\n")
                response_content = response_content.replace("\n\n", "\n") 
                response_content = response_content.lstrip(' ')  # Remove leading space if present
                response_content = response_content.lstrip('\n')  # Remove leading newline if present
                contentList = response_content.split("\n")

            contentTitle = self.config.get('General', 'Content Title', fallback='Default Title')
            itemsPerCard = int(self.config.get('General', "Items Per Card", fallback='1'))
            contentFont = self.config.get('Fonts', 'Title Font', fallback='Arial')
            cardBackTitle = self.config.get("Card Back", "Title", fallback='Back Title')
            cardBackFont = self.config.get("Card Back", "Font", fallback='Arial')
            cardBackGenerate = self.config.get("Card Back", "Generate", fallback='FALSE')
            cardBackImageGenContent = self.config.get("Card Back", "Gen Content", fallback='')
            imagePath = self.config.get('Card Back', 'Image', fallback='')

            if (content_type == 'questionsandanswers'): 
                itemsPerCard *= 2

            # Get the layout file path from the config
            layout_file = self.config.get('PDF Layout', 'Layout File', fallback='./pdf_layouts/pdf-layout-2.5x2.5cards.json')

            # Create the output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)

            if cardBackGenerate.upper() == 'TRUE':
                imagePath = generate_image_withSD.gen_image(cardBackImageGenContent, cardBackTitle)

            log_func(f"Generating Cards...\n")
            generate_card_pdf.generate_card_pdf(content_type, contentList, contentTitle, contentFont, itemsPerCard, layout_file) 
            generate_cardbacks_pdf.create_image_grid(imagePath, contentTitle+"-Backs.pdf", cardBackTitle, cardBackFont, layout_file)
            log_func(f"Card generation completed!")

        except Exception as e:
            log_func(f"An error occurred: {str(e)}\n")
            raise

class MainApp(ConfigEditor):
    def __init__(self, master):
        super().__init__(master)
        
    def run_callback(self):
        if not self.current_file:
            tk.messagebox.showerror("Error", "Please open or save a configuration file first.")
            return
             
        self.save_file()
        self.log("Saved config file and starting PDF generation.\n")

        threading.Thread(target=self.run_card_generation, daemon=True).start()

    def run_card_generation(self):
        try:
            generator = CardGenerator(self.config)
            generator.run_card_generation(self.log)
        except Exception as e:
            self.log(f"An error occurred: {str(e)}\n")
            self.master.after(0, lambda: tk.messagebox.showerror("Error", f"An error occurred: {str(e)}"))

def run_cli(config_path,testnumber):
    config = configparser.ConfigParser()
    config.read(config_path)
    generator = CardGenerator(config,testnumber)
    generator.run_card_generation()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Card Generator")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--testnumber", type=int, help="Test number for specific behavior")
    args = parser.parse_args()

    if args.config:
        run_cli(args.config, args.testnumber)
    else:
        root = tk.Tk()
        ico = Image.open('./gameicon-midjourney.png')
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(False, photo)
        app = MainApp(root)
        sys.stdout = app.StdoutRedirector(app.log_queue)
        sys.stderr = app.StdoutRedirector(app.log_queue)
        root.mainloop()
