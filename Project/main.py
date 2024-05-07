from threading import Thread,Event
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice, QPoint
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np
from scipy import signal
import sys
import time
import threading




class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp,self).__init__()
        loadUi('design.ui', self)

        self.btn_normal.hide()
        self.click_posicion = QPoint()
        self.btn_minimize.clicked.connect(lambda : self.showMinimized())
        self.btn_normal.clicked.connect(self.control_btn_normal)
        self.btn_maximize.clicked.connect(self.control_btn_maximize)
        self.btn_close.clicked.connect(lambda: self.close())

        #Eliminar opacidad
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        #SizeGrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)
        # mover ventana
        self.frame_sup.mouseMoveEvent = self.mover_ventana

        ##Control connect
        self.serial = QSerialPort()
        #self.thread = None
        self.btn_update_2.clicked.connect(self.read_ports)
        self.btn_connect_2.clicked.connect(self.serial_connect)
        self.btn_disconnect_2.clicked.connect(self.serial_disconnect)
        self.btn_apply_filters.setEnabled(False)
        self.btn_apply_filters.clicked.connect(self.filters)
        self.btn_apply_fft.clicked.connect(self.fourierTransform)
        #self.start_thread()
        self.serial.readyRead.connect(self.read_data)

        self.channel_1 = []
        self.channel_2 = []
        self.channel_3 = []
        self.channel_4 = []


        self.x = list(np.linspace(0,2000,2000))
        self.y = list(np.linspace(0,0,2000))

        self.x1 = list(np.linspace(0,2000,2000))
        self.y1 = list(np.linspace(0,0,2000))

        
        self.x2 = list(np.linspace(0,2000,2000))
        self.y2 = list(np.linspace(0,0,2000))

        
        self.x3 = list(np.linspace(0,2000,2000))
        self.y3 = list(np.linspace(0,0,2000))

        #Grafica
        pg.setConfigOption('background', '#2c2c2c')
        pg.setConfigOption('foreground', '#ffffff')
        self.plt = pg.PlotWidget(title = 'Grafica tiempo CH1')
        self.graph_time_layout.addWidget(self.plt)

        self.plt2 = pg.PlotWidget(title = 'Grafica tiempo CH2')
        self.graph_time_layout.addWidget(self.plt2)

        self.plt3 = pg.PlotWidget(title = 'Grafica tiempo CH3')
        self.graph_time_layout.addWidget(self.plt3)

        self.plt4 = pg.PlotWidget(title = 'Grafica tiempo CH3')
        self.graph_time_layout.addWidget(self.plt4)

        pg.setConfigOption('background', '#2c2c2c')
        pg.setConfigOption('foreground', '#ffffff')
        self.plt5 = pg.PlotWidget(title = 'Grafica Fourier')
        self.graph_fourier_layout.addWidget(self.plt5)

        self.read_ports()

    def read_ports(self):
        self.filter =  ['','EMG', 'EEG', 'ECG']
        self.baudrates =  ['1200', '2400', '4800', '9600',
                           '19200','38400', '115200']
        self.canal =  ['','1', '2', '3', '4']
        portList = []
        ports = QSerialPortInfo().availablePorts()
        for i in ports:
            portList.append(i.portName())

        self.cb_list_ports_2.clear()
        self.cb_list_baudrates_2.clear()
        self.filter_list.clear()
        self.canal_list.clear()
        self.cb_list_ports_2.addItems(portList)
        self.cb_list_baudrates_2.addItems(self.baudrates)
        self.filter_list.addItems(self.filter)
        self.canal_list.addItems(self.canal)
        self.cb_list_baudrates_2.setCurrentText("115200")        
        self.filter_list.setCurrentText('')
        self.canal_list.setCurrentText('')


    def serial_connect(self):
        self.serial.waitForReadyRead(100)
        self.port = self.cb_list_ports_2.currentText()
        self.baud = self.cb_list_baudrates_2.currentText()
        self.serial.setBaudRate(int(self.baud))
        self.serial.setPortName(self.port)
        self.serial.open(QIODevice.ReadWrite)
    def serial_disconnect(self):
        self.serial.close()
        self.btn_apply_filters.setEnabled(True)
    def read_data(self):   
        if not self.serial.canReadLine: return
        value = self.serial.readLine()
        value_str = str(value, 'latin-1').strip()
        canal = value_str.split(':') # Dividir la línea en número de canal y referencia de canal
        if len(canal[0])<=1:
            if canal[0] == '0':
                try:
                    value_ch1 = float(canal[1])
                    valueNormalizado = (value_ch1)*1.2/(2**24)
                    self.channel_1.append(valueNormalizado)
                    self.graficar()
                except:
                    pass
            elif canal[0] == '1':
                try:
                    value_ch2 = float(canal[1])
                    valueNormalizado2 = (value_ch2)*1.2/(2**24)
                    self.channel_2.append(valueNormalizado2)
                    self.graficar()
                except:
                    pass
            elif canal[0] == '2':
                try:
                    value_ch3 = float(canal[1])
                    valueNormalizado3 = (value_ch3)*1.2/(2**24)
                    self.channel_3.append(valueNormalizado3)
                    self.graficar()
                except:
                    pass
            elif canal[0] == '3':
                try:
                    value_ch4 = float(canal[1])
                    valueNormalizado4 = (value_ch4)*1.2/(2**24)
                    self.channel_4.append(valueNormalizado4)
                    #self.graficar4()
                except:
                    pass
            else: 
                pass  
        
    def filters(self):
        #f = np.linspace(0,(N-1*fstep,N))
        if self.canal_list.currentText() == '1':
            graph = self.plt
            self.filterType(self.channel_1,graph)
        elif self.canal_list.currentText() == '2':
            graph1 = self.plt2
            self.filterType(self.channel_2,graph1)
        elif self.canal_list.currentText() == '3':
            graph2 = self.plt3
            self.filterType(self.channel_3,graph2)
        elif self.canal_list.currentText() == '4':
            graph3 = self.plt4
            self.filterType(self.channel_4,graph3)
        else:
            print("BLANK TYPE CHANNEL")

    def filterType(self,canal, position):
        if self.filter_list.currentText() == 'EMG':
            sos = signal.butter(20, 121, 'low', fs = 244,output = 'sos')
            filtered = signal.sosfilt(sos, canal)
            sos = signal.butter(20, [58, 62], 'bandstop', fs = 244,output = 'sos')
            filtered1 = signal.sosfilt(sos, filtered)
            self.plotFilter(filtered1,position)
            self.fourierTransformClean(filtered1)

        elif  self.filter_list.currentText() == 'ECG':
            sos = signal.butter(20, 100, 'low', fs = 244,output = 'sos')
            filtered = signal.sosfilt(sos, canal)
            sos = signal.butter(20, [58, 62], 'bandstop', fs = 244,output = 'sos')
            filtered1 = signal.sosfilt(sos, filtered)
            self.plotFilter(filtered1,position)
            self.fourierTransformClean(filtered1)

        elif self.filter_list.currentText() == 'EEG':
            sos = signal.butter(20, 50, 'low', fs = 244,output = 'sos')
            filtered = signal.sosfilt(sos, canal)
            self.plotFilter(filtered,position)
            self.fourierTransformClean(filtered) 
        else:
            print("BLANK TYPE FILTER")

    def fourierTransform(self):
        if self.canal_list.currentText() == '1':
            canal = self.channel_1
        elif self.canal_list.currentText() == '2':
            canal = self.channel_2
        elif self.canal_list.currentText() == '3':
            canal = self.channel_3
        elif self.canal_list.currentText() == '4':
            canal = self.channel_4
        else:
            print("BLANK CHANNEL")
        N = len(canal)
        Fs = 244
        yfft = np.fft.fft(canal)
        P2 = abs(yfft/N)
        P1 = P2[:int(N/2) + 1]
        P1[2:-1] *= 2
        self.plt5.clear()
        try:
            f = Fs/N * np.arange(0, N/2)
            self.plt5.plot(f, P1, pen = pg.mkPen('#da0037',width = 2))
            self.plt5.setLabel("left", "Amplitude")
            self.plt5.setLabel("bottom", "Frequency")
        except:
            f = Fs/N * np.arange(0, N/2+1)
            self.plt5.plot(f, P1, pen = pg.mkPen('#da0037',width = 2))
            self.plt5.setLabel("left", "Amplitude")
            self.plt5.setLabel("bottom", "Frequency")

    def fourierTransformClean(self,canal):
        N = len(canal)
        Fs = 244
        yfft = np.fft.fft(canal)
        P2 = abs(yfft/N)
        P1 = P2[:int(N/2) + 1]
        P1[2:-1] *= 2
        self.plt5.clear()
        try:
            f = Fs/N * np.arange(0, N/2)
            self.plt5.plot(f, P1, pen = pg.mkPen('#da0037',width = 2))
            self.plt5.setLabel("left", "Amplitude")
            self.plt5.setLabel("bottom", "Frequency")
        except:
            f = Fs/N * np.arange(0, N/2+1)
            self.plt5.plot(f, P1, pen = pg.mkPen('#da0037',width = 2))
            self.plt5.setLabel("left", "Amplitude")
            self.plt5.setLabel("bottom", "Frequency")

    def plotFilter(self,signal,position):
        a = np.arange(1,len(signal) +1)
        position.clear()
        position.plot(a,signal, pen = pg.mkPen('#da0037',width = 2))
        position.setLabel("left", "Voltage(V)")
        position.setLabel("bottom", "Muestras (N)")
        position.showGrid(x=True, y=True)

    def graficar(self):
        print(self.channel_1[-1])
        print(self.channel_2[-1])
        print(self.channel_3[-1])
        print(self.channel_4[-1])

        self.y = self.y[1:]
        self.y.append(self.channel_1[-1])
        self.plt.clear()
        self.plt.plot(self.x,self.y, pen = pg.mkPen('#da0037',width = 2))
        self.plt.setLabel("left", "Voltage(V)")
        self.plt.setLabel("bottom", "Muestras (N)")
        self.plt.showGrid(x=True, y=True)


        self.y1 = self.y1[1:]
        self.y1.append(self.channel_2[-1])
        self.plt2.clear()
        self.plt2.plot(self.x1,self.y1, pen = pg.mkPen('#da0037',width = 2))
        self.plt2.setLabel("left", "Voltage(V)")
        self.plt2.setLabel("bottom", "Muestras (N)")
        self.plt2.showGrid(x=True, y=True)
    
        self.y2 = self.y2[1:]
        self.y2.append(self.channel_3[-1])
        self.plt3.clear()
        self.plt3.plot(self.x2,self.y2, pen = pg.mkPen('#da0037',width = 2))
        self.plt3.setLabel("left", "Voltage(V)")
        self.plt3.setLabel("bottom", "Muestras (N)")
        self.plt3.showGrid(x=True, y=True)
    
        self.y3 = self.y3[1:]
        self.y3.append(self.channel_4[-1])
        self.plt4.clear()
        self.plt4.plot(self.x3,self.y3, pen = pg.mkPen('#da0037',width = 2))
        self.plt4.setLabel("left", "Voltage(V)")
        self.plt4.setLabel("bottom", "Muestras (N)")
        self.plt4.showGrid(x=True, y=True)

    def control_btn_normal(self):
        self.showNormal()
        self.btn_normal.hide()
        self.btn_maximize.show()

    def control_btn_maximize(self):
        self.showMaximized()
        self.btn_maximize.hide()
        self.btn_normal.show()

    def resizeEvent(self,event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    def mousePressEvent(self, event):
        self.click_posicion = event.globalPos()

    ## move window
    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos()- self.click_posicion)
                self.click_posicion = event.globalPos()
                event.accept()
        if event.globalPos().y() <=5 or event.globalPos().x() <=5:
            self.showMaximized()
            self.btn_maximize.hide()
            self.btn_normal.show()
        else:
            self.showNormal()
            self.btn_normal.hide()
            self.btn_maximize.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec())