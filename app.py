import tkinter as tk
from tkinter import filedialog as fd
from turtle import back
import wave
import os
import sys
import time
import threading
import subprocess
import codecs
import json
import numpy as np
import torch

#Audio
import pyaudio
import soundfile as sf
import sounddevice as sd

#Data
import pandas as pd
import csv

#Speech Recognition
import speech_recognition as sr

#Text to Speech
import pyttsx3

#Modules
from textGenerator import TextGenerator
from recognizer import Recognizer
from recorder import Recorder
from sentsim import cer_sentences_similarity,windowed_cer_sentences_similarity
from prepare_citations import *
from utils import check_connection,clean_transcription,digit_format,get_key_from_value

class sylviaApp():

    def __init__(self):

        #GUI initialization (Tk)
        self.root = tk.Tk()
        self.root.title("Sylvia")
        self.root.iconbitmap("res/images/logo_sylvia.ico")
        self.root.resizable(True,True)
        self.root.state('zoomed')

        #Image icons
        self.icon_micro = tk.PhotoImage(file = "res/images/micro.png")
        self.icon_square = tk.PhotoImage(file = "res/images/square.png")
        self.icon_sylvia = tk.PhotoImage(file = "res/images/sylvia.png")
        self.icon_sylvia_activate = tk.PhotoImage(file = "res/images/sylvia_activate.png")
        self.icon_sylvia_recording = tk.PhotoImage(file = "res/images/sylvia_recording.png")
        self.icon_sylvia_talking = tk.PhotoImage(file = "res/images/sylvia_talking.png")
        self.icon_on = tk.PhotoImage(file = "res/images/on.png")
        self.icon_off = tk.PhotoImage(file = "res/images/off.png")

        #Frames
        self.frame_settings = tk.Frame(self.root)#,highlightbackground="blue",highlightthickness=2)
        self.frame_settings.place(relx=0.7,y=0, relwidth=.3, relheight=.9)
        self.frame_sylvia = tk.Frame(self.root)#,highlightbackground="blue",highlightthickness=2)
        self.frame_sylvia.place(x=0,y=0,relwidth=.7 ,relheight=.9)


        #Labels
        self.label_intro = tk.Label(self.frame_sylvia,text = "Sylvia vous souhaite la bienvenue.")
        self.label_intro.place(x=10,rely=0.03)

        #Texts
        self.text_output = tk.Text(self.frame_sylvia, height = 10, width = 70, bg = "white")
        self.text_output.place(relx=.7,rely=.7,anchor = tk.CENTER)

        self.text_timing = tk.Text(self.frame_settings, height = 3, width = 20, bg = "light green")
        self.text_timing.place(relx=.5,rely=0.7,anchor = tk.CENTER)
        #Mode selection (push to talk, detection, etc.)
        self.label_intro = tk.Label(self.frame_settings,text = "Mode selection :")
        self.label_intro.place(relx=.5,rely=0.03,anchor = tk.CENTER)
        self.modes = ["Push to Talk","Activity Detection"]
        self.selected_mode = tk.StringVar(self.frame_settings)
        self.selected_mode.set(self.modes[0])
        self.mode_menu = tk.OptionMenu(self.frame_settings,self.selected_mode,*self.modes,command=self.mode_switch)
        self.mode_menu.place(relx=.5,rely=0.07,anchor = tk.CENTER)
        
        #File browser
        self.button_open = tk.Button(self.frame_settings,text = "Browse Triggers", command = self.browser_handler,state = tk.DISABLED)

        #Record button initialization
        self.button_rec = tk.Button(self.frame_sylvia,text = "Click",command = self.record_click_handler_ptt,image = self.icon_micro,bd = 0,activebackground = self.root.cget('bg'))
        self.button_rec.place(relx=.7,rely=.4,anchor=tk.CENTER)
        #Exit button initialization
        self.button_exit = tk.Button(self.root,text = "Exit",command = self.exit_handler)
        self.button_exit.place(relx=.9,rely=0.89)

        #Timer initialization
        self.label = tk.Label(self.frame_sylvia,text = "00:00:00")
        self.label.place(relx=.7,rely=.5,anchor=tk.CENTER)

        #Wait before transcribe slider
        self.label_bt = tk.Label(self.frame_settings,text = "Wait before transcribe :")
        self.label_bt.place(relx=.5,rely=0.36,anchor = tk.CENTER)
        self.slider_bt = tk.Scale(self.frame_settings, from_=0, to=5, resolution=0.1, orient = tk.HORIZONTAL)
        self.slider_bt.set(1)
        self.slider_bt.place(relx=.5,rely=0.40,anchor = tk.CENTER)

        #Energy threshold slider
        self.label_threshold = tk.Label(self.frame_settings,text = "Energy threshold :")
        self.label_threshold.place(relx=.5,rely=0.48,anchor = tk.CENTER)
        self.slider_threshold = tk.Scale(self.frame_settings, from_=0, to=200, resolution=1, length=300, orient = tk.HORIZONTAL)
        self.slider_threshold.set(25)
        self.slider_threshold.place(relx=.5,rely=0.52,anchor = tk.CENTER)

        #Recognition threshold slider
        self.label_recoth = tk.Label(self.frame_settings, text = "Recognition threshold :")
        self.label_recoth.place(relx=.5, rely=0.58, anchor = tk.CENTER)
        self.slider_recoth = tk.Scale(self.frame_settings, from_=0, to=100, resolution=1, length=300, orient = tk.HORIZONTAL)
        self.slider_recoth.set(80)
        self.slider_recoth.place(relx=.5, rely=0.62, anchor = tk.CENTER)

        #Recording state initialization
        self.record_state = False
        self.rec_thread = None

        #Initialization of the recognizer (asr)
        self.recognizer = Recognizer()
        #Initialization of the microphone
        self.mic = pyaudio.PyAudio()

        self.reco_history = [""] * 5

        #Audio
        self.recorder = Recorder()
        self.recorder.close()

        #Loading citations and audios
        self.triggers = get_sentence_by_id_from_csv("res/citations/declencheuse.csv")
        self.answers = get_sentence_by_id_from_csv("res/citations/reponse.csv")
        self.associations = get_association_by_id("res/citations/association.csv",triggers)

        def changeInput():
            self.inputDevice = self.get_first_input_device_by_name(self.selected_micro.get())

        #Microphone menu initialization
        self.label_intro = tk.Label(self.frame_settings,text = "Microphone selection :")
        self.label_intro.place(relx=.5,rely=0.15,anchor = tk.CENTER)
        self.devices = self.get_microphones()
        self.selected_micro = tk.StringVar(self.frame_settings)
        self.selected_micro.set(self.devices[0])
        self.micro_menu = tk.OptionMenu(self.frame_settings,self.selected_micro,*self.devices, command=lambda value: changeInput())
        self.micro_menu.place(relx=.5,rely=0.19,anchor = tk.CENTER)
        changeInput()

        def changeOutput():
            sd.default.device = self.get_first_output_device_by_name(self.selected_output.get())

        #Output menu initialization
        self.label_output_intro = tk.Label(self.frame_settings,text = "Output selection :")
        self.label_output_intro.place(relx=.5,rely=0.25,anchor = tk.CENTER)
        self.devices_output = self.get_output_audio()
        self.selected_output = tk.StringVar(self.frame_settings)
        self.selected_output.set(self.devices_output[0])
        self.output_menu = tk.OptionMenu(self.frame_settings,self.selected_output,*self.devices_output, command=lambda value: changeOutput())
        self.output_menu.place(relx=.5,rely=0.29,anchor = tk.CENTER)
        changeOutput()

        #Check button for the history
        self.check_histo_var = tk.IntVar()
        self.check_histo = tk.Checkbutton(self.frame_settings,text = "Speech History",variable = self.check_histo_var, onvalue = 1, offvalue=0)
        self.check_histo.place(relx=.5,rely=0.8,anchor = tk.CENTER)

        #Check button for text generation
        self.check_gen_var = tk.IntVar()
        self.check_gen = tk.Checkbutton(self.frame_settings,text = "Text Generation",variable = self.check_gen_var, onvalue = 1, offvalue=0)
        self.check_gen.place(relx=.5,rely=0.85,anchor = tk.CENTER)

        #Check button for automatic voice or not
        self.check_voice_var = tk.IntVar()
        self.check_voice = tk.Checkbutton(self.frame_settings,text = "Robotic Voice",variable = self.check_voice_var, onvalue = 1, offvalue=0)
        self.check_voice.place(relx=.5,rely=0.90,anchor = tk.CENTER)

        #Text Generator
        self.tts_engine = pyttsx3.init()

        #Loading dataset to train
        self.citations = []

        for keyid in self.answers:

            self.citations.append(self.answers[str(keyid)])

        #Ngram model
        self.text_generator = TextGenerator(n = 3)
        self.text_generator.train(self.citations)

        #Start the window
        self.root.mainloop()

    def mode_switch(self,*args):
        '''Method to switch mode (push to talk / activity detection)'''

        if(str(self.selected_mode.get()) == "Push to Talk"):
            self.button_rec.config(image = self.icon_micro)
            self.button_rec.config(command = self.record_click_handler_ptt)
            self.label.place(relx=.7,rely=.5,anchor=tk.CENTER)
        
        elif(str(self.selected_mode.get()) == "Activity Detection"):
            self.button_rec.config(image = self.icon_sylvia)
            self.button_rec.config(command = self.record_click_handler_ad)
            self.label.place_forget()
    
    def wifi_switch(self):
        '''Method to switch mode between wifi or not connected'''

        if(self.wifi_state):
            self.button_switch_wifi.config(image = self.icon_off)
            self.wifi_state = False
        else:
            self.button_switch_wifi.config(image = self.icon_on)
            self.wifi_state = True

    
    def get_microphones(self):
        '''Method to get the list of available record devices'''

        audio = pyaudio.PyAudio()
        dev_infos = audio.get_host_api_info_by_index(0)
        num_dev = dev_infos.get('deviceCount')
        devices = []

        for i in range(0,num_dev):
            if(audio.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')) > 0:
                devices.append(audio.get_device_info_by_host_api_device_index(0,i).get('name'))

        audio.terminate()
        
        return devices

    def get_output_audio(self):
        """Retourne une liste des périphériques de sortie disponibles."""
        audio = pyaudio.PyAudio()
        dev_infos = audio.get_host_api_info_by_index(0)
        num_dev = dev_infos.get('deviceCount')  
        output_devices = []

        for i in range(0,num_dev):
            if(audio.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')) > 0:
                output_devices.append(audio.get_device_info_by_host_api_device_index(0,i).get('name'))

        audio.terminate()
        return output_devices

    def record_click_handler_ptt(self):
        '''Handler to begin recording or end recording following the state'''

        #Start recording
        if self.record_state == False:
            self.record_state = True
            self.button_rec.config(image = self.icon_square)
            self.mode_menu.config(state = tk.DISABLED)

            #Prepare the recording thread in push to talk mode.
            self.rec_thread = threading.Thread(target = self.listen_push_to_talk)

            #Launch the recording thread
            self.rec_thread.start()

        #End recording
        else:
            self.record_state = False
            #Disable the record button
            self.button_rec.config(state = tk.DISABLED)
            self.button_rec.config(image = self.icon_micro)

    def record_click_handler_ad(self):
        '''Handler to begin recording or end recording following the state'''

        #Start recording
        if self.record_state == False:
            self.record_state = True
            self.button_rec.config(image = self.icon_sylvia_activate)
            self.mode_menu.config(state = tk.DISABLED)

            #Prepare the recording thread in activity detection mode.
            self.rec_thread = threading.Thread(target = self.listen_activity_detection)

            #Launch the recording thread
            self.rec_thread.start()

        #End recording
        else:
            self.record_state = False
            #Disable the record button
            self.button_rec.config(state = tk.DISABLED)
            self.button_rec.config(image = self.icon_sylvia)
            
    def browser_handler(self):
        '''Handler to browse csv files'''
        
        filename = fd.askopenfilename(title = 'Select a .csv file',initialdir='/app')
        print(filename)
    
    def exit_handler(self):
        '''Handler to exit the application when clicking on "exit" button'''

        sys.exit()

    def get_first_input_device_by_name(self, target_name):
        """Retourne l'ID du premier périphérique d'entré correspondant au nom donné."""
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            if device['name'] == target_name and device['max_input_channels'] > 0:
                return i  # Retourne le premier ID correspondant
        
        return None 

    def get_first_output_device_by_name(self, target_name):
        """Retourne l'ID du premier périphérique de sortie correspondant au nom donné."""
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            if device['name'] == target_name and device['max_output_channels'] > 0:
                return i  # Retourne le premier ID correspondant
        
        return None        

    def listen_activity_detection(self):
        '''Method to record until the record state becomes False from activity detection'''

        transcripting = False
        recording = False
        frames = []
        last_sound_time = None

        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16, 
            channels=1,rate=16000,
            input=True,
            frames_per_buffer=1024,
            input_device_index=self.inputDevice)

        print("Écoute du microphone...")

        while self.record_state:

            #Capture de l'audio
            audio_data = stream.read(1024, exception_on_overflow=False)

            #Calcul du volume (amplitude moyenne)
            rms_val = self.recorder.rms(audio_data)

            if rms_val > self.slider_threshold.get() and not transcripting:
                self.button_rec.config(image = self.icon_sylvia_recording)
                if not recording:
                    print("Début de l'enregistrement...")
                    recording = True
                    frames = []  # Reset les frames
                    
                last_sound_time = time.time()

            elif recording and (time.time() - last_sound_time >= self.slider_bt.get()):
                #Arrêt de l'enregistrement
                print("Fin de l'enregistrement. Transcription en cours...")
                asr_time_start = time.time()
                recording = False
                transcripting = True
                    
                #Sauvegarde en WAV
                soundfile = wave.open("tmp/output.wav","wb")
                soundfile.setnchannels(1)
                soundfile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                soundfile.setframerate(16000)
                soundfile.writeframes(b"".join(frames))
                soundfile.close()

                #Transcription avec Whisper
                transcription = self.recognizer.decode("tmp/output.wav")

                if(transcription == ""):
                    transcription = None

                self.text_timing.delete(1.0,tk.END)
                self.text_timing.insert(tk.END,f"Decoder: {int(time.time() - asr_time_start):02d}s")

                #Handling history
                if(self.check_histo_var.get() == 1 and transcription != None):
                    self.reco_history.pop(0)
                    self.reco_history.append(transcription)

                #transcription = check_history(self.reco_history)
                
                if(transcription != None) :
                    #Get the closest sentence(s) of the input from WER evaluation
                    cer_sim = windowed_cer_sentences_similarity(transcription,get_sentence_from_dict(self.triggers))

                    if(cer_sim[1] >= self.slider_recoth.get()/100):

                        if(self.check_gen_var.get() == 1):
                                
                            input_text = "<start> <start> <start>"#cer_sim[0]
                            result = self.text_generator.predict_text(str(input_text))

                            self.text_output.delete(1.0,tk.END)
                            self.text_output.insert(tk.END,f"Received : {transcription}\n\nPredicted trigger : {cer_sim[0]}\n\nCitation : {result}")

                            #Read the closest citation
                            self.tts_engine.say(str(result))
                            self.tts_engine.runAndWait()

                        else:

                            answer_id = int(get_random_answer_from_trigger(self.associations,str(get_key_from_value(self.triggers,cer_sim[0]))))
                            answer_text = self.answers[str(answer_id)]


                            self.text_output.delete(1.0,tk.END)
                            self.text_output.insert(tk.END,f"Received : {transcription}\n\nPredicted trigger : {cer_sim[0]}\n\nCitation : {answer_text}")

                            self.button_rec.config(image = self.icon_sylvia_talking)

                            if(self.check_voice_var.get() == 0):
                                answer = digit_format(answer_id)
                                path = "res/sounds/answers/"+answer+".wav"
                                #If the .wav file exists
                                if(os.path.exists(path)):
                                    datas,fs = sf.read(path,dtype='float32')
                                    sd.play(datas,fs)
                                    sd.wait()

                                #Else, plays the default answer
                                else:
                                    datas,fs = sf.read("res/sounds/answers/0001.wav",dtype='float32')
                                    sd.play(datas,fs)
                                    sd.wait()
                                
                            else:

                                #Read the closest citation
                                self.tts_engine.say(str(answer_text))
                                self.tts_engine.runAndWait()
                            
                        #Reset the history
                        self.reco_history = [""] * 5

                    #Display the non recognized trigger
                    else:
                        self.text_output.delete(1.0,tk.END)
                        self.text_output.insert(tk.END,f"Received : {transcription}\n\nNot recognized as a trigger")

                transcripting = False   
                self.button_rec.config(image = self.icon_sylvia_activate)

            else:
                self.button_rec.config(image = self.icon_sylvia_activate)

            if recording and not transcripting:
                frames.append(audio_data)  # Stocker l'audio
                    
        #Enable the record button
        stream.stop_stream()
        self.button_rec.config(image = self.icon_sylvia)
        self.button_rec.config(state = tk.NORMAL)
        self.mode_menu.config(state = tk.NORMAL)

    def listen_push_to_talk(self):
        '''Method to record until the record state becomes False from push to talk'''

        #Begin timer
        start = time.time()

        #Initialize audio recorder and stream
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16, 
            channels=1, rate=16000, 
            input=True, 
            frames_per_buffer=1024, 
            input_device_index=self.inputDevice
            )

        frames = []
        
        while self.record_state:
            data = stream.read(1024)
            frames.append(data)

            #Update the label of the timer
            passed = time.time() - start
            s = passed % 60
            m = passed // 60
            h = m // 60
            self.label.config(text=f"{int(h):02d}:{int(m):02d}:{int(s):02d}")

        #Close stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        asr_time_start = time.time()

        #Audio (WAV) file
        soundfile = wave.open("tmp/output.wav","wb")
        soundfile.setnchannels(1)
        soundfile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        soundfile.setframerate(16000)
        soundfile.writeframes(b"".join(frames))
        soundfile.close()

        self.label.config(text = "00:00:00")

        #Decode
        transcription = self.recognizer.decode("tmp/output.wav")

        self.text_timing.delete(1.0,tk.END)
        self.text_timing.insert(tk.END,f"Decoder: {int(time.time() - asr_time_start):02d}s")

        if(transcription != None) :

            #Get the closest sentence(s) of the input from WER evaluation
            cer_sim = windowed_cer_sentences_similarity(transcription,get_sentence_from_dict(self.triggers))

            if(cer_sim[1] >= self.slider_recoth.get()/100):

                if(self.check_gen_var.get() == 1):

                    input_text = "<start> <start> <start>"#cer_sim[0]
                    result = self.text_generator.predict_text(str(input_text))

                    self.text_output.delete(1.0,tk.END)
                    self.text_output.insert(tk.END,f"Received : {transcription}\n\nPredicted trigger : {cer_sim[0]}\n\nCitation : {result}")

                    #Read the closest citation
                    self.tts_engine.say(str(result))
                    self.tts_engine.runAndWait()

                else:

                    answer_id = int(get_random_answer_from_trigger(self.associations,str(get_key_from_value(self.triggers,cer_sim[0]))))
                    answer_text = self.answers[str(answer_id)]


                    self.text_output.delete(1.0,tk.END)
                    self.text_output.insert(tk.END,f"Received : {transcription}\n\nPredicted trigger : {cer_sim[0]}\n\nCitation : {answer_text}")

                    if(self.check_voice_var.get() == 0):
                        answer = digit_format(answer_id)
                        path = "res/sounds/answers/"+answer+".wav"

                        #If the .wav file exists
                        if(os.path.exists(path)):
                            datas,fs = sf.read(path,dtype='float32')
                            sd.play(datas,fs)
                            sd.wait()
                                    
                        #Else, plays the default answer
                        else:
                            datas,fs = sf.read("res/sounds/answers/0001.wav",dtype='float32')
                            sd.play(datas,fs)
                            sd.wait()
                            
                    else:

                        #Read the closest citation
                        self.tts_engine.say(str(answer_text))
                        self.tts_engine.runAndWait()

            #Display the non recognized trigger
            else:
                self.text_output.delete(1.0,tk.END)
                self.text_output.insert(tk.END,f"Received : {transcription}\n\nNot recognized as a trigger")
        
        #Enable the record button
        self.button_rec.config(state = tk.NORMAL)
        self.mode_menu.config(state = tk.NORMAL)


def check_history(history, n = 4):
    '''Function to check the history of the transcription to avoid cut'''

    history_text = history[-n]
    size = len(history)

    for i in range((size - n), size, 1):

        if(history[i] != "" and history[i] != None):

            if(history_text == ""):
                history_text = history[i]

            else:
                history_text = history_text + ' ' + history[i]

    return history_text


if __name__ == "__main__":
    os.environ["CUDA_HOME"] = "./NVIDIA GPU Computing Toolkit/CUDA/v11.8"
    os.environ["PATH"] += ";./NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin"
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True
    sylviaApp()