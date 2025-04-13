from tkinter.filedialog import askopenfile, asksaveasfilename
from tkinter.ttk import Combobox
from tkinter.colorchooser import askcolor
from PIL import ImageFont, ImageDraw
from tkinterdnd2 import TkinterDnD, DND_ALL
from active_img import *
from watermark import Watermark
import datetime as dt
from matplotlib import font_manager
import sys

if sys.version_info.major == 3:
    import tkinter as tk, tkinter.font as tk_font
else:
    import Tkinter as tk, tkFont as tk_font

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
    watermark_txt_entry.delete(0, END)
    on_focus_out(event=None, entry=watermark_txt_entry, text='Type Text here...')
    watermark.text = ''
    img_path = askopenfile()
    watermark.img_path = img_path.name if img_path is not None else ''
    img_watermark_entry.delete(0, END)
    img_watermark_entry.insert("end", watermark.img_path)

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
def get_semi_transparent_watermark(transparency):
    global watermark
    watermark_img = watermark.get_image().convert("RGBA")
    r, g, b, a = watermark_img.split()
    new_alpha = a.point(lambda p: int(p * (transparency / 255)))
    watermark_img.putalpha(new_alpha)
    return watermark_img

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
    img_watermark_entry.delete(0, END)
    on_focus_out(event=None, entry=img_watermark_entry, text='Drop Watermark here...')
    watermark.img_path = ''
    text = watermark_txt_entry.get()
    if text_repeat.get() == 1:
        for n in range(333):
            print(n)
            text += f" {watermark_txt_entry.get()}"
            if n%11 == 0:
                text += "\n"
    watermark.text = text
    watermark.label.config(text=watermark.text)

    img_width, img_height = active_img.get_image().size
    center_x = img_width // 2
    center_y = img_height // 2

    dummy_event = type("DummyEvent", (), {})()
    dummy_event.x = center_x
    dummy_event.y = center_y

    move_watermark(dummy_event)

def update_opacity(new_op):
    watermark.opacity = int(new_op)
    watermark.color = (watermark.color[0], watermark.color[1], watermark.color[2], watermark.opacity)

    dummy_event = type("DummyEvent", (), {})()
    dummy_event.x = watermark.pos[0]
    dummy_event.y = watermark.pos[1]

    move_watermark(dummy_event)

