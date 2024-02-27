import glob
import os
import shutil
import tkinter as tk
import zipfile
from tkinter import filedialog
from tkinter import simpledialog

# from pathlib import Path


class ZipSearcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zip File Searcher")
        self.geometry("400x200")

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

        # Search term entry and search button
        self.search_button = tk.Button(
            self, text="Enter Search Term and Start Search", command=self.start_search
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

        self.output_results_label = tk.Label(self, text="", fg="white")
        self.output_results_label.pack()

    def select_source_dir(self):
        self.source_dir = filedialog.askdirectory()
        print("Selected source directory:", self.source_dir)
        self.source_dir_label.config(text=f"Source Directory: {self.source_dir}")

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        print("Selected output directory:", self.output_dir)
        self.output_dir_label.config(text=f"Output Directory: {self.output_dir}")

    def start_search(self):
        self.search_term = simpledialog.askstring("Input", "What are you looking for?")
        print("Searching for:", self.search_term)
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
                    ecr = zip_ref.open("CDA_eICR.xml")
                    ecr_data = ecr.read().decode("utf-8")

                    rr = zip_ref.open("CDA_RR.xml")
                    rr_data = rr.read().decode("utf-8")

                    if self.search_term in ecr_data or self.search_term in rr_data:
                        id_num = os.path.basename(filename)
                        shutil.copy(filename, os.path.join(self.output_dir, id_num))
                        print(filename + " was copied to new directory")
                        results_count += 1
                except KeyError:
                    print("No eICR/RR here")
                    pass
        self.output_results_label.config(text=f"Found {results_count} result(s)")


if __name__ == "__main__":
    app = ZipSearcher()
    app.mainloop()
