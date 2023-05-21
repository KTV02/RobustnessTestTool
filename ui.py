import tkinter as tk
from tkinter import filedialog, messagebox
import os
import tarfile
import datetime
import sqlite3


class RobustnessTestUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Robustness Test Tool")

        self.images_folder = "images"  # Pfad zum Ordner für die entpackten Docker-Images
        self.create_images_folder()  # Erstelle den Ordner, falls er noch nicht existiert

        self.results_listbox = tk.Listbox(self.window)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.results_listbox.bind("<<ListboxSelect>>", self.show_result_overview)
        
        self.result_overview = tk.Text(self.window, state=tk.DISABLED)
        self.result_overview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.add_button = tk.Button(self.window, text="Add", command=self.add_algorithm)
        self.add_button.pack(anchor=tk.NE, padx=10, pady=10)

        
        self.database_file = "docker_containers.db"  # Dateiname der SQLite-Datenbank
        self.create_database()  # Erstelle die Datenbank, falls sie noch nicht existiert

        self.load_docker_containers()


    def create_images_folder(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)

    def create_database(self):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS docker_containers
                     (name TEXT, path TEXT, date_added TEXT, size INTEGER)''')
        conn.commit()
        conn.close()

    def load_docker_containers(self):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute("SELECT name FROM docker_containers")
        results = c.fetchall()
        conn.close()

        self.results_listbox.delete(0, tk.END)
        for result in results:
            self.results_listbox.insert(tk.END, result[0])

    def add_algorithm(self):
        file_path = filedialog.askopenfilename(filetypes=[("Tar Archive", "*.tar")])
        if file_path:
            if self.is_tar_file(file_path):
                self.extract_docker_image(file_path)
                self.save_docker_container(file_path)
                self.load_docker_containers()
            else:
                messagebox.showerror("Error", "The selected file is not a valid .tar file.")

    def is_tar_file(self, file_path):
        return tarfile.is_tarfile(file_path)

    def extract_docker_image(self, file_path):
        unique_name = self.generate_unique_name()
        extract_path = os.path.join(self.images_folder, unique_name)

        try:
            with tarfile.open(file_path, "r") as tar:
                tar.extractall(extract_path)
            messagebox.showinfo("Success", f"Docker image extracted to: {extract_path}")
        except tarfile.TarError as e:
            messagebox.showerror("Error", f"Failed to extract Docker image: {str(e)}")

    def generate_unique_name(self):
        i = 1
        while True:
            unique_name = f"image{i}"
            extract_path = os.path.join(self.images_folder, unique_name)
            if not os.path.exists(extract_path):
                return unique_name
            i += 1


    def save_docker_container(self, file_path):
        unique_name = self.generate_unique_name()
        extract_path = os.path.join(self.images_folder, unique_name)

        # Daten für die Datenbank
        name = os.path.splitext(os.path.basename(file_path))[0]
        date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        size = os.path.getsize(file_path)

        try:
            with tarfile.open(file_path, "r") as tar:
                tar.extractall(extract_path)

            # Daten in die SQLite-Datenbank speichern
            conn = sqlite3.connect(self.database_file)
            c = conn.cursor()
            c.execute("INSERT INTO docker_containers VALUES (?, ?, ?, ?)",
                      (name, extract_path, date_added, size))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Docker container '{name}' saved.")
        except tarfile.TarError as e:
            messagebox.showerror("Error", f"Failed to save Docker container: {str(e)}")

    def show_result_overview(self, event):
        selected_item = self.results_listbox.get(self.results_listbox.curselection())
        self.result_overview.config(state=tk.NORMAL)
        self.result_overview.delete("1.0", tk.END)
        self.result_overview.insert(tk.END, f"Selected Docker Container: {selected_item}\n")
        self.result_overview.insert(tk.END, "Current Result:\n")
        self.result_overview.insert(tk.END, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n")
        self.result_overview.config(state=tk.DISABLED)

            
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
