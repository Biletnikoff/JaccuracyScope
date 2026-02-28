from picamera2 import Picamera2
from threading import Thread, Lock
import logging

logger = logging.getLogger(__name__)
import time 


class CameraThread(Thread): 

    def __init__(self): 
    
        Thread.__init__(self)
        self._lock = Lock()

        self.val1 = 1
        self.clickx = 0
        self.clicky = 0 
        self.clickxOld = 0
        self.clickyOld = 0 
        
        self.val1 = 1
        self.zoom = 1.0 
        self.zoomold = 1.0 
        
        #initial Camera Setup! 
        #instantiate the processes
        self.camera = Picamera2()
        preview_config = self.camera.create_preview_configuration(main = {"size": (240, 180)}, raw = self.camera.sensor_modes[2]) #(240, 180) (480, 360) (620, 480)
        
        #sensor Mode 2  = use 3040 as full height 
        #Sensor mode 1, use 1080 as full height 
        
        #print(preview_config)
        self.camera.configure(preview_config)
        
        print("Starting Camera...")
        self.camera.start()
        
        #self.camera.framerate = 30
        self.camera.rotation = 90
        
        time.sleep(1)
        
        self.OGsize = self.camera.capture_metadata()['ScalerCrop'][2:]
        self.full_res = self.camera.camera_properties['PixelArraySize']
        self.camera.capture_metadata()
        
        #mode zero limits 'crop_limits': (696, 528, 2664, 1980) 
        size = [int(s * self.zoom) for s in self.OGsize]   #0.0625
        offset = [(r - s) // 2 for r, s in zip(self.full_res, size)] 
        self.camera.set_controls({"ScalerCrop": offset + size , "FrameRate": (45), "Sharpness": (16)}) #, "AnalogueGain": 2.0
                
        
        self.fpsaveout = 0
        self.imageout = None

        #Create the variables needed 
        
        
        
        
        
        
        
    def get_frame(self):
        with self._lock:
            return self.imageout

    def get_fps(self):
        with self._lock:
            return self.fpsaveout

    def _run_loop(self):
        while True:
            #sleep(.1)
            #self.val1 = self.val1 +1

            #Get a frame :
            fpsave=0

            for i in range (1,30,1):
                t_start = time.time()

                (buffer, ), metadata = self.camera.capture_buffers(["main"])

                imageout = self.camera.helpers.make_image(buffer, self.camera.camera_configuration()["main"])

                if ( self.zoom != self.zoomold or self.clickx != self.clickxOld or self.clicky != self.clickyOld):
                    size = [int(s * self.zoom) for s in self.OGsize]
                    offset = [(r - s) // 2 for r, s in zip(self.full_res, size)]
                    offset[0] = offset[0] + self.clickx
                    offset[1] = offset[1] + self.clicky
                    self.camera.set_controls({"ScalerCrop": offset + size })
                    self.zoomold = self.zoom
                    self.clickxOld = self.clickx
                    self.clickyOld = self.clicky

                t_end = time.time()
                fps = -1/(t_start - t_end)
                fpsave = fpsave + (fps/30)

                with self._lock:
                    self.imageout = imageout

            with self._lock:
                self.fpsaveout = fpsave

    def run(self):
        try:
            self._run_loop()
        except Exception:
            logger.exception("Thread %s died unexpectedly", self.__class__.__name__)


#def getFrame(obj): 
#    
#        image = thread.imageout
#    
#    
#    return image #send this to the main program 
#


            
thread = CameraThread()
thread.start()

