import tkinter as tk
from tkinter import ttk
#blurred text
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)
#init
root = tk.Tk()



tk.Label(root, text='Classic Label').pack()
ttk.Label(root, text='Themed Label').pack()
button=ttk.Button(root,text='Button').pack()
ttk.Checkbutton(root,text='checkbutton').pack()

root.mainloop()