"""Sensor thread for IMU, magnetometer, and rotary encoders."""

import logging
import math
import time
from threading import Thread, Lock, Event

import board
import numpy as np
from adafruit_lsm6ds import GyroRange
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
from adafruit_seesaw import seesaw, rotaryio, digitalio
from mmc5983_2 import MMC5983

logger = logging.getLogger(__name__)


class SensorThread(Thread):
    """Reads IMU (ISM330DHCX), magnetometer (MMC5983MA), and rotary encoders.

    Provides orientation, compass heading, and encoder positions via thread-safe
    getters. Runs as a daemon thread.
    """

    def __init__(self) -> None:
        Thread.__init__(self)
        self._lock = Lock()
        self._stop_event = Event()

        self.pitch = 0
        self.output_heading = 0
        self.roll = 0
        self.fpsaveout = 0

        i2c = board.I2C()

        self.accSensor = ISM330DHCX(i2c, 0x6b)

        self.seesaw1 = seesaw.Seesaw(i2c, addr=0x37, reset=True)
        self.seesaw2 = seesaw.Seesaw(i2c, addr=0x36, reset=True)

        self.seesaw1.pin_mode(24, self.seesaw1.INPUT_PULLUP)
        self.enc1_button = digitalio.DigitalIO(self.seesaw1, 24)
        self.enc1_button_held = False

        self.seesaw2.pin_mode(24, self.seesaw2.INPUT_PULLUP)
        self.enc2_button = digitalio.DigitalIO(self.seesaw2, 24)
        self.enc2_button_held = False

        self.encoder1 = rotaryio.IncrementalEncoder(self.seesaw1)
        self.enc1_last_position = 0

        self.encoder2 = rotaryio.IncrementalEncoder(self.seesaw2)
        self.enc2_last_position = 0

        self.encoder1Output = 0
        self.encoder2Output = 0

        self.mmc = MMC5983(i2cbus=1)

        self.declinationAngle = 10 - 7.85 - 3

        self.MafVal = 3

        self.rollmaker = np.zeros(self.MafVal)
        self.pitchmaker = np.zeros(self.MafVal)
        self.wobble2xmaker = np.zeros(self.MafVal)
        self.wobble2ymaker = np.zeros(self.MafVal)
        self.leadmaker = np.zeros(self.MafVal)
        self.headmaker = 0
        self.compassx = np.zeros(self.MafVal)
        self.compassy = np.zeros(self.MafVal)
        self.compassz = np.zeros(self.MafVal)

        self.lead = 0
        self.wobbleY = 0
        self.wobbleX = 0

        self.xoffset = 371.0
        self.yoffset = -2326.5
        self.zoffset = -117.50

        self.xscale = 7808.0
        self.yscale = 7643.50
        self.zscale = 7807.50

        self.cal()

        self.gyrox = 0
        self.gyroy = 0
        self.gyroz = 0

        self.gyroFixX = 0.004734205596034618
        self.gyroFixY = -0.010995574287564275
        self.gyroFixZ = 0.0030543261909900766

        self.accSensor.gyro_range = GyroRange.RANGE_125_DPS

    def convertToheading(self, rawX: float, rawY: float, rawZ: float) -> float:
        """Convert raw magnetometer values to compass heading in degrees."""
        _normX = (rawX - self.xoffset) / self.xscale
        normY = (rawY - self.yoffset) / self.yscale
        normZ = (rawZ - self.zoffset) / self.zscale

        heading_r = math.atan2(-normZ, -normY)

        heading_deg = heading_r * (180 / math.pi) - self.declinationAngle + 180

        if heading_deg < 0:
            heading_deg = heading_deg + 360

        return heading_deg

    def cal(self) -> None:
        """Run magnetometer calibration."""
        self.mmc.calibrate()

    def stop(self) -> None:
        self._stop_event.set()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            fpsave = 0
            for i in range(1, self.MafVal + 1, 1):
                t_start = time.time()
                try:
                    self.data = self.mmc.read_data()
                except OSError as e:
                    logger.warning("Magnetometer read failed: %s", e, exc_info=True)
                    if not hasattr(self, 'data'):
                        continue

                self.compassx[i - 1] = self.data.x_raw
                self.compassy[i - 1] = self.data.y_raw
                self.compassz[i - 1] = self.data.z_raw

                output_accX = 0
                output_accY = 0
                output_accZ = 0
                for attempt in range(3):
                    try:
                        output_accX = self.accSensor.acceleration[0]
                        output_accY = self.accSensor.acceleration[1]
                        output_accZ = self.accSensor.acceleration[2]
                        break
                    except OSError:
                        if attempt == 2:
                            logger.error("I2C read failed after 3 attempts")
                        time.sleep(0.01 * (2 ** attempt))

                try:
                    self.gyrox = self.accSensor.gyro[0] - self.gyroFixX
                    self.gyroy = self.accSensor.gyro[1] - self.gyroFixY
                    self.gyroz = self.accSensor.gyro[2] - self.gyroFixZ
                except OSError as e:
                    logger.warning("Gyro read failed: %s", e, exc_info=True)
                    self.gyrox = 0
                    self.gyroy = 0
                    self.gyroz = 0

                self.leadmaker[i - 1] = self.gyroy
                self.wobble2xmaker[i - 1] = self.gyroz
                self.wobble2ymaker[i - 1] = self.gyroy
                self.pitchmaker[i - 1] = math.atan2(
                    output_accZ, math.sqrt((output_accY * output_accY) + (output_accX * output_accX))
                )
                self.rollmaker[i - 1] = math.atan2(
                    output_accY, math.sqrt((output_accX * output_accX) + (output_accZ * output_accZ))
                )

                time.sleep(0.01)
                t_end = time.time()
                fps = -1 / (t_start - t_end)
                fpsave = fpsave + (fps / self.MafVal)

            try:
                self.enc1_position = -self.encoder1.position
                self.enc2_position = -self.encoder2.position
            except OSError as e:
                logger.warning("Encoder position read failed: %s", e, exc_info=True)
                self.enc1_position = 0
                self.enc2_position = 0

            try:
                if self.enc1_position != self.enc1_last_position and self.enc1_position < 2147000000:
                    self.encoder1Output = self.enc1_position - self.enc1_last_position
                    self.enc1_last_position = self.enc1_position
                if not self.enc1_button.value and not self.enc1_button_held:
                    self.enc1_button_held = True
                if self.enc1_button.value and self.enc1_button_held:
                    self.enc1_button_held = False
                if self.enc2_position != self.enc2_last_position and self.enc2_position < 2147000000:
                    self.encoder2Output = self.enc2_position - self.enc2_last_position
                    self.enc2_last_position = self.enc2_position
                if not self.enc2_button.value and not self.enc2_button_held:
                    self.enc2_button_held = True
                if self.enc2_button.value and self.enc2_button_held:
                    self.enc2_button_held = False
            except OSError as e:
                logger.warning("Encoder/button read failed: %s", e, exc_info=True)

            self.lead = np.average(self.leadmaker)
            self.pitch = np.average(self.pitchmaker)
            self.roll = np.average(self.rollmaker)
            self.wobbleX = np.std(self.wobble2xmaker) * 10000
            self.wobbleY = np.std(self.wobble2ymaker) * 10000
            self.output_heading = self.convertToheading(
                np.average(self.compassx), np.average(self.compassy), np.average(self.compassz)
            )

            with self._lock:
                self.fpsaveout = fpsave

    def run(self) -> None:
        try:
            self._run_loop()
        except Exception:
            logger.exception("Thread %s died unexpectedly", self.__class__.__name__)

    def get_orientation(self) -> tuple:
        """Return (pitch, roll, lead, wobbleX, wobbleY) (thread-safe)."""
        with self._lock:
            return (self.pitch, self.roll, self.lead, self.wobbleX, self.wobbleY)

    def get_encoders(self) -> tuple:
        """Return (encoder1Output, encoder2Output) delta positions (thread-safe)."""
        with self._lock:
            return (self.encoder1Output, self.encoder2Output)

    def get_compass(self) -> float:
        """Return compass heading in degrees (thread-safe)."""
        with self._lock:
            return self.output_heading

    def get_fps(self) -> float:
        """Return the current sensor read FPS (thread-safe)."""
        with self._lock:
            return self.fpsaveout

    def consume_encoder1(self) -> None:
        """Reset encoder 1 delta to 0 (thread-safe)."""
        with self._lock:
            self.encoder1Output = 0

    def consume_encoder2(self) -> None:
        """Reset encoder 2 delta to 0 (thread-safe)."""
        with self._lock:
            self.encoder2Output = 0
