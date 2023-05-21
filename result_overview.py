import tkinter as tk
import sqlite3

class ResultOverview:
    def __init__(self, result_overview_text):
        self.result_overview_text = result_overview_text

    def show_result_overview(self, selected_item):
        db_connection = sqlite3.connect('results.db')
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM results WHERE Dockerpath=?", (selected_item,))
        result = db_cursor.fetchone()
        db_connection.close()

        if result is not None:
            self.result_overview_text.config(state=tk.NORMAL)
            self.result_overview_text.delete("1.0", tk.END)

            # Zeige alle Ergebnisse an
            self.result_overview_text.insert(tk.END, f"Docker Container: {selected_item}\n\n")
            self.result_overview_text.insert(tk.END, "Robustness Score: {}\n".format(result[1]))
            self.result_overview_text.insert(tk.END, "Date: {}\n".format(result[2]))
            self.result_overview_text.insert(tk.END, "\nTransformation Results:\n")

            # Für jede Transformation den Graphen anzeigen
            for i in range(3, len(result)):
                self.result_overview_text.insert(tk.END, "Transformation {}: {}\n".format(i-2, result[i]))

            self.result_overview_text.config(state=tk.DISABLED)
        else:
            self.result_overview_text.config(state=tk.NORMAL)
            self.result_overview_text.delete("1.0", tk.END)
            self.result_overview_text.insert(tk.END, "No results available for this Docker container.")
            self.result_overview_text.config(state=tk.DISABLED)
