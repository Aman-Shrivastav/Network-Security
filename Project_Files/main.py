#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 14:55:57 2021

@author: surbhi
"""


import sqlite3 as lite
from utils import *

############## Main Method #################
if __name__ == '__main__' :
    conn = createDatabases()
    print("Menu Driven Program")
    print("1.Setup sensor node")
    print("2.Register as doctor")
    print("3.Register as patient")
    print("4.User Login")
    print("5.Add new Sensor Node Dynamically")

    
    choice = -1
    while choice != 9:
        choice=int(input("\n\nEnter your choice : "))
        if choice==1:
            print('Initiating setup Phase')
            setup()
            print('Setup completed successfully')
        elif choice==2:
            print("Doctor Registration started")
            register_doctor()
        elif choice==3:
            print("register patient")
            patient_registration()
        elif choice==4:
            print("User Login Initiated")
            login_user()
        elif choice==5:
            print("Dynamic sensor node addition")
            add_sensor_node_dynamically()
        
    conn.close()