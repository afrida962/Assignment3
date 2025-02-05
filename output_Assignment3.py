import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class CustomImageEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Custom Image Editor")

        self.original_img = None
        self.edited_img = None
        self.tk_original_img = None
        self.tk_edited_img = None
        self.crop_rectangle = None
        self.crop_start_x = None
        self.crop_start_y = None
        self.undo_stack = []  # Stack to store previous states of the edited image

        # Create main frames
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(fill=tk.X)

        # Canvas for displaying images
        self.original_canvas = tk.Canvas(self.main_frame, width=400, height=400, cursor="cross")
        self.original_canvas.pack(side=tk.LEFT, padx=10, pady=10)

        self.edited_canvas = tk.Canvas(self.main_frame, width=400, height=400)
        self.edited_canvas.pack(side=tk.RIGHT, padx=10, pady=10)

        # Control buttons and scale
        self.load_btn = tk.Button(self.control_frame, text="Open Image", command=self.open_image, bg="red", fg="white")
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.crop_btn = tk.Button(self.control_frame, text="Crop", command=self.perform_crop, bg="blue", fg="white")
        self.crop_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.resize_label = tk.Label(self.control_frame, text="Resize (%)")
        self.resize_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.resize_scale = tk.Scale(self.control_frame, from_=10, to=200, orient=tk.HORIZONTAL, command=self.adjust_size)
        self.resize_scale.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_btn = tk.Button(self.control_frame, text="Save", command=self.save_image, bg="green", fg="white")
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.undo_btn = tk.Button(self.control_frame, text="Undo", command=self.undo, bg="orange", fg="white")
        self.undo_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.rotate_btn = tk.Button(self.control_frame, text="Rotate", command=self.rotate_image, bg="purple", fg="white")
        self.rotate_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.grayscale_btn = tk.Button(self.control_frame, text="Grayscale", command=self.convert_to_grayscale, bg="gray", fg="white")
        self.grayscale_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Bind mouse events for cropping
        self.original_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.original_canvas.bind("<B1-Motion>", self.update_crop)
        self.original_canvas.bind("<ButtonRelease-1>", self.finalize_crop)

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_img = cv2.imread(file_path)
            self.edited_img = self.original_img.copy()  # Initialize edited_img with the original image
            self.undo_stack = []  # Clear the undo stack when a new image is loaded
            self.show_image(self.original_img, self.original_canvas, "original")
            self.show_image(self.edited_img, self.edited_canvas, "edited")
            self.reset_cursor()  # Reset the cursor after loading a new image

    def show_image(self, image, canvas, canvas_type):
        if len(image.shape) == 2:  # Check if the image is grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)  # Convert grayscale to RGB for display
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(image)
        image.thumbnail((400, 400))  # Resize image to fit canvas

        if canvas_type == "original":
            self.tk_original_img = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_original_img)
        elif canvas_type == "edited":
            self.tk_edited_img = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_edited_img)

    def start_crop(self, event):
        self.crop_start_x = self.original_canvas.canvasx(event.x)
        self.crop_start_y = self.original_canvas.canvasy(event.y)

        if not self.crop_rectangle:
            self.crop_rectangle = self.original_canvas.create_rectangle(
                self.crop_start_x, self.crop_start_y, self.crop_start_x, self.crop_start_y, outline="red"
            )

    def update_crop(self, event):
        cur_x = self.original_canvas.canvasx(event.x)
        cur_y = self.original_canvas.canvasy(event.y)
        self.original_canvas.coords(self.crop_rectangle, self.crop_start_x, self.crop_start_y, cur_x, cur_y)

    def finalize_crop(self, event):
        end_x = self.original_canvas.canvasx(event.x)
        end_y = self.original_canvas.canvasy(event.y)

        if self.original_img is not None:
            # Get the dimensions of the displayed image
            img_width = self.tk_original_img.width()
            img_height = self.tk_original_img.height()

            # Calculate the scaling factors
            scale_x = self.original_img.shape[1] / img_width
            scale_y = self.original_img.shape[0] / img_height

            # Map the canvas coordinates to image coordinates
            x1 = int(self.crop_start_x * scale_x)
            y1 = int(self.crop_start_y * scale_y)
            x2 = int(end_x * scale_x)
            y2 = int(end_y * scale_y)

            # Ensure the coordinates are within the image bounds
            x1 = max(0, min(x1, self.original_img.shape[1]))
            y1 = max(0, min(y1, self.original_img.shape[0]))
            x2 = max(0, min(x2, self.original_img.shape[1]))
            y2 = max(0, min(y2, self.original_img.shape[0]))

            # Push the current state to the undo stack
            self.undo_stack.append(self.edited_img.copy())

            # Crop the image
            self.edited_img = self.original_img[y1:y2, x1:x2]
            self.show_image(self.edited_img, self.edited_canvas, "edited")

    def perform_crop(self):
        # This method is now handled by mouse events
        pass

    def adjust_size(self, value):
        if self.edited_img is not None:
            scale_factor = int(value) / 100
            width = int(self.edited_img.shape[1] * scale_factor)
            height = int(self.edited_img.shape[0] * scale_factor)
            resized_img = cv2.resize(self.edited_img, (width, height))
            self.show_image(resized_img, self.edited_canvas, "edited")

    def save_image(self):
        if self.edited_img is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            if file_path:
                cv2.imwrite(file_path, self.edited_img)

    def undo(self):
        if self.undo_stack:
            # Pop the last state from the stack
            self.edited_img = self.undo_stack.pop()
            self.show_image(self.edited_img, self.edited_canvas, "edited")

    def reset_cursor(self):
        # Reset the cursor to "cross" after loading a new image
        self.original_canvas.config(cursor="cross")

    def rotate_image(self):
        if self.edited_img is not None:
            self.undo_stack.append(self.edited_img.copy())  # Save state for undo
            self.edited_img = cv2.rotate(self.edited_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.show_image(self.edited_img, self.edited_canvas, "edited")

    def convert_to_grayscale(self):
        if self.edited_img is not None:
            self.undo_stack.append(self.edited_img.copy())  # Save state for undo
            self.edited_img = cv2.cvtColor(self.edited_img, cv2.COLOR_BGR2GRAY)
            self.show_image(self.edited_img, self.edited_canvas, "edited")

if __name__ == "__main__":
    root = tk.Tk()
    editor = CustomImageEditor(root)
    root.mainloop()