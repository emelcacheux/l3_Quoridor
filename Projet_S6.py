import tkinter as tk
import time
from random import choice

#-----------------------------TO-DO---------------------------------#
#ADD verification of emprisonment when placing walls.
#
#
#
#
#-------------------------------------------------------------------#

# (\_/)
# (°.°)
# /< >\
# -Marine


## SETTINGS
#-------------------------------DIMENSIONS (PIXELS)-------------------------------#
dimC = 60
dimW = dimC//3
dimT = dimC+dimW
dimP = dimW//3
#-------------------------------DIMENSIONS (NUMBERS)------------------------------#
nbC = 9
nbW = nbC-1
size = dimC * ((4*nbC)//3)-dimW
length = 2*nbC-1
total = length**2
#-------------------------------------PLAYERS-------------------------------------#
nb_players = 2
player_turn = 0
#-------------------------------------COLORS--------------------------------------#
colorCell,colorBack = "antique white","Grey15"
colorP = "skyblue2"

#-----------------------------SETUP, VARS & TKINTER-------------------------------#
root = tk.Tk()
root.title("Maze Generator")
root.config(bg=colorBack)
root.geometry(f"{size+100}x{size+100}")
canvas = tk.Canvas(root, width=size, height=size, background=colorBack, highlightthickness=0)


Board_dict = {} #Obvious for those three...
Walls_dict = {}
Cells_dict = {} 
Players_dict = {0:[(length+1)//2,'NSE',0],
                1:[total-(length)//2,'NSW',0]} #Contains per Player(key):[cell index, 'directions', pawn OID](vals)
# Players_dict = {0:[(145),'NESW',0],
#                 1:[(145+2*length),'NESW',0]}
Player_list = Players_dict.keys()
colors = ["Red", "Blue"]
mapped_dir = {
    'N': -2,
    'E': +length*2,
    'S': +2,
    'W': -length*2 } #To simplify later calls

clrdClist = [] #selected cells (greyed ones) in memory
clrdWlist = [] #selected walls (greyed ones) in memory
spos_oid = [] #Suggested Positions Object IDs list (move suggestions overlay)
suggested_newpos = {0:[],1:[]} #Keeping track of suggestions based on players to avoid teleportations
colision_dict = {}
#-------------------------------------WIN VERIFICATION-------------------------------------#

def end_program(event):
    exit()

def animate(tid):
    color = choice(["green", "purple","orange","dark goldenrod","goldenrod", "dark green", "sea green", "dark violet", "dark orchid"])
    canvas.itemconfig(tid, fill=color)
    canvas.after(500, lambda: animate(tid))

def won(player):
    print(f"{player} won !!")
    txt = canvas.create_text(size//2,size//2,angle=45,text=f"PLAYER {player_turn+1} WON! GOOD GAME!!", fill="green", font=("Helvetica", 45, "bold"))
    animate(txt)

def reached_border(player):
    print(f"player: {player}")
    print(f"player id: {Players_dict[player]}")
    border = (0,length+1) if player == 1 else (total-length,total+1)
    if border[0]<(Players_dict[player][0])<border[1]:
        canvas.unbind("<Button-1>")
        canvas.unbind("<Button-3>")
        canvas.bind("<Return>", end_program)
        return True
    return False

#-------------------------------------COLISION OPERATOR-------------------------------------#
#Programmer les colisions aux murs et le cas ou saut par dessus joueur mais mur derriere.
def colision_detector(index,direction):
    index=index+mapped_dir[direction]
    windex=index-mapped_dir[direction]//2
    if windex in colision_dict or not 0<index<total+1:
        return None
    if index in colision_dict:
        nindex = index+mapped_dir[direction]
        if not 0<nindex<total+1 or windex+mapped_dir[direction] in colision_dict:
            dirindex = "NESW".find(direction)
            nindex = colision_detector(index,direction)
            if nindex == None:
                nindex=(colision_detector(index,"NESW"[(dirindex+1)%4]),colision_detector(index,"NESW"[(dirindex+3)%4]))
        return nindex
    return index

#-------------------------------------SUGGESTED PAWN PLACEMENT-------------------------------------#
def cardinal_directions(index):
    if index == 1: #top-left corner
        return 'SE'
    elif index == length : #bottom-left corner
        return 'NE'
    elif index == total-length: #top-right corner
        return 'SW'
    elif index == total: #bottom-right corner
        return 'NW'
    else:
        if index-length<=0: #left column
            return 'NSE'
        elif index+length>=total:#right column
            return 'NSW'
        elif index%length==1: #top row
            return 'SEW'
        elif index%length==0: #bottom row
            return 'NEW'
        else: #center square
            return 'NSEW'

def suggest_newpos(index):
    suggested_newpos = []
    cards = cardinal_directions(index)
    for direction in cards:
        nindex = colision_detector(index,direction)
        if nindex == None:
            continue
        if type(nindex) is tuple:
            if nindex[0] is not None: suggested_newpos.append(nindex[0])
            if nindex[1] is not None: suggested_newpos.append(nindex[1])
        else:
            suggested_newpos.append(nindex) #new coords
    return suggested_newpos

def delete_suggested_oldpos(suggested_oldpos):
    for spid in suggested_oldpos:
        canvas.delete(spid)
    return []

def display_suggested_newpos(index):
    spidlist=[]
    suggested_newpos = suggest_newpos(index)
    for index in suggested_newpos:
        c1,c2 = index2coords(index)
        spid = canvas.create_oval(c1[0]+dimW,c1[1]+dimW,c2[0]-dimW,c2[1]-dimW,fill="rosy brown",outline="rosy brown")
        spidlist.append(spid)
    return spidlist,suggested_newpos


#-------------------------------------CONVERTION FROM/TO INDEX-------------------------------------#

def index2coords(rid):
    rid-=1
    block = rid//(length*2)
    rid %= (length*2)
    if rid-length < 0 : #HCW row
        yid = rid//2
        x1 = block*dimT
        if rid % 2==1: #Wall
            y1 = dimC + yid*dimT
            coords1,coords2 = (x1,y1),(x1+dimC,y1+dimW)
        else: #Cell
            y1 = yid * dimT
            coords1,coords2 =(x1,y1),(x1+dimC,y1+dimC)
        return coords1,coords2
    else : #FW row
        rid %= length
        yid = rid//2
        x1 = dimC + block*dimT
        if rid % 2==1: #square wall
            y1 = dimC + yid*dimT
            coords1,coords2 = (x1,y1),(x1+dimW,y1+dimW)
        else: #vertical wall
            y1 = yid*dimT
            coords1,coords2 =(x1,y1),(x1+dimW,y1+dimC)
        return coords1,coords2

def mouse2index():
    x,y = root.winfo_pointerxy()
    cx,cy = canvas.winfo_rootx(),canvas.winfo_rooty()
    rx,ry = x-cx, y-cy
    if not 0<rx<size or not 0<ry<size:
        print("mouse outside of active scope")
        return False
    else:
        ix = rx//dimT
        iy = ry//dimT
        keyW = list(Walls_dict.keys())[ix]
        keyC = list(Cells_dict.keys())[ix]
        if keyW[0]<=rx<=keyW[1]: #FW row
            idW = Walls_dict[keyW][iy][0]
            rid = length+(idW%nbW+1)*2+(idW//nbW)*2*length
            state = 'W'
            if iy!=0 and ry<Walls_dict[keyW][iy][1][0]-dimC//2:
                rid-=2
        elif Cells_dict[keyC][iy][1][0]<=ry<=Cells_dict[keyC][iy][1][1]: #Cells in CW row
            idC = Cells_dict[keyC][iy][0]
            rid = idC%nbC*2+(idC//nbC)*2*length + 1
            state = 'C'
        else: #Walls in CW row
            idW = Walls_dict[keyW][iy][0]
            rid = length+idW%nbW*2+(idW//nbW)*2*length + 2
            state = 'H'
            if ix!=0 and rx<keyW[0]-dimC//2:
                rid-=2*length
        return state, rid

#-------------------------------------DISPLAY // PLAYER TURNS-------------------------------------#

def clear_list(arglist):
    while len(arglist) > 0:
        tid = arglist[-1]
        tags = canvas.gettags(tid)
        if 'movable' in tags:
            canvas.delete(tid)
        else:
            color = colorCell if "Cell" in tags else colorBack
            canvas.itemconfig(tid, fill=color, outline=color)
        arglist.pop()

def wall_placement(index,vertical=True):
    returnlist = []
    returnlist.append(index)
    canvas.itemconfig(index, fill="seashell4", outline="seashell4")
    if vertical:
        if index-1 in colision_dict or index+1 in colision_dict:
            return returnlist
        returnlist.extend([index-1,index+1])
        canvas.itemconfig(index-1, fill="seashell4", outline="seashell4")
        canvas.itemconfig(index+1, fill="seashell4", outline="seashell4")
    else:
        if index-length in colision_dict or index+length in colision_dict:
            return returnlist
        returnlist.extend([index-length,index+length])
        canvas.itemconfig(index-length, fill="seashell4", outline="seashell4")
        canvas.itemconfig(index+length, fill="seashell4", outline="seashell4")
    return returnlist

def display_wall(indexlist):
    if len(indexlist)>3:
        print("Error in given argument for display_wall, list of 3 elements expected...")
    else:
        c1 = index2coords(indexlist[1])
        c2 = index2coords(indexlist[2])
        wid = canvas.create_rectangle(c1[0],c2[1],fill=colors[player_turn],outline=colors[player_turn])
        return wid

def mouse_overlay(pid,left_click):
    global player_turn,spos_oid,suggested_newpos,clrdWlist,colision_dict
    clear_list(clrdClist)
    state,cid = mouse2index()
    if not 0<cid<total+1:
        return 0
    if state=='C':
        clear_list(clrdWlist)
        c1,c2 = index2coords(cid)
        cp1,_ = index2coords(Players_dict[pid][0])
        if cid in suggested_newpos[player_turn] and left_click:
            canvas.coords(Players_dict[player_turn][2],c1[0]+dimP,c1[1]+dimP,c2[0]-dimP,c2[1]-dimP)
            suggested_newpos[player_turn]=[]
            colision_dict[cid] = colision_dict.pop(Players_dict[player_turn][0])
            Players_dict[player_turn][0]=cid
            if reached_border(player_turn): won(player_turn)
            player_turn = (player_turn+1)%2
            spos_oid = delete_suggested_oldpos(spos_oid)
        if c1[0]==cp1[0] and c1[1]==cp1[1] and left_click:
            delete_suggested_oldpos(spos_oid)
            suggested_newpos[player_turn]=[]
            spos_oid,suggested_newpos[player_turn] = display_suggested_newpos(cid)
        else:
            spos_oid = delete_suggested_oldpos(spos_oid)
            suggested_newpos[player_turn]=[]
        clrdClist.append(cid)
        canvas.itemconfig(cid, fill="seashell4", outline="seashell4")
    else:
        spos_oid = delete_suggested_oldpos(spos_oid)
        suggested_newpos[player_turn]=[]
        if cid-length in clrdWlist and not left_click or cid+1 in clrdWlist and left_click: #wall placement
            wid = display_wall(clrdWlist)
            for windex in clrdWlist:
                colision_dict[windex] = wid
            player_turn = (player_turn+1)%2
        clear_list(clrdWlist)
        if cid not in colision_dict:
            clrdWlist = wall_placement(cid,True if left_click else False)



def test_event(event):
    if event.num == 1:
        mouse_overlay(player_turn,True)
    else:
        mouse_overlay(player_turn,False)


def display_circle(index, color, tags=None):
    c1,c2 = index2coords(index)
    c1 = tuple(map(lambda x: x+dimW/3, c1))
    c2 = tuple(map(lambda x: x-dimW/3, c2))
    oid = canvas.create_oval(c1,c2,fill=color,outline=color,tags=tags)
    return oid

#-------------------------------------INITILIZATION-------------------------------------#

def initialize_players(nb=2,colors=colors):
    if nb == 2:
        p1 = display_circle(Players_dict[0][0],colors[0], "Player")
        p2 = display_circle(Players_dict[1][0], colors[1], "Player")
        return p1,p2

def initialize_board():
    global Board_dict
    x=0
    for i in range(length):
        y=0
        WoCi = i%2==1
        di = dimW if WoCi else dimC
        if not WoCi:
            k = i//2
            Walls_dict[(dimC+k*dimT,(k+1)*dimT)] = []
            Cells_dict[(k*dimT,dimC+k*dimT)] = []
        for j in range(length):
            WoCj = j%2==1
            if not WoCi and not WoCj:
                l = j//2
                Walls_dict[(dimC+k*dimT,(k+1)*dimT)].append([k*(nbW)+l,(dimC+l*dimT,(l+1)*dimT)])
                Cells_dict[(k*dimT,dimC+k*dimT)].append([k*(nbC)+l,(l*dimT,dimC+l*dimT)])
            dj = dimW if WoCj else dimC
            color = colorBack if WoCj or WoCi else colorCell
            cell = canvas.create_rectangle((x, y),(x+di,y+dj), fill=color, outline=color, tags='Wall' if color==colorBack else "Cell")
            Board_dict[i*length+j+1] = cell
            y += dj
        x += di


#-------------------------------------Function calls-------------------------------------#

initialize_board()
p1,p2 = initialize_players()
Players_dict[0][2]=p1
Players_dict[1][2]=p2
colision_dict = {Players_dict[x][0]:Players_dict[x][2] for x in Players_dict.keys()}
canvas.bind("<Button-1>", test_event)
canvas.bind("<Button-3>", test_event)
canvas.pack(padx=50,pady=50)
root.mainloop()
