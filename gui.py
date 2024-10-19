# gui.py
 
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import logging

class GUI:
    """
    Manages the graphical user interface for selecting and displaying images.
    """
    def __init__(self, root, on_select_callback):
        """
        Initializes the GUI components.

        :param root: The root Tkinter window.
        :param on_select_callback: Callback function to be called with selected file paths.
        """
        self.root = root
        self.on_select_callback = on_select_callback
        self.setup_gui()
        
        # Initialize variables to hold PhotoImage references
        self.photo_left = None
        self.photo_right = None

    def setup_gui(self):
        """
        Sets up the GUI layout and widgets.
        """
        self.root.title("Dual Object Detection App")
        self.root.geometry("1400x940")  # Increased size to accommodate images and info
        self.root.resizable(False, False)
        
        # Button to select images
        self.btn_select = tk.Button(
            self.root, 
            text="Select Two Images", 
            command=self.select_images, 
            width=20, 
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 12, "bold")
        )
        self.btn_select.pack(pady=10)
        
        # Frame to hold images and their information
        self.frame_images = tk.Frame(self.root)
        self.frame_images.pack(pady=10)
        
        # Left Image Canvas and Info
        self.frame_left = tk.Frame(self.frame_images)
        self.frame_left.pack(side=tk.LEFT, padx=10)
        
        self.canvas_left = tk.Canvas(self.frame_left, width=640, height=480, bg="grey")
        self.canvas_left.pack()
        
        self.lbl_res_left = tk.Label(self.frame_left, text="Resolution: N/A", font=("Helvetica", 10))
        self.lbl_res_left.pack(pady=5)
        
        self.lbl_coords_left = tk.Label(self.frame_left, text="x: -, y: -", font=("Helvetica", 10))
        self.lbl_coords_left.pack()
        
        # Bind mouse motion to left canvas
        self.canvas_left.bind("<Motion>", self.mouse_move_left)
        
        # Right Image Canvas and Info
        self.frame_right = tk.Frame(self.frame_images)
        self.frame_right.pack(side=tk.RIGHT, padx=10)
        
        self.canvas_right = tk.Canvas(self.frame_right, width=640, height=480, bg="grey")
        self.canvas_right.pack()
        
        self.lbl_res_right = tk.Label(self.frame_right, text="Resolution: N/A", font=("Helvetica", 10))
        self.lbl_res_right.pack(pady=5)
        
        self.lbl_coords_right = tk.Label(self.frame_right, text="x: -, y: -", font=("Helvetica", 10))
        self.lbl_coords_right.pack()
        
        # Bind mouse motion to right canvas
        self.canvas_right.bind("<Motion>", self.mouse_move_right)
        
    def display_images(self, detected_img_left, detected_img_right):
        """
        Displays the detected left and right images on the GUI.

        :param detected_img_left: Image array (RGB) for the left image.
        :param detected_img_right: Image array (RGB) for the right image.
        """
        try:
            # Convert NumPy arrays to PIL Images
            img_left = Image.fromarray(detected_img_left)
            img_right = Image.fromarray(detected_img_right)
            
            # Resize images to fit the canvas while maintaining aspect ratio
            #img_left.thumbnail((480, 360))
            #img_right.thumbnail((480, 360))
            
            # Convert PIL Images to ImageTk.PhotoImage
            self.photo_left = ImageTk.PhotoImage(img_left)
            self.photo_right = ImageTk.PhotoImage(img_right)
            
            # Clear previous images
            self.canvas_left.delete("all")
            self.canvas_right.delete("all")
            
            # Display images on the canvases
            self.canvas_left.create_image(0, 0, anchor=tk.NW, image=self.photo_left)
            self.canvas_right.create_image(0, 0, anchor=tk.NW, image=self.photo_right)
        except Exception as e:
            logging.error(f"Error displaying images: {e}")
            messagebox.showerror("Display Error", f"Failed to display images:\n{e}")
    
    def update_resolution(self, res_left, res_right):
        """
        Updates the resolution labels for both images.

        :param res_left: Tuple (width, height) for the left image.
        :param res_right: Tuple (width, height) for the right image.
        """
        self.lbl_res_left.config(text=f"Resolution: {res_left[0]}x{res_left[1]}")
        self.lbl_res_right.config(text=f"Resolution: {res_right[0]}x{res_right[1]}")
    
    def mouse_move_left(self, event):
        """
        Updates the coordinates label for the left image as the mouse moves.

        :param event: Tkinter event.
        """
        x, y = event.x, event.y
        self.lbl_coords_left.config(text=f"x: {x}, y: {y}")
    
    def mouse_move_right(self, event):
        """
        Updates the coordinates label for the right image as the mouse moves.

        :param event: Tkinter event.
        """
        x, y = event.x, event.y
        self.lbl_coords_right.config(text=f"x: {x}, y: {y}")
    
    def select_images(self):
        """
        Opens a file dialog for the user to select two images.
        """
        file_paths = filedialog.askopenfilenames(
            title="Select Two Images",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")],
            initialdir="."
        )
        if file_paths:
            if len(file_paths) != 2:
                messagebox.showwarning("Selection Error", "Please select exactly two images.")
                return
            # Invoke the callback with the selected file paths
            self.on_select_callback(file_paths)