def update_scale():
    watermark.scale = float(wm_img_scale_box.get())

    dummy_event = type("DummyEvent", (), {})()
    dummy_event.x = watermark.pos[0]
    dummy_event.y = watermark.pos[1]

    move_watermark(dummy_event)

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
        orig_font_size = int(font_size_box.get())
        try:
            font_family = font_type_box.get()
            font_path = font_manager.findfont(font_family)
            font = ImageFont.truetype(font_path, orig_font_size)
        except Exception as e:
            print("Text couldn't load for error: ", e)
            font = ImageFont.load_default(size=orig_font_size)
        draw.text(watermark.pos, watermark.text, font=font, fill=watermark.color, anchor="mm")
        composite = Image.alpha_composite(img, overlay)
        active_img.show(composite)
    elif watermark.img_path != '' and watermark.img_path is not None:
        image_to_edit = active_img.get_image()
        img = image_to_edit
        foreground = get_semi_transparent_watermark(transparency=watermark.opacity)
        foreground = foreground.resize(size=(int(foreground.size[0] * watermark.scale), int(foreground.size[1] * watermark.scale)))
        watermark.pos = (event.x, event.y)
        wm_width, wm_height = foreground.size
        pos = (int(event.x - wm_width//2), int(event.y - wm_height//2))
        image_to_edit.paste(foreground, pos, mask=foreground)
        ImageDraw.Draw(img)
        active_img.show(img)

#Formats and upscales the image and watermark to the final product before saving
def format_image_to_save(_img, _watermark):
    original_img = active_img.original_img.convert("RGBA")
    orig_width, orig_height = original_img.size

    # This is the resized preview image
    disp_img = _img
    disp_width, disp_height = disp_img.size

    scale_x = orig_width / disp_width
    scale_y = orig_height / disp_height

    upscaled_pos: tuple = int(_watermark.pos[0] * scale_x), int(_watermark.pos[1] * scale_y)
    overlay = Image.new("RGBA", (orig_width, orig_height), (255, 255, 255, 0))
    if _watermark.img_path != '' and _watermark.img_path is not None:
        _watermark = get_semi_transparent_watermark(transparency=watermark.opacity)
        wm_width, wm_height = _watermark.size
        new_wm_width = int(wm_width * scale_x * watermark.scale)
        new_wm_height = int(wm_height * scale_y * watermark.scale)
        _watermark = _watermark.resize((new_wm_width, new_wm_height), Image.LANCZOS)
        # Create a composite image
        centered_pos = (upscaled_pos[0] - new_wm_width // 2, upscaled_pos[1] - new_wm_height // 2)
        overlay.paste(_watermark, centered_pos, mask=_watermark)
    elif _watermark.text != '':
        draw = ImageDraw.Draw(overlay)
        orig_font_size = int(int(font_size_box.get()) * scale_y)
        try:
            font_family = font_type_box.get()
            font_path = font_manager.findfont(font_family)
            font = ImageFont.truetype(font_path, orig_font_size)
        except Exception as e:
            print("Text couldn't load for error: ", e)
            font = ImageFont.load_default(size=orig_font_size)
        # Create a composite image
        draw.text(upscaled_pos, _watermark.text, font=font, fill=watermark.color, anchor="mm")

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

#--------------------------UI----------------------------

#Window initial config------------------------------------
window = TkinterDnD.Tk()
window.minsize(IMG_FRAME_WIDTH+200, IMG_FRAME_HEIGHT+130)
window.title("Image Watermarker")
window.config(padx=30, pady=24, bg=BACKGROUND_COLOR)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
window.resizable(False, False)

# Central frame------------------------------
img_frame = Frame(window, width=IMG_FRAME_WIDTH, height=IMG_FRAME_HEIGHT, bg=FRAME_BG_COLOR)
img_frame.grid(column=1, columnspan=9, row=0)
img_frame.grid_propagate(False)  # Prevent resizing

#Init of image instance in frame (a placeholder image is loaded first)------------------------------
active_img = ActiveImg(frame_width=IMG_FRAME_WIDTH, frame_height=IMG_FRAME_HEIGHT, bg_color=FRAME_BG_COLOR,
                       frame=img_frame)

options_spacer = Label(window, width=24, background=BACKGROUND_COLOR)
options_spacer.grid(column=0, row=1, columnspan=9)

#Entries placeholders
def on_entry_click(event, entry, text):
    if entry.get() == text:
        entry.delete(0, tk.END)
        entry.config(foreground="black")

def on_focus_out(event, entry, text):
    if entry.get() == "":
        entry.insert(0, text)
        entry.config(foreground="gray")

#Entry widget that allows to drag and drop--------------------------
path_entry_label = Label(window, text='Insert Image:', justify=LEFT, background=BACKGROUND_COLOR)
path_entry_label.grid(column=1, row=2, sticky=W)

path_entry = Entry(window, width=38, justify=LEFT, foreground="gray")
path_entry.grid(column=1, row=3)
path_entry.insert(END, 'Drop Image here...')
path_entry.bind("<FocusIn>", lambda event: on_entry_click(event, path_entry, 'Drop Image here...'))
path_entry.bind("<FocusOut>", lambda event: on_focus_out(event, path_entry, 'Drop Image here...'))
path_entry.drop_target_register(DND_ALL)
path_entry.dnd_bind("<<Drop>>", drop_img_inside_entry)

#Button to open file explorer
get_img_path_button = Button(text='...', command=get_img_path, anchor='w')
get_img_path_button.grid(column=2, row=3)

#Loads image from the inserted path
open_img_button = Button(text='Open', command=active_img.show, anchor='w')
open_img_button.grid(column=3, row=3)

#Spacer I had to add to push the path entry and its buttons on the left side-----------------------------------
spacer = Label(window, width=21, text='\n\n\n\n\n\n', background=BACKGROUND_COLOR)
spacer.grid(column=4, row=1,rowspan=5)

#Watermark section---------------------------
# Watermark
watermark = Watermark(img_frame)

#Slider to control opacity of both text and image watermarks
opacity_spacer = Label(window, text='\n', width=12, background=BACKGROUND_COLOR)
opacity_spacer.grid(column=0, row=0)
opacity_slider = Scale(window, from_=0, to=255, command=update_opacity, background=BACKGROUND_COLOR, length=300, label='Opacity', bd=1, sliderrelief='ridge', highlightthickness=0)
opacity_slider.set(128)
opacity_slider.grid(column=10, row=0)

#Image
wm_entry_label = Label(window, text='Insert Watermark:', justify=LEFT, background=BACKGROUND_COLOR)
wm_entry_label.grid(column=5, row=2, sticky=W)

img_watermark_entry = Entry(window, width=38, foreground='gray')
img_watermark_entry.grid(column=5, row=3, columnspan=2)
img_watermark_entry.insert(END, 'Drop Watermark here...')
img_watermark_entry.bind("<FocusIn>", lambda event: on_entry_click(event, img_watermark_entry, 'Drop Watermark here...'))
img_watermark_entry.bind("<FocusOut>", lambda event: on_focus_out(event, img_watermark_entry, 'Drop Watermark here...'))
img_watermark_entry.drop_target_register(DND_ALL)
img_watermark_entry.dnd_bind("<<Drop>>", drop_watermark_inside_entry)

get_watermark_path_button = Button(text='...', command=get_watermarker_path)
get_watermark_path_button.grid(column=7, row=3)

open_img_watermark = Button(text='Open', command=load_watermark_img, width=6)
open_img_watermark.grid(column=9, row=3)

wm_scale_label = Label(window, text='Scale:', justify=LEFT, background=BACKGROUND_COLOR)
wm_scale_label.grid(column=8, row=2, sticky=W)

wm_img_scale_box = Spinbox(window, from_=0.01, to=10, increment=.05, width=4, command=update_scale)
wm_img_scale_box.delete(0, END)
wm_img_scale_box.insert(END, '1.0')
wm_img_scale_box.grid(column=8, row=3)

#Text
wm_text_label = Label(window, text='Type Text as Watermark:', justify=LEFT, background=BACKGROUND_COLOR)
wm_text_label.grid(column=5, row=4, sticky=W)

watermark_txt_entry = Entry(window, width=38, foreground='gray')
watermark_txt_entry.grid(column=5, row=5, columnspan=2)
watermark_txt_entry.insert(END, 'Type Text here...')
watermark_txt_entry.bind("<FocusIn>", lambda event: on_entry_click(event, watermark_txt_entry, 'Type Text here...'))
watermark_txt_entry.bind("<FocusOut>", lambda event: on_focus_out(event, watermark_txt_entry, 'Type Text here...'))

confirm_txt_watermark = Button(text='Confirm', height=2, command=load_watermark_text)
confirm_txt_watermark.grid(column=9, row=5, rowspan=2)

#Text options
def load_working_fonts():
    fonts = []
    for font in tk_font.families():
        try:
            font_path = font_manager.findfont(font, fallback_to_default=False)
            if font_path:
                print(font_path)
                fonts.append(font)
        except Exception as e:
            print("Couldn't load font due to error: ", e)
    return fonts

font_type_box = Combobox(window, values=load_working_fonts(), width=30)
font_type_box.insert("end", 'Arial')
font_type_box.config(state="readonly")
font_type_box.grid(column=5, row=6)

font_size_box = Spinbox(window, from_=2, to=999, width=3)
font_size_box.delete(0, END)
font_size_box.insert("end", '60')
font_size_box.grid(column=6, row=6)

def load_color():
    color = askcolor()
    if color:
        watermark.color = (color[0][0], color[0][1], color[0][2], 128)
        wm_color_choice_button.config(background=color[1])

wm_color_choice_button = Button(command=load_color, text='Color', background='#fff', width=6)
wm_color_choice_button.grid(column=7, row=6, columnspan=2)

#Multiplies the text if checked to cover the whole screen
text_repeat = IntVar()
check_repeat = Checkbutton(window, background=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, variable=text_repeat, text='Repeat')
check_repeat.grid(column=7, row=5, columnspan=2)

#Keeps track of mouse pos when pressing lmb (used for the drag and drop function for the watermark)
active_img.img_label.bind("<B1-Motion>", move_watermark)

#Save---------------------

save_spacer = Label(window, width=24, background=BACKGROUND_COLOR)
save_spacer.grid(column=1, row=7, columnspan=9)

save_button = Button(text='Save', command=save_watermark, width=10)
save_button.grid(column=1, row=8, columnspan=9)

window.mainloop()