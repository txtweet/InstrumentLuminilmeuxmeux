#Instrument Lumineuneu

## Instalation 
Il faut bien installer les dépendances écrites au début du fichier (et peut-être d'autres).
Le mieux c'est de faire ça dans un venv. 

Ensuite il faut lancer la configuration système pour choisir le port MIDI.
Et enfin le mapping des touches du clavier midi. 
Le mapping midi-dmx et le port midi sont sauvgardés quand vous fermez l'application.

Si l'appli ne marche plus du tout supprimer le fichier `config.cfg` peut aider. 

## Fonctionnement

Executer ``python -m DMXEnttecPro.utils`` et noter le port COM de l'adaptateur DMX 
Lancer l'application avec une commande du type ```python3 main.py <PORTCOM>``` par ex : `python3 main.py COM4` ou `python3 main.py \dev\ttyUSB`



