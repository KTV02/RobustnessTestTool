import tkinter as tk

class ResultsList(tk.Frame):
    def __init__(self, parent, width):
        super().__init__(parent, width=int(parent.winfo_screenwidth() * width))
        self.pack(side=tk.LEFT, fill=tk.BOTH)
        
        self.label = tk.Label(self, text="Previous Results")
        self.label.pack(padx=10, pady=10)
        
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
    def load_results(self, results):
        # Load results from the database
        # Replace this with actual database retrieval code
        pass       
