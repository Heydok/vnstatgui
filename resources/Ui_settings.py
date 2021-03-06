# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/karl/scripts-heydok/python/Heydok GIT Projects/vnstatgui/settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(659, 578)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("/home/karl/scripts-heydok/python/Heydok GIT Projects/vnstatgui/resources/icon.bmp"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Settings.setWindowIcon(icon)
        self.tabWidget = QtWidgets.QTabWidget(Settings)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 531, 561))
        self.tabWidget.setObjectName("tabWidget")
        self.resetBtn = QtWidgets.QPushButton(Settings)
        self.resetBtn.setGeometry(QtCore.QRect(550, 40, 101, 23))
        self.resetBtn.setObjectName("resetBtn")
        self.saveBtn = QtWidgets.QPushButton(Settings)
        self.saveBtn.setGeometry(QtCore.QRect(550, 70, 101, 23))
        self.saveBtn.setObjectName("saveBtn")

        self.retranslateUi(Settings)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Vnstat Settings"))
        self.resetBtn.setToolTip(_translate("Settings", "<html><head/><body><p>Reset the vnstat config file back to befaults</p></body></html>"))
        self.resetBtn.setText(_translate("Settings", "Reset Config"))
        self.saveBtn.setToolTip(_translate("Settings", "<html><head/><body><p>Save the changes to config</p></body></html>"))
        self.saveBtn.setText(_translate("Settings", "Save Config"))
