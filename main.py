from tkinter import *
import math
from tkinter.messagebox import *
import os
import sys
import random as rd
import webbrowser
from PIL import Image, ImageTk

"""BIENVENUE DANS LE PROJET VECH CE CODE EST PEUX DOCUMENTER ETANT UN PROGRAMME DE NIVEAU PUREMENT TECHNIQUE DESTNES AUX TELECOMS 
SA CONTRIBUTION PEUT ETRE COMPLIQUER SI LE DEVELOPPEUR NE SAIT RIEN DU DOMAIN MAIS TOUTE FOIS UNE DOCUMENTATION SERA FAITE POUR LA PROCHAINE 
VERSION DU PROGRAMME """

__version__ = "1.0"
print(__doc__)

"""
def ressource_path(relative_path):
    #inclus le chemin absolu des resssources incluses
    if hasattr(sys,"_MEIPASS"):

        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)
"""


def ressource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# convertisseur binaire -> decimal / dec -> binaire

def converter(seq: str or int, identifier):
    liste1 = ['000', '001', '010', '011', '100', '101', '110', '111']
    liste2 = ['0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111',
              '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111']
    dec = 0
    bin_ = 0
    if identifier == "abc":
        # convertion decimal

        if seq not in liste1:
            for i, q in enumerate(liste1):
                if seq == i:
                    bin_ = q
                    break
            return bin_

        for i, q in enumerate(liste1):
            if seq == q:
                dec = i
                break
        return dec

    # return "la plage narrive pas a cet level"

    elif identifier == "wxyz":

        if seq not in liste2:
            for i, q in enumerate(liste2):
                if seq == i:
                    bin_ = q
                    break
            return bin_

        for i, q in enumerate(liste2):
            if seq == q:
                dec = i
                break
        return dec


# generateur de binaire de 256 bits
def binaire():
    for i in range(256):
        yield format(i, "b")


