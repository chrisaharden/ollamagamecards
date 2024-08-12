import ollama
import generate_card_pdf
import generate_cardbacks_pdf
import generate_image_withSD
import sys
from ollama import chat
import configparser
import tkinter as tk
from ConfigEditor import ConfigEditor
import threading

class MainApp(ConfigEditor):
    def __init__(self, master):
        super().__init__(master)
        
    def run_callback(self):
        if not self.current_file:
            tk.messagebox.showerror("Error", "Please open or save a configuration file first.")
            return
             
        # Save current changes
        self.save_file()
        self.log("Saved config file and starting PDF generation.\n")

        # Run the card generation process in a separate thread
        threading.Thread(target=self.run_card_generation, daemon=True).start()

    def run_card_generation(self):
        try:
            self.log(f"Prepping prompts...\n")

            # use the Content Type to choose the right prompt
            content_type = self.config.get('General', 'Content Type', fallback='').lower()
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
            content_length = self.config.get('General', 'Content Length', fallback='10')
            content = self.config.get('General', 'Content', fallback='')
            userPrompt = f"List {content_length} unique {content}. no yapping."
            self.log(f"userPrompt: {userPrompt}\n")
            self.log(f"systemPrompt: {systemPrompt}\n")

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

            modelName:str = 'llama3.1'
            self.log(f"Sending chat to {modelName}...\n")
            response = chat('llama3.1', messages=messages)
            self.log('Model Response:\r\n'+response['message']['content'] + '\n')

            # get some params
            imagePath = self.config.get('Card Back', 'Image', fallback='')
            contentTitle = self.config.get('General', 'Content Title', fallback='Default Title')
            contentFont = self.config.get('Fonts', 'Title Font', fallback='Arial')
            cardBackTitle = self.config.get("Card Back", "Title", fallback='Back Title')
            cardBackFont = self.config.get("Card Back", "Font", fallback='Arial')
            cardBackGenerate = self.config.get("Card Back", "Generate", fallback='FALSE')
            cardBackImageGenContent = self.config.get("Card Back", "Gen Content", fallback='')

            # generate the card image, or use the one specified?
            if cardBackGenerate.upper() == 'TRUE':
                imagePath = generate_image_withSD.gen_image(cardBackImageGenContent, cardBackTitle)

            # generate the cards
            self.log(f"Generating Cards...\n")
            generate_card_pdf.generate_card_pdf(response['message']['content'], contentTitle, contentFont) 
            generate_cardbacks_pdf.create_image_grid(imagePath, contentTitle+"-Backs.pdf", cardBackTitle, cardBackFont)
            self.log(f"Card generation completed!")

            #self.master.after(0, lambda: tk.messagebox.showinfo("Success", "Card generation completed!"))

        except Exception as e:
            self.log(f"An error occurred: {str(e)}\n")
            self.master.after(0, lambda: tk.messagebox.showerror("Error", f"An error occurred: {str(e)}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    sys.stdout = app.StdoutRedirector(app.log_queue)
    sys.stderr = app.StdoutRedirector(app.log_queue)
    root.mainloop()