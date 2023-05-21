import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sqlite3
from result_overview import ResultOverview
from database_helper import DatabaseHelper
from tkinter import font as tkfont


class RobustnessTestUI:
    def __init__(self, database_helper,transformations_helper, files_helper):

        self.window = tk.Tk()
        self.window.title("Robustness Test Tool")
        self.run_tests_button = None  # Variable zum Verfolgen des "Run Tests" Buttons

        self.results_listbox = tk.Listbox(self.window)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind("<<ListboxSelect>>", self.show_result_overview)

        self.add_button = tk.Button(self.window, text="Add", command=self.add_container)
        self.add_button.pack(anchor=tk.NE, padx=10, pady=10)

        self.result_overview = tk.Text(self.window, state=tk.DISABLED)
        self.result_overview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.database_helper = database_helper
        self.transformations_helper = transformations_helper
        self.files_helper = files_helper
        self.load_docker_containers()

        # Set minimum size for the window
        self.window.update()
        self.window.minsize(self.window.winfo_width(), self.window.winfo_height())

        self.window.mainloop()




    def load_docker_containers(self):
        results = self.database_helper.load_docker_containers()
        self.results_listbox.delete(0, tk.END)
        for result in results:
            name = result[0]
            path = result[1]
            item_text = f"{name}#{path}"  # Kombinieren von Name und Pfad
            self.results_listbox.insert(tk.END, item_text)


    def add_container(self):
        #get path to docker container
        file_path = filedialog.askopenfilename(filetypes=[("Tar Archive", "*.tar")])

        # Prompt for container name
        name = simpledialog.askstring("Container Name", "Enter the name for the Docker container:")

        #store docker container
        success, message, extract_path, size = self.files_helper.store_docker(file_path)
        #if store worked -> create database 
        if success:
            success, message = self.database_helper.save_docker_container(extract_path, name, size)
            if success:
                messagebox.showinfo("Success", message)
                self.load_docker_containers()
            else:
                messagebox.showerror("Error", message)
        else:
            messagebox.showerror("Error", message)



    def show_result_overview(self, event):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            selected_item = self.results_listbox.get(selected_index)

            # Überprüfen, ob bereits ein Textfeld für die Resultatübersicht angezeigt wird
            result_overview_text = None
            for widget in self.window.pack_slaves():
                if isinstance(widget, tk.Text):
                    result_overview_text = widget
                    break

            # Falls bereits ein Textfeld vorhanden ist, lösche den Inhalt und zeige den neuen Text an
            if result_overview_text:
                result_overview_text.config(state=tk.NORMAL)
                result_overview_text.delete("1.0", tk.END)
                result_overview_text.insert(tk.END, f"Results for Docker container: {selected_item}\n")
                result_overview_text.config(state=tk.DISABLED)
            else:
                # Erstelle ein neues Textfeld für die Resultatübersicht
                result_overview_text = tk.Text(self.window, state=tk.DISABLED)
                result_overview_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                result_overview_text.insert(tk.END, f"Results for Docker container: {selected_item}\n")
                result_overview_text.config(state=tk.DISABLED)


            # Check if results are available for the selected Docker container
            path=selected_item.split("#")[1]

            #
            #add Run Tests button
            if not self.run_tests_button:
                self.run_tests_button = tk.Button(
                    self.window,
                    text="Run Tests",
                    command=self.run_tests_for_container,
                    bg="green",
                    fg="white",
                    font=tkfont.Font(weight="bold")
                )
                self.run_tests_button.pack(side=tk.BOTTOM, pady=10)
        else:
            messagebox.showinfo("No Selection", "Please select a Docker container.")
                
    def run_tests_for_container(self):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            selected_item = self.results_listbox.get(selected_index)
            # Run tests for the selected Docker container
            # ...
        
    def run(self):
        self.window.mainloop()
        # Close the database connection when the UI is closed
        self.db_connection.close()


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        
    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip_window, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
        
    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None



    
if __name__ == "__main__":
    ui = RobustnessTestUI()
    ui.run()
