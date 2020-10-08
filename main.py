# =============================================
# Application de liaison pour l'instrument lumineuneuX
# Noé G--B@TeckTC v0.1
# Dependencies : mido, python-rtmidi, DMXEnttecPro
# =============================================

import mido
import os, sys
import configparser
from DMXEnttecPro import Controller

global port, func, map_note, dmx
cfg = configparser.ConfigParser()


def init():
    global port, func, dmx, map_note
    map_note = dict()
    if not os.path.isfile('./config.cfg'):
        config()

    cfg.read("./config.cfg", encoding='utf_8')
    port = cfg.get("MIDI", "port")

    if (len(sys.argv) < 2):
        print("Lancement sans DMX")
    else:
        print("Lancement avec DMX sur le port" + sys.argv[1])
        dmx = Controller(sys.argv[1])

    if cfg.has_section("mapmidi"):
        for key in cfg['mapmidi']:
            keyint=int(key)
            map_note[keyint] = int(cfg['mapmidi'][key]) #A Proteger

    func = ["menu", "bla", "Configuration Systeme", "Ajouter/modifier mapping","Supprimer mapping", "Lancement de l'app"]

    # config restant
    # pirse en compte de la velocity


def config():
    # Config du port MIDI IN
    print("Voici les ports MIDI-IN disponibles:")
    ports = scan_po()
    i = 1
    for elt in ports:
        print(str(i) + ". : " + elt)
        i += 1
    while (True):
        try:
            port_val = input("Entrez votre numero de port ?")
            port_val = int(port_val)
            assert (port_val > 0) and (port_val < i)
            break
        except ValueError:
            print("La valeur saisie n'est pas un nombre")
        except AssertionError:
            print("La valeur saisie n'est pas valide")
    print("Vous avez choisi : " + ports[port_val - 1])
    try:
        cfg.add_section("MIDI")
    except configparser.DuplicateSectionError:
        pass
    cfg.set("MIDI", "port", ports[port_val - 1])

    cfg.write(open("./config.cfg", 'w', encoding='utf-8'))

    # Config du mapping


def config_mapp():
    global map_note
    oldnote = -1
    while (True):
        with mido.open_input(port) as inport:  # connexion VMPK-Out à RtMidi-In
            print(
                "Appuyer sur une touche du clavier MIDI\n Pour quitter ce mode rappuyer sur la dernière note configurée.")
            msg = inport.receive()
            note = msg.note
            if note == oldnote:
                break
            try:
                f = input("Entrer le channel DMX à controler avec la note " + str(note)+':\n')
                f = int(f)
                assert ((f > 0) and f < 256)
            except ValueError:
                print("La valeur saisie n'est pas un nombre")
            except AssertionError:
                print("La valeur saisie n'est pas entre 1-255")
            else:
                map_note[note] = f
            oldnote = note
    print(map_note)
    if cfg.has_section("mapmidi"):
        cfg.remove_section("mapmidi")
    cfg.add_section("mapmidi")
    cfg["mapmidi"]=map_note
    cfg.write(open("./config.cfg", 'w', encoding='utf-8'))

def suppr_mapp():
    global map_note
    oldnote = -1
    while (True):
        with mido.open_input(port) as inport:  # connexion VMPK-Out à RtMidi-In
            print(
                "Appuyer sur une touche du clavier MIDI pour supprimer son entrée dans la table de mapping\n Pour quitter ce mode rappuyer sur la dernière note configurée.")
            msgval =False
            while(msgval!=True):
                msg = inport.receive()
                if msg.type=='note_on':
                    msgval=True
            note = msg.note
            if note == oldnote:
                break
            try:
                del map_note[note]
            except KeyError:
                print("Cette note n'est pas dans la table ")
            else:
                print("Note "+str(note)+" supprimée.\n")
            oldnote = note
    print(map_note)
    if cfg.has_section("mapmidi"):
        cfg.remove_section("mapmidi")
    cfg.add_section("mapmidi")
    cfg["mapmidi"]=map_note
    cfg.write(open("./config.cfg", 'w', encoding='utf-8'))




def scan_po():
    return mido.get_input_names()


def loop_midi(name):
    # @param name : nom du port à utiliser pour recevoir le midi
    # @return : None

    print("2. == START... MIDI INPUTS SCAN ==")
    print("* Aquisition + Affichage des messages MIDI envoyés par VMPK *")
    with mido.open_input(name) as inport:  # connexion VMPK-Out à RtMidi-In
        for msg in inport:  # passe contenu 'inport' à 'msg'
            if msg.bytes() != [144, 24, 127]:  # touche Do1 pour sortir boucle acquisition messages
                print("Humain: ", msg)  # affiche contenu 'msg' Humain à l'écran
                print("  Bytes:", msg.bytes())  # affiche contenu 'msg' Bytes décimal à l'écran
                # outport.send(msg)  # envoie contenu 'msg' à RtMidi-Out vers Synth-In
            else:
                print("\nACQUISITION MIDI-IN TERMINÉE...")
                exit()  # arrête le script avec demande confirmation (fonction IDE utilisé)


def main_app():
    # attente msg midi
    # note on grada on / note off grada off
    # velocité pour courbe de grada ?
    global port
    print("== C'EST PARTI ! ==\n =Pour quitter Do1 (24) @ velocity 127=")
    print(map_note)
    print("* For debug purpose :")
    with mido.open_input(port) as inport:  # connexion VMPK-Out à RtMidi-In
        for msg in inport:  # passe contenu 'inport' à 'msg'

            if msg.note in map_note:
                if msg.type == 'note_on':
                    inten =min(255, 2*msg.velocity)
                    dmx.set_channel(map_note[msg.note], inten)  # Sets DMX channel 1 to max 255
                    dmx.submit()  # Sends the update to the controller
                    print("Note : {note}, DMX : {dmx}, Intensité : {inte}".format(note=msg.note, dmx=map_note[msg.note], inte=inten))
                elif msg.type =='note_off':
                    inten =0
                    dmx.set_channel(map_note[msg.note], inten)  # Sets DMX channel 1 to max 255
                    dmx.submit()  # Sends the update to the controller
                    print("Note : {note}, DMX : {dmx}, Intensité : {inte}".format(note=msg.note, dmx=map_note[msg.note],
                                                                                  inte=inten))

            else:
                print("Note ignorée")
            if msg.bytes() != [144, 24, 127]:  # touche Do1 pour sortir boucle acquisition messages
                pass



def menu():
    global func
    print("************************************")
    print("*        Menu Principal            *")
    print("************************************")
    print("\n")
    for i in range(len(func)):
        print(str(i) + ". " + func[i])
    print("9. Quiter")
    valide = False
    while valide != True:
        try:
            f = input("Choisissez votre action : ")
            f = int(f)
            assert ((f >= 0) and (f < len(func)) or f == 9)
            valide = True
        except ValueError:
            print("La valeur saisie n'est pas un nombre")
        except AssertionError:
            print("La valeur saisie n'est pas valide")
    return f


def bla():
    print("bla bla")


if __name__ == '__main__':
    # recuperation de la config
    init()
    global port
    while (True):
        choix = menu()
        if choix == 0:
            pass
        elif choix == 1:
            bla()
        elif choix == 2:
            config()
        elif choix == 3:
            config_mapp()
        elif choix == 4:
            suppr_mapp()
        elif choix == 5:
            main_app()
        elif choix == 9:
            exit()
    # loop_midi(port)
