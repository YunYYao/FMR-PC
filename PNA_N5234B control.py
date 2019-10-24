# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 15:52:15 2019

@author: YY YAO
"""

import SpectromagControl as sgc



pna=sgc.PNA()


pna.fmr_init(freq_start=1e9,freq_stop=43e9,points=169,power=-5,IF=10e3)

pna.set_ave(20)