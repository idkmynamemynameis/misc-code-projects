import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
#blurred text
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)
#init
root = tk.Tk()
def funct():
    showinfo(
        title='Test title',
        message=str(counter),
        
    )
#set counter
counter=0
def add_one():
    global counter
    counter+=1
    counterstring.set(str(counter))
    return
#make button
ttk.Button(
   root, 
   text="Click Me", 
   command=funct
).pack()
#make strvar
counterstring=tk.StringVar()
counterstring.set(str(counter))

ttk.Button(root,text='Add one',command=add_one).pack()
clabel=ttk.Label(root, textvariable=counterstring).pack()

root.mainloop()