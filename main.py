import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import pyautogui
import time
import keyboard
import psutil
import pygetwindow as gw

def load_image(image_path):
    """Load image and convert to grayscale."""
    image = Image.open(image_path).convert('L')
    return image

def crop_image(image, threshold=128):
    """Crop the image to remove whitespace."""
    image_array = np.array(image)
    non_white_pixels = np.where(image_array < threshold)

    if non_white_pixels[0].size > 0 and non_white_pixels[1].size > 0:
        top = non_white_pixels[0].min()
        bottom = non_white_pixels[0].max() + 1
        left = non_white_pixels[1].min()
        right = non_white_pixels[1].max() + 1

        image = image.crop((left, top, right, bottom))

    return image

def resize_image(image, height, width):
    """Resize image to the specified height and width."""
    return image.resize((width, height), Image.LANCZOS)

def image_to_binary_grid(image, threshold=128):
    """Convert image to binary grid."""
    image_array = np.array(image)
    binary_grid = (image_array < threshold).astype(int)  # Black pixels as 1, white as 0
    return binary_grid

def display_grid(grid):
    """Display grid in console (for debugging purposes)."""
    for row in grid:
        print("".join(['▓▓▓▓' if cell else '░░░░' for cell in row]))

def save_grid_to_file(grid, output_file, height, width):
    """Save grid to a file."""
    with open(output_file, 'w') as f:
        for row_idx, row in enumerate(grid):
            line = ""
            for col_idx, cell in enumerate(row):
                if cell:
                    line += f"{width - col_idx},"
                else:
                    line += "=,"
            f.write(line + f'   -{height - row_idx} \n')

def automate_clicks(grid, start_x, start_y):
    """Automate the clicking process based on the grid."""
    cell_width = 20  # Adjust these values based on the GTT program's cell size
    cell_height = 10

    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if keyboard.is_pressed('space'):  # Stop if the spacebar is pressed
                print("Automation stopped by user.")
                return

            x = start_x + j * cell_width
            y = start_y + i * cell_height

            if cell:
                pyautogui.click(x, y)

def is_gtt_running():
    """Check if GTT is running."""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'GTT.exe':  # Check for exact process name
            return True
    return False

def focus_gtt_window():
    """Focus and maximize the GTT window."""
    for window in gw.getAllTitles():
        if "Guntram" in window:  # Match only the exact window title "GTT"
            gtt_window = gw.getWindowsWithTitle(window)[0]
            gtt_window.activate()
            gtt_window.maximize()

            python_window = gw.getWindowsWithTitle("Christian's Letters to GTT Software Thingy")[0]
            python_window.activate()
            python_window.moveTo(0, 5)

            return True
    return False

def generate_grid():
    image_path = entry_image_path.get().strip('"')  # Remove quotation marks if present
    height = int(entry_height.get())
    width = int(entry_width.get())
    start_cell_height = int(entry_start_height.get())

    try:
        image = load_image(image_path)
        image = crop_image(image)
        image = resize_image(image, height, width)
        binary_grid = image_to_binary_grid(image)
        display_grid(binary_grid)
        save_grid_to_file(binary_grid, 'font_grid.txt', height, width)

        if is_gtt_running():
            if focus_gtt_window():
                # Adjust the start_y based on the starting cell height
                start_y = 280 + (24 - start_cell_height) * 10
                messagebox.showinfo("Captured letter", "Starting the generation of cells in GTT. Click space to cancel")
                automate_clicks(binary_grid, 140, start_y)
                messagebox.showinfo("Process finished", "GTT generation of cells has completed")
            else:
                messagebox.showerror("An error has occurred", "Close the process and try again.")
        else:
            messagebox.showerror("GTT not running", "The GTT program is not currently running.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if file_path:
        entry_image_path.delete(0, tk.END)
        entry_image_path.insert(0, file_path)

# Create the GUI window
window = tk.Tk()
window.title("Christian's Letters to GTT Software Thingy")

# Image path entry
tk.Label(window, text="Letters image path:").grid(row=0, column=0, padx=10, pady=5)
entry_image_path = tk.Entry(window, width=50)
entry_image_path.grid(row=0, column=1, padx=10, pady=5)
tk.Button(window, text="Browse", command=browse_image).grid(row=0, column=2, padx=10, pady=5)

# Height entry
tk.Label(window, text="Letter cell height:").grid(row=1, column=0, padx=10, pady=5)
entry_height = tk.Entry(window)
entry_height.grid(row=1, column=1, padx=10, pady=5)
entry_height.insert(0, "20")  # Default value

# Width entry
tk.Label(window, text="Letter cell width:").grid(row=2, column=0, padx=10, pady=5)
entry_width = tk.Entry(window)
entry_width.grid(row=2, column=1, padx=10, pady=5)
entry_width.insert(0, "16")  # Default value

# Starting cell height entry
tk.Label(window, text="Starting cell height:").grid(row=3, column=0, padx=10, pady=5)
entry_start_height = tk.Entry(window)
entry_start_height.grid(row=3, column=1, padx=10, pady=5)
entry_start_height.insert(0, "24")  # Default value

# Generate button
tk.Button(window, text="Generate", command=generate_grid).grid(row=4, column=0, columnspan=3, padx=10, pady=20)

# Run the GUI loop
window.mainloop()
