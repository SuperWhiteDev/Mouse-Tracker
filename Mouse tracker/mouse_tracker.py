from pynput import mouse
from threading import Timer
from tkinter import Tk
import json
from datetime import datetime
from os import makedirs, path

MOUSE_TRACKER_FOLDER = r"C:\ProgramData\MouseTracker"
MOUSE_TRACKER_DATA = "data.json"

class MouseTracker():
    def __init__(self) -> None:
        self.distance = 0
        self.last_pos = None

        root = Tk()
        root.withdraw() #Hide the main window

        width_pixels = root.winfo_screenwidth()
        height_pixels = root.winfo_screenheight()
    
        dpi = root.winfo_fpixels('1i') # Get the number of pixels in 1 inch

        width_inches = width_pixels / dpi
        height_inches = height_pixels / dpi

        #Getting screen diagonal in inches
        diagonal_inches = (width_inches**2 + height_inches**2)**0.5

        root.destroy()

        self.ppi = ((width_pixels**2 + height_pixels**2)**0.5) / diagonal_inches
    
    def on_move(self, x, y):
        if self.last_pos:
            dx = x - self.last_pos[0]
            dy = y - self.last_pos[1]
            self.distance += (dx**2 + dy**2)**0.5
        self.last_pos = (x, y)
    
    def get_data(self):
        try:
            with open(path.join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_DATA), "r", encoding="utf-8") as f:  
                data = json.load(f) 
        except json.decoder.JSONDecodeError:
            data = {}
        except FileNotFoundError:
            data = {}

        return data
    def prepare(self):
        #Prepares all necessary files and folders
        if not path.exists(MOUSE_TRACKER_FOLDER):
            makedirs(MOUSE_TRACKER_FOLDER)
    def save_data(self):
        distance = (self.distance / self.ppi) * 0.0254 # Converting distance to meters

        data = self.get_data()

        day = datetime.now().strftime("%Y-%m-%d")
        hour = datetime.now().strftime("%H")

        # Saves the data
        if day in data:
            data[day]["total_distance"] += distance
        else:
            data[day] = {"total_distance": distance}

        if hour in data[day]:
            data[day][hour] += distance
        else:
            data[day][hour] = distance

        with open(path.join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_DATA), "w") as f:
            json.dump(data, f, indent=4)

        self.distance = 0
        
        # Timer is set which will call this function again after 60 seconds.
        Timer(60, self.save_data).start()
        
    def start(self):
        with mouse.Listener(self.on_move) as listener:
            self.save_data()
            listener.join()

if __name__ == "__main__":
    tracker = MouseTracker()
    tracker.prepare()
    tracker.start()
