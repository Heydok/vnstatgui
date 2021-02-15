import json
from os import replace
from tkinter import *
from tkinter import ttk, filedialog
from tkinter.font import Font
from datetime import datetime, time
from tkcalendar import Calendar
from Functions import getoutput, getinterfaces


LargeFont = ("Verdana", 12)
startDate = datetime(2021, 1, 1, 00, 00, 00)
endDate = datetime.now()
saveli = []

#  Containter Class
class vnstatgui(Tk):

    def __init__(self, *args, **kwargs):
        
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        self.geometry('550x550')
        self.title('Heydok\'s VNSTAT GUI')
            
        menubar = MenuBar(self)
        self.config(menu=menubar)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (maingui, filterdate):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(maingui)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

#  Main window
class maingui(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="VNSTAT GUI BY HEYDOK", font = LargeFont)
        label.pack(padx=10, pady=10)
        
        self.filterBtn = Button(self, text='>>> Filter Date <<<', command = lambda: controller.show_frame(filterdate))
        self.filterBtn.pack(fill=X, padx=10)
      
        self.treeframe = LabelFrame(self, text="Data")
        self.treeframe.pack(pady=20)

        self.comframe = Frame(self)
        self.comframe.pack(padx=20, fill=BOTH)

        self.radio_frame = LabelFrame(self.comframe, text="Data Options", labelanchor=N)
        self.radio_frame.pack(side=LEFT, anchor=N, expand=1)

        self.iface_frame = LabelFrame(self.comframe, text="Select Interface", labelanchor=N)
        self.iface_frame.pack(side=RIGHT, anchor=N, expand=1,)

        self.tree_scroll = Scrollbar(self.treeframe)
        self.tree_scroll.pack(side=RIGHT, fill=Y)

        self.setupiface()
        self.createTreeview()
        self.setupRadioButons()

        self.minsizeVar = StringVar()
        self.minsizeVar.set(-1)
        self.minsizelbl = Label(self.iface_frame, text='Min Data Size').pack()   
        self.minsize = Spinbox(self.iface_frame, textvariable=self.minsizeVar, from_=-1, to=10000).pack()

        global savefile  # Allows me to save file from menu in diffrent class
        savefile = lambda: self.savefile()
    
        
    #  Function to sort treeview data when clicking on column headers
    def treeview_sort_column(self, tv, col, reverse):
        try:
            data_list = [
                (float(self.treeview.set(k, col)[0:-3]), k) for k in self.treeview.get_children("")]

        except Exception:
            data_list = [(self.treeview.set(k, col), k) for k in self.treeview.get_children("")]

        data_list.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(data_list):
            self.treeview.move(k, "", index)

        # reverse sort next time
        self.treeview.heading(
            column=col,
            text=col,
            command=lambda _col=col: self.treeview_sort_column(
                self.treeview, _col, not reverse
            ),
        )
    
    #  Create and configure treeview
    def createTreeview(self):
        self.columns = ("Date", "Down", "Up", "Total")

        self.treeview = ttk.Treeview(self.treeframe, columns=self.columns, show='headings', yscrollcommand=self.tree_scroll.set)
        for col in self.columns:
            self.treeview.heading(col, text=col, command=lambda _col=col: \
                            self.treeview_sort_column(self.treeview, _col, False))

        self.treeview.pack(fill=Y)

        self.treeview.column("#0", width=0, stretch=NO)
        self.treeview.column("Date", anchor=CENTER, width=150)
        self.treeview.column("Down", anchor=CENTER, width=110)
        self.treeview.column("Up", anchor=CENTER, width=110)
        self.treeview.column("Total", anchor=CENTER, width=110)

        # Configure Scrollbar
        self.tree_scroll.config(command=self.treeview.yview)
        
    def setupiface(self):
        # Create Dropdown menu for Interface Selection
        self.ifaces = getinterfaces() # Get List of interfaces

        self.ifaceVar = StringVar(self.iface_frame) # Create choice Variable
        self.ifaceVar.set(self.ifaces[0]) # Set default value to first in list      

        self.ifaceMenu = OptionMenu(self.iface_frame, self.ifaceVar, *self.ifaces)
        self.ifaceMenu.config(indicatoron=1, width=15, height=1)
        self.ifaceMenu.pack()

    #  Add data to treeview
    def add_data(self, option, iface):
        for record in self.treeview.get_children():
            self.treeview.delete(record)
       
        self.count = 0
        
        for line in getoutput(option, iface):
            self.ddate = line[0]
            self.download = '%0.2f %s' % (line[1], line[2])
            self.upload = '%0.2f %s' % (line[3], line[4])
            self.total = '%0.2f %s' % (line[5], line[6])
            self.pdate = ''
            if option == 'm':
                self.pdate = self.ddate.strftime('%Y-%m-%d')
            elif option == 'f' or option == 'h':
                self.pdate = self.ddate.strftime('%Y-%m-%d | %H:%M')
            else:
                self.pdate = self.ddate
            
            #  Still needs changes to be made to the datetime filter

            try:
                if self.ddate >= startDate and self.ddate <= endDate and line[5] > float(self.minsizeVar.get()):
                    self.treeview.insert(parent='', 
                                    index='end', 
                                    iid=self.count, 
                                    text="Parent", 
                                    values=(self.pdate, self.download, self.upload, self.total))
                    self.count += 1
            except:
                try:
                    if self.ddate >= startDate.date() and self.ddate <= endDate.date() and line[5] > float(self.minsizeVar.get()):
                        self.treeview.insert(parent='',
                                        index='end', 
                                        iid=self.count, 
                                        text="Parent", 
                                        values=(self.pdate, self.download, self.upload, self.total))
                        self.count += 1
                except:
                    pass

    #  Fill in treeview data according to choice
    def showChoice(self):
        for op, val in self.dataOptions:
            if val == self.r.get():
                saveli.clear()
                saveli.append(op)
                saveli.append(self.ifaceVar.get())
                self.treeframe.config(text=op)
                self.add_data(self.r.get(), self.ifaceVar.get())

    #  Setup and add radio buttons for data type
    def setupRadioButons(self):
        self.r = StringVar()
        self.r.set(1)
        self.grow = 0
        self.gcolumn = 0
        self.dataOptions = [("Five Minute Data", "f"),
                            ("Hourly Data", "h"),
                            ("Daily Data", "d"),
                            ("Monthly Data", "m"),
                            ("Top 10 Data", "t")]
        
        for op, val in self.dataOptions:
            Radiobutton(self.radio_frame, 
                        text=op,
                        indicatoron=0,
                        width=20,
                        padx = 20, 
                        variable=self.r, 
                        command=self.showChoice,
                        value=val).grid(row=self.grow, column=self.gcolumn, sticky=N)
            self.grow += 1

    #  Test function for export option
    def savefile(self):
        
        for record in self.treeview.get_children():
            row = self.treeview.item(record)['values']
            rdate = row[0]
            try:
                pdate = datetime.strptime(rdate, '%Y-%m-%d | %H:%M')
            except:
                pdate = datetime.strptime(rdate, '%Y-%m-%d')
            y = {"id":int(record),
                "date":str(pdate),
                "download":float(row[1].replace(" MB", "")),
                "upload":float(row[2].replace(" MB", "")),
                "total":float(row[3].replace(" MB", ""))

                }
            saveli.append(y)

        file_opt = options = {}
        options['filetypes'] = [('all files', '.*'), ('text files', '.json')]
        options['initialfile'] = 'vnstatgui.json'

        savefile = filedialog.asksaveasfile(defaultextension=".json", **file_opt)
        if savefile is None:
            return
        json.dump(saveli, savefile, indent=4)

