import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import time
from random import choice
from collections import deque
import copy as cp

#-----------------------------TO-DO---------------------------------#
# ADD verification of emprisonment when placing walls. (update algorithm)
# le bot ne gagne pas directement s'il est en face de la ligne d'arrivée, à investiguer
#
#
#
#
#-------------------------------------------------------------------#


# ------------------------------TKINTER SETUP----------------------------------#
def dessiner_fond(event=None):
    canvas.delete("all")
    largeur = canvas.winfo_width()
    hauteur = canvas.winfo_height()

    taille_plateau = max(largeur, hauteur) 
    taille_case = taille_plateau / 5
    x_start = (largeur - taille_plateau) / 2
    y_start = (hauteur - taille_plateau) / 2

    canvas.create_rectangle(x_start, y_start, x_start + taille_plateau, y_start + taille_plateau, fill="Grey15")
    epaisseur_mur = 25
    for ligne in range(5):
        for colonne in range(5):
            x1 = x_start + colonne * taille_case
            y1 = y_start + ligne * taille_case
            x2 = x1 + taille_case - epaisseur_mur
            y2 = y1 + taille_case - epaisseur_mur
            canvas.create_rectangle(x1, y1, x2, y2, fill="antique white")

def afficher_regles():
    regles = tk.Tk()
    regles.title("Règles du Quoridor")
    regles.geometry("500x400")

    # Optionnel : force la fenêtre des règles à rester au premier plan
    regles.attributes("-topmost", True)
    zone_texte = ctk.CTkTextbox(
        regles, 
        wrap="word", 
        font=("Arial", 14),
        fg_color="Grey15",       
        text_color="antique white"
    )
    zone_texte.pack(fill="both", expand=True, padx=20, pady=20)


    texte_des_regles = """BUT DU JEU :
Atteindre le premier la ligne opposée à sa ligne de départ.

DÉROULEMENT :
À tour de rôle, chaque joueur choisit de :
- Soit déplacer son pion d'une case (horizontalement ou verticalement).
- Soit poser un mur pour bloquer son adversaire.

ATTENTION :
Il est interdit d'enfermer totalement l'adversaire, il faut toujours lui laisser au moins un chemin d'accès à sa ligne d'arrivée !
    """
    
    zone_texte.insert("0.0", texte_des_regles)
    zone_texte.configure(state="disabled")


menu = tk.Tk()
menu.title("Menu")
screen_width = menu.winfo_screenwidth()
screen_height = menu.winfo_screenheight()
menu_width = int(screen_width * 0.5)
menu_height = int(screen_height * 0.5)
center_x = int((screen_width - menu_width) / 2)
center_y = int((screen_height - menu_height) / 2)
menu.geometry(f"{menu_width}x{menu_height}+{center_x}+{center_y}")

