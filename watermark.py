from tkinter import Label
from PIL import Image
import urllib.request
import io

class Watermark:
    def __init__(self, img_frame, watermark_img_path='', watermark_text=''):
        self.label = Label(img_frame, text='Hi')
        self.pos = (0,0)
        self.img_path = watermark_img_path
        self.text = watermark_text

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