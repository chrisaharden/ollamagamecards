import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import configparser
import os
import sys
import queue
import threading

class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Game Card Generator")
        self.master.geometry("800x600")  

        self.config = configparser.ConfigParser()
        self.current_file = None

        # Create menu
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

        # Create main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill="both", expand=True)

        # Create scrollable frame for config entries
        self.canvas = tk.Canvas(main_frame)
        self.scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

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

        # Create Run button
        self.run_button = tk.Button(main_frame, text="Generate PDF", command=self.run_callback,
                                    height=10, width=15, font=("Arial", 14, "bold"),
                                    bg="#007bff", fg="white")
        self.run_button.pack(pady=20)

        # Add hover effect
        self.run_button.bind("<Enter>", lambda e: self.run_button.config(bg="#4da3ff"))
        self.run_button.bind("<Leave>", lambda e: self.run_button.config(bg="#007bff"))

        # Create log text box
        self.log_text = scrolledtext.ScrolledText(self.master, height=5)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

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

        # Save to file
        with open(self.current_file, 'w') as configfile:
            self.config.write(configfile)

    def refresh_display(self):
        # Clear existing entries
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        # Create input fields for each parameter
        for section in self.config.sections():
            section_frame = tk.Frame(self.scrollable_frame)
            section_frame.pack(fill="x", padx=5, pady=(10, 5))
            
            tk.Label(section_frame, text=section, font=("Arial", 12, "bold")).pack(side="left")
            tk.Button(section_frame, text="+", command=lambda s=section: self.add_new_key(s)).pack(side="right")

            for key, value in self.config[section].items():
                frame = tk.Frame(self.scrollable_frame)
                frame.pack(fill="x", padx=5, pady=2)
                tk.Label(frame, text=key, width=20, anchor="w").pack(side="left")
                entry = tk.Entry(frame, width=90)
                entry.insert(0, value)
                entry.pack(side="left", expand=True, fill="x")
                self.entries[(section, key)] = entry

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()