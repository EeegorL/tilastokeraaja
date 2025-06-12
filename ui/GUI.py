import os;
import time;
from datetime import datetime;

from tkinter import Frame, ttk, IntVar, N, W, S, E, END, NSEW, EW;
import tkinter.font as tkFont;

import threading;
from tkinter import filedialog;
from handlers.bmaHandler import fetchData;
from handlers.xlsxHandler import doXlsxThings, xlsxIsOpen, delXlsx, getFileName;

class UI:
    def __init__(self, root):
        self._root = root;
        self.fonts = {
            "small": tkFont.Font(family="Arial", size=10),
            "smallBold": tkFont.Font(family="Arial", size=10, weight="bold"),
            "default": tkFont.Font(family="Arial", size=10),
            "defaultBold": tkFont.Font(family="Arial", size=10, weight="bold"),
            "title": tkFont.Font(family="Arial", size=15, weight="bold"),
            "status": tkFont.Font(family="Arial", size=12, weight="bold"),
            "credits": tkFont.Font(family="Arial", size=6),
        }

    def start(self, window):
        self.folderPath = os.path.expanduser("~/Downloads"); # default dir Downloads
        self.fetchLocations = [];
        self.statusElems = [];
        def select():
            selected = [];
            if(kaisa.get()): selected.append("Kaisa");
            if(kumpula.get()): selected.append("Kumpula");
            if(viikki.get()): selected.append("Viikki");
            if(terkko.get()): selected.append("Terkko");

            self.fetchLocations = selected[:];
        
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

            # input values
            dateStart = dateStartInput.get();
            dateEnd = dateEndInput.get();
            timeStart = timeStartInput.get();
            timeEnd = timeEndInput.get();

            if(len(self.fetchLocations) == 0):
                errors.append("Sijaintia ei valittu");
                canProceed = False;
            if(not datesAreValid(dateStart, dateEnd)):
                errors.append("Tarkista päivämäärät");
                canProceed = False;
            if(not timesAreValid(timeStart, timeEnd)):
                errors.append("Tarkista ajat");
                canProceed = False;
            if(xlsxIsOpen(self.folderPath)):
                errors.append("Sulje tulostiedosto: " + self.folderPath + getFileName());
                canProceed = False;      

            def doFetch():
                button["state"] = "disable";
                button["state"] = "disable";

                statusMarginMult = 0;
                delXlsx(self.folderPath);
                for location in self.fetchLocations:
                    statusMarginMult += 1;

                    statusElem = ttk.Label(mainFrame, text=location, font=self.fonts["small"]);
                    statusElem.place(x=0, y=250+(25*statusMarginMult));

                    self.statusElems.append(statusElem);
                    
                    statusElem.config(text=location + "...");
                    data = fetchData(location=location, dateStart=dateStart, dateEnd=dateEnd, timeStart=timeStart, timeEnd=timeEnd);
                    doXlsxThings(data, self.folderPath);
                
                    statusElem.config(text=location+": \u2713", foreground="green", font=self.fonts["status"]);
                if(avaaheti.get()):
                    os.startfile((self.folderPath + getFileName()).replace("/","\\"));
                time.sleep(2);
                
                statusMarginMult = 0;
                forget();
                button["state"] = "enable";
            
            def forget():
                for elem in self.statusElems:
                    elem.destroy();

                dateExample.config(font=self.fonts["small"], foreground="black");
                timeExampleLabel.config(font=self.fonts["small"], foreground="black");
                filePathLabel.config(font=self.fonts["small"], foreground="black");
                radioFrame.config(highlightbackground="black", highlightthickness=1);

                button["state"] = "enable";
            
            if(canProceed):
                forget();

                thrd = threading.Thread(target=doFetch);
                thrd.start();
            else:
                button["state"] = "disable";
                statusMarginMult = 0;
                errorTitle = ttk.Label(mainFrame, text="Virheet:", font=self.fonts["smallBold"], style="errorLabel.TLabel");
                errorTitle.place(x=0, y=250);
                self.statusElems.append(errorTitle);

                for error in errors:
                    if("päivämäärät" in error):
                        dateExample.config(font=self.fonts["smallBold"], foreground="red");

                    if("ajat" in error):
                        timeExampleLabel.config(font=self.fonts["smallBold"], foreground="red");
                        
                    if("Sulje" in error):
                        filePathLabel.config(font=self.fonts["smallBold"], foreground="red");
                    
                    if("Sijaintia" in error):
                        radioFrame.config(highlightbackground="red", highlightthickness=2);

                    statusElem = ttk.Label(mainFrame, text=error, font=self.fonts["small"]);
                    statusElem.place(x=0, y=275+(20*statusMarginMult));
                    self.statusElems.append(statusElem);
                    statusMarginMult += 1;
                
                forgetTimer = threading.Timer(3, forget);
                forgetTimer.start();

        kaisa = IntVar();
        kumpula = IntVar();
        viikki = IntVar();
        terkko = IntVar();

        # default to checked
        kaisa.set(1);
        kumpula.set(1);
        viikki.set(1);
        terkko.set(1);

        avaaheti = IntVar();

        s = ttk.Style();
        s.configure("s.TLabel", background="white", foreground="black");
        s.configure("errorLabel.TLabel", foreground="red");

        # Elements
        #------------------------------------------
        # > Frames
        window.columnconfigure(0, weight=1);
        window.rowconfigure(0, weight=1);

        mainFrame = Frame(window);
        mainFrame.grid(row=0, column=0, sticky=EW);
        mainFrame.columnconfigure(0, weight=1);
        mainFrame.rowconfigure(0, weight=1);

        centerFrame = Frame(mainFrame);
        centerFrame.grid(row=1, column=0);

        centerLeftFrame = Frame(centerFrame);
        centerLeftFrame.grid(row=1, column=0, columnspan=2);
        centerLeftFrame.columnconfigure(0, minsize=150);
        centerLeftFrame.rowconfigure(0, minsize=150);
        
        centerRightFrame = Frame(centerFrame);
        centerRightFrame.grid(row=1, column=3, columnspan=5); 

        headerFrame = Frame(mainFrame);
        headerFrame.grid(row=0, column=0, sticky=N);

        filePathFrame = Frame(mainFrame);
        filePathFrame.grid(row=3, column=0, rowspan=1, columnspan=10);

        radioFrame = Frame(centerLeftFrame, highlightbackground="black", highlightthickness=1);
        radioFrame.grid(row=0, column=0);
        radioFrame.rowconfigure(0, weight=1);

        bottomFrame = Frame(mainFrame);
        bottomFrame.grid(row=4, column=0, rowspan=1, columnspan=100);
        #------------------------------------------

        # > Labels
        titleLabel = ttk.Label(headerFrame, text="Tilastokerääjä", style="s.TLabel", font=self.fonts["title"]);
        titleLabel.grid(row=0, column=2, padx=10, pady=10);

        dateFormatLabel = ttk.Label(centerRightFrame, text="PP.KK.VVVV", font=self.fonts["default"]);
        dateFormatLabel.grid(row=0, column=2, sticky=W);

        dateStartLabel = ttk.Label(centerRightFrame, text="Pvm - alku", font=self.fonts["default"]);
        dateStartLabel.grid(row=1, column=1, sticky=W);

        dateExample = ttk.Label(centerRightFrame, text="esim. 01.03.2023, 12.11.2020", font=self.fonts["small"]);
        dateExample.grid(row=1, column=3, sticky=W);

        dateEndLabel = ttk.Label(centerRightFrame, text="Pvm - loppu", font=self.fonts["default"]);
        dateEndLabel.grid(row=2, column=1, sticky=W);

        timeFormatLabel = ttk.Label(centerRightFrame, text="TT", font=self.fonts["default"]);
        timeFormatLabel.grid(row=3, column=2, sticky=W);

        dateStartLabel = ttk.Label(centerRightFrame, text="Aika - alku", font=self.fonts["default"]);
        dateStartLabel.grid(row=4, column=1, sticky=W);

        timeEndLabel = ttk.Label(centerRightFrame, text="Aika - loppu", font=self.fonts["default"]);
        timeEndLabel.grid(row=5, column=1, sticky=W);

        filePathLabel = ttk.Label(filePathFrame, text=self.folderPath, font=self.fonts["small"], borderwidth=3, relief="solid", background="#ffffff");
        filePathLabel.grid(row=10, column=0, columnspan=10, padx=10, pady=10);

        timeExampleLabel = ttk.Label(centerRightFrame, text="esim. 08, 14 ( 00-24 ). Ei minuutteja", font=self.fonts["small"]);
        timeExampleLabel.grid(row=4, column=3, sticky=W);

        creditsLabel = ttk.Label(bottomFrame, text="Mikko Legezin - 2024", font=self.fonts["credits"]);
        creditsLabel.grid(row=13, column=3, sticky=S, pady=(100, 0));
        #------------------------------------------
    
        # > Other
        rad1 = ttk.Checkbutton(radioFrame, text="Kaisa-talo",variable=kaisa, onvalue=1, offvalue=0, command=select);
        rad1.grid(row=1, column=0, sticky=W);

        rad2 = ttk.Checkbutton(radioFrame, text="Kumpula",variable=kumpula, onvalue=1, offvalue=0, command=select)
        rad2.grid(row=2, column=0, sticky=W);

        rad3 = ttk.Checkbutton(radioFrame, text="Viikki",variable=viikki, onvalue=1, offvalue=0, command=select)
        rad3.grid(row=3, column=0, sticky=W);
        
        rad4 = ttk.Checkbutton(radioFrame, text="Terkko",variable=terkko, onvalue=1, offvalue=0, command=select)
        rad4.grid(row=4, column=0, sticky=W);

        dateStartInput = ttk.Entry(centerRightFrame, width=12, font=self.fonts["default"]);
        dateStartInput.grid(row=1, column=2, sticky=N);

        dateEndInput = ttk.Entry(centerRightFrame, width=12, font=self.fonts["default"]);
        dateEndInput.grid(row=2, column=2, sticky=N);

        timeStartInput = ttk.Entry(centerRightFrame, width=12, font=self.fonts["default"]);
        timeStartInput.insert(END, "08");
        timeStartInput.grid(row=4, column=2, sticky=N);
    
        timeEndInput = ttk.Entry(centerRightFrame, width=12, font=self.fonts["default"]);
        timeEndInput.insert(END, "23"); # default end
        timeEndInput.grid(row=5, column=2, sticky=N);

        button = ttk.Button(centerRightFrame, text="Hae", command=submit);
        button.grid(row=8, column=2, pady=(10,0));
        avaa = ttk.Checkbutton(centerRightFrame, text="Avaa heti",variable=avaaheti, onvalue=1, offvalue=0, command=select);
        avaa.invoke(); # päällä oletuksena
        avaa.grid(row=9, column=2);
        
        def changeFilePath():
            newFolderPath = filedialog.askdirectory(initialdir="/");
            if(len(newFolderPath) > 0): # if the folder path was chosen and not cancelled
                self.folderPath = newFolderPath;
                filePathLabel.config(text=self.folderPath);
        def LOnHoverIn():
            filePathLabel.config(background="#c7c7c7");
        def LOnHoverOut():
            filePathLabel.config(background="#ffffff");
        
        filePathLabel.bind("<Button-1>", lambda e:changeFilePath());
        filePathLabel.bind("<Enter>", lambda e:LOnHoverIn());
        filePathLabel.bind("<Leave>", lambda e:LOnHoverOut());