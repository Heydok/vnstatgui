from matplotlib import pyplot
from resources.mplwidget import MplCanvas
import sys
import os
import time
import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidget, QWidget, QMessageBox, QFileDialog
from resources.Functions import get_data, getinterfaces, default_conf
import pandas as pd
import datetime
from configparser import ConfigParser, ExtendedInterpolation
from resources.Ui_mainwindow import Ui_MainWindow
from resources.Ui_about import Ui_About
from resources.Ui_settings import Ui_Settings
from resources.Ui_myplot import Ui_myplot


import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT


now = datetime.datetime.now()

testdf = []


class QCustomTableWidgetItem (QtWidgets.QTableWidgetItem):

    def __init__ (self, value):
        super(QCustomTableWidgetItem, self).__init__(str('%s' % value))

    def __lt__ (self, other):
        if (isinstance(other, QCustomTableWidgetItem)):
            try:
                selfDataValue = float(str(self.data(QtCore.Qt.EditRole)))
                otherDataValue = float(str(other.data(QtCore.Qt.EditRole)))
                return selfDataValue < otherDataValue
            except:
                selfDataValue = str(self.data(QtCore.Qt.EditRole))
                otherDataValue = str(other.data(QtCore.Qt.EditRole))
                return selfDataValue < otherDataValue
        else:
            return QtWidgets.QTableWidgetItem.__lt__(self, other)


class Mainwindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Mainwindow, self).__init__()
        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.endDate.setDateTime(now)

        self.ui.tableWidget.setColumnWidth(0, 70)
        self.ui.tableWidget.setColumnWidth(1, 120)
        self.ui.tableWidget.setColumnWidth(2, 95)
        self.ui.tableWidget.setColumnWidth(3, 95)
        self.ui.tableWidget.setColumnWidth(4, 100)

        self.ui.plotdataBtn.clicked.connect(lambda: self.showplot())
        self.ui.refreshBtn.clicked.connect(lambda: self.refesh())
        self.ui.actionRefresh.triggered.connect(lambda: self.refesh())
        self.ui.actionSettings.triggered.connect(lambda: self.showSettings())
        self.ui.actionExit.triggered.connect(lambda: self.exitCall())
        self.ui.actionAbout.triggered.connect(lambda: self.showabout())
        self.ui.actionSave_Data.triggered.connect(lambda: self.saveFileDialog())

        self.interfaces()
        self.datatype()
        self.dataSize()
        self.loaddata()

        self.worker = WorkThread()
        self.workerThread = QtCore.QThread()
        self.workerThread.started.connect(self.worker.run)
        self.worker.moveToThread(self.workerThread)
        self.worker.UpdateSignals.connect(self.UpdateLiveDataFunction)

        self.ui.ispausedBtn.clicked.connect(self.PauseThreading)
        app.aboutToQuit.connect(lambda: self.StopThreading(None))
        self.StartThreading(None)


    def StartThreading(self, event):
        self.workerThread.start()


    def StopThreading(self, event):
        self.worker.stop()
        self.workerThread.quit()
        self.workerThread.wait()


    def PauseThreading(self, event):
        self.worker.pause()


    def UpdateLiveDataFunction(self, value):
        self.ui.rxLbl.setText(value[0])
        self.ui.txLbl.setText(value[1])

    def loaddata(self):
        # self.ui.tableWidget.clearContents()
        iface = self.ui.interfaceCB.currentText()
        datatype = self.ui.datatypeCB.currentData()
        startdate = self.ui.startDate.dateTime().toPyDateTime()  # toString("yyyy-MM-dd HH:MM:SS")
        enddate = self.ui.endDate.dateTime().toPyDateTime()
        dataSize = self.ui.minSize.value()

        df = get_data(datatype, iface)
        df.drop(columns=['id'], inplace=True)

        df['Download'] = df['Download'].apply('{:,.2f}'.format).replace({'\$': '', ',': ''}, regex=True).astype(float)
        df['Upload'] = df['Upload'].apply('{:,.2f}'.format).replace({'\$': '', ',': ''}, regex=True).astype(float)
        df['Total'] = df['Total'].apply('{:,.2f}'.format).replace({'\$': '', ',': ''}, regex=True).astype(float)
        df['FiltDate'] = pd.to_datetime(df['Date'])

        filt = (df['FiltDate'] >= startdate) & (df['FiltDate'] <= enddate) & (df['Total'] >= dataSize)
        df = df.loc[filt] 
        
        self.ui.tableWidget.setRowCount(df.shape[0])
        self.ui.tablewdgBox.setTitle(self.ui.datatypeCB.currentText())
        self.ui.tableWidget.resizeRowsToContents()

        df_array = df.values
        for row in range(df.shape[0]):
            # self.ui.tableWidget.setRowHeight(row, 5)
            for col in range(df.shape[1]):
                self.ui.tableWidget.setItem(row, col, QCustomTableWidgetItem(df_array[row,col]))
        
        self.readTableData()

    
    def interfaces(self):
        ifacelist = getinterfaces()
        self.ui.interfaceCB.addItem('All', 'All')
        self.ui.interfaceCB.addItems(ifacelist)
        self.ui.interfaceCB.setCurrentIndex(1)
        self.ui.interfaceCB.currentIndexChanged.connect( lambda: self.loaddata())


    def datatype(self):
        types = ["fiveminute", "hour", "day", "month", "year", "top"]
        index = 0
        
        for i in types:
            self.ui.datatypeCB.setItemData(index, i)
            index += 1

        self.ui.datatypeCB.setCurrentIndex(2)
        self.ui.datatypeCB.currentIndexChanged.connect( lambda: self.loaddata())


    def dataSize(self):
        minSize = self.ui.minSize.value()
        self.ui.minSize.valueChanged.connect(lambda: self.loaddata())
        return minSize


    def refesh(self):
        self.ui.tableWidget.clearSelection()
        #self.ui.tableWidget.disconnect()
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)
        self.loaddata()
        print("Done!")


    def exitCall(self):
            print("Thank you, Come again.")
            self.close()


    def showabout(self):
        self.about = about_ui()
        self.about.show()


    def showSettings(self):
        self.settings = settings_ui()
        self.settings.show()


    def showplot(self):
        self.myplot = myplot_ui()
        self.myplot.show()


    def readTableData(self):
        table = self.ui.tableWidget
        col_count = table.columnCount()
        row_count = table.rowCount()
        headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Download'] = df['Download'].astype(float)
        df['Upload'] = df['Upload'].astype(float)
        df['Total'] = df['Total'].astype(float)
        
        global testdf
        testdf = df


    def saveFileDialog(self):
        savedf = testdf        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "vnstat.json","JSON Files (*.json)", options=options)
        if filename == "":
            return
        with open(filename, 'w') as f:
            text = savedf.to_json(orient="table")
            parsed = json.loads(text)
            f.write(json.dumps(parsed, indent=4))
        