canvas = ctk.CTkCanvas(menu, bg="Grey15", highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.bind("<Configure>", dessiner_fond)

menu_cadre = ctk.CTkFrame(menu, fg_color="#482F24", corner_radius=15)
menu_cadre.place(relx=0.5, rely=0.5, anchor="center")
main_title = ctk.CTkLabel(menu_cadre, text="Quoridor", font=("Helvetica", 45, "bold"), text_color="#F4A261").pack(pady=(40, 20), padx=50)

## SETTINGS
#-------------------------------DIMENSIONS (PIXELS)-------------------------------#
minsize = int(min(screen_width, screen_height)*0.7)
dimW = minsize//35
dimC = dimW*3
dimT = dimC+dimW
dimP = dimW//3
#-------------------------------DIMENSIONS (NUMBERS)------------------------------#
nbC = 9
nbW = nbC-1
size = dimC * ((4*nbC)//3)-dimW
length = 2*nbC-1
total = length**2
#-------------------------------------PLAYERS-------------------------------------#
nb_walls = 10
nb_players = 2
player_turn = 0
#-------------------------------------COLORS--------------------------------------#
colorCell,colorBack = "antique white","Grey15"
colorP = "skyblue2"


# --------------------------------------VARS--------------------------------------#
#All directions are stored in the following order : NESW. This allows for better management down the line.
Walls_dict = {} # {(coords1,coords2) : [[nb, (coords1,coords2)],[],...]}
Cells_dict = {} # {(coords1,coords2) : [[nb, (coords1,coords2)],[],...]}
Players_dict = {0:[(length+1)//2,nb_walls,0],
                1:[total-(length)//2,nb_walls,0]} #Contains per Player(key):[cell index, 'directions', pawn OID](vals)
Player_list = Players_dict.keys()
colors = ("Red", "Blue")
dirlist = [-2,length*2,2,-length*2] #Index mapped to "NESW" directions

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


def won():
    txt = canvas.create_text(size//2,size//2,angle=45,text=f"PLAYER {player_turn+1} WON! GOOD GAME!!", fill="green", font=("Helvetica", 45, "bold"))
    animate(txt)


def reached_border(player):
    border = (0, length + 1) if player == 1 else (total - length + 1, total + 1)
    if border[0] <= (Players_dict[player][0]) <= border[1]:
        canvas.unbind("<Button-1>")
        canvas.unbind("<Button-3>")
        canvas.bind("<Return>", end_program)
        return True
    return False


#-------------------------------------COLISION OPERATOR-------------------------------------#
def wall_checker(index, direction, colision_dict):
    if str(direction) not in cardinal_directions(index): return True
    windex = index+dirlist[direction]//2
    if windex in colision_dict: return True
    return False
    

def colision_avoider(index, direction, colision_dict):
    if wall_checker(index, direction, colision_dict): return None
    index = index+dirlist[direction]
    if index in colision_dict:
        nindex = index + dirlist[direction]
        if str(direction) not in cardinal_directions(index) or index+dirlist[direction]//2 in colision_dict:
            nindex = colision_avoider(index, direction, colision_dict)
            if nindex == None:
                nindex = (colision_avoider(index, (int(direction)+1)%4,  colision_dict), colision_avoider(index, (int(direction)-1)%4, colision_dict))
        return nindex
    return index

#-------------------------------------SUGGESTED PAWN PLACEMENT-------------------------------------#
def cardinal_directions(index):
    if index == 1: #top-left corner
        return '12'
    elif index == length : #bottom-left corner
        return '01'
    elif index == total-length+1: #top-right corner
        return '23'
    elif index == total: #bottom-right corner
        return '03'
    else:
        if index-length<=0: #left column
            return '012'
        elif index+length>=total:#right column
            return '023'
        elif index%length==1: #top row
            return '123'
        elif index%length==0: #bottom row
            return '013'
        else: #center cells
            return '0123'


def suggest_newpos(index, dict_collisions=None):
    if dict_collisions is None:
        dict_collisions = colision_dict
    suggested_newpos = []
    cards = cardinal_directions(index)

    # fouille tous les tupples et extrait uniquement les nombres
    def extraire_cases(element):
        if isinstance(element, (list, tuple)):
            for sous_element in element:
                extraire_cases(sous_element)
        elif element is not None and element not in suggested_newpos:
            suggested_newpos.append(element)

    for direction in cards:
        nindex = colision_avoider(index, int(direction), dict_collisions)
        if nindex is None:
            continue

        extraire_cases(nindex)

    return suggested_newpos


def delete_suggested_oldpos(suggested_oldpos):
    for spid in suggested_oldpos:
        canvas.delete(spid)
    return []


def display_suggested_newpos(index):
    global colision_dict
    spidlist = []
    suggested_newpos = suggest_newpos(index, colision_dict)
    for index in suggested_newpos:
        c1, c2 = index2coords(index)
        spid = canvas.create_oval(c1[0]+dimW,c1[1]+dimW,c2[0]-dimW,c2[1]-dimW,fill="rosy brown",outline="rosy brown")
        spidlist.append(spid)
    return spidlist, suggested_newpos


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
            nb_of_rows = idW%nbC+1
            rid = length+idW//nbC*length*2+nb_of_rows*2
            state = 'W'
            if (iy!=0 and ry<Walls_dict[keyW][iy][1][0]-dimC//2) or (nb_of_rows==nbC):
                rid-=2
        elif Cells_dict[keyC][iy][1][0]<=ry<=Cells_dict[keyC][iy][1][1]: #Cells in CW row
            idC = Cells_dict[keyC][iy][0]
            rid = idC%nbC*2+(idC//nbC)*2*length + 1
            state = 'C'
        else: #Walls in CW row
            idW = Walls_dict[keyW][iy][0]
            nb_of_cols = idW//nbC
            rid = length+(idW%nbC+1)*2+nb_of_cols*2*length
            state = 'H'
            if nb_of_cols==nbW or (ix!=0 and rx<keyW[0]-dimC//2):
                rid-=2*length
        return state, rid


# -------------------------------------BOT EXECUTION------------------------------------- #
def botturn():
    global player_turn, colision_dict
    if reached_border(0):  # on test si le joueur a déjà gagné pour pas faire de mouvement en trop
        return

    if player_turn == 1:
        arrive_bot = [i for i in range(0, length+1)]
        arrive_joueur = [i for i in range(total - length, total + 1)]

        pos_bot = Players_dict[player_turn][0]  # indice où on est
        pos_joueur = Players_dict[player_turn-1][0]  # indice de où est le joueur
        pion = Players_dict[nb_players-1][2]  # oid du pion sur le canva

        meilleure_dist = float("inf")
        meilleur_coup = None

        if Players_dict[1][1] == 0: # Si le bot n'a plus de murs, on va juste à l'arrivée
            for coup in suggest_newpos(pos_bot):
                dist = parcours_largeur(coup, arrive_bot, colision_dict)
                
                if dist < meilleure_dist:
                    meilleure_dist = dist           
                    meilleur_coup = ("pion", coup)
            
            move = meilleur_coup

        else:
            score, move = minimax(3, True, pos_bot, arrive_bot, pos_joueur, arrive_joueur, colision_dict, float('-inf'), float('inf'))  # calcul de la case

        if move is None:
            print("Erreur bot bloqué")  # deboguage
            return
        
        type_coup, donnee = move

        if move is not None:
            if type_coup == "pion":
                if pos_bot in colision_dict:
                    colision_dict[donnee] = colision_dict.pop(pos_bot)  # maj de la position du bot pour les collisions
                    c1, c2 = index2coords(donnee)
                    canvas.coords(pion, c1[0] + dimP, c1[1] + dimP, c2[0] - dimP, c2[1] - dimP)  # on bouge le pion
                    Players_dict[player_turn][0] = donnee  # on maj la pos du bot dans le dict des joueurs
            else:
                Players_dict[player_turn][1] -= 1
                mur = display_wall(donnee)
                for i in donnee:
                    colision_dict[i] = mur

        if reached_border(player_turn):  # faut gagner si on arrive au bout
            won()
        player_turn = 0


def parcours_largeur(depart, arrivee, dict_collisions=None):
    if dict_collisions is None:
        dict_collisions = colision_dict

    file_attente = deque([(depart, 0)])
    cases_visitees = {depart}
    while file_attente:
        case_actuelle, dist_actuelle = file_attente.popleft()
        if case_actuelle in arrivee:
            return dist_actuelle
        options = suggest_newpos(case_actuelle, dict_collisions)
        for voisin in options:
            if voisin not in cases_visitees:
                cases_visitees.add(voisin)
                file_attente.append((voisin, dist_actuelle + 1))
    return float("inf")


def evaluation(dep_bot, arrive_bot, dep_joueur, arrive_joueur, dict_collision):
    dist_bot = parcours_largeur(dep_bot, arrive_bot, dict_collision)
    dist_joueur = parcours_largeur(dep_joueur, arrive_joueur, dict_collision)
    score = dist_joueur - dist_bot
    return score


def generer_murs_proximite(index = 145, rayon = 5):
    murs_interessants = []
    # Conversion de l'indice plat en coordonnées (x, y)
    row, column = (index-1) % 17, (index-1) // 17
    for dx in range(-rayon, rayon+1):
        if dx == 0 or column+dx<1 or column+dx>15:
            continue
        rayonY = rayon+1-abs(dx)
        Vwall = index+(dx*2+1)*17 if dx<0 else index+(dx*2-1)*17
        for dy in range(-rayonY,rayonY+1):
            if dy == 0 or row+dy<1 or row+dy>15:
                continue
            intersection = Vwall+(dy*2+1) if dy<0 else Vwall+(dy*2-1)
            murs_interessants.extend([(intersection,True),(intersection,False)])
    return murs_interessants 


def indices_murs(index: int, vertical: bool,colision_dict):
    """calcule les deux indices supplémentaires 
    nécéssaires pour poser un mur"""
    if vertical :
        if index-1 in colision_dict or index+1 in colision_dict:
            return None
        return [index, index-1, index+1]
    else:
        if index-length in colision_dict or index+length in colision_dict:
            return None
        return [index, index-length, index+length]


def mur_legal(indices_mur: list, pos_bot: int, arrive_bot: list, pos_joueur: int, arrive_joueur: list, dict_collisions: dict):
    """prend l'indice de où on veut poser le mur et
    renvoie un booléen qui indique si on a la droit de le poser"""
    for indice in indices_mur:
        dict_collisions[indice] = "mur_bot"
    dist_bot = parcours_largeur(pos_bot,  arrive_bot,  dict_collisions)
    dist_joueur = parcours_largeur(pos_joueur,  arrive_joueur,  dict_collisions)
    if dist_bot == float("inf") or dist_joueur == float("inf"):
        return False
    else:
        return True



def minimax(profondeur: int, tour_ia: bool, pos_bot: int, arrive_bot: list, pos_joueur: int, arrive_joueur: list, dict_collisons: dict, alpha, beta):
    if profondeur == 0:
        return evaluation(pos_bot, arrive_bot, pos_joueur, arrive_joueur, dict_collisons), None

    # Tour bot (Maximiser)
    if tour_ia:
        meilleur_score = float('-inf')
        meilleur_coup = None

        for coup in suggest_newpos(pos_bot, dict_collisons):  # on parcourt la liste des coups disponibles pour la position actuelle
            dico_pion = dict_collisons.copy()  # on copie le dictionnaire de collisions pour simuler les prochains coups possibles
            if pos_bot in dico_pion:
                dico_pion.pop(pos_bot)  # on efface l'ancienne position
            dico_pion[coup] = "bot"  # on simule le coup dans le dico temporaire puis on lance minimax
            score_pion = minimax(profondeur - 1, False, coup, arrive_bot, pos_joueur, arrive_joueur, dico_pion, alpha, beta)[0]
            if score_pion > meilleur_score:
                meilleur_score = score_pion
                meilleur_coup = ("pion", coup)
            alpha = max(alpha, meilleur_score)  # elagage alpha beta
            if beta <= alpha:
                break  # on coupe la branche si  son score est moins bien qu'une branche déjà parcourrue

        murs_potentiels = generer_murs_proximite(pos_joueur, rayon=2)

        for indice, est_vertical in murs_potentiels:
            mur = indices_murs(indice, (est_vertical),colision_dict)
            if mur == None: #Si indices_murs retourne un mur vide (dans le cas d'une intersection invalide)
                continue

            if Players_dict[1][1] > 0:  # on vérifie s'il nous reste des murs à poser
                if all(m not in dict_collisons for m in mur):   # on vérifie si les segments du mur sont libres
                    dico_temp = dict_collisons.copy()
                    if mur_legal(mur, pos_bot, arrive_bot, pos_joueur, arrive_joueur, dico_temp): # on verifie que le mur n'enferme pas le joueur
                        score_mur = minimax(profondeur - 1, False, pos_bot, arrive_bot, pos_joueur, arrive_joueur, dico_temp, alpha, beta)[0]
                        if score_mur > meilleur_score:
                            meilleur_score = score_mur
                            meilleur_coup = ("mur", mur)
                        alpha = max(alpha, meilleur_score)
                        if beta <= alpha:
                            break  # On coupe la branche !
        return meilleur_score, meilleur_coup

    # Tour joueur(Minimiser)
    else:
        meilleur_score = float('inf')
        meilleur_coup = None

        for coup in suggest_newpos(pos_joueur, dict_collisons):
            dico_pion = dict_collisons.copy()
            if pos_bot in dico_pion:
                dico_pion.pop(pos_bot)
            dico_pion[coup] = "bot"
            score = minimax(profondeur - 1, True, pos_bot, arrive_bot, coup, arrive_joueur, dico_pion, alpha, beta)[0]
            if score < meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            alpha = max(alpha, meilleur_score)
            if beta <= alpha:
                break  # On coupe la branche !

        murs_potentiels = generer_murs_proximite(pos_bot, rayon=2)

        for indice, est_vertical in murs_potentiels:
            mur = indices_murs(indice, (est_vertical),colision_dict)
            if mur == None: #Si indices_murs retourne un mur vide (dans le cas d'une intersection invalide)
                continue

            if Players_dict[0][1] > 0:
                if all(m not in dict_collisons for m in mur):  # On vérifie si les segments du mur sont libres
                    dico_temp = dict_collisons.copy()
                    if mur_legal(mur, pos_bot, arrive_bot, pos_joueur, arrive_joueur, dico_temp):
                        score_mur = minimax(profondeur - 1, True, pos_bot, arrive_bot, pos_joueur, arrive_joueur, dico_temp, alpha, beta)[0]
                        if score_mur < meilleur_score:
                            meilleur_score = score_mur
                            meilleur_coup = ("mur", mur)
                        beta = min(beta, meilleur_score)
                        if beta <= alpha:
                            break  # On coupe la branche !
        return meilleur_score, meilleur_coup


#-------------------------------------DISPLAY // PLAYER TURNS-------------------------------------#
def wall_placement(index, vertical=True):
    returnlist = []
    returnlist.append(index)
    canvas.itemconfig(index, fill="seashell4", outline="seashell4")
    if vertical:
        if index-1 in colision_dict or index+1 in colision_dict:
            return returnlist
        returnlist.extend([index-1, index+1])
        canvas.itemconfig(index-1, fill="seashell4", outline="seashell4")
        canvas.itemconfig(index+1, fill="seashell4", outline="seashell4")
    else:
        if index-length in colision_dict or index+length in colision_dict:
            return returnlist
        returnlist.extend([index-length, index+length])
        canvas.itemconfig(index-length, fill="seashell4", outline="seashell4")
        canvas.itemconfig(index+length, fill="seashell4", outline="seashell4")
    return returnlist


def display_wall(indexlist):
    if len(indexlist) > 3:
        print("Error in given argument for display_wall, list of 3 elements expected...")
    else:
        c1 = index2coords(indexlist[1])
        c2 = index2coords(indexlist[2])
        wid = canvas.create_rectangle(c1[0], c2[1], fill=colors[player_turn], outline=colors[player_turn])
        return wid


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


def mouse_overlay(pid,against_bot,left_click):
    global player_turn,spos_oid,suggested_newpos,clrdWlist,colision_dict,Players_dict
    clear_list(clrdClist)
    arrive_bot = [i for i in range(0, length+1)]
    arrive_joueur = [i for i in range(total - length, total + 1)]
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
            if reached_border(player_turn): won()
            player_turn = (player_turn+1)%2
            if against_bot:
                canvas.update_idletasks() # pour tester le bot
                botturn()  # pour pas qu'on ait l'impression que les deux joueurs jouent en même temps 
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
        if Players_dict[player_turn][1] > 0:
            spos_oid = delete_suggested_oldpos(spos_oid)
            suggested_newpos[player_turn]=[]
            if ((not left_click and cid-length in clrdWlist and cid+length in clrdWlist) or (left_click and cid+1 in clrdWlist and cid-1 in clrdWlist)) and mur_legal(clrdWlist, Players_dict[1][0], arrive_bot, Players_dict[0][0], arrive_joueur, cp.deepcopy(colision_dict)):  # wall placement
                Players_dict[player_turn][1]-=1
                wid = display_wall(clrdWlist)
                for windex in clrdWlist:
                    colision_dict[windex] = wid
                player_turn = (player_turn+1)%2
                if against_bot:
                    canvas.update_idletasks()  # On affiche le mur posé
                    botturn()
                # canvas.after(500, botturn)  # de nouveau le tour du bot (juste des test on fera ça mieux)
            clear_list(clrdWlist)
            if cid not in colision_dict:
                clrdWlist = wall_placement(cid,True if left_click else False)


def test_event(event,against_bot):
    if event.num == 1:
        mouse_overlay(player_turn, against_bot, True)
    else:
        mouse_overlay(player_turn, against_bot, False)


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
    global canvas
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
                Walls_dict[(dimC+k*dimT,(k+1)*dimT)].append([k*(nbC)+l,(dimC+l*dimT,(l+1)*dimT)])
                Cells_dict[(k*dimT,dimC+k*dimT)].append([k*(nbC)+l,(l*dimT,dimC+l*dimT)])
            dj = dimW if WoCj else dimC
            color = colorBack if WoCj or WoCi else colorCell
            cell = canvas.create_rectangle((x, y),(x+di,y+dj), fill=color, outline=color, tags='Wall' if color==colorBack else "Cell")
            y += dj
        x += di


#------------------------------------Function calls-------------------------------------#
def new_game(against_bot: bool):
    global root, canvas, p1, p2, colision_dict, player_turn, colision_dict
    global Walls_dict, Cells_dict, Players_dict
    global clrdWlist, clrdClist, suggested_newpos, spos_oid
    
    #Reset all variables used for a game
    player_turn = 0
    Walls_dict.clear()
    Cells_dict.clear()
    Players_dict = {0: [(length+1)//2, nb_walls, 0],
                    1: [total-(length)//2, nb_walls, 0]}
    clrdClist.clear()
    clrdWlist.clear()
    spos_oid .clear()
    suggested_newpos = {0: [], 1: []}
    colision_dict.clear()

    title = "Partie contre l'IA" if against_bot else "Partie entre amis"
    root = tk.Toplevel()
    root.title(title)
    root.config(bg=colorBack)
    center_x = int((screen_width - (size+100)) / 2)
    center_y = int((screen_height - (size+100)) / 2)
    root.geometry(f"{size+100}x{size+100}+{center_x}+{center_y}")
    root.protocol("WM_DELETE_WINDOW", retour_menu)
    canvas = tk.Canvas(root, width=size, height=size, background=colorBack, highlightthickness=0)
    initialize_board()
    p1, p2 = initialize_players()
    Players_dict[0][2] = p1
    Players_dict[1][2] = p2
    colision_dict = {Players_dict[x][0]: Players_dict[x][2] for x in Players_dict.keys()}
    canvas.bind("<Button-1>", lambda event: test_event(event, against_bot))
    canvas.bind("<Button-3>", lambda event: test_event(event, against_bot))
    canvas.pack(padx=50, pady=50)
    menu.withdraw()


def retour_menu():
    root.destroy()
    menu.deiconify()


def analyser_performances_ia():
    print("\n--- DÉBUT DE L'ANALYSE DES PERFORMANCES MINIMAX ---")
    
    # On simule l'état initial du plateau (comme en début de partie)
    pos_bot = Players_dict[1][0]
    pos_joueur = Players_dict[0][0]
    arrive_bot = [i for i in range(0, length+1)]
    arrive_joueur = [i for i in range(total - length+1, total + 1)]
    dict_collisions_test = {} # Aucun mur sur le plateau
    
    # On teste jusqu'à la profondeur 4 (grâce à ton élagage Alpha-Beta)
    profondeurs_a_tester = [1, 2, 3, 4] 
    resultats = {}

    for prof in profondeurs_a_tester:
        print(f"Calcul en cours pour la profondeur {prof}...")
        
        # Lancement du chrono
        debut = time.perf_counter()
        
        # Appel de ta fonction minimax avec alpha et beta !
        minimax(prof, True, pos_bot, arrive_bot, pos_joueur, arrive_joueur, dict_collisions_test, float('-inf'), float('inf'))
        
        # Arrêt du chrono
        fin = time.perf_counter()
        
        temps_ecoule = fin - debut
        resultats[prof] = temps_ecoule
        print(f"-> Résultat : Profondeur {prof} exécutée en {temps_ecoule:.4f} secondes.\n")

    print("--- FIN DE L'ANALYSE ---")

# Add Buttons
ctk.CTkButton(menu_cadre, 
    text="Jouer contre l'IA", 
    font=("Helvetica", 14), 
    width=220, 
    height=45,
    fg_color="#8B5A2B", 
    hover_color="#A06932",
    text_color= "antique white",
    corner_radius=8,
    command=lambda: new_game(True)).pack(pady=10)

ctk.CTkButton(menu_cadre, 
    text="Jouer contre un ami", 
    font=("Helvetica", 14), 
    width=220, 
    height=45,
    fg_color="#8B5A2B", 
    hover_color="#A06932",
    text_color= "antique white",
    corner_radius=8,
    command=lambda: new_game(False)).pack(pady=(10, 40))

ctk.CTkButton(
    menu_cadre, 
    text="Règles du jeu",
    font=("Helvetica", 12),       
    width=120,                
    height=28,                 
    fg_color="#8B5A2B", 
    hover_color="#A06932",
    text_color= "antique white",
    corner_radius=8,
    command=afficher_regles 
).pack(pady=(0, 30))

ctk.CTkButton(menu_cadre, 
    text="Test de Performance IA", 
    font=("Helvetica", 14), 
    width=220, 
    height=45,
    fg_color="#5B8A72", # Vert pour le distinguer
    hover_color="#4A755F",
    text_color="antique white",
    corner_radius=8,
    command=analyser_performances_ia
).pack(pady=(0, 40))

menu.mainloop()
