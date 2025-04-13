from tkinter import Label
from PIL import Image
import urllib.request
import io

class Watermark:
    def __init__(self, img_frame, watermark_img_path='', watermark_text='', font='', scale=1, color=(0,0,0,0)):
        self.pos = (0,0)
        self.label = Label(img_frame, text='Hi')
        #Image variable
        self.img_path = watermark_img_path
        #Text watermark variables
        self.text = watermark_text
        self.font = font
        self.color = color
        self.scale = scale

    def get_image(self, img_path=None):
        if img_path is None:
            img_path = self.img_path
        print(img_path)
        if img_path.startswith(('http://', 'https://')):
            try:
                with urllib.request.urlopen(img_path) as file:
                    img = Image.open(io.BytesIO(file.read()))
                    return img
                    # Keep a reference
            except Exception as e:
                print("Error loading link:", e)
        else:
            try:
                img = Image.open(img_path)
                return img
            except Exception as e:
                print("Error loading image:", e)