class about_ui(QtWidgets.QWidget):
    def __init__(self):
        super(about_ui, self).__init__()
        self.ui = Ui_About()
        self.ui.setupUi(self)


class settings_ui(QtWidgets.QWidget):
    def __init__(self):
        super(settings_ui, self).__init__()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)

        self.ui.resetBtn.clicked.connect(lambda: self.reset_config())
        self.ui.saveBtn.clicked.connect(lambda: self.save_config())

        self.configpath = '~/.vnstatrc'
        if not self.configpath is None:
            self.configpath = os.path.expanduser(self.configpath)
        self.defaultdict = default_conf


        # assess the parser dict
        parser = ConfigParser(comment_prefixes='#', delimiters=' ', interpolation=ExtendedInterpolation())
        parser.optionxform = str
        try:
            parser.read(self.configpath)
        except TypeError as e:
            print(e)
            print("Using the defaultdict instead")
            parser.read_dict(self.defaultdict)
        finally:
            parser_dict = self.as_dict(parser)
            self.build(parser_dict)


    def build(self, parser_dict: dict) -> None:
        
        self.parser_dict = parser_dict
        self._fields = []  # list of the input widgets from every section
        self._sections = self.parser_dict.keys()  # list of all the sections
        self._section_keys = []  # list of keys from every section
        
        for section in self._sections:
            self._section_keys.extend(self.parser_dict[section].keys())

        # make a LabelFrame for each section in the ConfigParser
        for section in self.parser_dict.keys():
            
            self.tabWidget = QtWidgets.QTabWidget()
            self.ui.tabWidget.addTab(self.tabWidget, section.title())
            
            self.scrollArea = QtWidgets.QScrollArea(self.tabWidget)
            self.scrollArea.setGeometry(QtCore.QRect(20, 20, 480, 480))
            
            self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 480, 800))
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
            self.ax = 10
            self.ay = 10

            for idx, section_key in enumerate(self.parser_dict[section].keys()):
                self.label = QtWidgets.QLabel(section_key.title(), self.scrollAreaWidgetContents)
                self.label.setGeometry(QtCore.QRect(self.ax, self.ay, 210, 20))
                self.lineEdit = QtWidgets.QLineEdit(self.parser_dict[section][section_key], self.scrollAreaWidgetContents)
                self.lineEdit.setGeometry(QtCore.QRect(220, self.ay, 210, 20))
                self.ay += 25

                self._fields.append(self.lineEdit)
            

    def save_config(self):
        #Saves the contents of the form to configpath if one was passed.
        # collect all the inputs
        all_inputs = []
        for child in self._fields:  # filter getting by widget class
            if isinstance(child, QtWidgets.QLineEdit):
                all_inputs.append(child.text())


        new_parser_dict = {}
        for section in self._sections:
            new_parser_dict[section] = {}
            for section_key, input in zip(self._section_keys, all_inputs):
                if section_key in self.parser_dict[section]:
                    # configparser uses ordereddicts by default
                    # this should maintain their order
                    new_parser_dict[section][section_key] = input
        #print(new_parser_dict)

        parser = ConfigParser(comment_prefixes='#', delimiters=' ', interpolation=ExtendedInterpolation())
        parser.optionxform = str
        parser.read_dict(new_parser_dict)
        if self.configpath is None:
            print(f'Not saving to file because configpath is {self.configpath}')
        else:
            with open("./deletethis.conf", 'w') as configfile:
                parser.write(configfile)
        # reset the form to reflect the changes
        self.reset_config(new_parser_dict)
        QMessageBox.information(self, "Config Saved", f"Config saved to {self.configpath}")


    def reset_config(self, dict=None):

        if dict == None:
            dict = self.defaultdict
            """Rebuilds the ConfigManager from the defaultdict."""
            print('Rebuilding form from defaultdict')
            QMessageBox.information(self, "Config Reset", "Default config loaded, remember to save!")
        self.ui.tabWidget.clear()
        self.ui.tabWidget.addTab(QtWidgets.QTabWidget(), "temp tab")
        self.build(dict)
        self.ui.tabWidget.removeTab(0)               


    def as_dict(self, config) -> dict:
        """
        Converts a ConfigParser object into a dictionary.
        The resulting dictionary has sections as keys which point to a dict of the
        sections options as key : value pairs.
        """
        the_dict = {}
        for section in config.sections():
            the_dict[section] = {}
            for key, val in config.items(section):
                the_dict[section][key] = val
        return the_dict


