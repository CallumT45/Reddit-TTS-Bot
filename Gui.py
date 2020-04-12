import queue
import threading
import tkinter.ttk as ttk
# from tkinter import *
from tkinter import filedialog, Label, Tk, Entry, Button, StringVar, HORIZONTAL

from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage

from Reddit_Video import Reddit_Video


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb   

def CreateLabel(row, col, h, w, rowspan, columnspan, bg, fg, **kwargs):
    """Fucntion to simplify and standardise creating labels for my grid system"""
    if "sticky" in kwargs:
        sk = kwargs["sticky"]
        label = Label(root, height = h, width=w, font = ('caviar dreams', 15), bg=bg, fg=fg)
        label.grid(sticky = sk, row=row, column= col, rowspan = rowspan, columnspan = columnspan)
    else:
        label = Label(root, height = h, width=w, bg = bg)
        label.grid(row=row, column= col, rowspan = rowspan, columnspan = columnspan)
    return label


def changePath():
    """Opens a dialog box and asks the user to select a folder, then converts the output to the correct format and updates the options"""
    global Path
    Path = r'.' + filedialog.askopenfilename(initialdir = './Images/clip_art').split("RedditVideo")[1]
    

def start_conv():
    global after_bar
    while True:
        q.get()
        URL=url.get().split('/')[3] 

        time_dict = {'< 5 mins' : 15, '< 10 mins' : 35, '> 10 mins' : 50}
        timing = time_dict[time_dropdown.get()]
        Reddit_Video(URL, timing, Path, "temp")
        progress['value'] = 100
        root.after_cancel(after_bar)

def update_bar(timing, x):
    """
    Every few seconds(value based on timing variable), update bar. Is an approximation, however once reddit function is done the progress bar will jump to finish.
    Therefore I need to overestimate how long it will take to make a video.
    """
    global after_bar
    x += 1
    progress['value'] = x
    after_bar = root.after(round(timing*0.5*1000), update_bar, timing, x)#timing is based on average time to run


def initialise():
    """
    Values are different here to better approximate progress bar total time.
    Place a value in the queue to let the while loop in start_conv progress, then start update bar function
    """
    time_dict = {'< 5 mins' : 20, '< 10 mins' : 25, '> 10 mins' : 40}
    timing = time_dict[time_dropdown.get()]
    q.put(450)
    update_bar(timing, 1)

Path = ''
q = queue.Queue()
t =  threading.Thread(target = start_conv, name = "thread", daemon = True)
t.start()


root = Tk()
root.title('Reddit to Video')
root.geometry("520x150")

Left = CreateLabel(0, 0, 20, 30, 2, 1, _from_rgb((51, 51, 51)), "black")

Right = CreateLabel(0, 1, 20, 50, 1, 2, _from_rgb((51, 51, 51)), "black")

Left.grid_propagate(False)
Right.grid_propagate(False)
#===============================================================>

label = Label(root, font = ('caviar dreams', 12, 'bold'), bg=_from_rgb((51, 51, 51)), fg='white')
label.config(text="Enter the Reddit Short URL")
label.grid(in_ = Right, row=0, columnspan=3)

InputStrings = StringVar()
url = Entry(root, textvariable=InputStrings, width = 40)
url.grid(in_ = Right, row=1, ipadx=20, pady = 5, ipady = 5, columnspan=3)


clip_art_button = Button(root, text='Change Thumbnail Art', font=("Ariel", 9, "bold"),  command=changePath)
clip_art_button.grid(in_ = Right, row=2, column = 1, pady = 5)

start_button = Button(root, text='Start', font=("Ariel", 9, "bold"), command=initialise)
start_button.grid(in_ = Right, row=2, column = 2, pady = 5)


time_dropdown = ttk.Combobox(root, values=['< 5 mins', '< 10 mins', '> 10 mins'], width=9)
time_dropdown.current(0)
time_dropdown.grid(in_ = Right, row=2, column = 0, pady = 5)

progress = ttk.Progressbar(root, orient = HORIZONTAL, length = 280, mode = 'determinate') 
progress.grid(in_=Right, row=3, columnspan=3, pady = 10)


#Puts the Reddit Logo into the left hand side and resizes
logo_path= 'images/reddit.png'
img = Image.open(logo_path)
img = img.resize((180, 120), Image.ANTIALIAS)
image = PhotoImage(img)#converts image to tkinter friendly format
thumbnailIM = Label(root, image=image, borderwidth = 0)
thumbnailIM.image = image
thumbnailIM.grid(in_=Left, row = 0, column = 0, pady = 15, padx = 15)


root.configure(bg=_from_rgb((51, 51, 51))) 

root.mainloop()
