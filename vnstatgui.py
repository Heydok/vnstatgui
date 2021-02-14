from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from datetime import datetime, time
from tkcalendar import Calendar
from Functions import getoutput, getinterfaces


LargeFont = ("Verdana", 12)
startDate = datetime(2021, 1, 1, 00, 00, 00)
endDate = datetime.now()

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

        #printBtn = Button(self, text="print tree", command=lambda: self.printtree())
        #printBtn.pack()

    def treeview_sort_column(self, tv, col, reverse):
        try:
            data_list = [
                (float(self.treeview.set(k, col)[0:-3]), k) for k in self.treeview.get_children("")]

        except Exception:
            data_list = [(self.treeview.set(k, col), k) for k in self.treeview.get_children("")]

        #pprint(data_list)

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

    def add_data(self, option, iface):
        for record in self.treeview.get_children():
            self.treeview.delete(record)
       
        self.count = 0
        
        for line in getoutput(option, iface):
            self.ddate = line[0]
            self.download = '%0.2f %s' % (line[1], line[2]) # download = '%0.2f %s' % (line[1], line[2])
            self.upload = '%0.2f %s' % (line[3], line[4]) # upload = '%0.2f %s' % (line[3], line[4])
            self.total = '%0.2f %s' % (line[5], line[6]) # total = '%0.2f %s' % (line[5], line[6])
            self.pdate = ''
            if option == 'm':
                self.pdate = self.ddate.strftime('%Y-%m')
            elif option == 'f' or option == 'h':
                self.pdate = self.ddate.strftime('%Y-%m-%d | %H:%M')
            else:
                self.pdate = self.ddate

            try:
                if self.ddate >= startDate and self.ddate <= endDate:
                    self.treeview.insert(parent='', 
                                    index='end', 
                                    iid=self.count, 
                                    text="Parent", 
                                    values=(self.pdate, self.download, self.upload, self.total))
                    self.count += 1
                    #print(type(self.ddate),' datetime ', self.ddate)
            except:
                try:
                    if self.ddate >= startDate.date() and self.ddate <= endDate.date():
                        self.treeview.insert(parent='',
                                        index='end', 
                                        iid=self.count, 
                                        text="Parent", 
                                        values=(self.pdate, self.download, self.upload, self.total))
                        self.count += 1
                        #print(type(self.ddate), ' date ', self.ddate)
                except:
                    pass
    
    def showChoice(self):
        for op, val in self.dataOptions:
            if val == self.r.get():
                self.treeframe.config(text=op)
                self.add_data(self.r.get(), self.ifaceVar.get())

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

    def printtree(self):
        for record in self.treeview.get_children():
            row = self.treeview.item(record)['values']
            print(row)

