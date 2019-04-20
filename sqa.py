# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 21:01:10 2016
sq_analysis
@author: QSong_pku
"""
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm
#from mlab.releases import latest_release as matlab
from scipy import  interpolate
import pandas as pd
import shutil
import os
import win32com.client
from scipy.optimize import least_squares
import sys

def fit_guassion_robust(fitx,fity,x0=False): #lineshape fitting
	'''
	p[0] sysmetrical height
	p[1] resonance field
	p[2] half linewidth
	p[3] asysmetrical height
	p[4] linear slope
	p[5] constant
	'''
	def fun_fit(p,x,y):
		return fun_cal_y(p,x)-y 
	def fun_cal_y(p,x):
		return (p[0]*p[2]**2-2*p[3]*p[2]*(x-p[1]))/((x-p[1])**2+p[2]**2)+p[4]*x+p[5]
	
	if not x0: 
		x0=[0,0,100,0,0,0] 
	else: 
		x0=x0
		
	res_robust=least_squares(fun_fit,x0,loss='soft_l1',f_scale=0.1,args=(fitx,fity))
	fitted_y=fun_cal_y(res_robust.x,fitx)
	if res_robust.x[2]<0:
		res_robust.x[2]=-res_robust.x[2]
	return res_robust.x,fitted_y



def fit_refine_data(rawx,rawy,leftx,rightx):
	leftindex=np.argmin(abs(rawx-leftx))
	rightindex=np.argmin(abs(rawx-rightx))
	minindex=min(leftindex,rightindex)
	maxindex=max(leftindex,rightindex)
	return rawx[minindex:maxindex],rawy[minindex:maxindex]
	
def fit_one_curve(curvex,curvey,width=[400,400],figure_path='C:\\Users\\QSong_pku\\Desktop\\temp.png'):
	#global figure_path
	
	if np.max(np.abs(curvex))<100:
		curvex=curvex*1000
	#plt.figure()
	#plt.figure()
	plt.ion()
	plt.plot(curvex,curvey,'r.')
	plt.title(figure_path)
	plt.draw()
	plt.pause(0.1)
	
	while True:
		print \
		'''
		no point => ok 
		1 point => center
		3 point => limit the left and right width
		>4 point => repeat
        5 point => give up
		'''
		try:
			ginput=plt.ginput(0)
		except:
			continue
		if len(ginput)==1:
			refinedx,refinedy=fit_refine_data(curvex,curvey,ginput[0][0]-width[0],ginput[0][0]+width[1])
			x0=[0,ginput[0][0],sum(width)/4.0,0,0,0]
			parameter,fitted_y=fit_guassion_robust(refinedx,refinedy,x0=x0)
			#plt.plot(refinedx,refinedy,'.')
			plt.plot(refinedx,fitted_y,'.',ms=3)
			plt.draw()
			#plt.pause(0.1)
		elif len(ginput)==3:
			refinedx,refinedy=fit_refine_data(curvex,curvey,ginput[0][0],ginput[2][0])
			plt.clf()
			plt.plot(refinedx,refinedy,'r.',ms=10)
			plt.draw()
			plt.pause(0.1)
			x0=[ginput[1][1]-ginput[0][1],ginput[1][0],(ginput[2][0]-ginput[0][0])/4.0,0,0,ginput[0][1]]
			parameter,fitted_y=fit_guassion_robust(refinedx,refinedy,x0=x0)
			#plt.plot(refinedx,refinedy,'.')
			plt.plot(refinedx,fitted_y,'b.',ms=15)
			plt.title(figure_path)
			plt.draw()
			plt.pause(0.1)
			#plt.pause(0.1)
		elif len(ginput)==0:
			break
		elif len(ginput)==4:
			plt.clf()
			plt.plot(curvex,curvey,'r.')
			plt.title(figure_path)
			plt.draw()
			plt.pause(0.1)
		elif len(ginput)>4:
			parameter=np.zeros(6)
			break
		else:
			print 'ginput error'
		#plt.savefig(figure_path)
	plt.clf()
	return parameter

def fit_positive_negtive_spinpumping(x,y):
    '''
    I would save fig and move it to the file you specify
    '''
    data=np.column_stack((np.array(x).flatten(),np.array(y).flatten()))
    data_positive=data[data[:,0]>0,:];data_negtive =data[data[:,0]<0,:]
        
    parameter_positive=fit_one_curve(data_positive[2:-2,0],data_positive[2:-2,1]);print parameter_positive

        
    parameter_negtive =fit_one_curve(data_negtive[2:-2,0] ,data_negtive[2:-2,1]);print parameter_negtive
	
    
    if parameter_negtive[0]==0:
        spin_pumping=(parameter_positive[0]-parameter_negtive[0])/2
        seebeck=(parameter_positive[0]+parameter_negtive[0])/2
        resonance_field=parameter_positive[1]
        half_linewidth=parameter_positive[2]
        ahe=(parameter_positive[3]+parameter_negtive[3])/2
        hysteresis=0
        print 'care ! negtive side no signal'
    elif parameter_positive[0]==0:
        spin_pumping=(parameter_positive[0]-parameter_negtive[0])/2
        seebeck=(parameter_positive[0]+parameter_negtive[0])/2
        resonance_field=-parameter_negtive[1]
        half_linewidth=parameter_negtive[2]
        ahe=(parameter_positive[3]+parameter_negtive[3])/2
        hysteresis=0
        print 'care! positive side no signal'
    else:
        spin_pumping=(parameter_positive[0]-parameter_negtive[0])/2
        seebeck=(parameter_positive[0]+parameter_negtive[0])/2
        resonance_field=(parameter_positive[1]-parameter_negtive[1])/2
        half_linewidth=(parameter_positive[2]+parameter_negtive[2])/2
        ahe=(parameter_positive[3]+parameter_negtive[3])/2
        hysteresis=(parameter_positive[1]+parameter_negtive[1])/2
    
    physical_quantity=np.array([spin_pumping,seebeck,resonance_field,half_linewidth,ahe,hysteresis],ndmin=2)
    fitting_parameters=np.column_stack((np.array(parameter_positive,ndmin=2),np.array(parameter_negtive,ndmin=2)));print physical_quantity
    return physical_quantity,fitting_parameters
    
def get_points_from_one_curve(x,y):
    plt.figure()
    plt.plot(x,y,'.')
    plt.margins(0.1,0.1)
    points=plt.ginput(n=0,timeout=60)
    plt.close()
    return points 

def substrate_background_from_one_curve(x,y,folder='C:\\Users\\user\\Desktop\\Ma-Young\\MR',filename='1702-bg.txt'):
    'take care, should have the same x'    
    
    okornot=0
    while not okornot==1:
        #plt.figure()
        plt.ion()
        plt.subplot(2,1,1)
        plt.margins(0.1,0.1)
        plt.plot(x,y,'.k',label='raw data',ms=10)
        point=plt.ginput(n=0,timeout=60)
        point=np.array(point)
        point[:,1]=point[np.argsort(point[:,0]),1]
        point[:,0]=point[np.argsort(point[:,0]),0]
        y_background=interpolate.UnivariateSpline(point[:,0],point[:,1],s=0)(x)
  
        y_new=y-y_background
    
        
        plt.plot(point[:,0],point[:,1],'sr',label='choosen point',ms=15)
        plt.plot(x,y_background,'*g',label='background')
        plt.legend(loc='best')
        
        plt.subplot(2,1,2)
        plt.margins(0.1,0.1)
        plt.plot(x,y_new,'.k',label='cleaned data',ms=10)
        plt.legend(loc='best')
        plt.draw()
        plt.pause(0.1)
        
        
        okornot=input('ok=1;   not=0:  please input the number')
        print os.path.join(folder,filename.replace('.txt','_Sub_background.jpg'))
        if not okornot==1:
            plt.clf()
    plt.savefig(os.path.join(folder,filename.replace('.txt','_Sub_background.jpg')))
    plt.clf()
    return y_new

def get_R_from_VI(V,I):
    R,intercept=np.polyfit(I,V,1)
    return R,intercept
    
def move_and_overwrite_a_file(filename,folder2):
    if os.path.basename(filename) in os.listdir(folder2):
        os.remove(os.path.join(folder2,os.path.basename(filename)))
        print 'deleting'+os.path.join(folder2,os.path.basename(filename))+'................'
    shutil.move(filename,folder2)
    
def convert_dbm_to_mw(dbm):
    return 10.0**(dbm/10.0)
	
def fmr_load_data(filepath):
    data=pd.read_csv(filepath,index_col=0)
    data.reindex(index=[float(i) for i in data.index])
    data=data.sort_index()
    return data    
    
def fmr_mesh_dataframe(dataframe,Dtype='fmr'):
    if Dtype=='fmr':
        dataframe=dataframe-dataframe.mean()
    
    X=np.array(dataframe.index)
    Y=np.array([float(i) for i in dataframe.columns])
    X,Y=np.meshgrid(Y,X)
    Z=dataframe.values;
    fig=plt.figure()
    #ax=fig.gca(projection='3d')
    ax=fig.gca()
    surf=ax.pcolormesh(Y,X,Z,vmin=Z.min(),vmax=Z.max(),linewidth=0,cmap=cm.coolwarm)
    #surf=ax.pcolormesh(X,Y,Z,rstride=100,cstride=10000000,vmin=Z.min(),vmax=Z.max(),linewidth=0,cmap=cm.coolwarm)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.xlabel('H (Oe)')
    plt.ylabel('Frequency (Hz)')

def fmr_select_frequency(data,frequency):
# the frequency is numericaial data
    frequencylist=np.array([float(i) for i in data.columns])
    return data[data.columns[np.argmin(abs(frequencylist-frequency))]]
   
def fmr_substrate_background(data,background):
	new_index=np.linspace(min(min(abs(data.index.values)),min(abs(background.index.values))),max(max(abs(data.index.values)),max(abs(background.index.values))),data.index.size)
	new_data=pd.DataFrame(np.zeros((new_index.size,data.columns.values.size)),index=new_index,columns=data.columns.values)
	new_background=pd.DataFrame(np.zeros((new_index.size,data.columns.values.size)),index=new_index,columns=data.columns.values)
	for i in range(data.columns.values.size):
		new_data[new_data.columns[i]]=np.interp(new_index,data.index.values,data[data.columns[i]].values)
		new_background[new_background.columns[i]]=np.interp(new_index,background.index.values,background[background.columns[i]].values)
	cleaned_data=new_data-new_background
	return cleaned_data

def fmr_substrate_background_new(data,background):
	new_index=np.linspace(min(min(abs(data.index.values)),min(abs(background.index.values))),max(max(abs(data.index.values)),max(abs(background.index.values))),data.index.size)
	new_data=pd.DataFrame(np.zeros((new_index.size,data.columns.values.size)),index=new_index,columns=data.columns.values)
	new_background=pd.DataFrame(np.zeros((new_index.size,data.columns.values.size)),index=new_index,columns=data.columns.values)
	for i in range(data.columns.values.size):
		new_data[new_data.columns[i]]=np.interp(new_index,data.index.values,data[data.columns[i]].values)
		new_background[new_background.columns[i]]=np.interp(new_index,background.index.values,background[background.columns[i]].values)
	cleaned_data=new_data-new_background
	return new_data
    
def origin_creat_table(name):
    origin=win32com.client.Dispatch('Origin.ApplicationSI')
    origin.visible=1
    pagename=origin.CreatePage(2,name,'origin')
    del origin
    return pagename

def origin_get_array(pagename,array,transpose=0,position=[0,0],longname_unit_comment=[]):
	'''
	take care the array shape,you can use transpose the adjust it 
	'''
	array=np.array(array,ndmin=2)
	origin=win32com.client.Dispatch('Origin.ApplicationSI')
	origin.visible=1
	wks=origin.FindWorksheet(pagename)
	origin.PutWorksheet(pagename,array,position[0],position[1])
	for i in range(len(longname_unit_comment)):
		wks.Columns(i+position[1]).LongName=longname_unit_comment[i][0]
		wks.Columns(i+position[1]).Units=longname_unit_comment[i][1]
		wks.Columns(i+position[1]).Comments=longname_unit_comment[i][2]