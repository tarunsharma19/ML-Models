# Importing Libraries

import numpy as np

import cv2
import os, sys
import time
import operator

from string import ascii_uppercase

import tkinter as tk
from PIL import Image, ImageTk

# from hunspell import Hunspell
from spylls.hunspell import Dictionary
import enchant

from keras.models import model_from_json

os.environ["THEANO_FLAGS"] = "device=cuda, assert_no_cpu_op=True"

#Application :

class Application:

    def __init__(self):

        self.hs = Dictionary.from_files('en_US')
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        self.json_file = open("Models\model_new_abcd.json", "r")
        self.model_json = self.json_file.read()
        self.json_file.close()

        self.loaded_model = model_from_json(self.model_json)
        self.loaded_model.load_weights("Models\model_new.h5")

        self.json_file_dru = open("Models\model-bw_dru.json" , "r")
        self.model_json_dru = self.json_file_dru.read()
        self.json_file_dru.close()

        self.loaded_model_dru = model_from_json(self.model_json_dru)
        self.loaded_model_dru.load_weights("Models\model-bw_dru.h5")
        self.json_file_tkdi = open("Models\model-bw_tkdi.json" , "r")
        self.model_json_tkdi = self.json_file_tkdi.read()
        self.json_file_tkdi.close()

        self.loaded_model_tkdi = model_from_json(self.model_json_tkdi)
        self.loaded_model_tkdi.load_weights("Models\model-bw_tkdi.h5")
        self.json_file_smn = open("Models\model-bw_smn.json" , "r")
        self.model_json_smn = self.json_file_smn.read()
        self.json_file_smn.close()

        self.loaded_model_smn = model_from_json(self.model_json_smn)
        self.loaded_model_smn.load_weights("Models\model-bw_smn.h5")

        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0

        for i in ascii_uppercase:
          self.ct[i] = 0
        
        print("Loaded model from disk")
        self.answer = ['C','B','A']

        self.root = tk.Tk()
        self.root.title("Sign Language Quiz POC")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("900x900")

        self.panel = tk.Label(self.root)
        self.panel.place(x = 100, y = 10, width = 580, height = 580)
        
        self.panel2 = tk.Label(self.root) # initialize image panel
        self.panel2.place(x = 400, y = 65, width = 275, height = 275)

        self.T = tk.Label(self.root)
        self.T.place(x = 60, y = 5)
        self.T.config(text = "Sign Language Quiz", font = ("Courier", 30, "bold"))

        self.panel3 = tk.Label(self.root) # Current Symbol
        self.panel3.place(x = 500, y = 540)

        self.T1 = tk.Label(self.root)
        self.T1.place(x = 10, y = 540)
        self.T1.config(text = "Character :", font = ("Courier", 30, "bold"))

        self.panel4 = tk.Label(self.root) # Word
        self.panel4.place(x = 220, y = 595)

        self.T2 = tk.Label(self.root)
        self.T2.place(x = 10,y = 595)
        self.T2.config(text = "1+1 is ? a)3, b)2, c)4 , d) 1", font = ("Courier", 30, "bold"))


        self.T4 = tk.Label(self.root)
        self.T4.place(x = 250, y = 690)
        self.T4.config(text = "Correct :", fg = "red", font = ("Courier", 30, "bold"))

        self.bt1 = tk.Button(self.root, command = self.action1, height = 0, width = 0)
        self.bt1.place(x = 26, y = 745)



        self.str = ""
        self.word = " "
        self.current_symbol = "Empty"
        self.photo = "Empty"
        self.video_loop()
        #demo answer

    def video_loop(self):
        ok, frame = self.vs.read()
        self.answer = ['B']
        if ok:
            cv2image = cv2.flip(frame, 1)

            x1 = int(0.5 * frame.shape[1])
            y1 = 10
            x2 = frame.shape[1] - 10
            y2 = int(0.5 * frame.shape[1])

            cv2.rectangle(frame, (x1 - 1, y1 - 1), (x2 + 1, y2 + 1), (255, 0, 0) ,1)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)

            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image = self.current_image)

            self.panel.imgtk = imgtk
            self.panel.config(image = imgtk)

            cv2image = cv2image[y1 : y2, x1 : x2]

            gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)

            blur = cv2.GaussianBlur(gray, (5, 5), 2)

            th3 = cv2.adaptiveThreshold(blur, 255 ,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            self.predict(res)

            self.current_image2 = Image.fromarray(res)

            imgtk = ImageTk.PhotoImage(image = self.current_image2)

            self.panel2.imgtk = imgtk
            self.panel2.config(image = imgtk)

            self.panel3.config(text = self.current_symbol, font = ("Courier", 30))

            self.panel4.config(text = self.word, font = ("Courier", 30))

            if len(self.word)>1 and self.word[-1] == self.answer[-1]:
                self.bt1.config(text ="Correct Answer", font = ("Courier", 20), bg='green')
            elif len(self.word)>1:
                self.bt1.config(text ="Wrong Answer", font = ("Courier", 20), bg='red')

        self.root.after(5, self.video_loop)

    def predict(self, test_image):

        test_image = cv2.resize(test_image, (128, 128))

        result = self.loaded_model.predict(test_image.reshape(1, 128, 128, 1))

        prediction = {}

        prediction['blank'] = result[0][0]

        inde = 1

        for i in ['A','B','C','D']:

            prediction[i] = result[0][inde]

            inde += 1

        #LAYER 1

        prediction = sorted(prediction.items(), key = operator.itemgetter(1), reverse = True)

        self.current_symbol = prediction[0][0]

        if(self.current_symbol == 'blank'):

            for i in ascii_uppercase:
                self.ct[i] = 0

        self.ct[self.current_symbol] += 1

        if(self.ct[self.current_symbol] > 60):
            print("========================================",self.ct[self.current_symbol],self.current_symbol)
            if self.current_symbol == 'A':
                print("A")
            
            if self.current_symbol == 'B' or self.current_symbol == 'K' or self.current_symbol == 'U':
                print("B")
            
            if self.current_symbol == 'C' or self.current_symbol == 'O' or self.current_symbol == 'X' or self.current_symbol == 'Z':
                print("C")
            
            if self.current_symbol == 'D':
                print("D")

            self.blank_flag = 0

            if self.current_symbol != 'blank':
                self.word += self.current_symbol

            self.ct[self.current_symbol] = 0

    def action1(self):

        ans = self.word
        if ans == self.answer[0] :
            self.str += "Correct Answer"


    def action2(self):

        ans = self.word
        if ans == self.answer[0] :
            self.str += "Correct Answer"

    def action3(self):

        ans = self.word
        if ans == self.answer[0] :
            self.str += "Correct Answer"
    	

    def action4(self):

        ans = self.word
        if ans == self.answer[0] :
            self.str += "Correct Answer"

    def action5(self):

        ans = self.word
        if ans == self.answer[0] :
            self.str += "Correct Answer"
            
    def destructor(self):

        print("Closing Application...")

        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()
    
print("Starting Application...")

(Application()).root.mainloop()