class filterdate(Frame):
    
    def __init__(self, parent, controller):
    	
        Frame.__init__(self, parent)
        label = Label(self, text="SELECT DATE RANGE", font = LargeFont)
        label.pack(pady=10,padx=10)
        from_hour_string=StringVar()
        from_min_string=StringVar()
        to_hour_string=StringVar()
        to_min_string=StringVar()
        from_hour_string.set(0)
        from_min_string.set(0)
        to_hour_string.set(datetime.now().hour)
        to_min_string.set(datetime.now().minute)
        f = ('Times', 12)

        mainFrame = Frame(self)
        mainFrame.pack(side=TOP)

        fromFrame = LabelFrame(mainFrame, text='From Date', labelanchor=N)
        toFrame = LabelFrame(mainFrame, text='To Date', labelanchor=N)
        fromFrame.pack(pady=10, side=LEFT)
        toFrame.pack(pady=10, side=RIGHT)

        calFrom = Calendar(fromFrame, selectmode='day') #  year=2021, month=1, day=1
        calFrom.pack(padx=5)

        calTo = Calendar(toFrame, selectmode='day')
        calTo.pack(padx=5)

        def setFromDateTime():
            fromDate = calFrom.selection_get()
            fromHour = from_hour_sb.get()
            fromMin = from_min_sb.get()
            fromtime = time(int(fromHour), int(fromMin))
            fromDateTime = datetime.combine(fromDate, fromtime)
            startDate = fromDateTime
            return startDate

        def setToDateTime():
            toDate = calTo.selection_get()
            toHour = to_hour_sb.get()
            toMin = to_min_sb.get()
            totime = time(int(toHour), int(toMin))
            toDateTime = datetime.combine(toDate, totime)
            endDate = toDateTime
            return endDate

        from_hour_sb = Spinbox(
            fromFrame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=from_hour_string,
            width=1,
            font=f,
            justify=CENTER
            )
        from_min_sb = Spinbox(
            fromFrame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=from_min_string,
            font=f,
            width=1,
            justify=CENTER
            )

        frommsg = Label(
            fromFrame, 
            text="Hour     Minute",
            font=("Times", 12)
            )
        frommsg.pack(pady=(10, 0))

        from_hour_sb.pack(padx=(60, 0),side=LEFT, fill=X, expand=True)
        from_min_sb.pack(padx=(0, 60), side=LEFT, fill=X, expand=True)


        to_hour_sb = Spinbox(
            toFrame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=to_hour_string,
            width=1,
            font=f,
            justify=CENTER
            )
        to_min_sb = Spinbox(
            toFrame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=to_min_string,
            font=f,
            width=1,
            justify=CENTER
            )

        tomsg = Label(
            toFrame, 
            text="Hour     Minute",
            font=("Times", 12)
            )
        tomsg.pack(pady=(10, 0))

        to_hour_sb.pack(padx=(60, 0), side=LEFT, fill=X, expand=True)
        to_min_sb.pack(padx=(0, 60), side=LEFT, fill=X, expand=True)

        def Confirm():
            global startDate, endDate
            #print('startDate', startDate)
            #print('endDate ', endDate)
            startDate = setFromDateTime()
            endDate = setToDateTime()
            #print('From Date ',type(startDate), startDate)
            #print('To Date ', type(endDate), endDate)
            controller.show_frame(maingui)

        confirmBtn = Button(self, text="Confirm", command=lambda: Confirm())
        confirmBtn.pack(side=TOP, fill=X, padx=5)
        backBtn = Button(self, text="Back", command=lambda: controller.show_frame(maingui))
        backBtn.pack(side=TOP, fill=X, padx=5)        

class MenuBar(Menu):
    def __init__(self, master):
        Menu.__init__(self, master)

        file = Menu(self, tearoff=False)
        #file.add_command(label="New")  
        #file.add_command(label="Open")  
        #file.add_command(label="Save")  
        #file.add_command(label="Save as")    
        file.add_separator()
        file.add_command(label="Exit", underline=1, command=self.quit)
        self.add_cascade(label="File",underline=0, menu=file)
        
        #edit = Menu(self, tearoff=0)  
        #edit.add_command(label="Undo")  
        #edit.add_separator()     
        #edit.add_command(label="Cut")  
        #edit.add_command(label="Copy")  
        #edit.add_command(label="Paste")  
        #self.add_cascade(label="Edit", menu=edit) 

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
        #self.aboutWindow.iconbitmap("@hd.xbm")
        self.aboutLbl = Label(self.aboutWindow, text="Created By Heydok", font=self.labelfont)
        self.aboutLbl.pack(pady=10, padx=10, anchor=CENTER)
        self.githubLbl = Label(self.aboutWindow, text=r"https://github.com/heydok", fg="blue", cursor="hand2")
        self.githubLbl.pack(pady=10, padx=10, anchor=CENTER)
        self.closeBtn = Button(self.aboutWindow, text="Close", command=lambda: self.aboutWindow.destroy())
        self.closeBtn.pack(pady=20, padx=10, side="bottom", anchor=W, fill=X)

app = vnstatgui()
app.mainloop()