#  Class for filtering the data by date
class filterdate(Frame):
    
    def __init__(self, parent, controller):
    	
        Frame.__init__(self, parent)
        label = Label(self, text="SELECT DATE RANGE", font = LargeFont)
        label.pack(pady=10,padx=10)
        
        self.from_hour_string=StringVar()
        self.from_min_string=StringVar()
        self.to_hour_string=StringVar()
        self.to_min_string=StringVar()
        self.from_hour_string.set(0)
        self.from_min_string.set(0)
        self.to_hour_string.set(datetime.now().hour)
        self.to_min_string.set(datetime.now().minute)
        self.f = ('Times', 12)

        self.mainFrame = Frame(self)
        self.mainFrame.pack(side=TOP)

        self.fromFrame = LabelFrame(self.mainFrame, text='From Date', labelanchor=N)
        self.toFrame = LabelFrame(self.mainFrame, text='To Date', labelanchor=N)
        self.fromFrame.pack(pady=10, side=LEFT)
        self.toFrame.pack(pady=10, side=RIGHT)

        self.calFrom = Calendar(self.fromFrame, selectmode='day')
        self.calFrom.pack(padx=5)

        self.calTo = Calendar(self.toFrame, selectmode='day')
        self.calTo.pack(padx=5)

        self.from_hour_sb = Spinbox(
            self.fromFrame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=self.from_hour_string,
            width=1,
            font=self.f,
            justify=CENTER
            )
        self.from_min_sb = Spinbox(
            self.fromFrame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=self.from_min_string,
            font=self.f,
            width=1,
            justify=CENTER
            )

        self.frommsg = Label(
            self.fromFrame, 
            text="Hour     Minute",
            font=("Times", 12)
            )
        self.frommsg.pack(pady=(10, 0))

        self.from_hour_sb.pack(padx=(60, 0),side=LEFT, fill=X, expand=True)
        self.from_min_sb.pack(padx=(0, 60), side=LEFT, fill=X, expand=True)


        self.to_hour_sb = Spinbox(
            self.toFrame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=self.to_hour_string,
            width=1,
            font=self.f,
            justify=CENTER
            )
        self.to_min_sb = Spinbox(
            self.toFrame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=self.to_min_string,
            font=self.f,
            width=1,
            justify=CENTER
            )

        self.tomsg = Label(
            self.toFrame, 
            text="Hour     Minute",
            font=("Times", 12)
            )
        self.tomsg.pack(pady=(10, 0))

        self.to_hour_sb.pack(padx=(60, 0), side=LEFT, fill=X, expand=True)
        self.to_min_sb.pack(padx=(0, 60), side=LEFT, fill=X, expand=True)

        self.confirmBtn = Button(self, text="Confirm", command=lambda: self.Confirm())
        self.confirmBtn.pack(side=TOP, fill=X, padx=5)
        self.backBtn = Button(self, text="Back", command=lambda: controller.show_frame(maingui))
        self.backBtn.pack(side=TOP, fill=X, padx=5)
        
        self.concom = lambda: controller.show_frame(maingui)

    def setFromDateTime(self):
        self.fromDate = self.calFrom.selection_get()
        self.fromHour = self.from_hour_sb.get()
        self.fromMin = self.from_min_sb.get()
        self.fromtime = time(int(self.fromHour), int(self.fromMin))
        self.fromDateTime = datetime.combine(self.fromDate, self.fromtime)
        startDate = self.fromDateTime
        return startDate

    def setToDateTime(self):
        self.toDate = self.calTo.selection_get()
        self.toHour = self.to_hour_sb.get()
        self.toMin = self.to_min_sb.get()
        self.totime = time(int(self.toHour), int(self.toMin))
        self.toDateTime = datetime.combine(self.toDate, self.totime)
        endDate = self.toDateTime
        return endDate

    def Confirm(self):
        global startDate, endDate
        startDate = self.setFromDateTime()
        endDate = self.setToDateTime()
        self.concom()

