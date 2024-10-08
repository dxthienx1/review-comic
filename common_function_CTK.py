from tkinter import messagebox, filedialog
import customtkinter as ctk
import ctypes
import os

padx = 5
pady = 2
height_element = 40
width_window = 500
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
left = 0.3
right = 0.7
LEFT = 'left'
RIGHT = 'right'
CENTER = 'center'


def choose_folder():
    folder_path = filedialog.askdirectory()
    return folder_path

def choose_file():
    file_path = filedialog.askopenfilename( title="Select a file", filetypes=(("All files", "*.*"),) )
    return file_path

def message_aks(message):
    messagebox.askquestion(title="Question", message=message)
def warning_message(message):
    messagebox.showinfo(title="WARNING", message=message)
def notification(parent=None, message=""):
    if parent:
        parent.after(0, lambda: messagebox.showinfo(title="Notification", message=message))
    else:
        messagebox.showinfo(title="Notification", message=message)

def error_message(message):
    messagebox.showinfo(title="ERROR", message=message)

def clear_widgets(root):
    for widget in root.winfo_children():
        widget.pack_forget()

def create_button_icon(frame = None, command=None, image=None, side=None, width=60):
    button = ctk.CTkButton( master=frame, text="", command=command, image=image, width=width)
    if side:
        button.pack(side=side, padx=0, pady=0)
    else:    
        button.pack(padx=0, pady=0)
    return button

def create_button(frame = None, text="", command=None, width=width_window, compound="left", anchor="center", image=None, side=None, pady=pady, padx=padx):
    button = ctk.CTkButton(master=frame, text=text, command=command, image=image, width=width, height= height_element, compound=compound, anchor=anchor, )
    if side:
        button.pack(side=side, pady=pady, padx=padx)
    else:    
        button.pack(pady=pady, padx=padx)
    return button

def create_label(frame=None, text="", compound="center", anchor="w", width=width_window, height=height_element, wraplength=None, side=None):
    if not width:
        width = width
    wraplength = width - 20
    label = ctk.CTkLabel(master=frame, text=text, width=width, height= height_element, wraplength=wraplength, anchor=anchor, compound=compound)
    if side:
        label.pack(side=side, pady=pady, padx=padx)
    else:
        label.pack(pady=pady, padx=padx)
    return label

def create_frame(frame, fill='x', side=None):
    frame = ctk.CTkFrame(master=frame, height=height_element*0.9)
    frame.pack(padx=padx, pady=pady, fill=fill, side=side)
    return frame

def create_text_input(frame, width=width_window, placeholder=None, side="right", default="", is_password=False):
    if not width:
        width = width
    if is_password:
        text_input = ctk.CTkEntry(master=frame, width=width, height=height_element*0.8, placeholder_text=placeholder, textvariable=default, show="*")
    else:
        text_input = ctk.CTkEntry(master=frame, width=width, height=height_element*0.8, placeholder_text=placeholder, textvariable=default)
    text_input.pack(pady=pady, padx=padx, side=side)
    return text_input

def create_combobox(frame, values=None, variable=None, side=RIGHT, width=width_window, height=height_element):
    val=None
    if variable:
        val = ctk.StringVar(value=str(variable))

    combobox = ctk.CTkComboBox(master=frame, values=values, variable=val, width=width, height=height)
    combobox.pack(side=side, padx=padx, pady=pady)
    return combobox

def create_frame_label_and_progress_bar(frame, label_text="", width=width_window, left=left, right=right):
    label = create_label(frame=frame, text=label_text, side=LEFT, width=width*left, compound=LEFT)
    processbar = create_progress_bar(frame=frame, width=width*right, side=RIGHT)
    return frame, processbar

def create_progress_bar(frame=None, width=width_window):
    processbar = ctk.CTkProgressBar(master=frame, width=width)
    processbar.pack(padx=padx, pady=pady)
    return processbar

def create_frame_label_input_input(root, label_text="", place_holder1=None, place_holder2=None, width=width_window, left=0.25, mid=0.56, right=0.19):
    frame = create_frame(root)
    label = create_label(frame=frame, text=label_text, side=LEFT, width=width*left, compound=LEFT, anchor='w')
    entry1 = create_text_input(frame=frame, width=width*mid, placeholder=place_holder1, side=RIGHT)
    entry2 = create_text_input(frame=frame, width=width*right, placeholder=place_holder2)
    return entry1, entry2

def create_frame_label_and_input(root, label_text="", place_holder=None, width=width_window, left=left, right=right, is_password=False):
    frame = create_frame(root)
    label = create_label(frame=frame, text=label_text, side=LEFT, width=width*left, compound=LEFT, anchor='w')
    entry = create_text_input(frame=frame, width=width*right, placeholder=place_holder, is_password=is_password)

    return entry

def create_frame_button_input_input(root,text, width=width_window, place_holder1=None, place_holder2=None, command=None, left=0.25, mid=0.56, right=0.19):
    frame = create_frame(root)
    button = create_button(frame=frame, text=text, width=width*left, side=LEFT, command=command)
    entry1 = create_text_input(frame, width=width*mid, placeholder=place_holder1, side=RIGHT)
    entry2 = create_text_input(frame, width=width*right, placeholder=place_holder2)
    return entry1, entry2

def create_frame_button_and_input(root, text, width=width_window, place_holder=None, command=None, left=left, right=right):
    frame = create_frame(root)
    button = create_button(frame=frame, text=text, width=width*left, side=LEFT, command=command)
    entry = create_text_input(frame, width=width*right, placeholder=place_holder)
    return entry

def create_frame_button_and_combobox(root, text, command=None, width=width_window, values=None, variable=None, left=left, right=right):
    frame = create_frame(root)
    button = create_button(frame=frame, text=text, width=width*left, side=LEFT, command=command)
    combobox = create_combobox(frame, width=width*right, side=RIGHT, values=values, variable=variable)
    return combobox

def create_frame_button_and_button(root, text1, text2, command1=None, command2=None, width=width_window, left=left, right=right):
    frame = create_frame(root)
    button1 = create_button(frame=frame, text=text1, width=width*left , side=LEFT, command=command1)
    button2 = create_button(frame=frame, text=text2, width=width*right -15, side=RIGHT, command=command2)
    return button1, button2


