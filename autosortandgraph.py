import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinterdnd2 as tkdnd  # Import tkinterdnd2 for drag-and-drop support

class DataAnalysisApp:
    def __init__(self):
        self.root = tkdnd.TkinterDnD.Tk()  # Use tkinterdnd2's Tk class for drag-and-drop support
        self.root.title("Data Analysis Tool")
        self.file_path = None
        self.data = None
        self.setup_ui()

        # Ensure the program exits when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.upload_button = tk.Button(self.root, text="Upload Spreadsheet", command=self.upload_file)
        self.upload_button.pack(pady=20)

        self.dnd_label = tk.Label(self.root, text="Or Drag and Drop a file here")
        self.dnd_label.pack(pady=10)

        # Register the label as a drop target
        self.root.drop_target_register(tkdnd.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop)

    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if self.file_path:
            self.process_file()

    def drop(self, event):
        self.file_path = event.data.strip('{}')  # Remove curly braces added by some systems
        if self.file_path:
            self.process_file()

    def process_file(self):
        try:
            if self.file_path.endswith('.csv'):
                self.data = pd.read_csv(self.file_path)  # Read CSV file
            else:
                self.data = pd.read_excel(self.file_path)  # Read Excel file
            self.root.withdraw()  # Hide the upload window instead of closing it
            self.show_sort_options()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the file: {e}")

    def show_sort_options(self):
        self.sort_window = tk.Toplevel()  # Create a new window for sorting options
        self.sort_window.title("Sort Data")
        
        self.sort_var = tk.StringVar(value="None")
        self.order_var = tk.StringVar(value="Ascending")

        # Place column selection radio buttons horizontally
        for idx, column in enumerate(self.data.columns):
            rb = tk.Radiobutton(self.sort_window, text=column, variable=self.sort_var, value=column)
            rb.grid(row=0, column=idx, padx=5, pady=5, sticky='w')  # Place in row 0, column idx

        # Create a frame for ascending/descending radio buttons
        order_frame = tk.Frame(self.sort_window)
        order_frame.grid(row=1, column=0, columnspan=len(self.data.columns), pady=10)

        # Place ascending/descending radio buttons in the frame
        tk.Radiobutton(order_frame, text="Ascending", variable=self.order_var, value="Ascending").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(order_frame, text="Descending", variable=self.order_var, value="Descending").pack(side=tk.LEFT, padx=5)

        # Add a confirm button
        confirm_button = tk.Button(self.sort_window, text="Confirm", command=self.sort_data)
        confirm_button.grid(row=2, column=0, columnspan=len(self.data.columns), pady=10)

    def sort_data(self):
        if self.sort_var.get() != "None":
            ascending = self.order_var.get() == "Ascending"
            sort_column = self.sort_var.get()

            # Handle string-based columns (case-insensitive sorting)
            if self.data[sort_column].dtype == object:  # Check if the column contains strings
                self.data = self.data.sort_values(by=sort_column, ascending=ascending, key=lambda col: col.str.lower())
            else:
                self.data = self.data.sort_values(by=sort_column, ascending=ascending)

            # Prompt the user if they want to save the sorted spreadsheet
            save_response = messagebox.askyesno("Save Spreadsheet", "Would you like to save the sorted spreadsheet?")
            if save_response:
                save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
                if save_path:
                    if save_path.endswith('.csv'):
                        self.data.to_csv(save_path, index=False)
                    else:
                        self.data.to_excel(save_path, index=False)
                    messagebox.showinfo("Success", "Sorted spreadsheet saved successfully!")

            self.sort_window.destroy()  # Close the sorting window
            self.ask_graph()

    def ask_graph(self):
        response = messagebox.askyesno("Graph", "Would you like to create a graph?")
        if response:
            self.show_graph_options()
        else:
            self.root.quit()

    def show_graph_options(self):
        self.graph_window = tk.Toplevel()  # Create a new window for graph options
        self.graph_window.title("Choose Graph Type")
        
        # Place chart type buttons horizontally
        button_frame = tk.Frame(self.graph_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Bar", command=lambda: self.create_graph('bar')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Line", command=lambda: self.create_graph('line')).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Pie", command=lambda: self.create_graph('pie')).pack(side=tk.LEFT, padx=5)

    def create_graph(self, graph_type):
        # Clear previous chart if it exists
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'toolbar'):
                self.toolbar.destroy()

        # Create a new window for axis selection
        self.axis_window = tk.Toplevel()
        self.axis_window.title("Select Axes and Grouping")

        # Add X-axis selection
        tk.Label(self.axis_window, text="Select X-axis:").grid(row=0, column=0, padx=5, pady=5)
        self.x_axis_var = tk.StringVar(value=self.sort_var.get())  # Default to the sort column
        for idx, column in enumerate(self.data.columns):
            rb = tk.Radiobutton(self.axis_window, text=column, variable=self.x_axis_var, value=column)
            rb.grid(row=1, column=idx, padx=5, pady=5, sticky='w')

        # Add Y-axis selection
        tk.Label(self.axis_window, text="Select Y-axis:").grid(row=2, column=0, padx=5, pady=5)
        self.y_axis_var = tk.StringVar(value=self.data.columns[1])  # Default to second column
        for idx, column in enumerate(self.data.columns):
            rb = tk.Radiobutton(self.axis_window, text=column, variable=self.y_axis_var, value=column)
            rb.grid(row=3, column=idx, padx=5, pady=5, sticky='w')

        # Add grouping selection
        tk.Label(self.axis_window, text="Select Grouping Column (optional):").grid(row=4, column=0, padx=5, pady=5)
        self.group_var = tk.StringVar(value="None")  # Default to no grouping
        for idx, column in enumerate(self.data.columns):
            rb = tk.Radiobutton(self.axis_window, text=column, variable=self.group_var, value=column)
            rb.grid(row=5, column=idx, padx=5, pady=5, sticky='w')

        # Add a confirm button
        confirm_button = tk.Button(self.axis_window, text="Confirm", command=lambda: self.draw_graph(graph_type))
        confirm_button.grid(row=6, column=0, columnspan=len(self.data.columns), pady=10)

    def draw_graph(self, graph_type):
        # Get selected axes and grouping column
        x_axis = self.x_axis_var.get()
        y_axis = self.y_axis_var.get()
        group_column = self.group_var.get()

        # Check if Y-axis is numeric
        if self.data[y_axis].dtype == object:  # Check if the column contains strings
            messagebox.showerror("Error", "Y-axis must be a numeric column. Please select a different column.")
            return

        # Create a new figure
        fig, ax = plt.subplots(figsize=(12, 8))  # Increase figure size for better readability

        if graph_type == 'bar':
            # Check if values are too large and scale them down
            max_value = self.data[y_axis].max()
            scale_factor = 1
            if max_value > 1_000_000:
                scale_factor = 1_000_000
                self.data[y_axis] = self.data[y_axis] / scale_factor
                y_label = f"{y_axis} (in millions)"
            elif max_value > 1_000:
                scale_factor = 1_000
                self.data[y_axis] = self.data[y_axis] / scale_factor
                y_label = f"{y_axis} (in thousands)"
            else:
                y_label = y_axis

            # Plot the bar graph with grouping
            if group_column != "None":
                # Group data by X-axis and Grouping column
                grouped_data = self.data.groupby([x_axis, group_column])[y_axis].sum().unstack()
                grouped_data.plot(kind='bar', ax=ax, stacked=True)
            else:
                self.data.plot(kind='bar', x=x_axis, y=y_axis, ax=ax, legend=False)

            ax.set_xlabel(x_axis)  # Label X-axis
            ax.set_ylabel(y_label)  # Label Y-axis with scaling information
            plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
            ax.grid(True)  # Add gridlines for better readability
            if group_column != "None":
                ax.legend(title=group_column)  # Add legend if grouping is applied

        elif graph_type == 'line':
            # Plot the line graph with grouping
            if group_column != "None":
                grouped_data = self.data.groupby([x_axis, group_column])[y_axis].sum().unstack()
                grouped_data.plot(kind='line', ax=ax)
            else:
                self.data.plot(kind='line', x=x_axis, y=y_axis, ax=ax)

            ax.set_xlabel(x_axis)  # Label X-axis
            ax.set_ylabel(y_axis)  # Label Y-axis
            ax.grid(True)  # Add gridlines for better readability
            if group_column != "None":
                ax.legend(title=group_column)  # Add legend if grouping is applied

        elif graph_type == 'pie':
            # Plot the pie chart
            if group_column != "None":
                grouped_data = self.data.groupby(group_column)[y_axis].sum()
                grouped_data.plot(kind='pie', ax=ax, legend=False, labels=grouped_data.index, autopct='%1.1f%%')
            else:
                self.data.plot(kind='pie', y=y_axis, labels=self.data[x_axis], ax=ax, legend=False, autopct='%1.1f%%')

            ax.set_ylabel("")  # Remove Y-axis label for pie chart

        plt.tight_layout()  # Adjust layout to prevent overlapping

        # Embed the chart in the Tkinter window
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add a toolbar for zooming and panning
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_window)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add a save button for the graph
        save_button = tk.Button(self.graph_window, text="Save Graph", command=lambda: self.save_graph(fig))
        save_button.pack(side=tk.BOTTOM, pady=10)

        # Close the axis selection window
        self.axis_window.destroy()

    def save_graph(self, fig):
        # Prompt the user to save the graph
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("PDF files", "*.pdf")])
        if save_path:
            fig.savefig(save_path)
            messagebox.showinfo("Success", "Graph saved successfully!")

    def on_close(self):
        """Handle window close event."""
        self.root.quit()

if __name__ == "__main__":
    app = DataAnalysisApp()
    app.root.mainloop()