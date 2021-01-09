# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 00:56:15 2016

@author: ppms
"""
import time
import win32com.client
import visa
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import clr
import Skype4Py 
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import subprocess as sp
import threading as td


DATA=''
COLUMNS=''

try:
    clr.AddReference('QDInstrument')
except:
    if clr.FindAssembly('QDInstrument') is None:
        print('Could not find QDInstrument.dll')
    else:
        print('Found QDInstrument.dll at {}'.format(clr.FindAssembly('QDInstrument')))
        print('Try right-clicking the .dll, selecting "Properties", and then clicking "Unblock"')

# import the C# classes for interfacing with the PPMS
import QuantumDesign.QDInstrument as QDInstrument


#labview=win32com.client.Dispatch('LabVIEW.Application')
rm=visa.ResourceManager()
k2400_address='GPIB0::24::INSTR'

class PPMS():
    """Thin wrapper around the QuantumDesign.QDInstrument.QDInstrumentBase class"""

    def __init__(self):
        self.QDI_PPMS_TYPE=QDInstrument.QDInstrumentBase.QDInstrumentType.PPMS
        self.ip_address='127.0.0.1'
        self.DEFAULT_PORT=11000
        self.qdi_instrument = QDInstrument.QDInstrumentFactory.GetQDInstrument(self.QDI_PPMS_TYPE, False, self.ip_address, self.DEFAULT_PORT)
        self.TstatusDict={0:'unknown',1:'stable',2:'tracking',6:'chasing',5:'near'}
        self.FieldStatusDict={6:'charging',4:'holding',3:'sw-cool',1:'persistent'}
       

    def getTemperature(self):
        """Return the current temperature, in Kelvin."""
        Tstatus=self.qdi_instrument.GetTemperature(0,0)
        try:
            return str(Tstatus[1]),self.TstatusDict[Tstatus[2]]
        except:
            return str(Tstatus[1]),'recognize problem'
                

    def setTemperature(self, temp, rate=10, stable=1):
        """Set the temperature.
            Keyword arguments:
            temp -- the temperature in Kelvin
            rate -- the cooling / heating rate, in K / min
            """
        self.qdi_instrument.SetTemperature(temp, rate, 0)
        
        if stable==1:
            time.sleep(10)
            Tstatus=self.getTemperature()
            while not Tstatus[1]=='stable':
                Tstatus=self.getTemperature()
                time.sleep(10)
                print 'Temperature is ' +Tstatus[0]+'K'
                
                
    def waitForTemperature(self, delay=5, timeout=600):
        """Pause execution until the PPMS reaches the temperature setpoint."""
        return self.qdi_instrument.WaitFor(True, False, False, False, delay, timeout)

    def getField(self):
        """Return the current field, in gauss."""
        FieldStatus=self.qdi_instrument.GetField(0,0)
        try:
            return str(FieldStatus[1]),self.FieldStatusDict[FieldStatus[2]]
        except:
            return str(FieldStatus[1]),'recognize problem'

    def setField(self, field, rate=100,holdingornot=1,stable=1):
        """Set the field.
            Keyword arguments:
            field -- the field, in gauss
            rate  -- the field sweep rate, in gauss / second
            """
        self.qdi_instrument.SetField(field, rate, 0,holdingornot )
        if stable==1:
            time.sleep(10)
            FieldStatus=self.getField()
            while not (FieldStatus[1]=='holding' or FieldStatus[1]=='persistent'):
                FieldStatus=self.getField()
                time.sleep(5)
                print 'Magnetic field is '+FieldStatus[0]+'Oe'
        
    def waitForField(self, delay=5, timeout=600):
        """Pause execution until the PPMS reaches the field setpoint."""
        return self.qdi_instrument.WaitFor(False, True, False, False, delay, timeout)
            
    def getPPMSStatus(self):
        Tstatus=self.getTemperature()
        Fieldstatus=self.getField()
        return Tstatus[0],Tstatus[1],Fieldstatus[0],Fieldstatus[1]
class K2400():
    def __init__(self,k2400_address='GPIB0::16::INSTR'):
        self.k2400=rm.open_resource(k2400_address)
        
    def IVCurve_sourceV(self,IVFilename,StartV=-0.05,EndV=0.05,StepV=0.01):
        f=open(IVFilename,'a')
        Voltage = StartV
        RealV=[]
        RealI=[]
        global COLUMNS,DATA
        COLUMNS='V(V), I(A)\n'
        while Voltage <= EndV:    
            self.k2400.write(':sour:volt '+str(Voltage))
            time.sleep(1)            
            VIpoint=self.k2400.query(':measure:curr:dc?').split(',')[0:2]
            print VIpoint
            RealV.append(float(VIpoint[0]))
            RealI.append(float(VIpoint[1]))
            DATA=str(VIpoint[0])+','+str(VIpoint[1])+'\r'
            f.write(DATA)          
            Voltage=Voltage+StepV
            time.sleep(1)
            
        self.k2400.write(':sour:volt 0')
        f.close()
        FitResult=np.polyfit(RealI,RealV,1)
        return FitResult[0]
    def IVCurve_sourceI(self,IVFilename,StartI=-1e-6,EndI=1e-6,StepI=1e-7):
        f=open(IVFilename,'a')
        Curr = StartI
        RealV=[]
        RealI=[]
        global COLUMNS,DATA
        COLUMNS='V(V), I(A)\n'
        while Curr <= EndI:    
            self.k2400.write(':sour:curr '+str(Curr))
            time.sleep(0.2)            
            print ':sour:curr '+str(Curr)
            VIpoint=self.k2400.query(':measure:volt:dc?').split(',')[0:2]
            print VIpoint
            RealV.append(float(VIpoint[0]))
            RealI.append(float(VIpoint[1]))
            DATA=str(VIpoint[0])+','+str(VIpoint[1])+'\r'
            f.write(DATA)          
            Curr=Curr+StepI
            
        self.k2400.write(':sour:volt 0')
        f.close()
        FitResult=np.polyfit(RealI,RealV,1)
        return FitResult[0]
    
class K2002():
    def __init__(self,k2002_address='GPIB0::14::INSTR'):
        self.k2002=rm.open_resource(k2002_address)
    def GetVoltageAverage(self,n=30,amplifier=1.0):
        VoltageList=[]
        for i in range(n):        
            VoltageList.append(float(self.k2002.query(':data?').split(',')[0][:-4]))
        if len(VoltageList)==n:
            print 'dc data ok'
        else:
            print 'dc data error'
        voltage=sum(VoltageList[1:])/(n-1.0)/amplifier
        return voltage
        

class VNA():
    def __init__(self,vna_address='GPIB0::17::INSTR'):
        self.vna=rm.open_resource(vna_address)
    def set_measure_type(self,measure_type='S21'):
        self.vna.write('calc1:par1:def '+measure_type)
    def SetFreqCenter(self,frequency):
        '''
        frequency unit Hz
        '''
        self.vna.write(':sens1:freq:cent '+str(frequency))
    def set_freq_start(self,freq_start=300e3):
        self.vna.write(':sens1:freq:star '+str(freq_start))
    def set_freq_stop(self,freq_stop=20e9):
        self.vna.write(':sens1:freq:stop '+str(freq_stop))
    def set_freq_point(self,point=1601):
        self.vna.write(':sens1:swe:poin '+str(point))
    def set_power(self,power=-4):
        '''
        frequency unit dbm
        '''
        self.vna.write(':sour1:pow '+str(power))
    def set_ave(self,n=16):
        self.vna.write(':sens1:aver on')
        self.vna.write(':sens1:aver:coun '+str(n))
    def set_IF(self,IF=10e3):
        self.vna.write(':sens1:bwid '+str(IF))
    def auto_scale(self):
        self.vna.write(':DISP:WIND1:TRAC1:Y:AUTO')
    def set_freq_span(self,span):
        self.vna.write(':sens1:freq:span '+str(span))
    def set_freq_cent(self,freq_cent):
        self.vna.write(':sens1:freq:cent '+str(freq_cent))
    def set_sweep_time(self,sweep_time):
        self.vna.write(':sens1:swe:time:auto off')
        self.vna.write(':sens1:swe:time:data '+str(sweep_time))
    def ReadLine(self,TraceNum=1):
        return self.vna.query(':CALC1:trac'+str(TraceNum)+':DATA:FDAT?').replace(',+0.00000000000E+000','')
        
    def GetFreq(self):
        return self.vna.query(':SENS1:FREQ:DATA?')
        
    def fmr_init(self,measure_type='S21',freq_start=300e3,freq_stop=20e9,points=1601,power=-4,ave=16,IF=10e3,sweep_time=0):
        self.set_measure_type(measure_type)
        self.set_freq_start(freq_start)
        self.set_freq_stop(freq_stop)
        self.set_freq_point(points)
        self.set_power(power)
        self.set_ave(ave)
        self.set_IF(IF)
        self.auto_scale()
        self.set_sweep_time(sweep_time)
        print 'VNA_FMR initilization is OK' 
    def fmr_text_init(self,pathfilename):
        global COLUMNS
        freq=self.GetFreq()
        COLUMNS='H,'+freq
        print COLUMNS
        if not os.path.exists(pathfilename):
            f1=open(pathfilename,'a')        
            f1.write(COLUMNS)
            f1.close()
    def fmr_measure(self,pathfilename,field,field_speed):
        global DATA
        self.fmr_text_init(pathfilename)        
        ppms=PPMS()
        ppms.setField(field)
        ppms.setField(0,field_speed,stable=0)
        field=float(ppms.getField()[0])
        data_last=DATA
        while abs(field)>1:
            s21=self.ReadLine(1)
            field=float(ppms.getField()[0])
            DATA=str(field)+','+s21
            if not DATA==data_last:
                f1=open(pathfilename,'a')
                f1.write(DATA)             
                f1.close()
                data_last=DATA
                print field
                time.sleep(0.4)
    def spin_pumping_init(self,measure_type='S21',freq_cent=7e9,power=-10,ave=16,IF=10e3,sweep_time=300):
        self.set_measure_type(measure_type)
        self.set_freq_cent(freq_cent)
        self.set_freq_span(0)
        self.set_freq_point(2)
        self.set_power(power)
        self.set_ave(ave)
        self.set_IF(IF)
        self.auto_scale()
        self.set_sweep_time(sweep_time)
        print 'VNA_Spin Pumping initilization is OK' 

class SR830():
    
    def __init__(self,address='GPIB0::9::INSTR'):
        self.sr830=rm.open_resource(address)
    def GetVoltageAverage(self,n=10,amplifier=1.0):
        '''
        return float numpy array '[x,y,R,theta]
        '''
        voltagelist=np.zeros((1,4))
        for i in range(n):    
            voltagelist=np.vstack((voltagelist,np.array(self.sr830.query('snap?1,2,3,4').split(','),dtype='float',ndmin=2)))
            time.sleep(0.05)
        voltage=np.sum(voltagelist[2:][:],axis=0)/(n-1.0)/[[amplifier,amplifier,amplifier,1]]
        return str.join(',',[str(i) for i in voltage[0]])
    def ClearBuffer(self):
        self.sr830.query('snap?1,2,3,4')
        self.sr830.write('REST')
        time.sleep(1)
        self.sr830.write('REST')
        time.sleep(1)
    def get_phase(self):
        lenth=3
        while not lenth==1:
            phase=self.sr830.query('phas?')
            lenth=len(phase.split(','))
            print phase
        return phase
    def auto_phase(self):
        self.sr830.write('aphs')
        time.sleep(20)
        print 'auto phaseing,wait 20s'
    def set_phase(self,phase):
        print 'setting phase to be',phase
        self.sr830.write('phas '+str(phase))
    def get_freq(self):
        lenth=3
        while not lenth==1:
            freq=self.sr830.query('freq?')
            lenth=len(freq.split(','))
            print freq
        print 'reference frequency is ', freq
        return freq
class RealPlot():
    '''
    
        
    '''
    def __init__(self,axes,title,PlotType='FMR'):
        self.axes=axes        
        self.title=title
        self.PlotType=PlotType
        self.initialize()
    def initialize(self):
        self.xylabel={'FMR':['Magnetic Field (Oe)','S21 (db)'],'SP':['Magnetic Field (Oe)','Voltage (V)'],'RT':['T (K)','Resistance (ohm)']}
        self.axes.set_title(self.title)
        self.axes.set_xlabel(self.xylabel[self.PlotType][0])
        self.axes.set_ylabel(self.xylabel[self.PlotType][1])
        plt.ion()
        self.graph=plt.plot([],[],r'b-D')[0]
    def plot(self,xdata,ydata):
        self.graph.set_data(xdata,ydata)
        self.axes.relim()
        self.axes.autoscale_view(True,True,True)
        plt.draw()
        plt.pause(0.01)        
def FourPointIVCurveSetV(IVFilename,StartV=-5e-1,EndV=5e-1,StepV=2e-2):
    global COLUMNS,DATA
    k2400=K2400()
    k2002=K2002()
    
    f=open(IVFilename,'a')
    AppliedVoltage=StartV
    currents=[]
    voltages=[]
    COLUMNS='SorceV,SorceI,VoltageV\n'
    f.write(COLUMNS)
    while abs(AppliedVoltage-EndV)>abs(StepV)*0.5:
        k2400.k2400.write(':sour:volt '+str(AppliedVoltage))
        time.sleep(1)
        source_voltage=k2400.k2400.query(':measure:curr:dc?').split(',')[0]
        source_current=k2400.k2400.query(':measure:curr:dc?').split(',')[1]
        Voltage=k2002.GetVoltageAverage()
        DATA=source_voltage+','+source_current+','+str(Voltage)+'\n'
        f.write(DATA)
        AppliedVoltage=AppliedVoltage+StepV
        #time.sleep(0.3)
        voltages.append(Voltage)
        currents.append(float(source_current))
    #k2400.k2400.write(':sour:volt 0')
    f.close()
    FitResult=np.polyfit(currents,voltages,1)
    return FitResult[0]
    
def FourPointIVCurveSetI(IVFilename,StartI=-1e-5,EndI=1e-5,StepV=1e-6):
    k2400=K2400()
    k2002=K2002()
    f=open(IVFilename,'a')
    AppliedVoltage=StartI
    currents=[]
    voltages=[]
    
    while AppliedVoltage<=EndI:
        k2400.k2400.write(':sour:curr '+str(AppliedVoltage))
        time.sleep(1)
        Current=k2400.k2400.query(':measure:curr:dc?').split(',')[1]
        Voltage=k2002.GetVoltageAverage()
        f.write(str(Voltage)+','+Current+'\r')
        AppliedVoltage=AppliedVoltage+StepV
        time.sleep(1)
        voltages.append(Voltage)
        currents.append(float(Current))
    k2400.k2400.write(':sour:curr 0')
    f.close()
    FitResult=np.polyfit(currents,voltages,1)
    return FitResult[0]
    
def SweepTMeasureR(RFilename,TDestination=10,Trate=10,current=1e-5):
    
    ppms=PPMS()
    k2400=K2400()
    k2002=K2002()  
    ppms.setTemperature(TDestina
    
    
    tion,Trate,0)
    temperature=1000
    while abs(temperature-TDestination)>0.1:
        temperature=float(ppms.getPPMSStatus()[0])
        k2400.k2400.write(':sour:curr '+ str(current)) 
        time.sleep(0.5)
        current=k2400.k2400.query(':measure:curr:dc?').split(',')[1]
        voltage=k2002.GetVoltageAverage()
        k2400.k2400.write(':sour:curr 0')         
        Resistance=voltage/float(current)
                
        f=open(RFilename,'a')
        f.write(str(temperature)+','+current+','+str(voltage)+','+str(Resistance)+'\r')
        f.close()
        print(str(temperature)+','+current+','+str(voltage)+','+str(Resistance))
        time.sleep(1)
    
def SpinPumingDC2002(filename,StartMag=1000,StopMag=0,Rate=2,amplifier=1):
    global COLUMNS,DATA
    #name=os.path.splitext(os.path.basename(filename))[0]    
    COLUMNS='H, Spin Pumping Voltage,Temperature\n'
    if not os.path.exists(filename):
        f=open(filename,'a')
        f.write(COLUMNS)
        f.close()  
    ppms=PPMS()
    k2002=K2002()
    ppms.setField(StartMag)
    time.sleep(5)
    ppms.setField(StopMag,rate=Rate,stable=0)
    time.sleep(3)
    
    #realplot=RealPlot(axes,name,'SP')

    Status=ppms.getPPMSStatus()
    Field=float(Status[2])
    #FieldList=[]
    #VoltageList=[]
    while abs(Field)>abs(StopMag)+1:
            Status=ppms.getPPMSStatus()
            Field=float(Status[2])
            try:
                Voltage=k2002.GetVoltageAverage(amplifier=amplifier,n=10)
            except:
                print '2002 read error'
                continue
                
            #FieldList.append(Field)
            #VoltageList.append(Voltage)
            DATA=str(Field)+','+str(Voltage)+','+Status[0]+'\n'
            f=open(filename,'a')                
            f.write(DATA)
            f.close()
            #realplot.plot(FieldList,VoltageList)
            #print Field,Voltage
            
            
    #plt.ioff()
    #f.close()

def SpinPumingSR830(filename,StartMag=1000,StopMag=0,Rate=2,amplifier=1,autophase=0):
    global COLUMNS,DATA
    COLUMNS='H,X,Y,R,Theta,Temperature\n'
    sr830=SR830()
    if autophase==1:        
        print 'auto phasing'
        sr830.auto_phase()
        print 'get phasing'
        sr830.ClearBuffer()
        sr830phase=sr830.get_phase()
        print 'phase is ',sr830phase
    elif autophase==0:
        sr830.set_phase(0)
        sr830phase='0'
        print 'phase is 0'
    print filename
    filename=filename.replace('.txt','phase'+sr830phase+'.txt').replace('\n','')
    #name=os.path.splitext(os.path.basename(filename))[0]    
    if not os.path.exists(filename):
        f=open(filename,'a')
        f.write(COLUMNS)
        f.close()           
    ppms=PPMS()
    
    ppms.setField(StartMag)
    time.sleep(5)
    ppms.setField(StopMag,rate=Rate,stable=0)
    time.sleep(3)
    

    
    Status=ppms.getPPMSStatus()
    Field=float(Status[2])
    #FieldList=[]
    #VoltageList=[]
    while abs(Field)>abs(StopMag)+1:
            Status=ppms.getPPMSStatus()
            Field=float(Status[2])
            try:
                Voltage=sr830.GetVoltageAverage(amplifier=amplifier)
                #print Voltage
            except:
                print 'sr830 error'
                continue
            DATA=str(Field)+','+Voltage+','+Status[0]+'\n'
            f=open(filename,'a')                
            f.write(DATA)
            f.close()
        

class Skype():
    def __init__(self):
        try:
            self.skype=Skype4Py.Skype()
            self.skype.Attach()
            print 'skype initialization is ok'
        except:
            print 'some thing wrong with skype'

    def send_message(self,words):
        try:
            self.skype.SendMessage('songqiskype',words)
        except:
            print'skype sending message error by skype'
            
    def call_songqi_skype(self):
        try:
            self.skype.PlaceCall('songqiskype')
        except:
            print 'skype call error'
            
def read_last_row(fname):
    with open(fname, 'rb') as fh:  
        #first = next(fh)  
        offs = -10000
        while True: 
            fh.seek(offs,2)  
            lines = fh.readlines()  
            if len(lines)>1:  
                last = lines[-1]  
                break  
            offs *= 2 
    return last
    
class dynamic_plotter():
    def __init__(self,plot_row_number,columns_list=[]):
        self.columns_list=columns_list
        #initialize the pyqtgraph
        self.app=QtGui.QApplication([])
        self.win=pg.GraphicsWindow(title='FMR')
        self.win.showFullScreen()
        self.data={}
        self.columsite={}
        self.plt={}
        self.curve={}        
        self.axies_initial(plot_row_number)
        #self.win.setFocus()
        #Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(250)
        #self.x=[]
        #self.y=[]
        #self.curve=self.plt1.plot(self.x,self.y,pen=(225,0,0))
        #self.i=0
        self.data_last=self.columns
    def axies_initial(self,plot_row_number):
        global COLUMNS
        while len(COLUMNS)==0:
            #print COLUMNS
            #print 'len(COLUMNS)=0,please wait some time'
            time.sleep(0.5)
            self.app.processEvents()
        self.columns=COLUMNS.split(',')
        i=0
        for column in self.columns:
            self.data[column]=[]
            self.columsite[column]=i
            i+=1
            print 'ok'
            row_number=plot_row_number
            if not column==self.columns[0]:
                if len(self.plt)%row_number==0 and len(self.plt)>=row_number:
                    self.win.nextRow()
                self.plt[column]=self.win.addPlot(title=column)
                print 'Plot ',self.columns[0],' VS ',column
                self.plt[column].showGrid(x=True, y=True)
                self.plt[column].setLabel('bottom', self.columns[0])
                self.plt[column].setLabel('left', column)
                self.curve[column]=self.plt[column].plot(self.data[self.columns[0]],self.data[column])
        print 'axies_initial ok'
    def update_plot(self):
        self.get_data()
        #print self.x,self.y
        for column in self.plt:    
            self.curve[column].setData(self.data[self.columns[0]],self.data[column],pen=(225,0,0),symbol='o')
            self.app.processEvents()
    def get_data(self):
        global DATA
        try:   
            datanew_read=DATA
            datanew=[float(i) for i in datanew_read.split(',')]
        except:
            #print 'data error'
            datanew=[0]
            datanew_read=''
            #print 'len(columns) should be',len(self.columns),'but your data is ',datanew
        if datanew_read==self.data_last or not len(self.columns)==len(datanew):
            pass
            #print 'datanew_read==self.data_last: ',datanew_read==self.data_last
            #print 'len(self.columns)==len(datanew): ',len(self.columns)==len(datanew)
            #print 'no update data,or data error, update next time'
        else:            
            for column in self.data:
                self.data[column].append(datanew[self.columsite[column]])
            self.data_last=datanew_read
            #print 'ok update!!'
    def run(self):
        sys.exit(self.app.exec_())
        #self.win.show()
    
def real_plot(plot_row_number,columns_list=[]):
    #global DATA,COLUMNS
    plotter=dynamic_plotter(plot_row_number,columns_list)
    plotter.run()

def real_plot_another_process(plot_row_number=1,columns_list=[]):
    #global DATA,COLUMNS
    th=td.Thread(target=real_plot,args = (plot_row_number,))
    th.setDaemon(True)
    th.start()


def find_low_pumping_background_frequency(filename,method='DC'):
    f=open(filename,'a')
    global COLUMNS,DATA
    COLUMNS='Frequency(Hz),Voltage_background\n'
    f.write(COLUMNS)
    f.close()
    freq_start=4e9
    freq_end=8e9
    freq_list=np.linspace(4e9,8e9,400)
    vna=VNA()
    if method=='DC':
        voltage_instru=K2002()
    else:
        voltage_instru=SR830()
    for freq in freq_list:       
        vna.set_freq_cent(freq)
        time.sleep(0.4)
        if method=='DC':
            background=voltage_instru.GetVoltageAverage()
        else:    
            background_list=voltage_instru.GetVoltageAverage().split(',')
            background=background_list[0]
        DATA=str(freq)+','+str(background)+'\n'
        print DATA
        f=open(filename,'a')
        f.write(DATA)
        f.close()


    

    
    
def MR_2400_2002(filename,StartMag=1000,StopMag=0,Rate=2,current_source=1e-5,amplifier=1):
    k2400=K2400()
    k2002=K2002()
    global COLUMNS,DATA
    COLUMNS='H,I,V,R,T\n'
    print filename   
    if not os.path.exists(filename):
        f=open(filename,'a')
        f.write(COLUMNS)
        f.close()           
    ppms=PPMS()
    ppms.setField(StartMag)
    time.sleep(5)
    ppms.setField(StopMag,rate=Rate,stable=0)
    time.sleep(3)
    
    Status=ppms.getPPMSStatus()
    Field=float(Status[2])
    #FieldList=[]
    #VoltageList=[]
    k2400.k2400.write(':sour:curr '+ str(current_source))
    while abs(Field-StopMag)>1:
            Status=ppms.getPPMSStatus()
            Field=float(Status[2])
            
            try:
                current=k2400.k2400.query(':measure:curr:dc?').split(',')[1]
                voltage=k2002.GetVoltageAverage(amplifier=amplifier)
                Resistance=voltage/float(current)
                #print Voltage
            except:
                print 'measurement error'
                continue
            DATA=str(Field)+','+str(current)+','+str(voltage)+','+str(Resistance)+','+Status[0]+'\n'
            f=open(filename,'a')                
            f.write(DATA)
            f.close()
       