from tkinter import *
from tkinter.filedialog import askopenfile
from PIL import ImageTk, Image
import urllib.request
import io

from PIL.ImageDraw import ImageDraw
from tkinterdnd2 import TkinterDnD, DND_ALL

BACKGROUND_COLOR = '#FFFDD0'
FRAME_BG_COLOR = '#090909'
IMG_FRAME_WIDTH = 800
IMG_FRAME_HEIGHT = 526

def resize_image_to_frame(img, frame_width, frame_height, bg_color=FRAME_BG_COLOR):
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
    final_img = Image.new("RGB", (frame_width, frame_height), bg_color)
    paste_x = (frame_width - new_width) // 2
    paste_y = (frame_height - new_height) // 2
    final_img.paste(resized_img, (paste_x, paste_y))
    return final_img

def get_image():
    img_path = path_entry.get()
    print(img_path)
    if img_path.startswith(('http://', 'https://')):
        try:
            with urllib.request.urlopen(img_path) as file:
                raw_img = Image.open(io.BytesIO(file.read()))
                final_img = resize_image_to_frame(raw_img, IMG_FRAME_WIDTH, IMG_FRAME_HEIGHT)
                return final_img
                # Keep a reference
        except Exception as e:
            print("Error loading link:", e)
    else:
        try:
            raw_img = Image.open(img_path)
            final_img = resize_image_to_frame(raw_img, IMG_FRAME_WIDTH, IMG_FRAME_HEIGHT)
            return final_img
        except Exception as e:
            print("Error loading image:", e)

def show(img):
    tk_img = ImageTk.PhotoImage(img)
    img_label.config(image=tk_img)
    img_label.image = tk_img

def get_img_path():
    img_path = askopenfile().name
    path_entry.delete(0, END)
    path_entry.insert(0, img_path)
    show(get_image())

def drop_inside_entry(event):
    path_entry.delete(0, END)
    print(event.data.strip().strip('{').strip('}'))
    path_entry.insert("end", event.data.strip().strip('{').strip('}'))
    show(get_image())

def show_txt_watermark():
    if watermark_txt_entry.get() != '':
        image_to_edit = get_image()
        edit_img = ImageDraw(image_to_edit)
        edit_img.text((image_to_edit.width/2, image_to_edit.height/2), watermark_txt_entry.get())
        show(image_to_edit)

#--------------------------UI----------------------------

window = TkinterDnD.Tk()
window.minsize(IMG_FRAME_WIDTH+200, IMG_FRAME_HEIGHT+130)
window.title("Image Watermarker")
window.config(padx=100, pady=50, bg=BACKGROUND_COLOR)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# No need for canvas if we're using a frame
img_frame = Frame(window, width=IMG_FRAME_WIDTH, height=IMG_FRAME_HEIGHT, bg=FRAME_BG_COLOR)
img_frame.grid(column=0, columnspan=10, row=0)
img_frame.grid_propagate(False)  # Prevent resizing

# Load initial image
placeholder_img = Image.open("./NeuroAssertsDominance.png")
placeholder_resized = resize_image_to_frame(placeholder_img, IMG_FRAME_WIDTH, IMG_FRAME_HEIGHT)
img = ImageTk.PhotoImage(placeholder_resized)

img_label = Label(img_frame, image=img, bg=BACKGROUND_COLOR)
img_label.image = img  # Keep reference
img_label.grid()

path_entry = Entry(window)
path_entry.grid(column=0, row=1)
path_entry.drop_target_register(DND_ALL)
path_entry.dnd_bind("<<Drop>>", drop_inside_entry)

get_img_path_button = Button(text='...', command=get_img_path)
get_img_path_button.grid(column=1, row=1)

open_img_button = Button(text='Open', command= lambda : show(get_image()))
open_img_button.grid(column=2, row=1)

watermark_txt_entry = Entry(window)
watermark_txt_entry.grid(column=4, row=1)

confirm_txt_watermark = Button(text='confirm', command=show_txt_watermark)
confirm_txt_watermark.grid(column=5, row=1)

window.mainloop()