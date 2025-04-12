from tkinter.filedialog import askopenfile, asksaveasfilename
from PIL import ImageFont, ImageDraw
from tkinterdnd2 import TkinterDnD, DND_ALL
from active_img import *
from watermark import Watermark
import datetime as dt

BACKGROUND_COLOR = '#FFFDD0'
FRAME_BG_COLOR = '#090909'
IMG_FRAME_WIDTH = 800
IMG_FRAME_HEIGHT = 526

img = None
active_img = None
watermark = None

def get_img_path():
    global active_img
    img_path = askopenfile().name
    path_entry.delete(0, END)
    path_entry.insert(0, img_path)
    active_img.img_path = img_path
    active_img.show()

def get_watermarker_path():
    global watermark
    watermark.text = ''
    watermark_txt_entry.delete(0, END)
    watermark.img_path = askopenfile().name
    img_path = watermark.img_path
    img_watermark_entry.delete(0, END)
    img_watermark_entry.insert("end", img_path)

#Takes care of the drop in the main image entry loading the image in the frame
def drop_img_inside_entry(event):
    path_entry.delete(0, END)
    print(event.data.strip().strip('{').strip('}'))
    path_entry.insert("end", event.data.strip().strip('{').strip('}'))
    active_img.img_path = path_entry.get()
    active_img.show()

#Works in the same way as the main image but for the watermark (image)
def drop_watermark_inside_entry(event):
    global watermark
    watermark_txt_entry.delete(0, END)
    watermark.text = ''
    img_watermark_entry.delete(0, END)
    img_watermark_entry.insert("end", event.data.strip().strip('{').strip('}'))
    watermark.img_path = img_watermark_entry.get()

#Lower the image opacity to makes it semi-transparent
def get_semi_transparent_watermark(transparency=128):
    global watermark
    watermark_img = watermark.get_image().convert("RGBA")
    r, g, b, a = watermark_img.split()
    new_alpha = a.point(lambda p: int(p * (transparency / 255)))
    watermark_img.putalpha(new_alpha)
    return watermark_img

