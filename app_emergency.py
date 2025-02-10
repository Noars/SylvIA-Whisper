import tkinter as tk
from tkinter import ttk
import threading
import sys

#Audio
import soundfile as sf
import sounddevice as sd

from prepare_citations import *
from utils import digit_format

playing_state = False

class soundBoard(ttk.Frame):
    
    def __init__(self,parent,triggers,answers,associations):

        ttk.Frame.__init__(self, parent)

        #Images / Icons
        self.icon_play = tk.PhotoImage(file = "res/images/play_bis.png")

        self.parent = parent
        self.triggers = triggers
        self.answers = answers
        self.associations = associations

        s = ttk.Style()
        s.map("Custom.Treeview", background=[("selected", "green")])
        s.map("Vertical.TScrollbar", activebackground = self.parent.cget('bg'))

        self.label_select = tk.Label(parent,text = "Select the trigger and play :")
        self.label_select.place(relx=0.005,rely=0, relwidth=.2, relheight=.1)

        #TreeView build
        self.tree= ttk.Treeview(parent, column=("c1", "c2"), show='headings', height= 8, selectmode="browse",style="Custom.Treeview")
        self.tree.heading("#1", text="Id")
        self.tree.heading("#2", text="Trigger")

        #Building rows
        for keyid in self.triggers:
            self.tree.insert(parent = "", index = "end", text = keyid, values = (keyid,self.triggers[keyid]))

        self.tree.place(relx=0.05,rely=0.1, relwidth=.8, relheight=.4)

        #Vertical Scrollbar for the tree view
        self.treeScroll = ttk.Scrollbar(parent,style="Vertical.TScrollbar")
        self.treeScroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.treeScroll.set)
        self.treeScroll.place(relx=0.85,rely=0.1, relwidth=.1, relheight=.4)

        #Play button
        self.play_button = tk.Button(parent, image = self.icon_play, bd = 0, activebackground = self.parent.cget('bg'), command = self.handler_play_button) 
        self.play_button.place(relx=0.47,rely=0.55)

        #Texts
        self.text_output = tk.Text(parent, height = 6, width = 80, bg = "white")
        self.text_output.place(relx=.5,rely=.8,anchor = tk.CENTER)

    def handler_play_button(self):
        '''Method of the play button'''

        if(self.tree.focus() != ""):

            #Prepare the recording thread in push to talk mode.
            self.rec_thread = threading.Thread(target = self.play_sound)

            #Launch the recording thread
            self.rec_thread.start()

    def play_sound(self):
        '''Method to play the selected sound'''

        self.play_button["state"] = tk.DISABLED

        item = self.tree.focus()
        row = self.tree.set(item)

        answer_id = int(get_random_answer_from_trigger(self.associations,str(row["c1"])))
        answer_text = self.answers[str(answer_id)]

        self.text_output.delete(1.0,tk.END)
        self.text_output.insert(tk.END,f"{answer_text}")

        datas,fs = sf.read("res/sounds/answers/"+digit_format(answer_id)+".wav",dtype='float32')
        sd.play(datas,fs)
        sd.wait()

        self.play_button["state"] = tk.NORMAL

class sylviaEmergencyApp():

    def __init__(self):

        #GUI initialization (Tk)
        self.root = tk.Tk()
        self.root.title("Sylvia Emergency")
        self.root.iconbitmap("res/images/logo_sylvia_emergency.ico")
        self.root.resizable(True,True)
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (width, height))

        #Images / Icons
        self.icon_play = tk.PhotoImage(file = "res/images/play.png")

        #Frames
        self.frame_scoreboard = tk.Frame(self.root,highlightbackground="green",highlightthickness=2)
        self.frame_scoreboard.place(relx=0.52,rely=0.43,relwidth=.8 ,relheight=.8, anchor = tk.CENTER)

        #Loading citations and audios
        self.triggers = get_sentence_by_id_from_csv("res/citations/declencheuse.csv")
        self.answers = get_sentence_by_id_from_csv("res/citations/reponse.csv")
        self.associations = get_association_by_id("res/citations/association.csv",triggers)

        #Soundboard
        self.soundboard = soundBoard(self.frame_scoreboard,self.triggers,self.answers,self.associations)
        self.soundboard.pack()

        #Exit button initialization
        self.button_exit = tk.Button(self.root,text = "Exit",command = self.exit_handler)
        self.button_exit.place(relx=.9,rely=0.85)

        #Start the window
        self.root.mainloop()
    

    def exit_handler(self):
        '''Handler to exit the application when clicking on "exit" button'''

        sys.exit()

if __name__ == "__main__":
    sylviaEmergencyApp()