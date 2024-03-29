import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sqlite3
from result_overview import ResultOverview
from tkinter import font as tkfont
import math


class RobustnessTestUI:
    def __init__(self, controller):
        self.controller=controller
        self.window = tk.Tk()
        self.window.geometry("800x600")  # Set the initial size to 800x600 pixels
        self.window.title("Robustness Test Tool")

        self.run_tests_button = None  # Variable zum Verfolgen des "Run Tests" Buttons
        self.graph_frames = []  # Liste zur Verfolgung der Frame-Widgets für die Graphen

        # Grid-Layout für das Hauptfenster
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # PanedWindow für linke und rechte Seite
        self.paned_window = tk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=0, column=0, sticky="nsew")

        # Linkes Frame für die Docker-Liste
        self.docker_list_frame = tk.Frame(self.paned_window, width=160)
        self.paned_window.add(self.docker_list_frame)

        self.results_listbox = tk.Listbox(self.docker_list_frame)
        self.results_listbox.bind("<<ListboxSelect>>", self.show_result_overview)
        self.results_listbox.grid(row=0, column=0, sticky="nsew")

        self.add_button = tk.Button(self.docker_list_frame, text="Add", command=self.add_container)
        self.add_button.grid(row=1, column=0, sticky="se", padx=10, pady=10)
        
        # Rechtes Frame für die Ergebnisübersicht und Transformationen
        self.result_transform_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.result_transform_frame)

        self.result_overview = tk.Text(self.result_transform_frame, height=1, state=tk.DISABLED, takefocus=False)
        self.result_overview.grid(row=0, column=0, sticky="new")

        self.transformations_frame = tk.Frame(self.result_transform_frame)
        self.transformations_frame.grid(row=1, column=0, sticky="nsew")

        self.load_docker_containers()

        # Set minimum size for the window
        self.window.update()
        self.window.minsize(self.window.winfo_width(), self.window.winfo_height())

        self.window.mainloop()


    def reset_right_panel(self):
        # Lösche alle vorhandenen Elemente im rechten Panel
        for child in self.transformations_frame.winfo_children():
            child.destroy()

        # Überprüfe, ob das result_overview-Textfeld noch existiert
        if hasattr(self, 'result_overview'):
            # Setze das result_overview-Textfeld zurück, falls vorhanden
            self.result_overview.config(state=tk.NORMAL)
            self.result_overview.delete(1.0, tk.END)
            self.result_overview.config(state=tk.DISABLED)

        # Entferne den "Run Tests" Button, falls vorhanden
        if self.run_tests_button:
            self.run_tests_button.destroy()
            self.run_tests_button = None

        # Entferne alle Graphen-Widgets
        for graph_frame in self.graph_frames:
            graph_frame.destroy()
        self.graph_frames = []

         # Entferne alle Labels
        for label in self.window.grid_slaves(row=2):
            label.grid_forget()
            label.destroy()


    def load_docker_containers(self):
        #clear container list
        self.results_listbox.delete(0, tk.END)
        #get all container names
        containers=self.controller.load_docker_containers()
        for c in containers:
            name = c[0]
            path = c[1]
            item_text = f"{name}#{path}"  # Kombinieren von Name und Pfad
            self.results_listbox.insert(tk.END, item_text)


    def add_container(self):
        # get path to docker container
        file_path = filedialog.askopenfilename(filetypes=[("Tar Archive", "*.tar")])

        # Prompt for container name
        name = simpledialog.askstring("Container Name", "Enter the name for the Docker container:")

        success,message = self.controller.store_container(file_path,name)

        if success:
            messagebox.showinfo("Success", message)
            self.load_docker_containers()
        else:
            messagebox.showerror("Error", message)

    def show_result_overview(self, event):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            selected_item = self.results_listbox.get(selected_index)
            self.reset_right_panel()
            self.result_overview.config(state=tk.NORMAL)
            self.result_overview.delete(1.0, tk.END)  # Lösche den Text im Textfeld

            # Überprüfe, ob der "Run Tests" Button bereits vorhanden ist
            if not self.run_tests_button:
                # Erzeuge den "Run Tests" Button, wenn er noch nicht vorhanden ist
                self.run_tests_button = tk.Button(
                    self.window,
                    text="Run Tests",
                    bg="green",
                    fg="white",
                    font=("Arial", 14, "bold"),
                    command=self.run_tests_for_container
                )
                self.run_tests_button.grid(row=1, column=1, sticky="se", padx=10, pady=10)

            # Überprüfe, ob Testergebnisse für den ausgewählten Container vorhanden sind
            path = selected_item.split("#")[1]
            
            if self.controller.results_available(path):
                # Ergebnisse vorhanden
                result_score = self.controller.get_result_score(path)
                self.result_overview.config(state=tk.NORMAL)
                self.result_overview.delete(1.0, tk.END)
                self.result_overview.insert(tk.END, f"Robustness Score: {result_score}")
                self.result_overview.config(state=tk.DISABLED)
                self.showTransformationGraphs()
            else:
                # Keine Ergebnisse vorhanden
                self.result_overview.config(state=tk.NORMAL)
                self.result_overview.delete(1.0, tk.END)
                self.result_overview.insert(tk.END, "No Results for this container yet, run the tests.")
                self.result_overview.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("No Selection", "Please select a Docker container.")

    def showTransformationGraphs(self):
        pass


    def run_tests_for_container(self):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            selected_item = self.results_listbox.get(selected_index)
            # Run tests for the selected Docker container
            # ...
            self.controller.run_tests_for_container()

    def run(self):
        self.window.mainloop()
        # Close the database connection when the UI is closed
        self.controller.exit()




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


