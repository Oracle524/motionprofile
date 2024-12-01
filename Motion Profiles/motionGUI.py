# |ROBT 3341 - Motion Profiles|------------------------------------------------
#
# Project: ROBT 3341 - Motion Profiles
# Program: motionGUI.py
#
# Description:
#   This program expects allows students to interact with the motion profiles
# that they design for ROBT 3341 Assignment #4. Each tab will aid with a 
# different part of the assignemnt.
#
# Tab 1: Motion Profile
#   This tab expects a module called motionProfile that contains a function 
# called motion. The tab will display the equations of motion based on the 
# start position, end position, and the total time given for the motion.
#
#   This program is designed to help students with the development of their
# own motion profiles while introducing them to Python programming.
#
#   The development of this program is completed for the BCIT Mechatronics and
# Robotic program for the ROBT 3341 Module on Motion Profiles.
#
# Classes:
#   - motionProfileGUI
#
# Execution:
#   Executing this script will open a GUI.
#
# Getting Started:
#   Set up an anaconda virtual environment with the packages shown below
# installed.
#
# v0.241115 - Initial Release
# v0.241116 - Joint Interpolation
# v0.241117 - Joint Interpolation++
# v1.241118 - Final Release
# v1.241128 - Fixed bugs with Position Checking and passing time as a list.
# v1.241128 - Some more bugs fixed, callbacks are called backwards...
#
# Author: Isaiah Regacho
# 
# Date Created: November 13, 2024
# Last Modified: November 28, 2024
# -----------------------------------------------------------------------------

# |Package Version Control|----------------------------------------------------
# Python 3.12.7 
#   conda create --name MotionProfiler
#   conda activate MotionProfiler
#   conda install python=3.12
#
# Package              | Version    : Command
# ==================== | ========== : =========================================
# matplotlib           | 3.9.2      : conda install matplotlib
# pandas               | 2.2.2      : conda install pandas
# ==================== | ========== : =========================================
# -----------------------------------------------------------------------------

# |PACKAGES|-------------------------------------------------------------------
import itertools
import izygui
import motionProfile

from izythread import TimedThread
from pandas import DataFrame
from math import pi, cos, sin, atan2, floor, ceil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.pyplot import subplots, tight_layout, subplots_adjust
from tkinter import N, E, W, S, IntVar, StringVar, DoubleVar, Canvas
from tkinter.ttk import Separator, Label, Button, Scale, Entry, Checkbutton


