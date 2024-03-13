import glob
import os
import shutil
import tkinter as tk
import zipfile
from tkinter import filedialog


class ZipSearcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zip File Searcher")
        self.geometry("500x500")

        # Variables
        self.source_dir = None
        self.output_dir = None
        self.search_term = None

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Source directory selection button
        self.source_button = tk.Button(
            self, text="Select Source Directory", command=self.select_source_dir
        )
        self.source_button.pack(pady=10)

        # Output directory selection button
        self.output_button = tk.Button(
            self, text="Select Output Directory", command=self.select_output_dir
        )
        self.output_button.pack(pady=10)

        # Search text
        self.search_entry_label = tk.Label(self, text="Search Term")
        self.search_entry_label.pack(pady=(10, 0))
        self.search_entry = tk.Entry(self)
        self.search_entry.pack(pady=(0, 10))

        # Files to search through
        self.file_type_label = tk.Label(self, text="Document names")
        self.file_type_label.pack(pady=(10, 0))
        self.entries = []
        self.init_entries()

        self.add_button = tk.Button(self, text="Add New Field", command=self.add_entry)
        self.add_button.pack(pady=10)

        # Button to start search
        self.search_button = tk.Button(
            self, text="Start Search", command=self.start_search
        )
        self.search_button.pack(pady=10)

        # Define labels for displaying selected directories
        self.source_dir_label = tk.Label(
            self, text="No source directory selected", fg="white"
        )
        self.source_dir_label.pack()

        self.output_dir_label = tk.Label(
            self, text="No output directory selected", fg="white"
        )
        self.output_dir_label.pack()

        self.search_term_label = tk.Label(self, text="")
        self.search_term_label.pack(pady=(0, 0))

        self.output_results_label = tk.Label(self, text="", fg="white")
        self.output_results_label.pack(pady=10)

    def init_entries(self):
        initial_values = ["CDA_eICR.xml", "CDA_RR.xml"]
        for value in initial_values:
            self.add_entry(predefined_value=value)

    def add_entry(self, predefined_value=""):
        # Frame to hold the entry and remove button
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=5)

        # Entry widget
        entry = tk.Entry(entry_frame, width=40)
        entry.insert(0, predefined_value)  # Prepopulate with a value if provided
        entry.pack(side=tk.LEFT, padx=5)
        self.entries.append(entry)  # Keep track of this entry

        # Button to remove the entry
        remove_button = tk.Button(
            entry_frame,
            text="Remove",
            command=lambda: self.remove_entry(entry_frame, entry),
        )
        remove_button.pack(side=tk.LEFT, padx=5)

    def remove_entry(self, frame, entry):
        # Remove the entry from the tracking list and destroy the frame
        self.entries.remove(entry)
        frame.destroy()

    def select_source_dir(self):
        self.source_dir = filedialog.askdirectory()
        print("Selected source directory:", self.source_dir)
        self.source_dir_label.config(text=f"Source Directory: {self.source_dir}")

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        print("Selected output directory:", self.output_dir)
        self.output_dir_label.config(text=f"Output Directory: {self.output_dir}")

    def start_search(self):
        self.search_term = self.search_entry.get()
        print("search term:")
        print(self.search_term)
        self.search_term_label.config(text=f"Searching for: {self.search_term}")
        if self.source_dir and self.output_dir and self.search_term:
            self.search_in_zips()
        else:
            print(
                "Please select both source and output directories "
                + "and enter a search term."
            )

    def search_in_zips(self):
        # Your search logic here, adapted to use self.source_dir, self.output_dir,
        # and self.search_term

        # Example adapted from your provided script
        results_count = 0
        for filename in glob.glob(os.path.join(self.source_dir, "*.zip")):
            with zipfile.ZipFile(filename) as zip_ref:
                try:
                    for doc_type in self.entries:
                        doc = zip_ref.open(doc_type.get())
                        doc_data = doc.read().decode("utf-8")
                        if self.search_term in doc_data:
                            id_num = os.path.basename(filename)
                            shutil.copy(filename, os.path.join(self.output_dir, id_num))
                            results_count += 1
                except KeyError:
                    print("No eICR/RR here")
                    pass
        print("done searching")
        print(f"Found {results_count} result(s)")
        self.output_results_label.config(text=f"Found {results_count} result(s)")


if __name__ == "__main__":
    app = ZipSearcher()
    app.mainloop()
