# |IzyGUI: First Edition|------------------------------------------------------
#
# Project: IzyGUI
# Program: izygui.py
#
# Description:
#   This module is used as a template for creating python GUI applications. In
# addition, this module will eventually incorporate an XML file for common
# fields such as the title, font, and subtitles.
#
# For a dynamic font, use the following line for each added widget with text.
# self.allLabels['TButton'].append(btn)
#
# Author: Isaiah Regacho
# Date Created:     October 16, 2020
# Last Modified:    April 26, 2021
# -----------------------------------------------------------------------------


# |MODULES|--------------------------------------------------------------------
import cProfile
import io
import pstats
import sys

import itertools as it
import tkinter as tk
import tkinter.ttk as ttk
import xml.etree.ElementTree as ET

from pstats import SortKey
from tkinter import N, E, W, S, font, RIDGE

class IzyGui(tk.Tk):
    def __init__(self):
        # Initialize the Tk Root
        tk.Tk.__init__(self)
        
        # Get the application XML root
        apptree = ET.parse('app.XML')
        approot = apptree.getroot()
        title = approot.find('Title').text

        dimension = approot.find('Dimension').text
        apptitle = approot.find('appTitle').text
        pages = approot.findall('page')
        deffont = approot.find('Font').text
        # Initialize ttk Style
        self.style = ttk.Style()
        # Ttk Style Label Settings
        self.allLabels = {'Main.TLabel': [],
                          'Controls.TLabel': [],
                          'Display.TLabel': [],
                          'ControlsL.TLabel': [],
                          'DisplayL.TLabel': [],
                          'Main.TNotebook': [],
                          'TButton': [],
                          'TMenubutton': [],
                          'Controls.TCheckbutton': []}

        self.fontpreset = {'Title': [deffont, 20, 'bold'],
                           'Tab': [deffont, 14, ''],
                           'Heading': [deffont, 14, 'bold'],
                           'Label': [deffont, 12, ''],
                           'Button': [deffont, 12, 'bold']}
        self.initstyle(approot)

        # List of Fonts
        self.fontlist = it.cycle(sorted(font.families()))
        self.after
        # Initialize the Main Window
        self.wm_protocol("WM_DELETE_WINDOW", self.closing)  # handle event when window is closed by user
        self.bind("<Escape>", self.on_close)  # Bind: Press Escape to Close Application

        self.title(title)
        self.geometry(dimension)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Main Frame
        mainpage = ttk.Frame(self, style='Main.TFrame')
        for i, w in enumerate([1]):
            mainpage.grid_columnconfigure(i, weight=w)
        for i, w in enumerate([0, 1]):
            mainpage.grid_rowconfigure(i, weight=w)
        mainpage.grid(sticky=N+E+W+S)

        # MF - Title
        ttk.Separator(mainpage, style='Main.TSeparator')\
            .grid(row=0, sticky=E+W, padx=200)
        lbl = ttk.Label(mainpage, style='Main.TLabel', text=apptitle)
        lbl.bind("<Button-1>", self.switchfont) # uncomment for dynamic font
        lbl.grid(row=0, padx=5, pady=5)
        self.allLabels['Main.TLabel'].append(lbl)

        # MF - Notebook
        self.note = ttk.Notebook(mainpage, style='Main.TNotebook')
        self.note.grid(row=1, sticky=N+E+W+S, padx=15, pady=15)
        self.allLabels['Main.TNotebook'].append(self.note)

        # Page Setup
        self.page = []
        self.pagectr = []
        self.pagedis = []
        self.pagectr2 = []

        for page in pages:
            frm = ttk.Frame(self.note, style='Page.TFrame')
            frm.grid_rowconfigure(0, weight=1)
            frm.grid_columnconfigure(1, weight=1)
            frm.grid(sticky=N+E+W+S, padx=15, pady=15)

            self.page.append(frm)
            self.note.add(frm, text=page.get('name'), sticky=N+E+W+S)

            frmctr = ttk.Frame(frm, style='Controls.TFrame')
            frmctr.grid(row=0, column=0, sticky=N+E+W+S, padx=10, pady=5)
            self.pagectr.append(frmctr)

            frmdis = ttk.Frame(frm, style='Display.TFrame')
            frmdis.grid(row=0, column=1, sticky=N+E+W+S, padx=10, pady=5)
            self.pagedis.append(frmdis)

            frmctr2 = ttk.Frame(frm, style='Controls.TFrame')
            frmctr2.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S, padx=10, pady=5)
            self.pagectr2.append(frmctr2)

            weightcx = [int(w) for w in page.find("weightCX").text.split(",")]
            weightcy = [int(w) for w in page.find("weightCY").text.split(",")]
            weightc2x = [int(w) for w in page.find("weightC2X").text.split(",")]
            weightc2y = [int(w) for w in page.find("weightC2Y").text.split(",")]
            weightdx = [int(w) for w in page.find("weightDX").text.split(",")]
            weightdy = [int(w) for w in page.find("weightDY").text.split(",")]

            for i, w in enumerate(weightcx):
                frmctr.grid_columnconfigure(i, weight=w)
            for i, w in enumerate(weightcy):
                frmctr.grid_rowconfigure(i, weight=w)
            
            for i, w in enumerate(weightc2x):
                frmctr2.grid_columnconfigure(i, weight=w)
            for i, w in enumerate(weightc2y):
                frmctr2.grid_rowconfigure(i, weight=w)

            for i, w in enumerate(weightdx):
                frmdis.grid_columnconfigure(i, weight=w)
            for i, w in enumerate(weightdy):
                frmdis.grid_rowconfigure(i, weight=w)

    # |METHODS|----------------------------------------------------------------
    # -------------------------------------------------------------------------
    # initStyle
    #
    # Description:
    #       This method updates the ttk style object to modify the widgets.
    #
    # -------------------------------------------------------------------------
    def initstyle(self, approot):
        # Colors
        ctrFontColor = approot.find('ControlFontColor').text
        mainBGcolor = approot.find('MainBGColor').text
        ctrBGcolor = approot.find('ControlBGColor').text
        disBGcolor = approot.find('DisplayBGColor').text
        accent1 = approot.find('AccentColor1').text
        accent2 = approot.find('AccentColor2').text

        # Ttk Style Settings
        self.style.theme_use('default')

        # Ttk Label Settings
        self.style.configure('Main.TLabel', foreground=ctrFontColor, background=mainBGcolor, padding=[10, 10],
                             font=self.fontpreset['Title'])
        self.style.configure('Controls.TLabel', foreground=ctrFontColor, background=ctrBGcolor, padding=[10, 10],
                             font=self.fontpreset['Heading'])
        self.style.configure('Display.TLabel', foreground=ctrBGcolor, background=disBGcolor, padding=[10, 10],
                             font=self.fontpreset['Heading'])
        self.style.configure('ControlsL.TLabel', foreground=ctrFontColor, background=ctrBGcolor, padding=[5, 5],
                             font=self.fontpreset['Label'])
        self.style.configure('DisplayL.TLabel', foreground=ctrBGcolor, background=disBGcolor, padding=[5, 5],
                             font=self.fontpreset['Button'])

        # Ttk Style Separator Settings
        self.style.configure('Main.TSeparator', background=ctrFontColor)
        self.style.configure('Controls.TSeparator', background=ctrFontColor)
        self.style.configure('Display.TSeparator', background=ctrBGcolor)

        # Ttk Style Notebook Settings
        self.style.map('Main.TNotebook.Tab',
                       background=[('selected', ctrBGcolor),
                                   ('active', accent2)],
                       focuscolor=[('selected', ctrBGcolor),
                                   ('active', accent2)])
        self.style.configure('Main.TNotebook.Tab', font=self.fontpreset['Tab'], expand=[-2, 0, -2, 0], width=20,
                             padding=[10, 10], foreground=ctrFontColor, background=mainBGcolor, focuscolor=mainBGcolor)
        self.style.configure('Main.TNotebook', tabmargins=[-6, 0, -6, 0], tabposition='wn', borderwidth=0, padding=[0],
                             background=mainBGcolor, lightcolor=mainBGcolor, darkcolor=mainBGcolor)

        # Ttk Style Frame Settings
        self.style.configure('TFrame', padding=[5, 5])
        self.style.configure('Main.TFrame', background=mainBGcolor, padding=[5, 5])
        self.style.configure('Page.TFrame', background=ctrBGcolor, bordercolor=mainBGcolor,
                             borderwidth=5, padding=[5, 5])
        self.style.configure('Controls.TFrame', background=ctrBGcolor, bordercolor=mainBGcolor,
                             borderwidth=5, padding=[5, 5])
        self.style.configure('Display.TFrame', background=disBGcolor, bordercolor=mainBGcolor,
                             borderwidth=5, relief=RIDGE, padding=[5, 5])

        # Ttk Style Scale Settings
        self.style.map('TScale', background=[('active', accent1)])
        self.style.configure('TScale', background=ctrFontColor, troughcolor=accent2)

        # Ttk Style Button Settings
        self.style.map('TButton', background=[('active', accent1)])
        self.style.configure('TButton', padding=[5, 5], background=ctrFontColor, foreground=ctrBGcolor,
                             font=self.fontpreset['Button'], width=15)
        self.style.map('TMenubutton', background=[('active', accent1)])
        self.style.configure('TMenubutton', padding=[5, 5], background=ctrFontColor, foreground=ctrBGcolor,
                             font=self.fontpreset['Button'], width=10)

        # Ttk Style Progressbar Settings
        self.style.configure('TProgressbar', background=ctrFontColor, troughcolor=accent2)

        # Ttk Style Checkbutton Settings
        self.style.configure('Controls.TCheckbutton', background=ctrFontColor, troughcolor=accent2)

    # -------------------------------------------------------------------------
    # switchfont
    #
    # Description:
    #       This method is used to change the font of all text in the
    # application.
    #
    # -------------------------------------------------------------------------
    def switchfont(self, event):
        # Update the font presets to preserve the size and modifiers.
        new = next(self.fontlist)
        self.fontpreset['Title'][0] = new
        self.fontpreset['Tab'][0] = new
        self.fontpreset['Heading'][0] = new
        self.fontpreset['Label'][0] = new
        self.fontpreset['Button'][0] = new

        # Update the Widget Styles
        self.style.configure('Main.TLabel', font=self.fontpreset['Title'])
        self.style.configure('Controls.TLabel', font=self.fontpreset['Heading'])
        self.style.configure('Display.TLabel', font=self.fontpreset['Heading'])
        self.style.configure('ControlsL.TLabel', font=self.fontpreset['Label'])
        self.style.configure('DisplayL.TLabel', font=self.fontpreset['Label'])
        self.style.configure('Main.TNotebook.Tab', font=self.fontpreset['Tab'])
        self.style.configure('TButton', font=self.fontpreset['Button'])
        self.style.configure('TMenubutton', font=self.fontpreset['Button'])

        for style in ['Main.TLabel', 'Controls.TLabel', 'Display.TLabel', 'ControlsL.TLabel', 'DisplayL.TLabel',
                      'Main.TNotebook', 'TButton', 'TMenubutton']:
            for widget in self.allLabels[style]:
                widget.config(style=style)
        print(new)

    # -------------------------------------------------------------------------
    # cleanup
    #
    # Description:
    #       This method is to be overridden for clean up purposes and must 
    # call self.after(self.quit).
    #
    # -------------------------------------------------------------------------
    def cleanup(self):
        self.quit()

    # -------------------------------------------------------------------------
    # closing
    #
    # Description:
    #       This method closes the application.
    #
    # -------------------------------------------------------------------------
    def closing(self):
        self.after(200, self.cleanup)

    # -------------------------------------------------------------------------
    # on_close
    #
    # Description:
    #       This method closes the application.
    #
    # -------------------------------------------------------------------------
    def on_close(self, event=None):
        self.closing()

if __name__ == "__main__":
    # Profiler Start
    useProfile = False
    if useProfile:
        pr = cProfile.Profile()
        pr.enable()

    app = IzyGui()
    app.mainloop()

    # Profiler End
    if useProfile:
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_callees(.05)
        print(s.getvalue())
    sys.exit(0)
