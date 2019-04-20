# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 19:50:43 2016

@author: ppms
"""


from sqm import *
import multiprocessing as mp













'''
#four point sweep T



SweepTMeasureR('E:\\Qi\\Smb6\\20160429\\RT300kto10k.txt',10,10)
'''






'''
#Four Point IV measurement 2002 2400
ppms=PPMS()
TemperaturePoint=[2]

for Temp in TemperaturePoint:
    ppms.SetPPMSTemp(Temp)
    time.sleep(20)

    print 'wait 600s to let the temperature more stalbe'

    FileName='FourPointPtCalibrationOnPunkWait600STemp'+str(Temp)+'KIV'+'.txt'    
    FourPointIVCurev(os.path.join(FilePath,FileName)) 
'''

'''
#Spin Pumping 
folder='E:\\Qi\\TI YIG\\6 0.35\\pumping' #.replace('\\','\\')  # take care not \  should be /
#NamePrefix='test90_3'
var=[300]#7.5e9,7e9,6.5e9,6e9,5.5e9,5e9,4.5e9,4e9]
frequency=6

#var.reverse()
unit='V'
amplifier=1
#temperature=[300]
ppms=PPMS()
#figure=plt.figure()
i=0
sr830=SR830()
modulation_freq=sr830.get_freq()
#k2400=K2400()
vna=VNA()
vna.spin_pumping_init(power=0,freq_cent=frequency*1e9)
real_plot_another_process(plot_row_number=2)
NameSuffix='0dbm'+'Hz_'+str(frequency)+'GHz_on300k AC'#+'modul_freq'+modulation_freq
for temp in var:
    i=i+1
    print temp,unit   
    #ppms.setTemperature(temp)
    
    #time.sleep(600)
    #k2400.k2400.write(':sour:volt '+str(temp))
    #time.sleep(600)
    #vna.set_power(temp)
    print 'temperature is ok, please wait some time untill it is stable',time.ctime()
    #vna.SetFreqCenter(temp)
    #time.sleep(1200)
    #time.sleep(300)
    #axes=plt.subplot(4,4,i)
    #axes.set_title(str(temp)+unit)  
    #time.sleep(600)
    
    #SpinPumingDC2002(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=2000,Rate=6,amplifier=amplifier)
    #SpinPumingDC2002(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=-2000,Rate=6,amplifier=amplifier)
    SpinPumingSR830(filename=os.path.join(folder,str(temp)+unit+NameSuffix+str(i)+'.txt'),StartMag=2000,StopMag=0,Rate=2,amplifier=amplifier)
    SpinPumingSR830(filename=os.path.join(folder,str(temp)+unit+NameSuffix+str(i)+'.txt'),StartMag=-2000,StopMag=-0,Rate=2,amplifier=amplifier)
vna.set_power(-40)
#ppms.setTemperature(100)
#ppms.setTemperature(300)
'''


#Four Point IV measurement 2002 2400

ppms=PPMS()

#TemperaturePoint=[10,20,30,40,50,60,70,80,90,100,125,150,175,200,225,250,275,300]
TemperaturePoint=[300,275,250,225,200,175,150,125,100,90,80,70,60,50,40,30,20,10]
#TemperaturePoint=[10]
fp='E:\\Qi\\TI YIG\\x0.5\\resistance'
IV_info='I78V1311'
f=open(os.path.join(fp,IV_info+'R.txt'),'a')
f.write('Temperature(k),Resistance\n')
real_plot_another_process()
for Temp in TemperaturePoint:    
    
    if Temp>10:
        speed=10
    elif Temp<10:
        speed=2
        
    ppms.setTemperature(Temp,speed)
    time.sleep(300)
    
    print 'wait 600s to let the temperature more stalbe'

    FileName=''+str(Temp)+'K_'+IV_info+'.txt'    
    StartV=-5e0
    EndV=5e0
    step=5e-1
    
    R=FourPointIVCurveSetV(os.path.join(fp,FileName),StartV=0,EndV=StartV,StepV=-1*step)
    f.write(str(Temp)+','+str(R)+'\n')
    R=FourPointIVCurveSetV(os.path.join(fp,FileName),StartV=StartV,EndV=EndV,StepV=step)
    f.write(str(Temp)+','+str(R)+'\n')
    R=FourPointIVCurveSetV(os.path.join(fp,FileName),StartV=EndV,EndV=0,StepV=-1*step)
    f.write(str(Temp)+','+str(R)+'\n')
       
f.close()
#ppms.setTemperature(20)


'''
# Two Point IV measurement 2400 only
FilePath='E:\\Qi\\TI YIG\\4 0.25\\Resistance'                                                            
ppms=PPMS()
k2400=K2400()
TemperaturePoint=[300]
#TemperaturePoint=[10]
#skype=Skype()
#TemperaturePoint=[300]
real_plot_another_process(plot_row_number=2)
filenumber='I34V134'
for Temp in TemperaturePoint:
    ppms.setTemperature(Temp)
    print 'wait 600s to let the temperature more stalbe' 
    #time.sleep(120)
    FileName=filenumber+'.txt'
    R=k2400.IVCurve_sourceV(os.path.join(FilePath,FileName),StartV=-5e-1,EndV=5e-1,StepV=1e-2)
    f1=open(os.path.join(FilePath,filenumber+'R'+'.txt'),'a')
    f1.write(str(Temp)+','+str(R)+'\n')
    f1.close()
'''


'''
#sweep T get R 2400
ppms=PPMS()
k2400=K2400()
temp_des=20
ppms.setTemperature(temp_des,rate=10,stable=0)
#time.sleep(1800)
#ppms.SetPPMSTemp(300,Rate=2,stable=0)
Temp=ppms.getPPMSStatus()[0]
print Temp
filename='E:\\Qi\\TI YIG\\4 0.25\\Resistance\\temperature dependence 2\\RT_2terminal'
f=open(filename,'a')
global COLUMNS,DATA
COLUMNS='T,R\n'
f.write(COLUMNS)
f.close()
real_plot_another_process(plot_row_number=3,columns_list=[])
while not abs(float(Temp)-temp_des)<0.1:
    #k2400.k2400.write(':sour:volt '+str(0.001))
    #time.sleep(1)
    R=k2400.k2400.query(':measure:res?').split(',')[2]
    time.sleep(0.4)
    #k2400.k2400.write(':sour:volt '+str(0))
    #R=float(VIpoint[0])/float(VIpoint[1])
    Temp=ppms.getPPMSStatus()[0]
    DATA=str(Temp)+','+str(R)+'\n'
    f=open(filename,'a')
    f.write(DATA)
    f.close()
    print 'Temperature is '+str(Temp)+'k'+'Resistance is '+str(R)+'ohm'

#ppms.setTemperature(300,rate=10,stable=1)
'''




'''
# T dependence of S21 and impedence

FilePath='E:\\Qi\\Prf Wang Nanlin\\LaAgSb\\Sample on waveguide tight loose'
ppms=PPMS()
vna=VNA()
TemperaturePoint=[10,15,20,30,40,50,60,70,80,90,100,125,150,175,200,225,250,275,300]

TemperaturePoint2=[TemperaturePoint[-i-1] for i in range(len(TemperaturePoint))]
f1=open(os.path.join(FilePath,'S21.txt'),'a')
f2=open(os.path.join(FilePath,'R1.txt'),'a')
f3=open(os.path.join(FilePath,'R2.txt'),'a')
freq=vna.GetFreq()
f1.write('freq,'+freq)
f2.write('freq,'+freq)
f3.write('freq,'+freq)
f1.close()
f2.close()
f3.close()
for Temp in TemperaturePoint:
    ppms.setTemperature(Temp)
    print 'wait 600s to let the temperature more stalbe'
    time.sleep(600)
    f1=open(os.path.join(FilePath,'S21.txt'),'a')
    f2=open(os.path.join(FilePath,'R1.txt'),'a')
    f3=open(os.path.join(FilePath,'R2.txt'),'a')
    s21=vna.ReadLine(1)
    R=vna.ReadLine(2).split(',')
    R1=','.join([R[i*2] for i in range(1601)])
    R2=','.join([R[i*2+1] for i in range(1601)])
    
    f1.write(str(Temp)+','+s21)
    f2.write(str(Temp)+','+R1+'\n')
    f3.write(str(Temp)+','+R1+'\n')
    
    f1.close()
    f2.close()
    f3.close()
    
    
    print Temp
'''


#FMR
FilePath='E:\\YYY\\FGT\\NO_1\\damping'
ppms=PPMS() 
vna=VNA()
vna.fmr_init(points=39,freq_start=1e9,freq_stop=20e9,power=5,IF=1e3)
#TemperaturePoint=[300]
TemperaturePoint=[300]


#sp.Popen(args=['python.exe','E:\\Qi\\labview\\Python\\real_plot.py',fp,[]],stdout=sp.PIPE,stderr=sp.PIPE)
real_plot_another_process(plot_row_number=3,columns_list=[])

for Temp in TemperaturePoint:
    filename='4th'+str(Temp)+'_S21.txt'
    fp=os.path.join(FilePath,filename)
    ppms.setTemperature(Temp)
    #vna.set_power(Temp)
    #vna.set_IF(Temp)    
    print 'wait 600s to let the temperature more stalbe'  
    #time.sleep(1800)
    vna.fmr_measure(fp,10000,5)
    #vna.fmr_measure(fp,-2000,10)
    #vna.fmr_measure(fp,-8000,10)

#ppms.setTemperature(75)



'''

#  SWeep T, MR, microwave on AC
folder='E:\\Qi\\MR calibration\\device 3\\second' #.replace('\\','\\')  # take care not \  should be /
#NamePrefix='test90_3'
var=[-1.5e-3,1.5e-3]
amplifier=1
current_source=-1e-8
#var.reverse()
unit='k'
#amplifier=100
#temperature=[300]
ppms=PPMS()
#figure=plt.figure()
i=0
#sr830=SR830()
#modulation_freq=sr830.get_freq()
k2400=K2400()
k2002=K2002()
vna=VNA()
vna.spin_pumping_init(power=0,freq_cent=8e9)
real_plot_another_process(plot_row_number=2)
NameSuffix='0dbm300k8G'+'Hz'#+'modul_freq'+modulation_freq
for temp in var:
    i=i+1
    print temp,unit   
    #ppms.setTemperature(temp)
    
    #time.sleep(600)
    #k2400.k2400.write(':sour:volt '+str(temp))
    #vna.set_power(temp)
    print 'temperature is ok, please wait some time untill it is stable',time.ctime()
    #vna.SetFreqCenter(temp)
    #time.sleep(1200)
    #time.sleep(300)
    #axes=plt.subplot(4,4,i)
    #axes.set_title(str(temp)+unit)  
    #time.sleep(600)
    k2400.k2400.write(':sour:curr '+ str(temp))
    time.sleep(600)
    SpinPumingSR830(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=3000,Rate=5,amplifier=amplifier)
    SpinPumingSR830(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=-3000,Rate=5,amplifier=amplifier)
    #MR_2400_2002(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=1200,StopMag=-1200,Rate=5,current_source=current_source,amplifier=amplifier)
    #MR_2400_2002(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=-2000,StopMag=-0,Rate=5,current_source=1e-5)
vna.set_power(-40)
k2400.k2400.write(':sour:curr '+ str(0))
#ppms.setTemperature(100)
#ppms.setTemperature(300)
'''
'''
#  SWeep T, MR  microwvave off , DC
folder='E:\\Qi\\TI YIG\\x0.7\\Hall' #.replace('\\','\\')  # take care not \  should be /
#NamePrefix='test90_3'
var=[300]#[-10e-3,-5e-3,-1e-3,-5e-4,0,5e-4,1e-3,5e-3,10e-3]`
amplifier=1
current_source=5e-6
#var.reverse()
unit='k'
#amplifier=100
#temperature=[300]
ppms=PPMS()
#figure=plt.figure()
i=0
#sr830=SR830()
#modulation_freq=sr830.get_freq()
k2400=K2400()
k2002=K2002()
#vna=VNA()
#vna.spin_pumping_init(power=-15,freq_cent=5e9)
real_plot_another_process(plot_row_number=2)
NameSuffix='5uAI8_13V7_11'#+'modul_freq'+modulation_freq
for temp in var:
    i=i+1
    print temp,unit   
    #ppms.setTemperature(temp)
    
    #time.sleep(600)
    #k2400.k2400.write(':sour:volt '+str(temp))
    #vna.set_power(temp)
    print 'temperature is ok, please wait some time untill it is stable',time.ctime()
    #vna.SetFreqCenter(temp)
    #time.sleep(1200)
    #time.sleep(300)
    #axes=plt.subplot(4,4,i)
    #axes.set_title(str(temp)+unit)  
    #time.sleep(600)
    #k2400.k2400.write(':sour:curr '+ str(temp))
    #time.sleep(600)
    #SpinPumingSR830(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=1500,Rate=15,amplifier=amplifier)
    #SpinPumingSR830(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'.txt'),StartMag=-1500,Rate=15,amplifier=amplifier)
    MR_2400_2002(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'up.txt'),StartMag=-15000,StopMag=15000,Rate=50,current_source=current_source,amplifier=amplifier)
    MR_2400_2002(filename=os.path.join(folder,str(temp)+unit+NameSuffix+'down.txt'),StartMag=15000,StopMag=-15000,Rate=50,current_source=current_source,amplifier=amplifier)
#vna.set_power(-40)
k2400.k2400.write(':sour:curr '+ str(0))
ppms.setField(0)
#ppms.setTemperature(100)
#ppms.setTemperature(300)
'''