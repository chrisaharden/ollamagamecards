import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import configparser
import os
import sys
import queue
import threading
from PIL import Image, ImageTk

# Color scheme (from Gemini)
BACKGROUND_COLOR = "#282c34"  # A deeper, more atmospheric base
DARKER_BACKGROUND = "#181a1f"  # For accents or deeper elements
TEXT_COLOR = "#ffffff"  # White remains a strong choice for text
BUTTON_BG = "#363a40"  # A darker button base for better contrast
BUTTON_FG = "#ffffff"  # White text for button clarity
BUTTON_HOVER_BG = "#4c5056"  # A slightly lighter hover state for buttons

class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Game Card Generator")
        self.master.geometry("800x600")  

        self.config = configparser.ConfigParser()
        self.current_file = None
        
        # Set window background color
        self.master.configure(bg=BACKGROUND_COLOR)

        # Create menu
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

        # Create main frame with matching background
        main_frame = tk.Frame(self.master, bg=BACKGROUND_COLOR)
        main_frame.pack(fill="both", expand=True)

        # Create scrollable frame for config entries
        self.canvas = tk.Canvas(main_frame, bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BACKGROUND_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.entries = {}
        self.dropdowns = {}  # New dictionary to store dropdown widgets

        # Create a frame for the button at the bottom
        button_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(side="bottom", fill="x", pady=10)

        # Load and resize the Run button image
        image = Image.open("GeneratePDFButtonArt-midjourney.png")
        image = image.resize((150, 150))  # Adjust the size as needed
        photo = ImageTk.PhotoImage(image)

        # Create Run button (note height and width are in pixels, when you add an image.)
        tk.Label(button_frame, text="Generate PDF", font=("Arial", 12, "bold"), 
        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="top")
        self.run_button = tk.Button(button_frame, command=self.run_callback,
                                    height=150, width=150, font=("Arial", 14, "bold"),
                                    bg=BUTTON_BG, fg=BUTTON_FG,
                                    image=photo, compound=tk.LEFT)
        self.run_button.image = photo  # Keep a reference to avoid garbage collection
        self.run_button.pack(pady=5, padx=(5, 20))

        # Add hover effect
        self.run_button.bind("<Enter>", lambda e: self.run_button.config(bg=BUTTON_HOVER_BG))
        self.run_button.bind("<Leave>", lambda e: self.run_button.config(bg=BUTTON_BG))

        # Create log text box with dark theme
        self.log_text = scrolledtext.ScrolledText(self.master, height=5, bg=DARKER_BACKGROUND, fg=TEXT_COLOR)
        self.log_text.pack(fill="both", expand=True, padx=0, pady=0)

        self.log_queue = queue.Queue()
        self.master.after(100, self.check_log_queue)

    def run_callback(self):
        # This method will be overridden in the main script
        self.log("Run button clicked")

    class StdoutRedirector:
        def __init__(self, log_queue):
            self.log_queue = log_queue

        def write(self, message):
            self.log_queue.put(message.strip())

        def flush(self):
            pass

    def log(self, message):
        self.log_queue.put(message)

    def check_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.see(tk.END)
        self.master.after(100, self.check_log_queue)
    
    def new_file(self):
        self.current_file = None
        self.config = configparser.ConfigParser()
        
        # Clear existing entries
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        self.dropdowns.clear()

        # Ask for a new section name
        section_name = simpledialog.askstring("New Section", "Enter a name for the new section:")
        if section_name:
            self.config.add_section(section_name)
            self.add_new_key(section_name)

    def add_new_key(self, section):
        key = simpledialog.askstring("New Key", f"Enter a new key for section '{section}':")
        if key:
            value = simpledialog.askstring("New Value", f"Enter the value for '{key}':")
            if value is not None:  # Allow empty string as a valid value
                self.config[section][key] = value
                self.refresh_display()

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("INI files", "*.ini")])
        if not filepath:
            return

        self.current_file = filepath
        self.config.read(filepath)
        self.refresh_display()

    def save_file(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(defaultextension=".ini", filetypes=[("INI files", "*.ini")])
        
        if not self.current_file:
            return

        # Update config with new values
        for (section, key), entry in self.entries.items():
            self.config[section][key] = entry.get()
        
        # Update config with dropdown values
        for (section, key), dropdown in self.dropdowns.items():
            self.config[section][key] = dropdown.get()

        # Save to file
        with open(self.current_file, 'w') as configfile:
            self.config.write(configfile)

    def refresh_display(self):
        # Clear existing entries
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

    def create_add_button(self, parent, section):
        button = tk.Button(parent, text="+", command=lambda s=section: self.add_new_key(s),
                           bg=BUTTON_BG, fg=BUTTON_FG)
        button.pack(side="right")

        # Add hover effect
        button.bind("<Enter>", lambda e: button.config(bg=BUTTON_HOVER_BG))
        button.bind("<Leave>", lambda e: button.config(bg=BUTTON_BG))

        return button
    
    def refresh_display(self):
        # Clear existing entries
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        self.dropdowns.clear()

        # Create input fields for each parameter
        for section in self.config.sections():
            section_frame = tk.Frame(self.scrollable_frame, bg=BACKGROUND_COLOR)
            section_frame.pack(fill="x", padx=5, pady=(10, 5))
            
            tk.Label(section_frame, text=section, font=("Arial", 12, "bold"), 
                    bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
            self.create_add_button(section_frame, section)

            for key, value in self.config[section].items():
                key = key.title()
                frame = tk.Frame(self.scrollable_frame, bg=BACKGROUND_COLOR)
                frame.pack(fill="x", padx=5, pady=2)
                tk.Label(frame, text=key, width=20, anchor="w", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
                
                if section == 'General' and key == 'Content Type':
                    # Create a dropdown for Content Type
                    dropdown = ttk.Combobox(frame, values=["Words", "Questions", "QuestionsAndAnswers"],
                                            width=88, state="readonly")
                    dropdown.set(value)  # Set the current value
                    dropdown.pack(side="left", expand=True, fill="x")
                    self.dropdowns[(section, key)] = dropdown
                else:
                    # Create a regular entry for other fields
                    entry = tk.Entry(frame, width=90, bg=DARKER_BACKGROUND, fg=TEXT_COLOR, 
                                    insertbackground=TEXT_COLOR)
                    entry.insert(0, value)
                    entry.pack(side="left", expand=True, fill="x")
                    self.entries[(section, key)] = entry

#if __name__ == "__main__":
    #root = tk.Tk()
    #ico = Image.open('./gameicon-midjourney.png')
    #photo = ImageTk.PhotoImage(ico)
    #root.wm_iconphoto(False, photo)
    #app = ConfigEditor(root)
    #root.mainloop()