class G711:

    def __init__(self, v_echantionnage=None, vmax=None):

        self.v_dec = None
        self.vech = v_echantionnage
        self.vmax = 4096 if vmax is None else vmax
        self.pas = None
        self.vq = None
        self.vp = None
        self.ns = None
        self.ns_int = None
        self.q = None
        self.q_int = None
        self.signe = None
        if self.vech is not None:
            self.signe = 1 if self.vech >= 0 else 0

        self.sabc_etc = None  # f"{self.signe}{self.ns}{self.Q}"
        self.snr = None
        self.v_br = None

    def sequence(self):

        if self.vech is None:
            return " calcule impossible sans vech "
        elif self.vech is not None:
            # 1ere etape determination du bit de signe
            self.signe = 0 if self.vech < 0 else 1
            # 2e etape determination des bits ABC ( numero du segmant )
            # bit A
            va = self.vmax / 16
            a = 0 if va > abs(self.vech) else 1
            # bit B
            vb = self.vmax / 64 if a == 1 else self.vmax / 4
            b = 0 if vb > abs(self.vech) else 1
            # bit C
            vc = self.vmax / 2 if b == 1 else self.vmax / 128
            c = 0 if vc > abs(self.vech) else 1

            self.ns = "%s%s%s" % (a, b, c)
            self.ns_int = converter(self.ns, identifier="abc")
            self.vp = round((self.vmax / 2 ** (8 - int(self.ns_int))), 2)

            # 3e etape determination des bits WXYZ ( place du sommet sur le segment d arrive )

            # bit W
            vp = abs(self.vp)
            vw = vp + vp / 2
            w = 0 if vw > abs(self.vech) else 1

            # bit X
            vx = vp + w * (vp / 2) + vp / 4
            x = 0 if vx > abs(self.vech) else 1

            # bit Y
            vy = vp + w * (vp / 2) + x * (vp / 4) + vp / 8
            y = 0 if vy > abs(self.vech) else 1

            # bit Z
            vz = vp + w * (vp / 2) + x * (vp / 4) + y * (vp / 8) + vp / 16
            z = 0 if vz > abs(self.vech) else 1

            self.q = "%s%s%s%s" % (w, x, y, z)
            self.q_int = converter(self.q, identifier="wxyz")
            self.sabc_etc = "%s%s%s" % (self.signe, self.ns, self.q)



    def calc_pas(self):  # avec la formule ***PAS(échelon) = vp/16**

        if self.vp is None and self.pas is not None:
            self.vp = self.pas * 16
        elif self.pas is None and self.vp is not None:
            self.pas = self.vp / 16

    def calc_vq(self):  # avec la formule vq = vp + PAS * Q

        if self.vq is None and self.vp is not None and self.q_int is not None and self.pas is not None:
            self.vq = round((self.vp + self.pas * self.q_int), 2)

        elif self.vp is None and self.vq is not None and self.q_int is not None and self.pas is not None:
            self.vp = self.vq - self.pas * self.q_int

        elif self.pas is None and self.vp is not None and self.q_int is not None and self.vq is not None:
            self.pas = (self.vq - self.vp) / self.q_int

        elif self.q_int is None and self.vp is not None and self.vq is not None and self.pas is not None:
            self.q_int = int(abs(abs(self.vq) - abs(self.vp)) / round(self.pas))
            self.q = converter(self.q_int, "wxyz")

    def calc_vp(self):  # avec la formule vp = vmax/2**(8-NS)

        if self.vp is None and self.ns_int is not None:
            self.vp = self.vmax / 2 ** (8 - self.ns_int)

        elif self.ns_int is None and self.vp is not None:
            self.ns_int = int(8 - math.log2(self.vmax / abs(self.vp)))
            self.ns = converter(seq=self.ns_int, identifier="abc")

    def calc_vdec(self):  # formule vr = vq + PAS / 2

        if self.v_dec is None and self.vq is not None and self.pas is not None:
            self.v_dec = self.vq + self.pas / 2

        elif self.vq is None and self.v_dec is not None and self.pas is not None:
            self.vq = abs(self.v_dec) - self.pas / 2
            if self.v_dec < 0 or self.signe == 0:
                self.vq = float("-" + str(self.vq))

        elif self.pas is None and self.vq is not None and self.v_dec is not None:
            self.pas = 2 * (abs(self.v_dec) - abs(self.vq))

    def calc_v_br(self):  # formule vb = vech - vr

        if self.v_br is None and self.vech is not None and self.v_dec is not None:
            self.v_br = round((abs(abs(self.vech) - abs(self.v_dec))), 3)
            if self.vech < 0 or self.v_dec < 0 or self.signe == 0:
                self.v_br = float("-" + str(self.v_br))

        elif self.vech is None and self.v_br is not None and self.v_dec is not None:
            self.vech = round((abs(abs(self.v_br) - abs(self.v_dec))), 3)
            if self.v_br < 0 or self.v_dec < 0 or self.signe:
                self.vech = float("-" + str(self.vech))

        elif self.v_dec is None and self.vech is not None and self.v_br is not None:
            self.v_dec = round((abs(abs(self.vech) - abs(self.v_br))), 3)
            if self.vech < 0 or self.v_br < 0 or self.signe:
                self.v_dec = float("-" + str(self.v_dec))

    def calc_snr(self):  # formule s/b = 20 log(abs(vech) / vbr)

        if self.snr is None and self.vech is not None and self.v_br is not None:
            self.snr = round((20 * math.log10(abs(self.vech) / abs(self.v_br))), 2)
            """if self.snr < 0:
                pass
            elif not self.snr < 0 and (self.v_br < 0 or self.signe < 0):
                    self.snr = float("-"+str(self.snr))"""

        elif self.vech is None and self.snr is not None and self.v_br is not None:
            self.vech = abs(self.v_br) * 10 ** (abs(self.snr) / 20)
            if self.v_br < 0 or self.snr < 0 or self.signe ==0 :
                self.vech = float("-" + str(self.vech))

        elif self.v_br is None and self.vech is not None and self.snr is not None:
            self.v_br = abs(self.vech) / 10 ** (abs(self.snr) / 20)

    def calc_sabc_etc(self):

        if self.signe is None and self.sabc_etc is not None:
            self.signe = str(self.sabc_etc).split(".")
            self.signe = self.signe[0][0]
        if self.ns is None and self.sabc_etc is not None:
            self.ns = str(self.sabc_etc).split(".")
            self.ns = self.ns[0][1:3 + 1]
            self.ns_int = converter(self.ns, "abc")
        if self.q is None and self.sabc_etc is not None:
            self.q = str(self.sabc_etc).split(".")
            self.q = self.q[0][4:8]
            self.q_int = converter(self.q, "wxyz")
        if self.sabc_etc is None and self.signe is not None and self.ns is not None and self.q is not None:
            self.sabc_etc = "%s%s%s" % (self.signe, self.ns, self.q)

        if self.ns_int is None and self.sabc_etc is not None:
            self.ns_int = converter(str(self.sabc_etc[1:3 + 1]), "wxyz")
            self.ns = converter(self.ns_int, "abc")
        if self.q_int is None and self.sabc_etc is not None:
            self.q_int = converter(str(self.sabc_etc[3:]), "wxyz")
            self.q = converter(self.q_int, "wxyz")
        if self.sabc_etc is None and self.signe is not None and self.ns_int is not None and self.q_int is not None:
            self.sabc_etc = "%s%s%s" % (self.signe, converter(self.ns_int, "abc"), converter(self.q_int, "wxyz"))

    def caller(self):

        if self.ns is not None:
            if "01" not in str(self.ns):
                self.ns_int = self.ns
                self.ns = converter(self.ns_int, "abc")

        if self.q is not None:
            if "01" not in str(self.q):
                self.q_int = self.q
                self.q = converter(self.q_int, "wxyz")

        """CEtte Methode appelle toutes les fonctions pour calculer les elements"""
        if list((self.__dict__.values())).count(None) <= 5:
            showwarning("exception", "valeur non suffissante pour les calculs")
            return True
        loi_codage.set("processing...")
        root.after(1000, lambda: label_codage.config(text="resultat"))
        compteur = 0
        while None in list(self.__dict__.values()):
            compteur += 1
            self.sequence()
            self.calc_sabc_etc()
            self.calc_pas()
            self.calc_vp()
            self.calc_snr()
            self.calc_vdec()
            self.calc_vq()
            self.calc_v_br()


            # print(list(self.__dict__.values()))

            # if list(self.__dict__.values()).count(None) < 7:
            #   break
            if compteur == 700:
                break

        self.affichage()
        # print(self.__dict__)


    @staticmethod
    def affichage():
        e_ns.config(validatecommand="")
        e_Q.config(validatecommand="")
        e_sabcetc.config(validatecommand="")
        if g711.signe == 0:
            vech.set(g711.vech)
            loi_codage.set("le signe est negatif il affecte les tensions ")
            c_vp.set(
                str(int(g711.vp)) + "= -" + str(int(g711.vp)) if g711.vp is not None else str(g711.vp) + "= -" + str(
                    g711.vp))
            c_vq.set(str(g711.vq) + "= -" + str(g711.vq))
            c_vr.set(str(g711.v_dec) + "= -" + str(g711.v_dec))

            c_pas.set(str(g711.pas))
            c_snr.set(str(g711.snr))
            c_Q.set(str(g711.q) + " place Numero " + str(g711.q_int))
            c_ns.set(str(g711.ns) + " numero de segment " + str(g711.ns_int))
            c_v_br.set(str(g711.v_br))
            c_sabcetc.set(str(g711.sabc_etc))

        else:
            loi_codage.set("G711")
            vech.set(g711.vech)
            c_vp.set(str(int(g711.vp)) if g711.vp is not None else str(g711.vp))
            c_vq.set(str(g711.vq))
            c_vr.set(str(g711.v_dec))
            c_pas.set(str(g711.pas))
            c_snr.set(str(g711.snr))
            c_Q.set(str(g711.q) + " place Numero " + str(g711.q_int))
            c_ns.set(str(g711.ns) + " numero de segment " + str(g711.ns_int))
            c_sabcetc.set(str(g711.sabc_etc))
            c_v_br.set(str(g711.v_br))

        g711.__init__()
        # loi_codage.set("Vech_Project")
        e_ns.config(validatecommand=vcmd_ns)
        e_Q.config(validatecommand=vcmd_q)
        e_sabcetc.config(validatecommand=vcmd)


