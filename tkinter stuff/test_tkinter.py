import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
#blurred text
from ctypes import windll
import numpy as np
windll.shcore.SetProcessDpiAwareness(1)





#init
root = tk.Tk()
# Wait 3 seconds without freezing

#set counter

def reset():
    global counter,reset_button,btn
    counter=100
    btn.config(state='normal')
    reset_button.config(state='disabled')
    counterstring.set('Counter = '+str(counter))
reset_button=tk.Button(
    root,
    text='Set counter to 100',
    command=reset

)

reset_button.config(state='disabled')
reset_button.pack()
counter=100
def add_one():
    global counter, btn
    turn_on=True
    #change counter
    counter-=np.random.randint(1,100)
    if counter < 0:
        counter=0
        turn_on=False
    if counter == 0:
        reset_button.config(state='normal')
    
    #update string
    counterstring.set('Counter = '+str(counter))
    
    #disable
    btn.config(state="disabled")
    
    #wait
    if turn_on:
        root.after(300, lambda: btn.config(state="normal"))
    
    return



btn=tk.Button(root,text='Minus 1-100',command=add_one)
btn.pack()

#make strvar
counterstring=tk.StringVar()
counterstring.set('Counter = '+str(counter))


label=ttk.Label(root, textvariable=counterstring).pack()



root.mainloop()