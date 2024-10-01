from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from tkinter import messagebox

from PIL import Image
from PIL import ImageTk

import cv2
import numpy as np
import reportLog
import runCamera



#deeplearning stuff
net = cv2.dnn.readNet("model.weights","model.cfg")
classes = []
with open("model.names","r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
a=1
outputlayers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors={'bata':(255,255,255),'no_bata':(0,0,255)}

class App(ttk.Frame):
    def __init__(self,master=None):
        self.currbg=cv2.imread('bg.jpg',0) #Cargo la imagen de fondo que se utilizara para binarizacion
        self.cont=[0,0] #Contador de personas, posicion 0 con bata, posicion 1 sin bata
        try:
            super().__init__(master)
            self.logReport = reportLog.ReportLog()
            self.camera=runCamera.RunCamera(name="Camera1")#Inicializo la camara
            self.master=master 
            self.width=1700
            self.height=410
            self.master.geometry("%dx%d" % (self.width,self.height))
            self.pack#empaqueta la informacion
            self.panel=None #inicializa el panel vacio 
            self.lastareas=[0,0]
            self.createWidgets()
            self.createFrameZeros()
            self.logReport.logger.info("GUI Created ")#informo en el log que se inizialiso la GUI
            self.master.mainloop()#toma la info y muestra el grafico

            #fotograma anterior
            self.inframe=False
            

            
        except Exception as e:
            self.logReport.logger.error("GUI not created: " + str(e))        

    #Creo los espacios para las imagenes
    def createFrameZeros(self):
        #Real time image
        self.rtimg = tk.Label(self.master,borderwidth=2,relief="solid")
        self.rtimg.place(x=20 ,y=30)
        frame=np.zeros([360,480,3],dtype=np.uint8)#creo una matriz de 480x640 con tres canales en cada posicion
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgArray=Image.fromarray(frame)
        imgTK=ImageTk.PhotoImage(image=imgArray)
        self.rtimg.configure(image=imgTK)
        self.rtimg.image=imgTK
        
        #Evaluated frames
        self.evalimg = tk.Label(self.master,borderwidth=2,relief="solid")
        self.evalimg.place(x=530 ,y=30)
        self.evalimg.configure(image=imgTK)
        self.evalimg.image=imgTK

        #Difference binarization
        frame=np.zeros([180,240,3],dtype=np.uint8)
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgArray=Image.fromarray(frame)
        self.movimg = tk.Label(self.master,borderwidth=2,relief="solid")
        self.movimg.place(x=1050 ,y=120)
        imgTK=ImageTk.PhotoImage(image=imgArray)
        self.movimg.configure(image=imgTK)
        self.movimg.image=imgTK

    #Creo botones y texto
    def createWidgets(self):
        self.fontText=font.Font(family='Helvetica',size=13,weight='bold')
        #label tiempo real
        self.Labels = tk.Label(self.master,text="Imagen en tiempo real",fg='#000000')
        self.Labels['font'] = self.fontText
        self.Labels.place(x=20,y=5)
        #Label detect
        self.Labels = tk.Label(self.master,text="Detección",fg='#000000')
        self.Labels['font'] = self.fontText
        self.Labels.place(x=530,y=5)

        #Label Ref
        self.Labels = tk.Label(self.master,text="Referencia",fg='#000000')
        self.Labels['font'] = self.fontText
        self.Labels.place(x=1400,y=40)
        #Label Cant
        self.Labels = tk.Label(self.master,text="Cantidad",fg='#000000')
        self.Labels['font'] = self.fontText
        self.Labels.place(x=1550,y=40)
        #Bata
        self.Labels = tk.Label(self.master,text="Con bata",fg='#000000')
        self.Labels['font'] = self.fontText
        self.Labels.place(x=1400,y=90)
        self.lblBat = tk.Label(self.master,text="0",fg='#000000')
        self.lblBat['font'] = self.fontText
        self.lblBat.place(x=1550,y=90)
        #No bata
        self.Labels = tk.Label(self.master,text="Sin bata",fg='#000000')
        self.Labels['font'] = self.fontText
        self.Labels.place(x=1400,y=115)
        self.lblNobat = tk.Label(self.master,text="0",fg='#000000')
        self.lblNobat['font'] = self.fontText
        self.lblNobat.place(x=1550,y=115)
        #Total
        self.Labels = tk.Label(self.master,text="Total",fg='#000000')
        self.Labels['font'] = self.fontText
        self.Labels.place(x=1400,y=140)
        self.lblTot = tk.Label(self.master,text="0",fg='#000000')
        self.lblTot['font'] = self.fontText
        self.lblTot.place(x=1550,y=140)


        #Iniciar
        self.btnInitVideo= tk.Button(self.master,text="Iniciar",bg='#007A39',fg='#FFFFFF',width=12,command=self.initCameraProcess) #Incio/despauso
        self.btnInitVideo.place(x=1400,y=250)
        #Pausa
        self.btnStopVideo= tk.Button(self.master,text="Pausa",bg='#646464',fg='#FFFFFF',width=12,command=self.stopCameraProcess) #pauso
        self.btnStopVideo.place(x=1550,y=250)
        #step
        self.btnStopVideo= tk.Button(self.master,text="Step",bg='#0000ff',fg='#FFFFFF',width=12,command=self.stepCameraProcess) #Avanzo solo un fotograma
        self.btnStopVideo.place(x=1550,y=280)
        #exit
        self.btnExit= tk.Button(self.master,text="Salir",bg='#943535',fg='#FFFFFF',width=12,command=self.confirm_exit)
        self.btnExit.place(x=1400,y=280)

    def confirm_exit(self):
        answer = messagebox.askyesno("Confirmar salida", "¿Está seguro de que desea salir?")
        if answer:
            self.master.destroy()  # Cierra la ventana principal

    def initCameraProcess(self):
        if self.camera.paused: #si esta pausado, resumo
            self.camera.paused=False
            self.getFrameInlabel()
        elif self.camera.grabbed == None: # Si ya esta corriendo la camara, no hago nada, de lo contrario la inicio
            self.framecont=0 #inicializo el contador de cuadros
            self.camera.start()
            self.getFrameInlabel()

    def stopCameraProcess(self): 
        self.camera.paused=True
    
    def stepCameraProcess(self):
        if self.camera.paused:
            self.camera.getframe=True
            self.getFrameInlabel()
            # cv2.imwrite('bg.jpg',self.currbg)

    def getFrameInlabel(self):
        try:
            if(self.camera.grabbed):
                font = cv2.FONT_HERSHEY_PLAIN
                #Agarro las imagenes
                frameCamera=self.camera.frame
                frame=cv2.resize(frameCamera,(480,360))
                #Actualizo la imagen tiempo real
                framec=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imgArray=Image.fromarray(framec)
                imgTK=ImageTk.PhotoImage(image=imgArray)
                self.rtimg.configure(image=imgTK)
                self.rtimg.image=imgTK


                #Imagen siendo evaluada
                imgGray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                Bin1=cv2.inRange(imgGray,0,116)
                imgEval=Bin1-self.currbg
                kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)) 
                imgEval=cv2.erode(imgEval,kernel=kernel,iterations=1)
                kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2)) 
                imgEval=cv2.erode(imgEval,kernel=kernel,iterations=1)
                currarea=sum(sum(imgEval))
                
                movim=cv2.cvtColor(cv2.resize(imgEval,(240,180)), cv2.COLOR_BGR2RGB)
                imgArray=Image.fromarray(movim)
                imgTK=ImageTk.PhotoImage(image=imgArray)
                self.movimg.configure(image=imgTK)
                self.movimg.image=imgTK
                if currarea>1000:
                    self.inframe=True #Hay movimiento
                    if self.framecont>=30: #Solo evaluo uno de cada 30 cuadros
                        #Evaluar modelo aca
                        imgModel=cv2.resize(frame,(608,608))
                        height,width,channels = imgModel.shape
                        blob = cv2.dnn.blobFromImage(imgModel,0.00392,(608,608),(0,0,0),True,crop=False)
                        net.setInput(blob)
                        outs = net.forward(outputlayers)
                        class_ids=[]
                        confidences=[]
                        boxes=[]
                        for out in outs:
                            for detection in out:
                                scores = detection[5:]
                                class_id = np.argmax(scores)
                                confidence = scores[class_id]
                                if confidence > 0.5:
                                    #object detected
                                    center_x= int(detection[0]*width)
                                    center_y= int(detection[1]*height)
                                    w = int(detection[2]*width)
                                    h = int(detection[3]*height)
                                    x=int(center_x - w/2)
                                    y=int(center_y - h/2)
                                    boxes.append([x,y,w,h]) #put all rectangle areas
                                    confidences.append(float(confidence)) #how confidence was that object detected and show that percentage
                                    class_ids.append(class_id) #name of the object tha was detected
                        indexes = cv2.dnn.NMSBoxes(boxes,confidences,0.4,0.6)
                        font = cv2.FONT_HERSHEY_PLAIN
                        for i in range(len(boxes)):
                            if i in indexes:
                                x,y,w,h = boxes[i]
                                label = str(classes[class_ids[i]])
                                color = colors[label] #diccionario de clase:color. Bata es blanco, no bata es rojo
                                cv2.rectangle(imgModel,(x,y),(x+w,y+h),color,1)
                                cv2.putText(imgModel,label,(x,y+30),font,1,(255,255,255),2)

                                #Hago conteo
                                if label=='bata':
                                    self.cont[0]+=1
                                elif label=='no_bata':
                                    self.cont[1]+=1
                                #actualizo los labels
                                self.lblBat.config(text=str(self.cont[0]))
                                self.lblNobat.config(text=str(self.cont[1]))
                                self.lblTot.config(text=str(sum(self.cont)))
                        #Muestro la imagen
                        framec=cv2.cvtColor(cv2.resize(imgModel,(480,360)), cv2.COLOR_BGR2RGB)
                        imgArray=Image.fromarray(framec)
                        imgTK=ImageTk.PhotoImage(image=imgArray)
                        self.evalimg.configure(image=imgTK)
                        self.evalimg.image=imgTK
                        #reseteo el conteo de frames
                        self.framecont=0
                    #aumento 1 al conteo de frames
                    self.framecont+=1
                elif self.inframe is True:
                    self.inframe=False
                if not self.camera.paused:
                    self.rtimg.after(10,self.getFrameInlabel)#vuelvo a llamar la funcion despues de 10ms 
        except Exception as e:
            self.logReport.logger.error("error getFrameInlabel: " + str(e))   
def main():
    root=tk.Tk() #raiz de tkinter
    root.title("Detección de personas")
    appRunCamera=App(master=root) #llamo la clase App