# -----------FONCTIONS DE VALIDATIONS---------------

# validations pour lentree vs
def est_binaire(value):
    # verifie que la chaine ne ccomprend que des 0 ou des 1
    return all(char in "01" for char in value)


def compris_0_7(value: str):
    # verifie que la chaine est un chiffre entre 0 et 7
    return value.isdigit() and 0 <= int(value) <= 7


def est_len_valide(value):
    # verifie que la chaine est de 3 caracteres
    return len(value) <= 3


def valider_ns(value):
    if not est_len_valide(value):
        showwarning(title="Validation", message="La longueur maximal est de 3 caracteres")
        return False
    if not (est_binaire(value) or compris_0_7(value)):
        showwarning("Validation", "L entrée doit être en binaire \nou un chiffre entre 0 et 7")
        return False

    return True


def on_validate_input_ns(p):
    if valider_ns(p):
        return True
    return False


# validatioon pour WXYZ


def compris_0_15(value: str):
    # verifie que la chaine est un chiffre entre 0 et 15
    return value.isdigit() and 0 <= int(value) <= 15


def est_len_valide_q(value):
    # verifie que la chaine nexcee pas 4 caracteres
    return len(value) <= 4


def valider_q(value):
    if not est_len_valide_q(value):
        showwarning(title="Validation", message="La longueur maximal est de 4 caracteres")
        return False
    if not (est_binaire(value) or compris_0_15(value)):
        showwarning("Validation", "L entrée doit être en binaire \nou un chiffre entre 0 et 15")
        return False
    return True


