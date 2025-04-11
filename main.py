from tkinter.filedialog import askopenfile
from PIL.ImageDraw import ImageDraw
from tkinterdnd2 import TkinterDnD, DND_ALL
from active_img import *

BACKGROUND_COLOR = '#FFFDD0'
FRAME_BG_COLOR = '#090909'
IMG_FRAME_WIDTH = 800
IMG_FRAME_HEIGHT = 526

def get_img_path():
    img_path = askopenfile().name
    path_entry.delete(0, END)
    path_entry.insert(0, img_path)
    active_img.img_path = img_path
    active_img.show()

def drop_inside_entry(event):
    path_entry.delete(0, END)
    print(event.data.strip().strip('{').strip('}'))
    path_entry.insert("end", event.data.strip().strip('{').strip('}'))
    active_img.img_path = path_entry.get()
    active_img.show()

img = None

def show_txt_watermark(event):
    global img
    if watermark_txt_entry.get() != '':
        image_to_edit = active_img.get_image()
        img = image_to_edit
        foreground = Image.open("./kyaruCry.jpg")
        image_to_edit.paste(foreground, (event.x, event.y))
        edit_img = ImageDraw(img)
        edit_img.text((event.x, event.y), watermark_txt_entry.get())
        active_img.show(img)

def save_watermark(event):
    img.save('./new_img.jpg')
# def move(event):
#     print(event.x, event.y)

#--------------------------UI----------------------------
#Window initial config
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

#Init of image instance in frame (a placeholder image is loaded first)
active_img = ActiveImg(frame_width=IMG_FRAME_WIDTH, frame_height=IMG_FRAME_HEIGHT, bg_color=FRAME_BG_COLOR, frame=img_frame)

#Entry widget that allows to drag and drop
path_entry = Entry(window)
path_entry.grid(column=0, row=1)
path_entry.drop_target_register(DND_ALL)
path_entry.dnd_bind("<<Drop>>", drop_inside_entry)

#Button to open file explorer
get_img_path_button = Button(text='...', command=get_img_path)
get_img_path_button.grid(column=1, row=1)

#Loads image from the inserted path
open_img_button = Button(text='Open', command=active_img.show)
open_img_button.grid(column=2, row=1)

#Watermark section
watermark_txt_entry = Entry(window)
watermark_txt_entry.grid(column=4, row=1)

#Keeps track of mouse pos when pressing lmb (used for the drag and drop function for the watermark)
watermark_label = Label(img_frame, text='Hi')
active_img.img_label.bind("<B1-Motion>", show_txt_watermark)
window.bind("<Return>", save_watermark)

confirm_txt_watermark = Button(text='Confirm', command=show_txt_watermark)
confirm_txt_watermark.grid(column=5, row=1)

window.mainloop()