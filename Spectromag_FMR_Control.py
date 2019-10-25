# -*- coding: utf-8 -*-
"""
Created on Tue Otc 09 00:06 2019

@author: YunYYao
"""

"""Module containing a class tp interface with a Oxford Spectromag iTC"""

import clr
import time
import pyvisa as visa
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import threading as td 
import subprocess as sp

COLUMNS=''
DATA=''

rm=visa.ResourceManager()


# load the c#.dll supplied by Oxford
'''
try:
    clr.AddReference('')
except: 
    if clr.FindAssembly('') is None:
        print('Could not find xx.dll')
    else:
        print('Found xx.dll at {}'.format(clr.FindAssembly('')))
        print('Try right-clicking the .dll, selecting "properities", and then clicking "Unblock"')
'''

# import the c# classes for interfaceing with the Oxford




class SPECTROMAG():
    """Thin wrapper around the xxx class, SPECTROMAG as stg """
        
    def __init__(self, itc_address='GPIB0::15::INSTR',ips_address='GPIB0::17::INSTR'):
        self.itc=rm.opem_resource(itc_address)
        self.ips=rm.open_resource(ips_address)
        self.TstatusDict={0:'unknown',1:'stable',2:'tracking',5:'near',6:'chasing'}   #still need check
        self.FieldStatusDict={6:'ramp to field',4:'clamp',3:'ramp to zero',1:'hold'}  # need check
        itc_config=self.itc.write('READ:SYS:CAT')
        ips_config=self.ips.write('READ:SYS:CAT')
        
        print 'iTC configuration:' itc_config
        print 'iPS configuration:' ips_config
        
    ''' iTC control TEMP, iPS control magnetic field'''
        
    def getTemperature(self):
        """Return the current temperature, in Kelvin"""
        Tstatus = self.itc.query('READ:DEV:DB7.T1:TEMP:SIG:TEMP')
        return Tstatus
        '''
        try:
            return str(Tstatus[1]),self.TstatusDict[Tstatus[2]]
        except:
            return str(Tstatus[1]),'recognize problem'
        '''
        
    def setTemperature(self,temp,rate=10, ramp_mode='ON'):
        """
        temp -- the temperature in Kelvin
        rate -- the cooling / heating rate, in Kelvin / min
        set ramp rate >> ramp mode on >> set temp
        """
        self.itc.write('SET:DEV:DB7.T1:TEMP:LOOP:RSET:'+str(rate))
        self.itc.write('SET:DEV:DB7.T1:TEMP:LOOP:RENA:'+ramp_mode)
        self.itc.write('SET:DEV:DB7.T1:TEMP:LOOP:TSET:'+str(temp))
        
        Tstatus=self.getTemperature()
        
        if stable==1:                             # need check
            time.sleep(10)
            Tstatus=self.getTemperature()
            
            while not Tstatus[1]=='stable':
                Tstatus=self.getTemperature()
                time.sleep(10)
                print 'Temperature is '+ Tstatus[0]+'K'
                
    def getField(self):
        """ return the current magnetic field, in Tesla"""
        I_H_rate=14.313               
        FieldStatus=self.ips.query('READ:DEV:GRPZ:PSU:SIG:FLD')
        PSU_curr=FieldStatus*I_H_rate
        return FieldStatus
        '''
        try:
            return str(FieldStatus[1]), self.FieldStatusDict[FieldStatus[2]]
        except:
            return str(FieldStatus[1]), 'reconginze problem'
        '''
        
    def Field_Temp(self):
        ''' the temperature of magnet, only read'''
        
        return self.itc.query('READ:DEV:MB1.T1:TEMP:SIG:TEMP')
        
    
    def persistField(self):
        self.ips.write('SET:DEV:UID:PSU:SIG:PFLD')
    
        
    def setField(self, field, current, rate=100, stable=1):
        """
        field -- the value of magnetic field, in Tesla
        current -- the correspond PSU current of setpoint field, in A
        rate -- the PSU ramping rate, in A/min
        
        set magnet curr >> set curr rate >> set magnet field
        
        """
        self.ips.write('SET:DEV:GRPZ:PSU:SIG:CSET:'+str(current))
        self.ips.write('SET:DEV:GRPZ:PSU:SIG:RCST:'+str(rate))
        self.ips.write('SET:DEV:GRPZ:PSU:SIG:ACTN:POTS:'+str(field))
        FieldStatus=self.getField()
        
        
        if stable == 1:
            time.sleep(10)
            FieldStatus=self.getField()
            while not (FieldStatus[1]=='holding' or FieldStatus[1]=='presistent'):
                FieldStatus=self.getField()
                time.sleep(5)
                print 'Magnetic field is ' + FieldStatus[0] + 'Oe'
                
    def getSPECTROMAG_status(self):
        Tstatus =self.getTemperature()
        FieldStatus = self.getField()
        return Tstatus[0],Tstatus[1],FieldStatus[0],FieldStatus[1]