def on_validate_input_q(p):
    if valider_q(p):
        return True
    return False


# validation sabc_etc
def validate_input(char):
    if char in ("0", "1", ""):
        return True
    else:
        showwarning("Validation", "L entrée doit être en binaire")
        return False


def validate_len(var):
    value = var.get()
    if len(value) == 8 or value == "":
        return True
    else:
        e_sabcetc.config(bg="red")
        showwarning("Validation", "le champs doit contenir 8 bits ou etre vide ")
        return False


def on_validate_input_sabc(char):
    return validate_input(char)


def on_validate_len():
    if not validate_len(c_sabcetc):
        e_sabcetc.config(bg="#12B329")
        c_sabcetc.set("")
        return True
    return False


def valuerror():
    showerror(title="entrée invalide", message=" veuillez entree une valeur Numerique")


def vmaxerror():
    showerror(title="ERREUR",
              message="veuillez resignez au moins un autre champs que vmax \ncalcul impossible avec vmax seul")


def binaryerror():
    showerror(title="VALEUR EN BINAIRE", message=" veuillez renseignez ce champs en binaire")


def sabcerror(p):
    return len(p) > 8


def reinit(event=None):
    e_sabcetc.config(validatecommand="")
    g711.__init__()
    c_vmax.set("4096")
    for i in WIDGET_ENTREE:
        if i != e_vmax:
            i.delete(0, END)
    loi_codage.set(" reinitialiser toujours apres une validation")
    e_sabcetc.config(validatecommand=vcmd)


def quit_app():
    label_codage.config(bg="white", font="lobster 50 bold")
    loi_codage.set("NyBye")
    root.after(1000, lambda: root.destroy())


def valider(event):

    if on_validate_len():
        return
    VALUES = ([WIDGET_ENTREE[i].get() for i in range(len(WIDGET_ENTREE))])
    VALUES.remove(c_vmax.get())
    # validation des entrees
    # verifier que au moins un champs outre que vmaxnest pas vide
    # print(VALUES)

    # verifie si tout les entree sont vides
    VALUES.append(c_vmax.get())
    if all(x == "" for x in VALUES):
        for i in WIDGET_ENTREE:
            i.config(bg="red")
        showwarning("entree invalide", " veuillez resignez les champs")
        for i in WIDGET_ENTREE:
            i.config(bg=bg_entree)
        return
    VALUES.remove(c_vmax.get())
    if all(x == "" for x in VALUES):
        vmaxerror()
        return

    # verifie si la valeur de chaque entre est une valeur numerique

    for i in WIDGET_ENTREE:

        if i.get() != "":
            try:
                float(i.get())

            except ValueError:
                i.config(bg="red")
                showwarning("silvousplait", "veuillez entree une valeur numerique")
                i.config(bg=bg_entree)
                return

    for i in WIDGET_ENTREE:
        if i.get():
            if i.winfo_name() != "sabc_etc" or i.winfo_name() != "ns" or i.winfo_name() != "q":
                g711.__setattr__(i.winfo_name(), float(i.get()))
            if i.winfo_name() == "sabc_etc" or i.winfo_name() == "ns" or i.winfo_name() == "q":
                g711.__setattr__(i.winfo_name(), i.get())

    # print("DANS VALIDER")
    # print(g711.__dict__.values())

    if g711.caller():
        return
