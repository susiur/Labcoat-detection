import reportLog
import cv2
import threading
import numpy as np

class RunCamera():
    def __init__(self,src='video.mp4',name="CameraThread"):
        try:
            self.name=name
            print('src: ',src)
            self.src=src
            self.logreport=reportLog.ReportLog()
            self.capture=None
            self.grabbed=None
            self.paused=None
            self.getframe=False

            self.logreport.logger.info("Init runcamera process")
        except Exception as e:
            self.logreport.logger.error("error runcamera process: " +str(e))
    def start(self):#agarra la primera frame
        try:
            self.capture=cv2.VideoCapture(self.src)
            self.grabbed,self.frame=self.capture.read()
            if(self.capture.isOpened()):
                self.cameraThread = threading.Thread(target=self.get,name=self.name, daemon=True)#creo un hilo paralelo: (funcion que correra,nombre de la thread, daemon decide si cierro el hilo cuando cierro la aplicacion)
            self.cameraThread.start() #corro la thread
        except Exception as e:
            self.logreport.logger.error("error runcamera.start: " +str(e))

    def get(self):#agarra los frames de la camara
        try:            
            while self.grabbed:
                #Si esta pausado, no hago nada
                if self.paused:
                    cv2.waitKey(100)
                    #si esta pausado, pero estan solicitando fotograma, mando un solo fotograma y reseteo la solicitud
                    if self.getframe:
                        self.grabbed,self.frame = self.capture.read()
                        self.getframe=False
                    continue
                cv2.waitKey(30)
                self.grabbed,self.frame = self.capture.read()
                if not self.grabbed:
                    break
        except Exception as e:
            self.logreport.logger.error("error runcamera.getframe: " +str(e))
            