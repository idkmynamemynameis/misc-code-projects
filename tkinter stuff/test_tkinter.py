import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
#blurred text
from ctypes import windll
import numpy as np
windll.shcore.SetProcessDpiAwareness(1)





#init
root = tk.Tk()
#set counter
counter_max=1000
counter=counter_max
minus_minimum=400
minus_maximum=500
quarter_threshold=counter_max/4
half_threshold=counter_max/2
three_quarters_threshold=(counter_max/4)*3

def reset():
    global counter,reset_button,btn
    counter=counter_max
    btn.config(state='normal')
    reset_button.config(state='disabled')
    #counterstring.set('Counter = '+str(counter))
    statusstring.set('status: good')

reset_button=tk.Button(
    root,
    text='Set counter to '+str(counter),
    command=reset

)
g=tk.Grid()
reset_button.config(state='disabled')
reset_button.pack()

def add_one():
    global counter, btn
    turn_on=True
    #change counter
    counter-=np.random.randint(minus_minimum,minus_maximum)
    if counter < 0:
        counter=0
        turn_on=False
    if counter == 0:
        reset_button.config(state='normal')
    
    #update string

    update_status()
    #disable
    btn.config(state="disabled")
    
    #wait
    if turn_on:
        root.after(300, lambda: btn.config(state="normal"))
    
    return




def update_status():
    status=''
    if counter >= three_quarters_threshold:
        status='good'
    elif counter >= half_threshold:
        status='okay'
    elif counter >= quarter_threshold:
        status='meh'
    elif counter == 0:
        status='dead'
    else:
        status='bad'

    statusstring.set('status: '+status)
    return 


btn=tk.Button(root,text='Minus '+str(minus_minimum)+' - '+str(minus_maximum),command=add_one)
btn.pack()

#make strvar
statusstring=tk.StringVar()

statusstring.set('status: good')

#label=ttk.Label(root, textvariable=counterstring)
#label.pack()
status_label=ttk.Label(root, textvariable=statusstring)
status_label.pack()


root.mainloop()