#  Class for creating the Menu
class MenuBar(Menu):
    def __init__(self, master):
        Menu.__init__(self, master)

        file = Menu(self, tearoff=False)
        file.add_command(label="Save File", underline=1, command=lambda: savefile())
        file.add_separator()
        file.add_command(label="Exit", underline=1, command=self.quit)
        self.add_cascade(label="File",underline=0, menu=file)

        help = Menu(self, tearoff=0)  
        help.add_command(label="About", command=self.about)  
        self.add_cascade(label="Help", menu=help)  

    def exit(self):
        self.exit

    def about(self):
        self.labelfont = Font(family='Times', size=15, underline=1, weight='bold', slant='italic')
        self.aboutWindow = Toplevel()
        self.aboutWindow.title('About')
        self.aboutWindow.geometry('300x200')
        self.aboutLbl = Label(self.aboutWindow, text="Created By Heydok", font=self.labelfont)
        self.aboutLbl.pack(pady=10, padx=10, anchor=CENTER)
        self.githubLbl = Label(self.aboutWindow, text=r"https://github.com/heydok/vnstatgui", fg="blue", cursor="hand2")
        self.githubLbl.pack(pady=10, padx=10, anchor=CENTER)
        self.closeBtn = Button(self.aboutWindow, text="Close", command=lambda: self.aboutWindow.destroy())
        self.closeBtn.pack(pady=20, padx=10, side="bottom", anchor=W, fill=X)

app = vnstatgui()
app.mainloop()

