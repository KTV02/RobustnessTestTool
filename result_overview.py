import tkinter as tk

class ResultOverview(tk.Frame):
    def __init__(self, parent, width):
        super().__init__(parent, width=int(parent.winfo_screenwidth() * width))
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.label = tk.Label(self, text="Result Overview")
        self.label.pack(padx=10, pady=10)
        
        # Graph canvas for displaying transformation results
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
    def display_result(self, robustness_score, transformations_data):
        # Clear the canvas
        self.canvas.delete("all")
        
        # Display the robustness score
        score_label = tk.Label(self.canvas, text=f"Robustness Score: {robustness_score}")
        score_label.pack(padx=10, pady=10)
        
        # Display the graphs for each transformation
        for transformation in transformations_data:
            name = transformation["name"]
            values = transformation["values"]
            
            # Create a graph for each transformation
            graph_label = tk.Label(self.canvas, text=name)
            graph_label.pack(padx=10, pady=10)
            
            # Plot the values on the graph
            graph = tk.Canvas(self.canvas, width=400, height=300)
            graph.pack()
            
            x_scale = 400 / len(values)
            y_scale = 300
            
            for i in range(len(values)):
                x1 = i * x_scale
                y1 = y_scale * (1 - values[i][1])
                x2 = (i + 1) * x_scale
                y2 = y_scale
                
                graph.create_rectangle(x1, y1, x2, y2, fill="blue")
                
                # Add text labels for values
                graph.create_text((x1 + x2) / 2, y1 - 10, text=f"{values[i][1]:.2f}")
                
        self.canvas.update()