import tkinter.ttk


def open_descr():
    win = Toplevel(root)
    win.title("NylockDEv")
    win.geometry("1000x400")
    win.config(bg="#59C3FF")

    win.update_idletasks()
    print(win.winfo_width())
    w = 500
    h = 450
    cnv = Canvas(win, width=w, height=h,bg="#59C3FF" )
    cnv.create_image(0, 0, anchor=NW, image=image)
    cnv.pack(side=LEFT, pady=20, padx=10,expand=1)

    cadre = Frame(win,bg="#59C3FF")
    # police
    ft = ("times new romn",15,"bold")
    cadre.pack(side=LEFT,expand=1)
    Label(cadre,text="Auteur: Adou Kouadio Toussaint",font=ft,bg="#59C3FF").pack(expand=1,pady=10)
    Label(cadre, text="Email: adoutoussaint5@gmail.com", font=ft,bg="#59C3FF").pack(pady=10)
    Label(cadre,text="Github: @AdouToussaint", font=ft,bg="#59C3FF").pack(pady=10)
    btn = Button(cadre, text="Visitez le compte github",
                 font=ft,command= lambda : webbrowser.open("http://github.com/AdouToussaint"),
                 activebackground="#52D8FF",
                 bg="#D954C4"
                 )
    btn.pack(pady=20,fill= X,padx=30)







g711 = G711()
root = Tk()
image = PhotoImage(file=ressource_path("images/logo1.gif"))

MonMenu = Menu(root)
Apropos = Menu(MonMenu,postcommand="",tearoff=0)
Apropos.add_command(label= "A propos",activebackground="blue",command= lambda : loi_codage.set("Hello world"))
Apropos.add_command(label="Auteur",activebackground="blue",command=open_descr)

MonMenu.add_cascade(label = "A propos",menu=Apropos)
MonMenu.add_command(label= "Quitter",command=root.quit)

root.config(menu=MonMenu)





# root.attributes("-fullscreen",True)
path = ressource_path("images/vech.GIF")
root.title("projet Vech")
root.iconphoto(False, PhotoImage(file=path))
root.geometry("+10+10")

LANCEMENT = root.mainloop

# -----------------les variables ----------------
# codageg711 = G711()
bg_entree = "ivory"
bg_error = "red"

# font des label_elements
label_elmt_font = ("arial", 11, "bold")
entree_font = "lobster 12 bold"
# largeurs des entrees
width_elmt = 15
# ----------------------------------------

# -------------GRAPHISME------------------
# creation dun canevas pour le logo de lApp
# instanciation de limage
cadre1 = Frame(root)
cadre1.pack(side=TOP, fill=X)
path2 = ressource_path("images/vech2.gif")
logo = PhotoImage(file=path2)
canevas = Canvas(cadre1, width=310, height=90)
canevas.pack(side=LEFT, pady=20, padx=10)
canevas.create_image(165, 37, image=logo)

# ncreation dun label qui affiche G711
loi_codage = StringVar()
label_codage = Label(cadre1,
                     textvariable=loi_codage,
                     font=("helvetica", 20, "bold"),
                     border=1, borderwidth=12,
                     highlightthickness=2,
                     bg="lightgrey"
                     )

label_codage.pack(side=RIGHT, padx=50)
# creation de cadre pour les autres elemnts
cadre2 = Frame(root, width=900, height=1000, highlightthickness=2, relief=SUNKEN)
cadre2.pack(side=TOP, anchor=CENTER, pady=5, padx=15)