class PNA():
    """ N5234B, """
    
    def __init__(self,pna_address='GPIB0::1::INSTR'):
        self.pna=rm.open_resource(pna_address)
        
    def set_measure_type(self, measure_type='S21'):
        self.pna.write('calc1:meas1:par '+ measure_type)
        
    def set_freq_center(self,freq_center):
        """ frequency, in Hz """
        
        self.pna.write(':sens1:freq:cent '+ str(freq_center))
        
    def set_freq_start(self, freq_start=500e3):
        self.pna.write(':sens1:freq:star '+ str(freq_start))
        
    def set_freq_stop(self, freq_stop=43e9):
        self.pna.write(':sens1:freq:stop '+ str(freq_stop))
        
    def set_freq_points(self, points= 1601):
        self.pna.write(':sens1:swe:poin '+ str(points)) 
        
    def set_freq_step(self,step=1e9):
        self.pna.write(':sens1:freq:cent:step:auto 0')
        self.pna.write(':sens1:freq:cent:step: '+str(step))
        
    def set_freq_span(self, freq_span=10e9):
        self.pna.write(':sens1:freq:span '+ str(freq_span))
        
    def set_power(self, power= -25):
        """ unit in dB"""
        self.pna.write(':sour1:pow:att '+ str(power))
        
    def set_on_off(self, on_off='ON'):
        self.pna.write(':OUTP '+on_off)
        
    def set_ave(self, n= 16):
        self.pna.write(':sens1:aver on')
        self.pna.write(':sens1:aver:coun '+ str(n))
        
    def set_IF(self, IF=10e3):
        self.pna.write(':sens1:bwid '+ str(IF))
    
    def auto_scale(self):
        self.pna.write(':DISP:WIND1:TRAC1:Y:AUTO')
    
    def set_sweep_mode(self,mode='hold'):
        """trigger types:
        HOLD,CONTiunous,GROups,SINgle
        """
        self.pna.write(':sens1:swe:mode '+mode)
        
    def set_sweep_time(self, sweep_time):
        self.pna.write(':sens1:sew:time:auto off')
        self.pna.write(':sens1:sew:time:data '+ str(sweep_time))
    
    def ReadLine(self, MeasureNum=1):
        line=self.pna.query(':CALC1:meas'+str(MeasureNum)+':DATA:FDAT?').replace(',+0.00000000000E+000','')
        return line
        
    def get_freq(self):
        return self.pna.query(':SENS1:FREQ:DATA?') 
    
    
    def fmr_init(self,measure_type='S21',freq_start=500e3,freq_stop=43e9,points=1601,power=-25,ave=16,IF=10e3,sweep_time=0):
        self.set_measure_type(measure_type)
        self.set_freq_start(freq_start)
        self.set_freq_stop(freq_stop)
        self.set_freq_points(points)
        self.set_power(power)
        self.set_ave(ave)
        self.set_IF(IF)
        self.auto_scale()
        self.set_sweep_time(sweep_time)
        print 'PNA_FMR initilization is OK' 
        
    def fmr_text_init(self,pathfile):
        global COLUMNS
        freq=self.get_freq()
        COLUMNS='H,'+freq
        print COLUMNS
        
        if not os.path.exists(pathfile):
            f1=open(pathfile, 'a')
            f1.write(COLUMNS)
            f1.close()
'''
    def fmr_measure(self, pathfile, field, field_ramp):
        global DATA
        self.fmr_text_init(pathfile)
        stg=SPECTROMAG()
        stg.setField(field)
        stg.setField(0,field_ramp,stable=0)
        field=float(stg.getField()[0])
        data_last=DATA
        
        while abs(field)>1:
            s21=ReadLine(1)
            field=float(stg.getField()[0])
            DATA=str(field)+','+s21
            if not DATA==data_last:
                f1=open(pathfile, 'a')
                f1.write(DATA)
                f1.close()
                data_last=DATA
                print field
                time.sleep(0.5)
'''
                
        
        
        
        
        
    
    

































    