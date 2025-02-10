# INSTALLATION

Pour installer SylvIA, il faut :

- Python version 3.11
- Avoir pip
- Utiliser le fichier requirements.txt afin de récupérer les libraires utilisées
- Avoir une carte graphique Nvidia
- Avoir installé CUDA version 11

Conseil : Faite le dans un environnement virtuel python

# LANCEMENT

Pour exécuter le logiciel principal, lancer le fichier app.py a la racine du projet<br>
```python ./app.py```

Pour le logiciel secondaire, lancer le fichier app_emergency.py a la racine du projet<br>
``python ./app_emergency.py``

# RELEASE

Pour faire une release, on utilise pyinstaller<br>
Pour lancer une release du logiciel principal, faire :<br>
``pyinstaller --onefile --icon=res/images/logo_sylvia.ico --clean --log-level=DEBUG --uac-admin .\app.py``

Sinon pour le logiciel secondaire,<br>
``pyinstaller --onefile --icon=res/images/logo_sylvia_emergency.ico --clean --log-level=DEBUG --uac-admin .\app_emergency.py``

Cela va creer un executable dans le dossier dist, ensuite recuperer celui-ci et mettre dans un dossier :
- L'exe creer
- Les 2 dossiers : res et tmp
- Le dossier de CUDA -> C:\Program Files\NVIDIA GPU Computing Toolkit

# OPTION WHISPER

Pour pouvoir regler l'appli entre vitesse et performance, voici les options a modifier dans le fichier recognizer.py :
- ligne 8 -> "small", on peux modifier la taille du modèle
- ligne 8 -> device, "cuda" pour GPU et "cpu" pour CPU
- ligne 8 -> compute_size, si "cuda" alors :
  - float16 si carte graphique Nvidia > 2000
  - float32 si carte graphique < 2000
  si CPU alors int8
- ligne 11 -> language="fr", cela permet de dire que l'on travaille sur de la langue française et que Whisper na pas besoin de chercher a reconnaitre la langue
- ligne 11 -> beam_size=1, cela permet de définir le niveau de traduction (1= traduction rapide moins précise, 5=par défaut, et au dessus de 5= traduction précise moins rapide)
- ligne 11 -> task="transcribe", dis a Whisper de faire que de la traduction
- ligne 11 -> vad_filter, dis a Whisper de ne pas gérer le début et fin de fichier audio
