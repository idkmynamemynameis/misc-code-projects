
from tkinter import * # type: ignore

import random as rand
import tkinter.messagebox 
#init config
x_len=7
y_len=5
#init tk stuff
root = Tk()
frame = Frame(root)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
frame.grid(row=0, column=0, sticky="news")
grid = Frame(frame)
grid.grid(sticky="news", column=0, row=x_len, columnspan=2)
frame.rowconfigure(x_len, weight=1)
frame.columnconfigure(0, weight=1)
#grabs icons
empty_icon=PhotoImage(file='./tkinter stuff/clicked-.png')
full_icon = PhotoImage(file='./tkinter stuff/unclicked.png')
bomb_icon=PhotoImage(file='./tkinter stuff/bomb.png')
one_icon=PhotoImage(file='./tkinter stuff/1.png')
two_icon=PhotoImage(file='./tkinter stuff/2.png')
three_icon=PhotoImage(file='./tkinter stuff/3.png')
four_icon=PhotoImage(file='./tkinter stuff/3.png')
#magically look around
nchecked=0
def check_around(x,y,clicked=False):
    global nbombs,nchecked
    if not (0 <= x < x_len and 0 <=y < y_len):
         print('oob')
         return
    if buttons[x][y].checked==1:
        print('checked')
        return
    button=buttons[x][y]
    if  str(button.winfo_name()).startswith('n'):
        if clicked:
            buttons[x][y].config(image=bomb_icon)
            response = tkinter.messagebox.askyesno("Game Over", " You Lost\n Do you want to replay?", icon='warning')
            if response==YES:
                make_board()
                return
            else:
                root.destroy()
                return
        else:
            return
    else:
        nchecked+=1
    

    tot_bombs=0
    #rest of code
    for ax in [-1,0,1]:
        ax+=x
        for ay in [1,0,-1]:
            ay+=y
            if 0 <= ax < x_len and 0 <= ay < y_len:
                question_button=buttons[ax][ay]
                if str(question_button.winfo_name()).startswith('n'):
                    tot_bombs+=1
    buttons[x][y].checked=1

    if tot_bombs==0:
        buttons[x][y].config(image=empty_icon)
        
        
        for bx in [-1,0,1]:
            bx+=x
            for by in [1,0,-1]:
                by+=y
                check_around(bx,by)
    elif tot_bombs == 1:
        buttons[x][y].config(image=one_icon)
    elif tot_bombs == 2:
        buttons[x][y].config(image=two_icon)
    elif tot_bombs == 3:
        buttons[x][y].config(image=three_icon)
    elif tot_bombs == 4:
        buttons[x][y].config(image=four_icon)
    if nchecked == (x_len*y_len)-nbombs:
        check_around(x,y)
        response = tkinter.messagebox.askyesno("You Won", " You won!\n Do you want to replay?", icon='question')
        if response==YES:
            make_board()
            return
        else:
            root.destroy()
            return

        
            


def clear_buttons():
    global buttons
    buttons=[[] for _ in range(x_len)]
nbombs=0
buttons=[[] for _ in range(x_len)]
def make_board():
    global nbombs,nchecked
    clear_buttons()
    #make the buttons
    nbombs,nchecked=0,0
    id=0
    for x in range(x_len):
        for y in range(y_len):
            
            id+=1
            #pick a name
            if not rand.randint(0,10):
                icon=full_icon
                name='not safe'+str(id)
                nbombs+=1
            else:
                icon=full_icon
                name='safe'+str(id)
            #make button
            btn = Button(frame,image=icon,name=name,command=lambda x=x,y=y,t=True:check_around(x,y,t))
            btn.checked=0 # type: ignore
            #add button to array
            buttons[x].append(btn)
            #add button to screen
            print(btn.winfo_name())
            btn.grid(column=x, row=y, sticky="news")

    frame.columnconfigure(tuple(range(y_len)), weight=1)
    frame.rowconfigure(tuple(range(x_len)), weight=1)
make_board()
root.mainloop()
