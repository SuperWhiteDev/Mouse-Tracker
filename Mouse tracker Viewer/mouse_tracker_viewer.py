import tkinter as tk
import sys
import json
from os.path import join, abspath
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import language

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 600

MOUSE_TRACKER_FOLDER = r"C:\ProgramData\MouseTracker"
MOUSE_TRACKER_DATA = "data.json"

# All strings used in the application
strings = (
    "Statistics for a specific period:",
    "Weekly Statistics",
    "All Time Statistics",
    "Distance in metres",
    "Statistics for the all time",
    "Statistics for each date:",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
)

def resource_path(relative_path : str):
    """
    Gets the absolute path to the resource, works in both development and compiled mode.

    :param relative_path: path to resource
    :return: path
    """

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(".")

    return join(base_path, relative_path)

def rgb_to_hex(r : int, g : int, b : int) -> str:
    """
    Converts RGB values to hexadecimal format.

    :param r: Red value (0-255)
    :param g: Green value (0-255)
    :param b: Blue value (0-255)
    :return: Colour in hexadecimal format (string)
    """

    # Проверяем, что значения находятся в диапазоне от 0 до 255
    if not all(0 <= value <= 255 for value in (r, g, b)):
        raise ValueError("Значения RGB должны быть в диапазоне от 0 до 255.")

    # Преобразуем значения в шестнадцатеричный формат и объединяем
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

