import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import configparser
import os

class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Config Editor")
        self.master.geometry("600x600")

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

        # Create scrollable frame
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
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
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.ini")])
        if not filepath:
            return

        self.current_file = filepath
        self.config.read(filepath)
        self.refresh_display()

    def save_file(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        
        if not self.current_file:
            return

        # Update config with new values
        for (section, key), entry in self.entries.items():
            self.config[section][key] = entry.get()

        # Save to file
        with open(self.current_file, 'w') as configfile:
            self.config.write(configfile)

        messagebox.showinfo("Success", f"File saved: {self.current_file}")

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
                entry = tk.Entry(frame)
                entry.insert(0, value)
                entry.pack(side="left", expand=True, fill="x")
                self.entries[(section, key)] = entry

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()