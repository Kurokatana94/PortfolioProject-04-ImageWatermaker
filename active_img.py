from tkinter import *
from PIL import ImageTk, Image
import urllib.request
import io, sys, os

#Function to get absolute path of the placeholder image from the system
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def resize_image_to_frame(img, frame_width, frame_height, bg_color):
    img_ratio = img.width / img.height
    frame_ratio = frame_width / frame_height

    if frame_ratio > img_ratio:
        # Fit height
        new_height = frame_height
        new_width = int(img_ratio * new_height)
    else:
        # Fit width
        new_width = frame_width
        new_height = int(new_width / img_ratio)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

    # Create background image and paste resized image centered
    final_img = Image.new("RGBA", (frame_width, frame_height), (9,9,9,0))
    paste_x = (frame_width - new_width) // 2
    paste_y = (frame_height - new_height) // 2
    final_img.paste(resized_img, (paste_x, paste_y))
    return final_img


class ActiveImg:
    def __init__(self, frame_width, frame_height, bg_color, frame, img_path=None):
        self._FRAME_WIDTH = frame_width
        self._FRAME_HEIGHT = frame_height
        self._BG_COLOR = bg_color
        self.img_path = resource_path(os.path.join("docs", "nwero_likey.jpg"))
        self.img_frame = frame
        self.img = None
        self.img_label = None
        self.original_img = None
        self.img_init()

    def img_init(self):
        placeholder_img = Image.open(self.img_path)
        self.original_img = placeholder_img
        placeholder_resized = resize_image_to_frame(placeholder_img, self._FRAME_WIDTH, self._FRAME_HEIGHT,
                                                         self._BG_COLOR)
        self.img = ImageTk.PhotoImage(placeholder_resized)
        self.img_label = Label(self.img_frame, image=self.img, bg=self._BG_COLOR)
        self.img_label.image = self.img  # Keep reference
        self.img_label.grid()

    def get_image(self, img_path=None):
        if img_path is None:
            img_path = self.img_path
        print(img_path)
        if img_path.startswith(('http://', 'https://')):
            try:
                with urllib.request.urlopen(img_path) as file:
                    raw_img = Image.open(io.BytesIO(file.read()))
                    self.original_img = raw_img
                    final_img = resize_image_to_frame(raw_img, self._FRAME_WIDTH, self._FRAME_HEIGHT, self._BG_COLOR)
                    return final_img
                    # Keep a reference
            except Exception as e:
                print("Error loading link:", e)
        else:
            try:
                raw_img = Image.open(img_path)
                self.original_img = raw_img
                final_img = resize_image_to_frame(raw_img, self._FRAME_WIDTH, self._FRAME_HEIGHT, self._BG_COLOR)
                return final_img
            except Exception as e:
                print("Error loading image:", e)

    def show(self, img=None):
        if img is None:
            img = self.get_image()
        tk_img = ImageTk.PhotoImage(img)
        self.img_label.config(image=tk_img)
        self.img_label.image = tk_img