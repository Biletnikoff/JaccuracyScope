"""Consolidated ballistic solver thread with optional printer and laser support."""

import ctypes
import logging
import math
import time
from threading import Thread, Lock, Event

import numpy as np
import serial
import adafruit_thermal_printer

from config import LIB_DIR

import DataPlotter as grapher

logger = logging.getLogger(__name__)

VALID_RANGES = {
    'caliber': (0.17, 1.0),
    'bullet_weight_grain': (10, 1000),
    'bc7_box': (0.01, 1.5),
    'fps_box': (100, 5000),
    'Atm_altitude': (-1000, 50000),
    'Atm_pressure': (20.0, 35.0),
    'Atm_temperature': (-60, 140),
    'Atm_RelHumidity': (0.0, 1.0),
    'zerodistance': (10, 2000),
    'windspeed': (0, 100),
}


def clamp(value, key):
    lo, hi = VALID_RANGES[key]
    return max(lo, min(hi, value))


class BallisticThread(Thread):
    """Ballistic solver thread with optional printer and laser rangefinder support."""

    def __init__(self, enable_printer=False, enable_laser=False, laser_precision=1):
        Thread.__init__(self)
        self._lock = Lock()
        self._stop_event = Event()
        self.enable_printer = enable_printer
        self.enable_laser = enable_laser
        self.laser_precision = laser_precision

        self.GNUballCLASS = ctypes.CDLL(str(LIB_DIR / "GNUball3.so"))

        self.GNUball = self.GNUballCLASS.SolveBallistic
        self.GNUball.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int,
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_double,
        ]
        self.GNUball.restype = ctypes.c_double

        self.GNUscope = self.GNUballCLASS.SolveforAngler
        self.GNUscope.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int,
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_double,
        ]
        self.GNUscope.restype = ctypes.c_double

        self.GNUp = self.GNUballCLASS.getThePosition
        self.GNUp.argtypes = [ctypes.c_double]
        self.GNUp.restype = ctypes.c_int

        self.GNUxdistance = self.GNUballCLASS.HandMeXdistance
        self.GNUxdistance.argtypes = [ctypes.c_int]
        self.GNUxdistance.restype = ctypes.c_double

        self.GNUydistance = self.GNUballCLASS.HandMeYdistance
        self.GNUydistance.argtypes = [ctypes.c_int]
        self.GNUydistance.restype = ctypes.c_double

        self.GNUdropMOA = self.GNUballCLASS.HandMeMOA
        self.GNUdropMOA.argtypes = [ctypes.c_int]
        self.GNUdropMOA.restype = ctypes.c_double

        self.GNUdriftWind = self.GNUballCLASS.HandMeWindage
        self.GNUdriftWind.argtypes = [ctypes.c_int]
        self.GNUdriftWind.restype = ctypes.c_double

        self.GNUWindageMOA = self.GNUballCLASS.HandMeWindageMOA
        self.GNUWindageMOA.argtypes = [ctypes.c_int]
        self.GNUWindageMOA.restype = ctypes.c_double

        self.GNUVnet = self.GNUballCLASS.HandMeVelocity
        self.GNUVnet.argtypes = [ctypes.c_int]
        self.GNUVnet.restype = ctypes.c_double

        self.GNUTime = self.GNUballCLASS.HandMeTime
        self.GNUTime.argtypes = [ctypes.c_int]
        self.GNUTime.restype = ctypes.c_double

        self.GNUfree = self.GNUballCLASS.free_pointer
        self.GNUfree.argtypes = [ctypes.c_int]
        self.GNUfree.restype = ctypes.c_int

        self.printerGO = False
        if self.enable_printer:
            self.uart = serial.Serial("/dev/serial0", baudrate=19200, timeout=3000)
            self.ThermalPrinter = adafruit_thermal_printer.get_printer_class(1.0)
            self.printer = self.ThermalPrinter(self.uart)
        else:
            self.uart = None
            self.ThermalPrinter = None
            self.printer = None

        if self.enable_laser:
            self.ser = serial.Serial('/dev/ttyS0', 9600, timeout=2)
            self.Lasering = False
            self.Lasercmdsingle = [0xAE, 0xA7, 0x04, 0x00, 0x05, 0x09, 0xBC, 0xBE]
            self.distancelaser = 0
            self.newLaserDistance = False
        else:
            self.ser = None
            self.Lasering = False
            self.distancelaser = 0
            self.newLaserDistance = False

        self.solver = "GNUsolver"

        self.g1_cd = [0.2629, 0.2558, 0.2487, 0.2413, 0.2344, 0.2278, 0.2214, 0.2155, 0.2104, 0.2061, 0.2032, 0.2020, 0.2034, 0.2165, 0.2230, 0.2313, 0.2417, 0.2546, 0.2706, 0.2901, 0.3136, 0.3415, 0.3734, 0.4084, 0.4448, 0.4805, 0.5136, 0.5427, 0.5677, 0.5883, 0.6053, 0.6191, 0.6393, 0.6518, 0.6589, 0.6621, 0.6625, 0.6607, 0.6573, 0.6528, 0.6474, 0.6413, 0.6347, 0.6280, 0.6210, 0.6141, 0.6072, 0.6003, 0.5934, 0.5867, 0.5804, 0.5743, 0.5685, 0.5630, 0.5577, 0.5527, 0.5481, 0.5438, 0.5397, 0.5325, 0.5264, 0.5211, 0.5168, 0.5133, 0.5105, 0.5084, 0.5067, 0.5054, 0.5040, 0.5030, 0.5022, 0.5016, 0.5010, 0.5006, 0.4998, 0.4995, 0.4992, 0.4990, 0.4988]
        self.g1_m = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.73, 0.75, 0.78, 0.8, 0.83, 0.85, 0.88, 0.9, 0.93, 0.95, 0.98, 1, 1.03, 1.05, 1.08, 1.1, 1.13, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.2, 4.4, 4.6, 4.8, 5]

        self.g7_cd = [0.1198, 0.1197, 0.1196, 0.1194, 0.1193, 0.1194, 0.1194, 0.1194, 0.1193, 0.1193, 0.1194, 0.1193, 0.1194, 0.1197, 0.1202, 0.1207, 0.1215, 0.1226, 0.1242, 0.1266, 0.1306, 0.1368, 0.1464, 0.166, 0.2054, 0.2993, 0.3803, 0.4015, 0.4043, 0.4034, 0.4014, 0.3987, 0.3955, 0.3884, 0.381, 0.3732, 0.3657, 0.358, 0.344, 0.3376, 0.3315, 0.326, 0.3209, 0.316, 0.3117, 0.3078, 0.3042, 0.301, 0.298, 0.2951, 0.2922, 0.2892, 0.2864, 0.2835, 0.2807, 0.2779, 0.2752, 0.2725, 0.2697, 0.267, 0.2643, 0.2615, 0.2588, 0.2561, 0.2533, 0.2506, 0.2479, 0.2451, 0.2424, 0.2368, 0.2313, 0.2258, 0.2205, 0.2154, 0.2106, 0.206, 0.2017, 0.1975, 0.1935, 0.1861, 0.1793, 0.173, 0.1672, 0.1618]
        self.g7_m = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.73, 0.75, 0.78, 0.8, 0.83, 0.85, 0.88, 0.9, 0.93, 0.95, 0.98, 1, 1.03, 1.05, 1.08, 1.1, 1.13, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6, 2.65, 2.7, 2.75, 2.8, 2.85, 2.9, 2.95, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.2, 4.4, 4.6, 4.8, 5]

        self.bullet_weight_grain = 150
        self.bullet_weight_lbs = self.bullet_weight_grain / 7000
        self.caliber = 0.308
        self.bc7_box = 0.242
        self.Gsolver = 7
        self.sectional_density = self.bullet_weight_lbs / (self.caliber * self.caliber)
        self.fps_box = 2600
        self.scope_height = 1.75
        self.zerodistance = 100

        self.Atm_altitude = 4000.0
        self.Atm_pressure = 29.53
        self.Atm_temperature = 59.0
        self.Atm_RelHumidity = 0.30

        self.gunSightangle = self.GNUscope(
            self.bc7_box, self.fps_box, self.scope_height, 0, self.zerodistance,
            0, 0, self.Gsolver, 0, 0, 1,
            self.Atm_altitude, self.Atm_pressure, self.Atm_temperature, self.Atm_RelHumidity,
        )

        self.alpha_ini = 4.2 / 60

        self.powder_w = 42.3 / 7000
        self.gun_w = 10.5
        self.powder_v = self.fps_box * 1.75
        self.bul_e = 0.5 * self.bullet_weight_lbs * self.fps_box * self.fps_box / 32.2
        self.bul_i = ((self.powder_w * self.powder_v) + (self.bullet_weight_lbs * self.fps_box)) / 32.2
        self.something1 = (self.powder_w + self.bullet_weight_lbs) * self.fps_box / self.gun_w
        self.gun_v = ((self.powder_w * self.powder_v) + (self.bullet_weight_lbs * self.fps_box)) / self.gun_w
        self.gun_e = 0.5 * self.gun_w * self.gun_v * self.gun_v / 32.2
        self.gun_i = self.gun_w * self.gun_v / 32.2

        self.MachSpeed = 343
        self.rho = 1.225
        self.S = 0.0000481
        self.cd = 1.6619e6
        self.m = self.bullet_weight_grain * 6.47989e-5
        self.g = 9.8065
        self.sim_max_time = 3
        self.tf = self.sim_max_time
        self.stepsize = 100
        self.dingus = self.sim_max_time / self.stepsize
        self.t0 = 0
        self.BC = 0.451 * 0.453592 / 0.0254 / 0.0254

        self.V0 = self.fps_box * 0.3048
        self.angle = math.radians(90)
        self.x0 = 0
        self.y0 = 2

        self.formfactor = self.sectional_density / self.bc7_box
        self.myg7 = np.array(self.g7_cd) * self.formfactor
        self.myg1 = np.array(self.g1_cd) * self.formfactor

        self.one_MOA = 1.047 / 100
        self.opz_aereo_y = 1

        self.x0in = 0.0
        self.y0in = 0.0
        self.Vx0in = 1
        self.Vy0in = 1
        self.targetdistin = 1
        self.elevation0in = 1

        self.MafVal = 5
        self.fpsaveout = 0

        self.facing = 10
        self.windinput = 0
        self.windspeed = 0
        self.wind_head_deg = 0

        self.dt = 0.05
        self.T = 3

        self.ScopeMode = 0
        self.maxheight = 0
        self.solution = []
        self.plotter = None
        self.ResolveAngle = False

        self.GNUxSender = np.array([50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100])
        self.GNUySender = np.zeros(len(self.GNUxSender))
        self.Toftracker = np.zeros(len(self.GNUxSender))
        self.inchdropper = np.zeros(len(self.GNUxSender))
        self.moadropper = np.zeros(len(self.GNUxSender))

    def printResults(self, x, pmoa, pinch, ptime):
        if not self.enable_printer or self.printer is None:
            return
        print('Feeding 2 lines ')
        self.printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
        self.printer.feed(1)
        self.printer.bold = True
        self.printer.print('++ Jaccuracy Scope v0.1 ++')
        self.printer.print('+++++ By Jack Toth ++++++')
        self.printer.print('***Atmospheric Conditions***')
        self.printer.bold = False
        self.printer.print('Alt(kft)= ' + str("{:.3f}".format(self.Atm_altitude / 1000)) + '  P(inHg)= ' + str("{:.2f}".format(self.Atm_pressure)))
        self.printer.print('Temp(F)= ' + str(int(self.Atm_temperature)) + '  Hum(%)= ' + str(int(self.Atm_RelHumidity * 100)))
        self.printer.print('Lat= ' + str(39.73555) + '  Long= ' + str(104.98972))
        self.printer.feed(1)
        self.printer.bold = True
        self.printer.print('***Bullet Statistics***')
        self.printer.bold = False
        self.printer.print('Cal(in)= ' + str("{:.3f}".format(self.caliber)) + '  Wght(gr)= ' + str(int(self.bullet_weight_grain)))
        self.printer.print('Vmuz(fps)= ' + str("{:.1f}".format(self.fps_box)) + '  G Model= ' + str(self.Gsolver))
        self.printer.print('BC= ' + str("{:.3f}".format(self.bc7_box)) + '  ZeroDist(yd)= ' + str(int(self.zerodistance)))
        self.printer.feed(1)
        self.printer.bold = True
        self.printer.print('*** WIND Conditions ***')
        self.printer.bold = False
        self.printer.print('Vwind(mph)= ' + str("{:.1f}".format(self.windspeed)) + 'W Dir(deg)= ' + str(int(self.wind_head_deg)))
        self.printer.feed(1)
        self.printer.bold = True
        self.printer.print('*** Shot Angle ***')
        self.printer.bold = False
        self.printer.print('Elevation  (deg) = ' + str("{:.1f}".format(self.elevation0in)))
        self.printer.feed(1)
        self.printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
        self.printer.print('*** Shot TABLE ***')
        self.printer.print('Dist(yd) Drp(MoA) Drp(in) ToF(s)')
        self.printer.print('********************************')
        for i in range(len(x)):
            self.printer.print(str("{:4.0f}".format(x[i])) + "   " + str("{:.1f}".format(-pmoa[i])) + "    " + str("{:.1f}".format(pinch[i])) + "   " + str("{:.3f}".format(ptime[i])))
        self.printer.feed(2)

    def aero(self, t, y):
        wind = self.windinput
        Vx = y[2]
        Vy = y[3]
        Vz = y[5] + wind
        angle_r = math.atan(Vy / Vx)
        Vtotal = math.sqrt((Vy * Vy) + (Vx * Vx) + (Vz * Vz))
        angle_w = math.asin(Vz / Vtotal)
        mach = Vtotal / self.MachSpeed
        q_air = 0.5 * self.rho * Vtotal * Vtotal
        Cd = np.interp(mach, self.g7_m, self.myg7)
        Fdrag = q_air * Cd * self.S
        Faereo_x = -Fdrag * math.cos(angle_r) * math.cos(angle_w)
        Faereo_z = -Fdrag * math.cos(angle_r) * math.sin(angle_w)
        Faereo_y = -Fdrag * math.sin(angle_r)
        Fgrav = -self.m * self.g
        yout1 = Vx
        yout2 = Vy
        yout3 = Faereo_x / self.m
        yout4 = (Faereo_y + Fgrav) / self.m
        yout5 = y[5]
        yout6 = Faereo_z / self.m
        yout7 = y[6]
        dy = [yout1, yout2, yout3, yout4, yout5, yout6, yout7]
        return np.array(dy)

    def rk4(self, func, dt, t0, y0):
        f1 = func(t0, y0)
        f2 = func(t0 + dt / 2, y0 + (dt / 2) * f1)
        f3 = func(t0 + dt / 2, y0 + (dt / 2) * f2)
        f4 = func(t0 + dt, y0 + dt * f3)
        yout = y0 + (dt / 6) * (f1 + (2 * f2) + (2 * f3) + f4)
        return yout

    def solveBallistics(self, x0, y0, Vx0, Vy0, dist_targ, elevation0, windinput, dt, T, scopermode):
        y00 = [x0, y0, Vx0, Vy0, 0, 0, windinput]
        num_time_pts = int(T / dt)
        t = np.linspace(0, T, num_time_pts + 1)
        Y = np.zeros((7, num_time_pts))
        outputY = np.zeros((num_time_pts + 1))
        outputDrop = np.zeros((num_time_pts + 1))
        outputheight = np.zeros((num_time_pts + 1))
        Y[:, 0] = y00
        yin = y00
        yout = [0, 0, 0, 0, 0, 0, 0]

        if scopermode == 0:
            for i in range(num_time_pts - 1):
                if (math.sqrt(yout[0] * yout[0]) + (yout[1] * yout[1])) <= dist_targ:
                    yout = self.rk4(self.aero, dt, t[i], yin)
                    Y[:, i + 1] = yout
                    yin = yout
                    outputY[i + 1] = yout[0] * 1.09361
                    outputheight[i + 1] = yout[1] * 1.09361
                    outputDrop[i + 1] = (yout[1] - y0) * 39.3701
            with self._lock:
                self.maxheight = np.max(outputheight)
            plot = grapher.plotme(outputY, outputDrop, dist_targ, 0)

        if scopermode == 1:
            for i in range(num_time_pts - 1):
                if yout[1] >= (y0 - 0.1):
                    yout = self.rk4(self.aero, dt, t[i], yin)
                    Y[:, i + 1] = yout
                    yin = yout
                    outputY[i + 1] = yout[0] * 1.09361
                    outputheight[i + 1] = yout[1] * 1.09361
                    outputDrop[i + 1] = (yout[1] - y0) * 39.3701
            with self._lock:
                self.maxheight = np.max(outputheight)
            plot = grapher.plotme(outputY, outputDrop, dist_targ, 1)

        if scopermode == 2:
            time.sleep(0.3)
            self.gunSightangle = self.GNUscope(
                self.bc7_box, self.fps_box, self.scope_height, 0, self.zerodistance,
                0, 0, self.Gsolver, 0, 0, 1,
                self.Atm_altitude, self.Atm_pressure, self.Atm_temperature, self.Atm_RelHumidity,
            )
            print("  A:" + str(self.Atm_altitude) + "  P:" + str(self.Atm_pressure) + "  T:" + str(self.Atm_temperature) + "  H:" + str(self.Atm_RelHumidity))
            print(str(self.gunSightangle))

        return yout, plot

    def stop(self):
        self._stop_event.set()

    def _run_loop(self):
        while not self._stop_event.is_set():
            fpsave = 0

            for i in range(1, self.MafVal + 1, 1):
                t_start = time.time()

                x0 = self.x0in
                y0 = self.y0in
                Vx0 = self.Vx0in
                Vy0 = self.Vy0in
                targetdist = self.targetdistin
                elevation0 = self.elevation0in

                windspeed_mps = self.windspeed * 0.44704
                wind_head_deggies = (self.facing - self.wind_head_deg)
                wind_head_rad = (self.facing - self.wind_head_deg) / 57.2958
                self.windinput = windspeed_mps * math.sin(wind_head_rad)

                if self.solver == "GNUsolver":
                    if self.ScopeMode == 0:
                        if self.fps_box <= 0 or self.bc7_box <= 0:
                            logger.warning(
                                "Invalid ballistic params: fps=%s bc=%s",
                                self.fps_box,
                                self.bc7_box,
                            )
                            time.sleep(0.1)
                            continue

                        dingusss = self.GNUball(
                            self.bc7_box, self.fps_box, self.scope_height, elevation0,
                            self.zerodistance, self.windspeed, wind_head_deggies, self.Gsolver,
                            self.gunSightangle, targetdist, 0,
                            self.Atm_altitude, self.Atm_pressure, self.Atm_temperature, self.Atm_RelHumidity,
                        )

                        position = self.GNUp(targetdist * 1.09361)
                        distancex = self.GNUxdistance(position)
                        distancey = self.GNUydistance(position)
                        self.GNUdropMOA(position)
                        Winddriffft = self.GNUdriftWind(position)
                        Windagemoaa = self.GNUWindageMOA(position)
                        netV = self.GNUVnet(position)
                        timesolveddist = self.GNUTime(position)
                        Windagemoaa = Winddriffft / (distancex * 1.047 / 100)

                        with self._lock:
                            self.solution = [distancex, distancey, netV, Winddriffft, Windagemoaa, timesolveddist, -dingusss]

                        for j in range(len(self.GNUxSender)):
                            thisposition = self.GNUp(self.GNUxSender[j] * 1.09361)
                            self.GNUySender[j] = (math.tan(elevation0 / 57.2958) * self.GNUxSender[j] * 36) + self.GNUydistance(thisposition) - distancey

                        if self.enable_printer and self.printerGO:
                            for j in range(len(self.GNUxSender)):
                                thisposition = self.GNUp(self.GNUxSender[j])
                                self.moadropper[j] = self.GNUdropMOA(thisposition)
                                self.inchdropper[j] = self.GNUydistance(thisposition)
                                self.Toftracker[j] = self.GNUTime(thisposition)
                            self.printResults(self.GNUxSender, self.moadropper, self.inchdropper, self.Toftracker)
                            self.printerGO = False

                        self.GNUfree(1)
                        plot = grapher.plotme(self.GNUxSender, self.GNUySender, targetdist, 0)
                        with self._lock:
                            self.plotter = plot

                        time.sleep(0.05)

                    elif self.ScopeMode in (2, 4):
                        time.sleep(0.3)
                        self.gunSightangle = self.GNUscope(
                            self.bc7_box, self.fps_box, self.scope_height, 0, self.zerodistance,
                            0, 0, self.Gsolver, 0, 0, 1,
                            self.Atm_altitude, self.Atm_pressure, self.Atm_temperature, self.Atm_RelHumidity,
                        )
                        print("  A:" + str(self.Atm_altitude) + "  P:" + str(self.Atm_pressure) + "  T:" + str(self.Atm_temperature) + "  H:" + str(self.Atm_RelHumidity))
                        print(str(self.gunSightangle))

                    else:
                        time.sleep(0.5)

                else:
                    sol, plot = self.solveBallistics(x0, y0, Vx0, Vy0, targetdist, elevation0, self.windinput, self.dt, self.T, self.ScopeMode)
                    with self._lock:
                        self.solution = sol
                        self.plotter = plot
                    time.sleep(0.05)

                t_end = time.time()
                fps = -1 / (t_start - t_end)
                fpsave = fpsave + (fps / self.MafVal)

            if self.enable_laser and self.ser is not None and self.Lasering:
                self.ser.write(serial.to_bytes(self.Lasercmdsingle))
                time.sleep(1)
                response = self.ser.read(27)
                recieved_data_length = len(response)

                if recieved_data_length > 8:
                    trythis = int.from_bytes(response[7:9], "big")
                    outputdata = float(trythis) * 0.1 * 1.09361
                    print("Distance measured: " + str(outputdata) + " yards")
                else:
                    print("Measrement Failed.")
                    outputdata = 0

                self.distancelaser = int(self.laser_precision * round(outputdata / self.laser_precision))
                self.newLaserDistance = True
                self.Lasering = False

            self.gunSightangle = self.GNUscope(
                self.bc7_box, self.fps_box, self.scope_height, 0, self.zerodistance,
                0, 0, self.Gsolver, 0, 0, 1,
                self.Atm_altitude, self.Atm_pressure, self.Atm_temperature, self.Atm_RelHumidity,
            )
            with self._lock:
                self.fpsaveout = fpsave

    def run(self):
        try:
            self._run_loop()
        except Exception:
            logger.exception("Thread %s died unexpectedly", self.__class__.__name__)

    def get_output(self):
        with self._lock:
            return (self.solution, self.plotter, self.fpsaveout, self.maxheight)