class MouseTrackerViewer():
    def __init__(self) -> None:
        self.language = language.Language()
        if not self.language.is_language_loaded() and self.language.current_language != "en":
            if self.language.create_language_file(strings):
                self.language.load_language_file()

        # Widget settings
        self.window_bg = rgb_to_hex(0, 0, 230)
        self.buttons_bg = rgb_to_hex(0, 0, 215)
        self.buttons_fg = "white"
        self.buttons_border_width = 0.0,
        self.buttons_anchor = "w"
        self.buttons_active_bg = rgb_to_hex(0, 0, 200)
        self.buttons_active_fg = "white"
        self.buttons_selected_bg = rgb_to_hex(0, 0, 180)
        self.buttons_selected_fg = "white"
        self.buttons_font = ("Bahnschrift SemiBold Condensed", 13, "bold")
        self.labels_fg = rgb_to_hex(217, 217, 217)
        

        # Creating an application window
        self.window = tk.Tk("Mouse tracker viewer")
        self.window.withdraw() # Hiding a window

        # Window customisation
        self.window.title("Mouse tracker viewer")
        self.window.iconbitmap(resource_path("icon.ico"))
        self.window.configure(bg=self.window_bg)
        self.window.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        width_pixels = self.window.winfo_screenwidth()
        height_pixels = self.window.winfo_screenheight()
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{width_pixels//2 - WINDOW_WIDTH//2}+{height_pixels//2 - WINDOW_HEIGHT//2}")

        # Create the left panel for the buttons
        self.left_list_box = tk.Listbox(self.window, bg=self.buttons_bg, height=100, width=32, fg=self.buttons_fg, activestyle='none',
                                         selectbackground=self.buttons_selected_bg, selectforeground=self.buttons_selected_fg, font=self.buttons_font)
        self.left_list_box.pack(expand=True, side='left', anchor="nw")
        self.left_list_box_bindings = { }

        self.left_list_box.insert(tk.END, self.language.get_string(strings[0]))
        self.left_list_box.itemconfig(0, {"selectbackground": self.window_bg, "selectforeground": self.buttons_fg, "fg": self.labels_fg})
        
        # Button for weekly statistics
        weekly_button_label = self.language.get_string(strings[1])
        self.left_list_box.insert(tk.END, weekly_button_label)
        self.left_list_box_bindings[weekly_button_label] = self.display_weekly_analytics
        
        # Button for all time statistics
        all_time_button_label = self.language.get_string(strings[2])
        self.left_list_box.insert(tk.END, all_time_button_label)
        self.left_list_box_bindings[all_time_button_label] = self.display_all_time_analytics
        
        # Loads all other buttons that show statistics for a specific day
        self.load_dates()

        self.left_list_box.bind("<<ListboxSelect>>", self.on_list_box_select)
        self.left_list_box.bind("<Motion>", self.on_buttons_enter)
        self.left_list_box.bind("<Leave>", self.on_buttons_leave)

        # Create a graph frame
        self.graph = tk.Frame(self.window)
        self.graph.pack(side=tk.RIGHT, pady=0) 
    
    def run(self):
        self.window.deiconify()
        self.window.mainloop()

    def on_exit(self):
        sys.exit(0)

    def display_analytics(self, data, title, rotation=0):
        dates = list(data.keys())
        total_distances = list(data.values())
        
        # Clears the previous graph
        self.clear_analytics()

        # Create a histogram
        plt.figure(figsize=(100, 100))
        plt.bar(dates, total_distances, color='blue')
        plt.title(title)
        plt.ylabel(self.language.get_string(strings[3]))

        # Create an array of indices for the offset
        x = np.arange(len(dates))

        plt.bar(x, total_distances, color='blue')
        plt.xticks(x, dates, rotation=rotation)  # Set the X-axis marks

        plt.grid(axis='y')

        # Embed the graph in the application
        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.graph)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.graph.pack()
    def clear_analytics(self):
        plt.clf()
        for widget in self.graph.winfo_children():
            widget.destroy()  # Remove all widgets from the graph frame
        self.graph.pack_forget()
    def display_weekly_analytics(self):
        with open(join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_DATA), "r", encoding="utf-8") as f:
            data = json.load(f)

        last_7_dates = sorted(data.keys())[-7:]

        weekly_data = {}
        for date in last_7_dates:
            day_of_week = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = day_of_week.strftime("%A")
            weekly_data[self.language.get_string(day_of_week)] = data[date]["total_distance"]

        self.display_analytics(weekly_data, self.language.get_string(strings[1]))
    
    def display_daily_analytics(self, date):
        with open(join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_DATA), "r", encoding="utf-8") as f:
            data = json.load(f)

        day_data = data[date]

        day_distance = {}
        for hour in day_data.keys():
            if hour != "total_distance":
                day_distance[hour] = day_data[hour]

        day_object = datetime.strptime(date, "%Y-%m-%d")
        day = day_object.day
        month = day_object.strftime("%B")
        year = day_object.year

        # Getting a suffix for the month
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        title = f"Statistics for the {day}{suffix} of {month} {year}"
        if self.language.current_language != "en":
            # The entire string is translated into the language of the system
            title = self.language.translate(title)
        
        self.display_analytics(day_distance, title)

    def display_all_time_analytics(self):
        with open(join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_DATA), "r", encoding="utf-8") as f:
            data = json.load(f)

        total_distances = []
        for day, value in data.items():
            total_distances.append((day, value.get("total_distance")))

        total_distances.sort(key=lambda x: x[1], reverse=True)
        
        top_values = total_distances[:10]

        self.display_analytics({date: distance for date, distance in top_values}, self.language.get_string(strings[4]), 30)

    def load_dates(self):
        with open(join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_DATA), "r", encoding="utf-8") as f:
            data = json.load(f)

        self.left_list_box.insert(tk.END, self.language.get_string(strings[5]))
        self.left_list_box.itemconfig(3, {"selectbackground": self.window_bg, "selectforeground": self.buttons_fg, "fg": self.labels_fg})
        
        # Create buttons for all dates for which there is information
        for _, date in enumerate(sorted(data.keys(), reverse=True)):
            year, month, day = date.split("-")

            label = f"{day} {self.language.get_string(datetime.strptime(month, "%m").strftime("%B"))} {year}"

            self.left_list_box.insert(tk.END, label)
            self.left_list_box_bindings[label] = lambda d=date: self.display_daily_analytics(d)
        
    def on_buttons_enter(self, event : tk.Event):
        widget = event.widget
        index = widget.nearest(event.y)
        for i in range(widget.size()):
            if i == index or i == 0 or i == 3:
                continue
            widget.itemconfig(i, {"bg": self.buttons_bg, "fg": self.buttons_fg})
        if index != 0 and index != 3:
            widget.itemconfig(index, {"bg": self.buttons_active_bg, "fg": self.buttons_active_fg})
    def on_buttons_leave(self, event):
        widget = event.widget
        for i in range(widget.size()):
            if i != 0 and i != 3:
                widget.itemconfig(i, {"bg": self.buttons_bg, "fg": self.buttons_fg})
    def on_list_box_select(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            try:
                self.left_list_box_bindings[widget.get(selection[0])]()
            except KeyError:
                pass
    
if __name__ == "__main__":
    app = MouseTrackerViewer()
    app.display_weekly_analytics()
    app.run()