# ajout des widgets sur le cadre
# labelframe echantillon

label_frame_ech = LabelFrame(cadre2, text="Echantillon")
label_frame_ech.pack(side=LEFT, padx=40)

# ajout des entrees
label_vech = Label(label_frame_ech, text=" Tension echantillonnage (Vech) en mw", font=label_elmt_font)
label_vech.grid(row=0, column=0, padx=5)
# entree de vech
# variable de controle de vech
vech = StringVar()
e_vech = Entry(label_frame_ech, textvariable=vech, name="vech", bg=bg_entree, width=width_elmt, font=entree_font)
e_vech.grid(row=1, column=0, padx=5)

# label vmax
label_vmax = Label(label_frame_ech, text="Tension maximale (Vmax) en mw", font=label_elmt_font)
label_vmax.grid(row=0, column=1, padx=5)
# variable de controle de vmax
c_vmax = StringVar()
# entree
e_vmax = Entry(label_frame_ech, textvariable=c_vmax, name="vmax", bg=bg_entree, width=width_elmt, font=entree_font)
e_vmax.grid(row=1, column=1)

# label frame pour la loi de codage

label_frame_loi = LabelFrame(cadre2, text="Loi de Codage", padx=2, pady=2, )
label_frame_loi.pack(side=RIGHT, padx=7)

# boutons radios G711 et Uniforme
loi = StringVar(value="G711")


def lb():
    loi_codage.set(loi.get())


radio_g711 = Radiobutton(label_frame_loi, text="G711", padx=2, value="G711", variable=loi,
                         command=lb, state=DISABLED)

radio_uniforme = Radiobutton(label_frame_loi,
                             text=" Uniforme",
                             value="Uniforme",
                             variable=loi,
                             padx=2,
                             command=lb,
                             state=DISABLED)
# packing
radio_g711.pack(side=LEFT, padx=3)
radio_uniforme.pack(side=LEFT, padx=3)
loi_codage.set(loi.get())  # on affiche la loi choisie dans le label a cote du logo qui afffiche G711 par defaut

# creation dun troisieme cadre

cadre3 = Frame(root, padx=20, pady=20)
cadre3.pack(side=TOP, fill=X)
# creation des labels et entrees
# numero segment ABC

c_ns = StringVar(value=None)
label_ns = Label(cadre3, text="Numero de segment (ABC)", font=label_elmt_font)
label_ns.grid(row=0, column=0, pady=5)
# entree
# validation
vcmd_ns = (root.register(on_validate_input_ns), "%P")
e_ns = Entry(cadre3, textvariable=c_ns, name="ns", bg=bg_entree, width=width_elmt, font=entree_font, validate="key",
             validatecommand=vcmd_ns)

e_ns.grid(row=0, column=1, pady=5, padx=7)

# pace de sommet WXYZ

c_Q = StringVar()
label_Q = Label(cadre3, text="Numero de sommet sur le  segment (WXYZ)", font=label_elmt_font)
label_Q.grid(row=1, column=0, pady=5)
# entree
# validation
vcmd_q = (root.register(on_validate_input_q), "%P")
e_Q = Entry(cadre3, textvariable=c_Q, name="q", bg=bg_entree, width=width_elmt, font=entree_font, validate="key",
            validatecommand=vcmd_q
            )

e_Q.grid(row=1, column=1, pady=5, padx=7)

# tension de piedestal

c_vp = StringVar()
label_vp = Label(cadre3, text="Tension de piedestal (vp) en mw", font=label_elmt_font)
label_vp.grid(row=2, column=0, pady=5)
# entree
e_vp = Entry(cadre3, textvariable=c_vp, bg=bg_entree, name="vp", width=width_elmt, font=entree_font)
e_vp.grid(row=2, column=1, pady=5, padx=7)

# pas de quantification

c_pas = StringVar()
label_pas = Label(cadre3, text="Pas en mw", font=label_elmt_font)
label_pas.grid(row=0, column=3, padx=15, pady=5)
# entree
e_pas = Entry(cadre3, textvariable=c_pas, name="pas", bg=bg_entree, width=width_elmt, font=entree_font)
e_pas.grid(row=0, column=4, pady=5)

# tension quantifié

