"""Camera capture thread for Pi Camera via picamera2."""

import time
from threading import Thread, Lock

from picamera2 import Picamera2

import logging

logger = logging.getLogger(__name__)


class CamThread(Thread):
    """Captures frames from the Pi Camera in a background thread.

    Provides thread-safe access to the latest frame and FPS measurement.
    fps_mode: 'fast' (45 FPS, no auto-exposure) or 'slow' (38 FPS, auto-exposure).
    """

    def __init__(self, fps_mode='fast') -> None:
        Thread.__init__(self)
        self._lock = Lock()
        self.fps_mode = fps_mode

        self.val1 = 1
        self.clickx = 0
        self.clicky = 0
        self.clickxOld = 0
        self.clickyOld = 0

        self.zoom = 1.0
        self.zoomold = 1.0

        self.camera = Picamera2()
        preview_config = self.camera.create_preview_configuration(
            main={"size": (240, 180)}, raw=self.camera.sensor_modes[2]
        )

        self.camera.configure(preview_config)

        print("Starting Camera...")
        self.camera.start()

        self.camera.rotation = 90

        time.sleep(1)

        self.OGsize = self.camera.capture_metadata()['ScalerCrop'][2:]
        self.full_res = self.camera.camera_properties['PixelArraySize']
        self.camera.capture_metadata()

        size = [int(s * self.zoom) for s in self.OGsize]
        offset = [(r - s) // 2 for r, s in zip(self.full_res, size)]
        if self.fps_mode == 'fast':
            self.camera.set_controls({"ScalerCrop": offset + size, "FrameRate": (45), "Sharpness": (16)})
        else:
            self.camera.set_controls({
                "ScalerCrop": offset + size,
                "FrameRate": (38),
                "Sharpness": (16),
                "AeEnable": (True),
                "AeConstraintMode": 0,
                "AeExposureMode": 0,
            })
                
        
        self.fpsaveout = 0
        self.imageout = None

        #Create the variables needed 
        
        
        
        
        
        
        
    def get_frame(self) -> object:
        """Return the latest captured frame (thread-safe)."""
        with self._lock:
            return self.imageout

    def get_fps(self) -> float:
        """Return the current frames-per-second measurement (thread-safe)."""
        with self._lock:
            return self.fpsaveout

    def _run_loop(self) -> None:
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

    def run(self) -> None:
        try:
            self._run_loop()
        except Exception:
            logger.exception("Thread %s died unexpectedly", self.__class__.__name__)



