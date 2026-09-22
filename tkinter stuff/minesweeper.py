# Source - https://stackoverflow.com/a/7591453
# Posted by Vaughn Cato, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-18, License - CC BY-SA 4.0

from tkinter import * # type: ignore
import os
import random as rand
import tkinter.messagebox 
#init config
x_len=5
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
empty_icon=PhotoImage(file='./tkinter stuff/empty.png')
full_icon = PhotoImage(file='./tkinter stuff/full.png')
bomb_icon=PhotoImage(file='./tkinter stuff/bomb.png')
one_icon=PhotoImage(file='./tkinter stuff/1_icon.png')
two_icon=PhotoImage(file='./tkinter stuff/2.png')
three_icon=PhotoImage(file='./tkinter stuff/3.png')
four_icon=PhotoImage(file='./tkinter stuff/3.png')
#magically look around
def check_around(x,y,clicked=False):
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
            



'''      
def echeck_around(x,y):
    if not (0 <= x < x_len and 0 <= y < y_len):
            return
    #GET NAME
    mbutton=buttons[x][y]

    name=buttons[x][y].winfo_name()
    #check if it's a bomb
    if name[0] == 'n':
        #if it is, die
        print('d')
        response = tkinter.messagebox.askyesno(
                    "Game Over", " You Lost\n Do you want to replay?", icon='warning')
        if response==YES:
            make_board()
        else:
            root.destroy()
    else:
        #if not, check around
        #make grid of spots to be checked
        x_pos=[-1,0,1]
        y_pos=[1,0,-1]
        for i in range(len(x_pos)):
            x_pos[i]+=x
            y_pos[i]+=y
        #count bombs
        tot_bomb = 0
        tot_bomb = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                # Ensure neighboring cell exists inside grid
                if 0 <= nx < x_len and 0 <= ny < y_len:
                    if find_type(nx, ny) == 'yes':
                        tot_bomb += 1
        mbutton.checked=1
        if tot_bomb == 0:
            mbutton.config(image=empty_icon, text="", bg="lightgrey")
            # Flood-fill: Reveal neighboring safe tiles recursively
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    check_around(x + dx, y + dy)
        elif tot_bomb == 1:
            buttons[x][y].config(image=one_icon)
        elif tot_bomb == 2:
            buttons[x][y].config(image=two_icon)
        else:
            buttons[x][y].config(image=three_icon)
        
                        
        
def find_type(x,y):
    if 0 < x < x_len and 0 < y < y_len:
        try:
            name=buttons[x][y].winfo_name()
            
            if name[0] == 'n':
                return 'yes'
            else:
                
                return 'no'
        except:
            return 'oob'
    '''
#make the empty array
def clear_buttons():
    global buttons
    buttons=[[] for _ in range(x_len)]

buttons=[[] for _ in range(x_len)]
def make_board():
    clear_buttons()
    #make the buttons
    id=0
    for x in range(x_len):
        for y in range(y_len):
            
            id+=1
            #pick a name
            if not rand.randint(0,10):
                icon=full_icon
                name='not safe'+str(id)
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