class myplot_ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(myplot_ui, self).__init__()
        self.ui = Ui_myplot()
        self.ui.setupUi(self)
        # print(pyplot.style.available)
        self.plot_data()


    def plot_data(self):
        pyplot.style.use('seaborn')
        sc = MplCanvas()
        sc.ax.set_title('Data Usage')
        testdf.plot(kind='barh', x="Date", y=["Download", "Upload", "Total"], ax=sc.ax)

        sc.ax.set_ylabel('Date Selected')
        sc.ax.set_xlabel('Date usage in Megabyte - Mb')
        self.setCentralWidget(sc)


        self.addToolBar(NavigationToolbar2QT(sc, self))

        pyplot.tight_layout()
        pyplot.autumn()


class WorkThread(QtCore.QObject):

    UpdateSignals = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.toStop = False
        self.isPaused = False


    def get_bytes(self, t, iface='wlan0'):
        with open('/sys/class/net/' + iface + '/statistics/' + t + '_bytes', 'r') as f:
            self.data = f.read()
            return int(self.data)


    def stop(self):
        self.toStop = True


    def pause(self):
        if not self.isPaused:
            self.isPaused = True
        else:
            self.isPaused = False


    @QtCore.pyqtSlot()
    def run(self):

        while not self.toStop:

            while self.isPaused:
                time.sleep(1)
                self.UpdateSignals.emit(['Paused!', 'Paused!'])

            tx1 = self.get_bytes('tx')
            rx1 = self.get_bytes('rx')

            time.sleep(1)

            tx2 = self.get_bytes('tx')
            rx2 = self.get_bytes('rx')

            tx_speed = round((tx2 - tx1) / 1024, 2)    # 1048576 for Mb
            rx_speed = round((rx2 - rx1) / 1024, 2)    # 1048576 for Mb

            tx_rate = ("{:.2f}".format(tx_speed))
            rx_rate = ("{:.2f}".format(rx_speed))

            rates = [str(rx_rate) + " Kbps", str(tx_rate) + " Kbps"]

            self.UpdateSignals.emit(rates)


app = QApplication(sys.argv)
window = Mainwindow()
window.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
