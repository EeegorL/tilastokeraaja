import os;
import re;
import time;
from datetime import datetime;
from tkinter import *;
from tkinter import ttk;
import tkinter as tk;
import threading
from tkinter import filedialog;
from handlers.bmaHandler import fetchData;
from handlers.xlsxHandler import doXlsxThings, xlsxIsOpen, delXlsx, getFileName;

class UI:
    def __init__(this, root):
        this._root = root;

    def start(this, window):
        this.folderPath = os.path.expanduser("~/Downloads"); # default dir = Downloads
        this.fetchLocations = [];
        this.statusElems = [];
        def select():
            selected = [];
            if(kaisa.get()): selected.append("Kaisa");
            if(kumpula.get()): selected.append("Kumpula");
            if(viikki.get()): selected.append("Viikki");
            if(terkko.get()): selected.append("Terkko");

            this.fetchLocations = selected[:];
        
        def datesAreValid(d1, d2):        
            d1Spl = d1.split(".");
            d2Spl = d2.split(".");

            if(len(d1Spl) != 3 or len(d2Spl) != 3):
                return False;

            if(len(d1Spl[0]) != 2 or len(d1Spl[1]) != 2 or len(d1Spl[2]) != 4 or
               len(d2Spl[0]) != 2 or len(d2Spl[1]) != 2 or len(d2Spl[2]) != 4
               ): return False

            format = "%d.%m.%Y";
            try:
                startDate = datetime.strptime(d1, format);
                endDate = datetime.strptime(d2, format);
            except ValueError:
                return False;

            if(startDate > endDate):
                return False;
        
            return True;
            
        def timesAreValid(t1, t2):
            if(":" in t1 or ":" in t2):
                return False;
        
            format = "%d.%m.%Y %H";
            dummyDate = "01.01.1990 "; # dummy date for time checking
            startDate = dummyDate + t1;
            endDate = dummyDate + t2;

            try:
                timedate1 = datetime.strptime(startDate, format);
                if(int(t2) != 24):
                    timedate2 = datetime.strptime(endDate, format);
                else:
                    minuteFormat = "%d.%m.%Y %H:%M:%S";
                    timedate2 = datetime.strptime(dummyDate + "23:59:59", minuteFormat);

            except ValueError:
                return False;

            if(timedate1 > timedate2):
                return False;
        
            return True;
    
        # actual functionality
        def submit():
            canProceed = True;
            errors = [];

            # init all radio buttons to 0 (=unticked)
            kaisa.set(0);
            kumpula.set(0);
            viikki.set(0);
            terkko.set(0);

            # input values
            dateStart = dateStartInput.get();
            dateEnd = dateEndInput.get();
            timeStart = timeStartInput.get();
            timeEnd = timeEndInput.get();

            if(len(this.fetchLocations) == 0):
                errors.append("Sijaintia ei valittu");
                canProceed = False;
            if(not datesAreValid(dateStart, dateEnd)):
                errors.append("Päivämäärät väärää muotoa");
                canProceed = False;
            if(not timesAreValid(timeStart, timeEnd)):
                errors.append("Ajat väärää muotoa");
                canProceed = False;
            if(xlsxIsOpen(this.folderPath)):
                errors.append("Sulje tulostiedosto: " + this.folderPath + getFileName());
                canProceed = False;      

            this.statusElems = [];

            def doFetch():
                button["state"] = "disable";
                button["state"] = "disable";

                stautsMarginMult = 0;
                delXlsx(this.folderPath);
                for location in this.fetchLocations:
                    stautsMarginMult += 1;

                    statusElem = ttk.Label(mainFrame, text=location, font="Arial 10");
                    statusElem.place(x=0, y=250+(25*stautsMarginMult));

                    this.statusElems.append(statusElem);
                    
                    statusElem.config(text=location + "...");
                    data = fetchData(location=location, dateStart=dateStart, dateEnd=dateEnd, timeStart=timeStart, timeEnd=timeEnd);
                    doXlsxThings(data, this.folderPath);
                
                    statusElem.config(text=location+": \u2713", foreground="green", font=("Arial","12","bold"));
                if(avaaheti.get()):
                    os.startfile((this.folderPath + getFileName()).replace("/","\\"));
                time.sleep(2);
                
                stautsMarginMult = 0;
                forget();
                this.fetchLocations = [];
                button["state"] = "enable";
            
            def forget():
                for elem in this.statusElems:
                    elem.destroy();

                dateExample.config(font="Arial 10",foreground="black");
                timeExample.config(font="Arial 10",foreground="black");
                filePathLabel.config(font="Arial 10",foreground="black");
                radioCont.config(highlightbackground="black", highlightthickness=1);

                button["state"] = "enable";
            
            if(canProceed):
                forget();

                thrd = threading.Thread(target=doFetch);
                thrd.start();
            else:
                button["state"] = "disable";
                stautsMarginMult = 0;
                errorTitle = ttk.Label(mainFrame, text="Virheet:", font=("Arial","10","bold"), style="errorLabel.TLabel");
                errorTitle.place(x=0, y=250);
                this.statusElems.append(errorTitle);
                this.fetchLocations = [];

                for error in errors:
                    if("Päivämäärät" in error):
                        dateExample.config(font=("Arial","10","bold"),foreground="red");

                    if("Ajat" in error):
                        timeExample.config(font=("Arial","10","bold"),foreground="red");
                        
                    if("Sulje" in error):
                        filePathLabel.config(font=("Arial","10","bold"),foreground="red");
                    
                    if("Sijaintia" in error):
                        radioCont.config(highlightbackground="red", highlightthickness=2);

                    statusElem = ttk.Label(mainFrame, text=error, font="Arial 10");
                    statusElem.place(x=0, y=275+(25*stautsMarginMult));
                    this.statusElems.append(statusElem);
                    stautsMarginMult += 1;
                
                forgetTimer = threading.Timer(3, forget);
                forgetTimer.start();

        kaisa = IntVar();
        kumpula = IntVar();
        viikki = IntVar();
        terkko = IntVar();

        avaaheti = IntVar();

        s = ttk.Style();
        s.configure("s.TLabel", background="white", foreground="black");
        s.configure("errorLabel.TLabel", foreground="red");

        # elements

        mainFrame = tk.Frame(window);
        mainFrame.grid(row=0, column=0, columnspan=10, rowspan=10, sticky=W);

        sideFrame = tk.Frame(mainFrame);
        sideFrame.grid(row=1, column=0, rowspan=10, columnspan=1);

        centerFrame = tk.Frame(mainFrame);
        centerFrame.grid(row=1, column=1, rowspan=10, columnspan=3, padx=10);

        headerFrame = ttk.Frame(mainFrame);
        headerFrame.grid(row=0, column=0, rowspan=1, columnspan=10);

        titleLabel = ttk.Label(headerFrame, text="Tilastokerääjä", style="s.TLabel", font="Arial 15");
        titleLabel.grid(row=0, column=0, padx=15, pady=10);

        radioCont = tk.Frame(sideFrame, highlightbackground="black", highlightthickness=1);
        radioCont.grid(row=1, column=0, columnspan= 1, padx=15, pady=(10, 9));
    
        rad1 = ttk.Checkbutton(radioCont, text="Kaisa-talo",variable=kaisa, onvalue=1, offvalue=0, command=select);
        rad1.grid(row=1, column=0, sticky=W);

        rad2 = ttk.Checkbutton(radioCont, text="Kumpula",variable=kumpula, onvalue=1, offvalue=0, command=select)
        rad2.grid(row=2, column=0, sticky=W);

        rad3 = ttk.Checkbutton(radioCont, text="Viikki",variable=viikki, onvalue=1, offvalue=0, command=select)
        rad3.grid(row=3, column=0, sticky=W);
        
        rad4 = ttk.Checkbutton(radioCont, text="Terkko",variable=terkko, onvalue=1, offvalue=0, command=select)
        rad4.grid(row=4, column=0, sticky=W);

        dateFormatLabel = ttk.Label(centerFrame, text="PP.KK.VVVV", font="Arial 12");
        dateFormatLabel.grid(row=0, column=2, sticky=W);

        dateStartLabel = ttk.Label(centerFrame, text="Pvm - alku", font="Arial 12");
        dateStartLabel.grid(row=1, column=1, sticky=W);

        dateExample = ttk.Label(centerFrame, text="esim. 01.03.2023, 12.11.2020", font="Arial 10");
        dateExample.grid(row=1, column=3, sticky=W);

        dateStartInput = ttk.Entry(centerFrame, width=12, font="Arial 12");
        dateStartInput.grid(row=1, column=2, sticky=N);

        dateEndLabel = ttk.Label(centerFrame, text="Pvm - loppu", font="Arial 12");
        dateEndLabel.grid(row=2, column=1, sticky=W);

        dateEndInput = ttk.Entry(centerFrame, width=12, font="Arial 12");
        dateEndInput.grid(row=2, column=2, sticky=N);

        timeFormatLabel = ttk.Label(centerFrame, text="TT", font="Arial 12");
        timeFormatLabel.grid(row=3, column=2, sticky=W);

        dateStartLabel = ttk.Label(centerFrame, text="Aika - alku", font="Arial 12");
        dateStartLabel.grid(row=4, column=1, sticky=W);

        timeExample = ttk.Label(centerFrame, text="esim. 08, 14 ( 00-24 ). Ei minuutteja", font="Arial 10");
        timeExample.grid(row=4, column=3, sticky=W);

        timeStartInput = ttk.Entry(centerFrame, width=12, font="Arial 12");
        timeStartInput.insert(END, "08"); # default start
        timeStartInput.grid(row=4, column=2, sticky=N);

        timeEndLabel = ttk.Label(centerFrame, text="Aika - loppu", font="Arial 12");
        timeEndLabel.grid(row=5, column=1, sticky=W);
    
        timeEndInput = ttk.Entry(centerFrame, width=12, font="Arial 12");
        timeEndInput.insert(END, "23"); # default end
        timeEndInput.grid(row=5, column=2, sticky=N);

        button = ttk.Button(centerFrame, text="Hae", command=submit);
        button.grid(row=8, column=2, pady=(10,0));
        avaa = ttk.Checkbutton(centerFrame, text="Avaa heti",variable=avaaheti, onvalue=1, offvalue=0, command=select);
        avaa.grid(row=9, column=2);

        statusFrame = tk.Frame(sideFrame);
        statusFrame.grid(row=8, column=0);
        
        filePathFrame = ttk.Frame(mainFrame);
        filePathFrame.grid(row=11, column=0, rowspan=1, columnspan=10);

        filePathLabel = ttk.Label(mainFrame, text=this.folderPath, font="Arial 10", borderwidth=3, relief="solid", background="#ffffff");
        filePathLabel.grid(row=11, column=0, columnspan=10, padx=10, pady=10);

        def changeFilePath():
            newFolderPath = filedialog.askdirectory(initialdir="/");
            if(len(newFolderPath) > 0): # if the folder path was chosen and not cancelled
                this.folderPath = newFolderPath;
                filePathLabel.config(text=this.folderPath);
        def LOnHoverIn():
            filePathLabel.config(background="#c7c7c7");
        def LOnHoverOut():
            filePathLabel.config(background="#ffffff");
        
        filePathLabel.bind("<Button-1>", lambda e:changeFilePath());
        filePathLabel.bind("<Enter>", lambda e:LOnHoverIn());
        filePathLabel.bind("<Leave>", lambda e:LOnHoverOut());

        bottomFrame = ttk.Frame(mainFrame);
        bottomFrame.grid(row=13, column=0, rowspan=1, columnspan=3);

        creditsLabel = ttk.Label(bottomFrame, text="Mikko Legezin - 2024", font="Arial 6");
        creditsLabel.grid(row=13, column= 2, sticky=S, pady=(100, 0), padx=(120,0));