#Moves the watermarker around on the image
def move_watermark(event):
    global img
    global watermark
    if watermark.text != '':
        image_to_edit = active_img.get_image()
        img = image_to_edit
        watermark.pos = (event.x, event.y)
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        orig_font_size = 60
        try:
            font = ImageFont.truetype("arial.ttf", orig_font_size)
        except Exception as e:
            print("Text couldn't load for error: ", e)
            font = ImageFont.load_default()
        draw.text(watermark.pos, watermark.text, font=font, fill=(255, 255, 255, 128), anchor="mm")
        composite = Image.alpha_composite(img, overlay)
        active_img.show(composite)
    elif watermark.img_path != '':
        image_to_edit = active_img.get_image()
        img = image_to_edit
        foreground = get_semi_transparent_watermark(transparency=128)
        watermark.pos = (event.x, event.y)
        wm_width, wm_height = foreground.size
        pos = (event.x - wm_width//2, event.y - wm_height//2)
        image_to_edit.paste(foreground, pos, mask=foreground)
        ImageDraw.Draw(img)
        active_img.show(img)

#They both load watermarker on screen
def load_watermark_img():
    global active_img
    global watermark

    watermark.img_path = img_watermark_entry.get()

    img_width, img_height = active_img.get_image().size
    center_x = img_width // 2
    center_y = img_height // 2

    dummy_event = type("DummyEvent", (), {})()
    dummy_event.x = center_x
    dummy_event.y = center_y

    move_watermark(dummy_event)

def load_watermark_text():
    global watermark
    watermark.img_path = ''
    img_watermark_entry.delete(0, END)
    watermark.text = watermark_txt_entry.get()
    watermark.label.config(text=watermark.text)

    img_width, img_height = active_img.get_image().size
    center_x = img_width // 2
    center_y = img_height // 2

    dummy_event = type("DummyEvent", (), {})()
    dummy_event.x = center_x
    dummy_event.y = center_y

    move_watermark(dummy_event)

def format_image_to_save(_img, _watermark):
    original_img = active_img.original_img.convert("RGBA")
    orig_width, orig_height = original_img.size

    # This is the resized preview image
    disp_img = _img
    disp_width, disp_height = disp_img.size

    scale_x = orig_width / disp_width
    scale_y = orig_height / disp_height

    upscaled_pos: tuple = int(_watermark.pos[0] * scale_x), int(_watermark.pos[1] * scale_y)

    _watermark = get_semi_transparent_watermark(transparency=200)
    wm_width, wm_height = _watermark.size
    new_wm_width = int(wm_width * scale_x)
    new_wm_height = int(wm_height * scale_y)
    _watermark = _watermark.resize((new_wm_width, new_wm_height), Image.LANCZOS)

    # Create a composite image
    overlay = Image.new("RGBA", (orig_width, orig_height), (255, 255, 255, 0))
    overlay.paste(_watermark, upscaled_pos, mask=_watermark)
    ImageDraw.Draw(overlay)

    return Image.alpha_composite(original_img, overlay)

def save_watermark():
    global img
    global watermark
    final_image = format_image_to_save(img, watermark)
    original_img = active_img.original_img.convert("RGBA")

    if img is None:
        img = original_img
    file = asksaveasfilename(initialfile=f"{dt.datetime.today().strftime('%Y%m%d_%H%M%S_%f')}.png",
                            defaultextension=".jpg",
                         filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
    final_image.save(file)
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
img_frame.grid(column=0, columnspan=6, row=0)
img_frame.grid_propagate(False)  # Prevent resizing

#Init of image instance in frame (a placeholder image is loaded first)
active_img = ActiveImg(frame_width=IMG_FRAME_WIDTH, frame_height=IMG_FRAME_HEIGHT, bg_color=FRAME_BG_COLOR, frame=img_frame)

#Entry widget that allows to drag and drop
path_entry = Entry(window)
path_entry.grid(column=0, row=1)
path_entry.drop_target_register(DND_ALL)
path_entry.dnd_bind("<<Drop>>", drop_img_inside_entry)

#Button to open file explorer
get_img_path_button = Button(text='...', command=get_img_path)
get_img_path_button.grid(column=1, row=1)

#Loads image from the inserted path
open_img_button = Button(text='Open', command=active_img.show)
open_img_button.grid(column=2, row=1)

#Watermark section
#Text
watermark_txt_entry = Entry(window)
watermark_txt_entry.grid(column=3, row=1)
confirm_txt_watermark = Button(text='Confirm', command=load_watermark_text)
confirm_txt_watermark.grid(column=4, row=1, columnspan=2)

#Image
img_watermark_entry = Entry(window)
img_watermark_entry.grid(column=3, row=2)
img_watermark_entry.drop_target_register(DND_ALL)
img_watermark_entry.dnd_bind("<<Drop>>", drop_watermark_inside_entry)

get_watermark_path_button = Button(text='...', command=get_watermarker_path)
get_watermark_path_button.grid(column=4, row=2)

open_img_watermark = Button(text='Open', command=load_watermark_img)
open_img_watermark.grid(column=5, row=2)

#Keeps track of mouse pos when pressing lmb (used for the drag and drop function for the watermark)
watermark = Watermark(img_frame)
active_img.img_label.bind("<B1-Motion>", move_watermark)

save_button = Button(text='Save', command=save_watermark)
save_button.grid(column=6, row=0)

#TODO ADD FONT SIZE AND TYPE OPTIONS
#TODO ADD WATERMARK IMAGE SIZE SLIDER/MULTIPLIER/SIZE ENTRY
#TODO ADD OPACITY SLIDER (BASED ON 128 AS MID VALUE) GOES FROM 0 TO 1? MAYBE

window.mainloop()