c_vq = StringVar()
label_vq = Label(cadre3, text="Tension Quantifié (vq) en mw", font=label_elmt_font)
label_vq.grid(row=1, column=3, padx=15, pady=5)
# entree
e_vq = Entry(cadre3, textvariable=c_vq, name="vq", bg=bg_entree, width=width_elmt, font=entree_font)
e_vq.grid(row=1, column=4, pady=5)

# rapport s/b


c_snr = StringVar()
label_snr = Label(cadre3, text=" SNR (rapport S/B) en dB", font=label_elmt_font)
label_snr.grid(row=2, column=3, padx=15, pady=5)
# entree
e_snr = Entry(cadre3, textvariable=c_snr, name="snr", bg=bg_entree, width=width_elmt, font=entree_font)
e_snr.grid(row=2, column=4, pady=5)

# les boutons

Button(cadre3, text=" QUITTER", bg="#FE002D", width=13, command=quit_app).grid(row=1, column=2, pady=7, padx=17)
Button(cadre3, text=" REINITIALISER", bg="#FEE84F", command=reinit).grid(row=2, column=2, pady=7, padx=17)

# tension decode

label_dec = Label(root, text="Tension Decodé ou Restitué (VB) en mw", font=label_elmt_font)
label_dec.pack(side=TOP, pady=5)
# entree
c_vr = StringVar()
e_vr = Entry(root, textvariable=c_vr, name="v_dec", width=width_elmt, font=entree_font, bg=bg_entree)
e_vr.pack(side=TOP, pady=2)

# tension bruit

label_v_br = Label(root, text="Tension du bruit (Vbr) en mw", font=label_elmt_font)
label_v_br.pack(side=TOP, pady=5)
# entree
c_v_br = StringVar()
e_v_br = Entry(root, textvariable=c_v_br, name="v_br", width=width_elmt, font=entree_font, bg=bg_entree)
e_v_br.pack(side=TOP, pady=5)

# code binaire
c_sabcetc = StringVar()
frame = LabelFrame(root, text="echantillon decodé", pady=5, width=100, font="12")
frame.pack(pady=18)

vcmd = (root.register(on_validate_input_sabc), "%S")
e_sabcetc = Entry(frame, textvariable=c_sabcetc, name="sabc_etc", font="courrier 14 bold", bg="#12B329", width=50,
                  fg="blue", validate="key",
                  highlightbackground="#12B329",
                  validatecommand=vcmd)

e_sabcetc.pack(expand=1, padx=10)
# e_sabcetc.bind("<KeyRelease>", sabcerror)

# ------------bindigs--------------------
"""
for widget in label_frame_ech.winfo_children():
    if isinstance(widget, Entry):
        widget.bind("<Return>", valider)

for widget in cadre3.winfo_children():
    if isinstance(widget, Entry):
        widget.bind("<Return>", valider)

e_vr.bind("<Return>", valider)
e_sabcetc.bind("<Return>", valider)
"""
# liste qui rassembles tous les widgets entree

root.bind("<Return>", valider)
root.bind("<Key-r>",reinit)
# liste qui rassamble tous les widgets entree
WIDGET_ENTREE = []

widget_entree_root = ([i for i in root.winfo_children() if isinstance(i, Entry)])
# frame a un seul widget entry
widget_entree_ech = ([i for i in label_frame_ech.winfo_children() if isinstance(i, Entry)])
widget_entree_cadre3 = ([i for i in cadre3.winfo_children() if isinstance(i, Entry)])

for i in widget_entree_root:
    WIDGET_ENTREE.append(i)
for i in widget_entree_ech:
    WIDGET_ENTREE.append(i)
for i in widget_entree_cadre3:
    WIDGET_ENTREE.append(i)
for i in frame.winfo_children():
    WIDGET_ENTREE.append(i)
# print(WIDGET_ENTREE)
# dictionnaire avec une clé avec le nom du widget et lobjet widjet lui meme

WIDGET = ({widget.winfo_name(): widget for widget in WIDGET_ENTREE})

# dictionnaires qui rassemble toute les valeurs  des widgets entre

# definition dune couleur de fond de focus
# creation de Menu



LANCEMENT()