# |MotionProfileGUI|-----------------------------------------------------------
class MotionProfileGUI(izygui.IzyGui):
    def __init__(self):
        # Initialize the Tk Root
        izygui.IzyGui.__init__(self)

        # Motion Profile Variables --------------------------------------------
        # Initialize TK Variables
        self.listMP = ['Time', 'Steps', 'Start', 'End']
        self.varMP = {v : StringVar(name=v) for v in self.listMP}
        self.varMP['Time'].set("10")
        self.varMP['Steps'].set("100")
        self.varMP['Start'].set("-10")
        self.varMP['End'].set("10")

        # Initialize Traces
        var_floats = ['Time', 'Start', 'End']
        var_counts = ['Steps']

        for var in self.listMP:
            self.varMP[var].trace_add('write', self.updatePlot)

        for var in var_floats:
            self.varMP[var].trace_add('write', self.updateFloat)

        for var in var_counts:
            self.varMP[var].trace_add('write', self.updateCount)

        # Joint Interpolation Variables ---------------------------------------
        # Initialize Tk Variables
        self.listJI = ['Start A', 'Start B', 'End A', 'End B', 'Velo. Limit A', 'Velo. Limit B', 'Accel. Limit A', 'Accel. Limit B', 'Interval', 'Total Time']
        self.varJI = {v: StringVar(name=v) for v in self.listJI}

        self.varJI['Start A'].set("0")
        self.varJI['End A'].set("60")
        self.varJI['Velo. Limit A'].set("50")
        self.varJI['Accel. Limit A'].set("50")
        self.varJI['Start B'].set("0")
        self.varJI['End B'].set("-40")
        self.varJI['Velo. Limit B'].set("60")
        self.varJI['Accel. Limit B'].set("30")
        self.varJI['Interval'].set("0.1")
        self.varJI['Total Time'].set("10")

        # Initialize Traces
        var_floats = ['Start A', 'Start B', 'End A', 'End B', 'Interval', 'Total Time']
        var_counts = ['Velo. Limit A', 'Velo. Limit B', 'Accel. Limit A', 'Accel. Limit B']
        for var in self.listJI:
            self.varJI[var].trace_add('write', self.updatePlot)

        for var in var_floats:
            self.varJI[var].trace_add('write', self.updateFloat)

        for var in var_counts:
            self.varJI[var].trace_add('write', self.updateCount)



        # Peak Measurement Variables ------------------------------------------
        # Initialize Tk Variables
        self.listPM = ['Final Pos. A', 'Peak Velo. A', 'Peak Accel. A', 'Final Pos. B', 'Peak Velo. B', 'Peak Accel. B']
        self.varPM = {v: StringVar(name=v) for v in self.listPM}

        for var in self.listPM:
            self.varPM[var].set('0')
            self.varPM[var].trace_add('write', self.checkLimits)
            self.varPM[var].trace_add('write', self.updateFloat)


        # Robot Variables -----------------------------------------------------
        # Initialize Tk Variables
        self.listRobot = ['X', 'Y', 'R', 'Theta', 'X1', 'Y1', 'X2', 'Y2']
        self.varRobot = {v: StringVar(name=v) for v in self.listRobot}

        self.varRobot['X'].set('100')
        self.varRobot['Y'].set('100')
        self.varRobot['X1'].set('100')
        self.varRobot['Y1'].set('100')
        self.varRobot['X2'].set('100')
        self.varRobot['Y2'].set('100')
        
        R, Theta = self.cylindricalIK(100, 100)
        self.varRobot['R'].set("{:.2f}".format(R))
        self.varRobot['Theta'].set("{:.2f}".format(Theta))

        # Initialize All Values
        self.var = {v: 0 for v in self.listMP + self.listJI + self.listPM}
        for v in self.listMP:
            self.var[v] = float(self.varMP[v].get())
        
        for v in self.listJI:
            self.var[v] = float(self.varJI[v].get())

        for v in self.listPM:
            self.var[v] = float(self.varPM[v].get())

        self.var['Steps'] = int(self.varMP['Steps'].get())

        # Plots
        self.fig = [None]*3
        self.axs = [None]*3

        # Layout the GUI
        p = 0
        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=0, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)

        Label(self.pagectr[p], text="Parameters", style='Controls.TLabel')\
            .grid(row=0, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Time:", style='Controls.TLabel')\
            .grid(row=1, column=0, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varMP['Time'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=1, justify='right')\
            .grid(row=1, column=1, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="Steps:", style='Controls.TLabel')\
            .grid(row=1, column=2, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varMP['Steps'], validate='focus', validatecommand=(self.register(self.validateCount), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=1, justify='right')\
            .grid(row=1, column=3, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="Start:", style='Controls.TLabel')\
            .grid(row=2, column=0, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varMP['Start'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=1, justify='right')\
            .grid(row=2, column=1, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="End:", style='Controls.TLabel')\
            .grid(row=2, column=2, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varMP['End'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=1, justify='right')\
            .grid(row=2, column=3, sticky=E, pady=5, padx=25)

        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=4, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)

        Label(self.pagectr[p], text="Measure", style='Controls.TLabel')\
            .grid(row=4, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Final Pos.:", style='Controls.TLabel')\
            .grid(row=5, column=0, columnspan=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Final Pos. A'], style='Controls.TLabel')\
            .grid(row=5, column=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Peak Velo.:", style='Controls.TLabel')\
            .grid(row=6, column=0, columnspan=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Peak Velo. A'], style='Controls.TLabel')\
            .grid(row=6, column=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Peak Accel.:", style='Controls.TLabel')\
            .grid(row=7, column=0, columnspan=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Peak Accel. A'], style='Controls.TLabel')\
            .grid(row=7, column=3, sticky=E, pady=5, padx=15)

        
        self.fig[p], self.axs[p] = subplots(1, 1)
        tight_layout(pad=2)
        self.fig[p].patch.set_facecolor('#F8C15A')
        self.fig[p].canvas.mpl_connect('button_press_event', self.switchplot)
        self.eomplot = FigureCanvasTkAgg(self.fig[p], self.pagedis[p])
        self.eomplot.get_tk_widget().grid(row=0, column=0, sticky=N+E+W+S, pady=5, padx=5)

        p=1
        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=0, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)

        Label(self.pagectr[p], text="Parameters A", style='Controls.TLabel')\
            .grid(row=0, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Start:", style='Controls.TLabel')\
            .grid(row=1, column=0, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['Start A'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=1, column=1, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="End:", style='Controls.TLabel')\
            .grid(row=1, column=2, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['End A'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=1, column=3, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="Velo. Limit:", style='Controls.TLabel')\
            .grid(row=2, column=0, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['Velo. Limit A'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=2, column=1, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="Accel. Limit:", style='Controls.TLabel')\
            .grid(row=2, column=2, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['Accel. Limit A'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=2, column=3, sticky=E, pady=5, padx=25)
        
        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=3, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)
        
        Label(self.pagectr[p], text="Parameters B", style='Controls.TLabel')\
            .grid(row=3, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Start:", style='Controls.TLabel')\
            .grid(row=4, column=0, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['Start B'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=4, column=1, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="End:", style='Controls.TLabel')\
            .grid(row=4, column=2, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['End B'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=4, column=3, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="Velo. Limit:", style='Controls.TLabel')\
            .grid(row=5, column=0, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['Velo. Limit B'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=5, column=1, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="Accel. Limit:", style='Controls.TLabel')\
            .grid(row=5, column=2, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['Accel. Limit B'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=2, justify='right')\
            .grid(row=5, column=3, sticky=E, pady=5, padx=25)
        
        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=6, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)
        
        Label(self.pagectr[p], text="Time", style='Controls.TLabel')\
            .grid(row=6, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Interval:", style='Controls.TLabel')\
            .grid(row=7, column=0, sticky=E, pady=5, padx=15)
        
        Entry(self.pagectr[p], textvariable=self.varJI['Interval'], validate='focus', validatecommand=(self.register(self.validateFloat), '%P'), style='Controls.TLabel', font=['@Yu Gothic UI Semibold', 14, ''], width=1, justify='right')\
            .grid(row=7, column=1, sticky=E, pady=5, padx=25)
        
        Label(self.pagectr[p], text="Total Time:", style='Controls.TLabel')\
            .grid(row=7, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varJI['Total Time'], style='Controls.TLabel')\
            .grid(row=7, column=3, sticky=E, pady=5, padx=15)
        
        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=8, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)
        
        Label(self.pagectr[p], text="Measure", style='Controls.TLabel')\
            .grid(row=8, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Final Pos. A:", style='Controls.TLabel')\
            .grid(row=9, column=0, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Final Pos. A'], style='Controls.TLabel')\
            .grid(row=9, column=1, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Peak Velo. A:", style='Controls.TLabel')\
            .grid(row=10, column=0, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Peak Velo. A'], style='Controls.TLabel')\
            .grid(row=10, column=1, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Peak Accel. A:", style='Controls.TLabel')\
            .grid(row=11, column=0, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Peak Accel. A'], style='Controls.TLabel')\
            .grid(row=11, column=1, sticky=E, pady=5, padx=15)
          
        Label(self.pagectr[p], text="Final Pos. B:", style='Controls.TLabel')\
            .grid(row=9, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Final Pos. B'], style='Controls.TLabel')\
            .grid(row=9, column=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Peak Velo. B:", style='Controls.TLabel')\
            .grid(row=10, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Peak Velo. B'], style='Controls.TLabel')\
            .grid(row=10, column=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Peak Accel. B:", style='Controls.TLabel')\
            .grid(row=11, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varPM['Peak Accel. B'], style='Controls.TLabel')\
            .grid(row=11, column=3, sticky=E, pady=5, padx=15)
        
        self.fig[p], self.axs[p] = subplots(1, 1)
        tight_layout(pad=2)
        self.fig[p].patch.set_facecolor('#F8C15A')
        self.fig[p].canvas.mpl_connect('button_press_event', self.switchplot)
        self.jointplot = FigureCanvasTkAgg(self.fig[p], self.pagedis[p])
        self.jointplot.get_tk_widget().grid(row=0, column=0, sticky=N+E+W+S, pady=5, padx=5)

        p = 2
        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=0, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)

        Label(self.pagectr[p], text="Current Position", style='Controls.TLabel')\
            .grid(row=0, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="X:", style='Controls.TLabel')\
            .grid(row=1, column=0, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['X'], style='Controls.TLabel', width=5)\
            .grid(row=1, column=1, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Y:", style='Controls.TLabel')\
            .grid(row=1, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['Y'], style='Controls.TLabel', width=5)\
            .grid(row=1, column=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="R:", style='Controls.TLabel')\
            .grid(row=2, column=0, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['R'], style='Controls.TLabel', width=5)\
            .grid(row=2, column=1, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Theta:", style='Controls.TLabel')\
            .grid(row=2, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['Theta'], style='Controls.TLabel', width=5)\
            .grid(row=2, column=3, sticky=E, pady=5, padx=15)

        Separator(self.pagectr[p], style='Controls.TSeparator')\
            .grid(row=3, column=0, columnspan=4, sticky=E+W, pady=5, padx=5)

        Label(self.pagectr[p], text="Target", style='Controls.TLabel')\
            .grid(row=3, column=0, columnspan=4, pady=5, padx=15)
        
        Label(self.pagectr[p], text="X1:", style='Controls.TLabel')\
            .grid(row=4, column=0, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['X1'], style='Controls.TLabel', width=5)\
            .grid(row=4, column=1, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Y1:", style='Controls.TLabel')\
            .grid(row=4, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['Y1'], style='Controls.TLabel', width=5)\
            .grid(row=4, column=3, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="X2:", style='Controls.TLabel')\
            .grid(row=5, column=0, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['X2'], style='Controls.TLabel', width=5)\
            .grid(row=5, column=1, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], text="Y2:", style='Controls.TLabel')\
            .grid(row=5, column=2, sticky=E, pady=5, padx=15)
        
        Label(self.pagectr[p], textvariable=self.varRobot['Y2'], style='Controls.TLabel', width=5)\
            .grid(row=5, column=3, sticky=E, pady=5, padx=15)
        
        self.canvas = Canvas(self.pagedis[p],width=600, height=400, bg='white')
        self.canvas.grid(row=0, column=0, sticky=N+E+W+S, pady=5, padx=5)

        self.canvas.bind('<Button-1>', self.updateP2)
        self.canvas.bind('<FocusIn>', self.updateCanvas)

        # Create List of Plots to Iterate
        self.eomdf = DataFrame(columns=['Time', 'Displacement', 'Velocity', 'Acceleration', 'Displacement2', 'Velocity2', 'Acceleration2'])
        self.checkdf = DataFrame(columns=['Time', 'Displacement', 'Velocity', 'Acceleration','Displacement2', 'Velocity2', 'Acceleration2', 
                                          'Displacement A', 'Velocity A', 'Acceleration A','Displacement B', 'Velocity B', 'Acceleration B'])
        self.jointdf = DataFrame(columns=['Time', 'Displacement A', 'Velocity A', 'Acceleration A', 'Displacement B', 'Velocity B', 'Acceleration B'])

        # Plot Cycler
        self.eom = ['Displacement', 'Velocity', 'Acceleration', 'Displacement2', 'Velocity2', 'Acceleration2']
        self.eoms = itertools.cycle(self.eom)
        self.selecteom = next(self.eoms)

        self.joint = ['Displacement', 'Velocity', 'Acceleration']
        self.joints = itertools.cycle(self.joint)
        self.selectjoint = next(self.joints)

        self.note.bind('<<NotebookTabChanged>>', self.updatePlot)
        
        self.rt = TimedThread("Moving Robot", self.moveRobot, float(self.varJI['Interval'].get())*1000_000, True, True)
        self.moving = False
        self.updatePlot()
        self.updateCanvas()


    # -------------------------------------------------------------------------
    # validateFloat
    #
    # Does it float?
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def validateFloat(self, input):
        try:
            float(input)
            return True # Its a witch!
        except:
            print("Invalid Float!!")
            return False
        
    # -------------------------------------------------------------------------
    # validateCount
    #
    # Checks if a number is an integer and above 0.
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def validateCount(self, input):
        try:
            test = int(input)
            if test <= 0 or input=='':
                raise ValueError("Counts must be an integer greater than 0!!")
            return True
        except:
            print("Invalid Count!!")
            return False

    # -------------------------------------------------------------------------
    # updateFloat
    #
    # Updates the value of a float variable.
    #
    # Last Modified: November 28, 2024
    # -------------------------------------------------------------------------
    def updateFloat(self, *args):
        # print("updateFloat called by {}".format(args[0]))
        if self.validateFloat(self.globalgetvar(args[0])):
            self.var[args[0]] = float(self.globalgetvar(args[0]))
        if args[0] in self.listJI + self.listMP:
            print("{} = {}".format(args[0], self.var[args[0]]))

    # -------------------------------------------------------------------------
    # updateCount
    #
    # Updates the value of a count variable.
    #
    # Last Modified: November 28, 2024
    # -------------------------------------------------------------------------
    def updateCount(self, *args):
        # print("updateCount called by {}".format(args[0]))
        if self.validateCount(self.globalgetvar(args[0])):
            self.var[args[0]] = int(self.globalgetvar(args[0]))
            print("{} = {}".format(args[0], self.var[args[0]]))

    # -------------------------------------------------------------------------
    # checkLimits
    #
    # Check if the generated velocity profile is correct.
    #
    # Last Modified: November 28, 2024
    # -------------------------------------------------------------------------
    def checkLimits(self, *args):
        # print("checkLimits called by {}".format(args[0]))
        page = self.note.index('current')
        tolerance = 0.01
        
        if page == 0:   
            if args[0] == 'Final Pos. A' and abs(self.var['Final Pos. A'] - self.var['End']) > tolerance:
                print("Check Profile!!! Final Pos. = {} is not at specified End = {}".format(self.var['Final Pos. A'], self.var['End']))
            elif args[0] == 'Final Pos. A':
                print("{} updated: {} Profile Passed!".format(args[0], self.var[args[0]]))
            
        if page == 1: 
            if args[0] == 'Final Pos. A' and abs(self.var['Final Pos. A'] - self.var['End A']) > tolerance:
                print("Check Profile!!! Final Pos. A = {} is not at specified End A = {}".format(self.var['Final Pos. A'], self.var['End A']))

            elif args[0] == 'Final Pos. B' and abs(self.var['Final Pos. B'] - self.var['End B']) > tolerance:
                print("Check Profile!!! Final Pos. B = {} is not at specified End B = {}".format(self.var['Final Pos. B'], self.var['End B']))

            elif args[0] == 'Peak Velo. A' and abs(self.var['Peak Velo. A'] > self.var['Velo. Limit A']):
                print("Check Profile!!! Peak Velo. A = {} is above specified Velo. Limit A = {}".format(self.var['Peak Velo. A'], self.var['Velo. Limit A']))

            elif args[0] == 'Peak Velo. B' and abs(self.var['Peak Velo. B'] > self.var['Velo. Limit B']):
                print("Check Profile!!! Peak Velo. B = {} is above specified Velo. Limit B = {}".format(self.var['Peak Velo. B'], self.var['Velo. Limit B']))

            elif args[0] == 'Peak Accel. A' and abs(self.var['Peak Accel. A'] > self.var['Accel. Limit A']):
                print("Check Profile!!! Peak Accel. A = {} is above specified Accel. Limit A = {}".format(self.var['Peak Accel. A'], self.var['Accel. Limit A']))

            elif args[0] == 'Peak Accel. B' and abs(self.var['Peak Accel. B'] > self.var['Accel. Limit B']):
                print("Check Profile!!! Peak Accel. B = {} is above specified Accel. Limit B = {}".format(self.var['Peak Accel. B'], self.var['Accel. Limit B']))
            
            elif args[0] in self.listPM:
                print("{} updated: {} Profile Passed!".format(args[0], self.var[args[0]]))

    # -------------------------------------------------------------------------
    # updatePlot
    #
    # Updates the plot if any variables have changed.
    #
    # Last Modified: November 28, 2024
    # -------------------------------------------------------------------------
    def updatePlot(self, *args):
        # try:
        #     print("updatePlot called by {}".format(args[0]))
        # except IndexError as e:
        #    print("updatePlot called manually")
            
        page = self.note.index('current')
        if page== 0:
            self.eomdf = self.eomdf.head(0)
            self.eomdf['Time'] = [x*self.var['Time']/self.var['Steps'] for x in range(self.var['Steps'] + 1)]
            self.checkdf['Time'] = [0, max(self.eomdf['Time'])]
            displacement = self.var['End'] - self.var['Start']
            
            d, v, a = motionProfile.profile(displacement, self.var['Start'], self.eomdf['Time'].tolist(), self.checkdf.iloc[1]['Time']/2)
            self.eomdf['Displacement'] = d
            self.eomdf['Velocity'] = v
            self.eomdf['Acceleration'] = a
            
            d2, v2, a2 = motionProfile.profile(displacement, self.var['Start'], self.eomdf['Time'].tolist(), self.checkdf.iloc[1]['Time']/3)
            self.eomdf['Displacement2'] = d2
            self.eomdf['Velocity2'] = v2
            self.eomdf['Acceleration2'] = a2

            if self.selecteom in ('Displacement', 'Velocity', 'Acceleration'):
                pd = d[-1]
                pv = max([abs(velocity) for velocity in v])
                pa = max([abs(acceleration) for acceleration in a])
                self.checkdf['Displacement'] = [pd, pd]
                self.checkdf['Velocity'] = [pv, pv]
                self.checkdf['Acceleration'] = [pa, pa]

            if self.selecteom in ('Displacement2', 'Velocity2', 'Acceleration2'):
                pd = d2[-1]
                pv = max([abs(velocity) for velocity in v2])
                pa = max([abs(acceleration) for acceleration in a2])
                self.checkdf['Displacement2'] = [pd, pd]
                self.checkdf['Velocity2'] = [pv, pv]
                self.checkdf['Acceleration2'] = [pa, pa]

            self.varPM['Peak Velo. A'].set("{:.2f}".format(pv))
            self.varPM['Peak Accel. A'].set("{:.2f}".format(pa))
            self.varPM['Final Pos. A'].set("{:.2f}".format(pd))
        
            self.checkdf['Displacement'] = [pd, pd]
            self.checkdf['Velocity'] = [pv, pv]
            self.checkdf['Acceleration'] = [pa, pa]

            self.axs[page].cla()
            self.axs[page].plot(self.eomdf['Time'], self.eomdf[self.selecteom], linewidth=0.5, label=self.selecteom)
            self.axs[page].plot(self.checkdf['Time'], self.checkdf[self.selecteom], linewidth=0.5)
            self.axs[page].set_title('Motion Profile')
            self.axs[page].set_xlabel('Time')
            self.axs[page].set_ylabel(self.selecteom)
            self.fig[page].canvas.draw()

        if page== 1:
            self.jointdf = self.jointdf.head(0)
            dispA = self.var['End A'] - self.var['Start A']
            startA = self.var['Start A']
            dispB = self.var['End B'] - self.var['Start B']
            startB = self.var['Start B']
            interval = self.var['Interval']
            accA = self.var['Accel. Limit A']
            accB = self.var['Accel. Limit B']
            veloA = self.var['Velo. Limit A']
            veloB = self.var['Velo. Limit B']
            eomA, eomB, time = motionProfile.jointInterpolation(dispA, startA, dispB, startB, interval, accA, veloA, accB, veloB)
            self.jointdf['Displacement A'] = eomA[0]
            self.jointdf['Displacement B'] = eomB[0]
            self.jointdf['Velocity A'] = eomA[1]
            self.jointdf['Velocity B'] = eomB[1]
            self.jointdf['Acceleration A'] = eomA[2]
            self.jointdf['Acceleration B'] = eomB[2]
            self.jointdf['Time'] = time

            self.checkdf['Time'] = [0, max(time)]
            self.varJI['Total Time'].set("{:.2f}".format(max(time)))

            pdA = eomA[0][-1]
            pdB = eomB[0][-1]

            if dispA > 0:
                pvA = max(eomA[1])
                paA = max(eomA[2])
            else:
                pvA = min(eomA[1])
                paA = min(eomA[2])
        
            if dispB > 0:
                pvB = max(eomB[1])
                paB = max(eomB[2])
            else:
                pvB = min(eomB[1])
                paB = min(eomB[2])

            self.varPM['Final Pos. A'].set("{:.2f}".format(pdA))
            self.varPM['Peak Velo. A'].set("{:.2f}".format(pvA))
            self.varPM['Peak Accel. A'].set("{:.2f}".format(paA))

            self.varPM['Final Pos. B'].set("{:.2f}".format(pdB))
            self.varPM['Peak Velo. B'].set("{:.2f}".format(pvB))
            self.varPM['Peak Accel. B'].set("{:.2f}".format(paB))
        
            self.checkdf['Displacement A'] = [pdA, pdA]
            self.checkdf['Velocity A'] = [pvA, pvA]
            self.checkdf['Acceleration A'] = [paA, paA]
            self.checkdf['Displacement B'] = [pdB, pdB]
            self.checkdf['Velocity B'] = [pvB, pvB]
            self.checkdf['Acceleration B'] = [paB, paB]

            self.axs[page].cla()
            self.axs[page].plot(self.jointdf['Time'], self.jointdf[self.selectjoint + ' A'], linewidth=0.5, label=self.selectjoint + ' A')
            self.axs[page].plot(self.jointdf['Time'], self.jointdf[self.selectjoint + ' B'], linewidth=0.5, label=self.selectjoint + ' B')
            self.axs[page].plot(self.checkdf['Time'], self.checkdf[self.selectjoint + ' A'], linewidth=0.5)
            self.axs[page].plot(self.checkdf['Time'], self.checkdf[self.selectjoint + ' B'], linewidth=0.5)
            self.axs[page].set_title('Joint Interpolation')
            self.axs[page].set_xlabel('Time')
            self.axs[page].set_ylabel(self.selectjoint)
            self.fig[page].canvas.draw()
    
    # -------------------------------------------------------------------------
    # switchPlot
    #
    # Clicking the plot will cycle through the equations of motion.
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def switchplot(self, event):
        page = self.note.index('current')
        if page == 0:
            self.selecteom = next(self.eoms)
        if page == 1: 
            self.selectjoint = next(self.joints)
        self.updatePlot()
    
    # -------------------------------------------------------------------------
    # updateP2
    #
    # Left-clicking the plot will update Position 2.
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def updateP2(self, event):
        if self.moving == False:
            x1 = float(self.varRobot['X'].get())
            y1 = float(self.varRobot['Y'].get())

            self.varRobot['X1'].set("{:.2f}".format(x1))
            self.varRobot['Y1'].set("{:.2f}".format(y1))

            x2 = event.x - self.robot_center_x
            y2 = self.robot_center_y - event.y
            self.varRobot['X2'].set("{:.2f}".format(x2))
            self.varRobot['Y2'].set("{:.2f}".format(y2))

            R1, Theta1 = self.cylindricalIK(x1, y1)
            R2, Theta2 = self.cylindricalIK(x2, y2)

            self.varJI['Start A'].set("{:.2f}".format(R1))
            self.varJI['End A'].set("{:.2f}".format(R2))
            self.varJI['Start B'].set("{:.2f}".format(Theta1))
            self.varJI['End B'].set("{:.2f}".format(Theta2))

            interval = self.var['Interval']
            velA = self.var['Velo. Limit A']
            accA = self.var['Accel. Limit A']
            velB = self.var['Velo. Limit B']
            accB = self.var['Accel. Limit B']
            

            self.motionR, self.motionTheta, time = motionProfile.jointInterpolation(R2 - R1, R1, Theta2 - Theta1, Theta1, interval,accA, velA, accB, velB)
            self.index = 0
            self.varJI['Total Time'].set("{:.2f}".format(max(time)))
            if self.rt.is_alive():
                self.rt.join(timeout=5)
            self.rt = TimedThread("Moving Robot", self.moveRobot, float(self.varJI['Interval'].get())*1000_000, True, True)
            
            self.rt.start()

            self.updateCanvas()
            self.moving = True

    # -------------------------------------------------------------------------
    # updateCanvas
    #
    # Clicking the plot will update the canvas.
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def updateCanvas(self, *args):
        self.canvas.delete('all')

        for y in range(0, self.canvas.winfo_height(), 100):
            self.canvas.create_line(0, y, self.canvas.winfo_width(), y)

        for x in range(0, self.canvas.winfo_width(), 100):
            self.canvas.create_line(x, 0, x, self.canvas.winfo_height())

        self.robot_center_x = floor(self.canvas.winfo_width()/200)*100
        self.robot_center_y = ceil(self.canvas.winfo_height()/200)*100
        x = float(self.varRobot['X'].get())
        y = float(self.varRobot['Y'].get())
        body = 30
        tool = 5
        self.canvas.create_line(self.robot_center_x, self.robot_center_y, self.robot_center_x + x, self.robot_center_y - y, fill='grey', width=30, capstyle='round', tags='Robot')
        self.canvas.create_oval(self.robot_center_x - body, self.robot_center_y - body, self.robot_center_x + body, self.robot_center_y + body, fill='black', tags='Robot')
        self.canvas.create_oval(self.robot_center_x + x - tool, self.robot_center_y - y - tool, self.robot_center_x + x + tool, self.robot_center_y - y + tool, fill='red')

    # -------------------------------------------------------------------------
    # moveRobot
    #
    # This method changes the position of the robot.
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def moveRobot(self):
        if self.index < len(self.motionR[0]):
            R = self.motionR[0][self.index]
            Theta = self.motionTheta[0][self.index]
            self.varRobot['R'].set("{:.2f}".format(R))
            self.varRobot['Theta'].set("{:.2f}".format(Theta))
            X, Y = self.cylindricalFK(R, Theta)
            self.varRobot['X'].set("{:.2f}".format(X))
            self.varRobot['Y'].set("{:.2f}".format(Y))
            self.index = self.index + 1
            print("Time = {:.2f}, X = {:.2f}, Y = {:.2f}".format(self.index*self.var['Interval'], X, Y))
            self.canvas.delete('Robot')
            tool = 5
            body = 30
            self.canvas.create_line(self.robot_center_x, self.robot_center_y, self.robot_center_x + X, self.robot_center_y - Y, fill='grey', width=30, capstyle='round', tags='Robot')
            self.canvas.create_oval(self.robot_center_x - body, self.robot_center_y - body, self.robot_center_x + body, self.robot_center_y + body, fill='black', tags='Robot')
            self.canvas.create_oval(self.robot_center_x + X - tool, self.robot_center_y - Y - tool, self.robot_center_x + X + tool, self.robot_center_y - Y + tool, fill='red')
        else:
            self.rt.stop.set()
            self.moving = False
            

    # -------------------------------------------------------------------------
    # cylindricalIK
    #
    # Calculates the R and Theta for a cylindrical robot.
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def cylindricalIK(self, x, y):
        R = (x**2 + y**2)**(1/2)
        Theta = 360*atan2(y, x)/(2*pi)
        return R, Theta

    # -------------------------------------------------------------------------
    # cylindricalFK
    #
    # Calculates the X and Y for a cylindrical robot.
    #
    # Last Modified: November 16, 2024
    # -------------------------------------------------------------------------
    def cylindricalFK(self, R, Theta):
        X = R*cos(Theta*2*pi/360)
        Y = R*sin(Theta*2*pi/360)
        return X, Y


if __name__ == "__main__":
    app = MotionProfileGUI()
    app.mainloop()