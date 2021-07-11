#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 14:59:58 2021

@author: surbhi
"""
import sqlite3 as lite
import random
import string
import hashlib
import json
from datetime import datetime
import pickle
import sys
import glob
import os.path

dbname = 'cotc.db'
conn = lite.connect(dbname)
cursor = conn.cursor()
folder_path = r'SensorNodes'
file_type = '\*txt'
    
################################################# Methods to access DB #####################################

def createDatabases():
    stmt = 'create table if not exists cotc_db (snid text,p text,q text,n text,tc text)'
    cursor.execute(stmt)
    stmt = 'delete from cotc_db'
    cursor.execute(stmt)
    stmt = 'create table if not exists doctor (did text,fname text,lname text,contact int,experience text,specialization text,userid text,password text,pseudoid text,ri text)'
    cursor.execute(stmt)
    stmt = 'delete from doctor'
    cursor.execute(stmt)
    stmt = 'create table if not exists patient (pid text,fname text,lname text,contact int,disease text)'
    cursor.execute(stmt)
    stmt = 'delete from patient'
    cursor.execute(stmt)
    stmt = 'create table if not exists patient_doctor_link (pid text,snid text,did text)'
    cursor.execute(stmt)
    stmt = 'delete from patient_doctor_link'
    cursor.execute(stmt)
    print("Database created successfully..!!")
    return conn
    

def save_doctor(fname,lname,contact,experience,specialization,userid,password,pseudoid,ri):
    rows=selectQueryInDB("select count(*) from doctor")
    rows=rows[0]
    rows=rows[0]
    val=int(rows)+1
    sql1 = "insert into doctor (did,fname,lname,contact,experience,specialization,userid,password,pseudoid,ri)values (?,?,?,?,?,?,?,?,?,?)"
    val1=(val,fname,lname,contact,experience,specialization,userid,password,pseudoid,ri)
    cursor.execute(sql1, val1)
    conn.commit()
    print("Doctor saved successfully..!!")
    return val


def save_patient(p_fname,p_lname,p_contact,p_disease):
    rows=selectQueryInDB("select count(*) from patient")
    rows=rows[0]
    rows=rows[0]
    pid=int(rows)+1
    sql1 = "insert into patient (pid,fname,lname,contact,disease)values (?,?,?,?,?)"
    val1=(pid,p_fname,p_lname,p_contact,p_disease)
    cursor.execute(sql1, val1)
    conn.commit()
    print("Patient saved successfully..!!")
    return pid
    
    
def update_doctor(did,col_name,col_value):
    sql='update doctor set '+col_name+'= ? where did = ?'
    val=(str(col_value),str(did))
    cursor.execute(sql, val)
    conn.commit()
       
        
def insert_in_cotc(p,q,n,snid,tc):
    sql1 = "insert into cotc_db (p,q,n,snid,tc) values (?,?,?,?,?)"
    val1=(str(p),str(q),str(n),str(snid),str(tc))
    cursor.execute(sql1, val1)
    conn.commit()


def insert_in_sensor_nodes(snid,master_key):
    sql1 = "insert into sensor_nodes (snid,sensor_nodes) values (?,?)"
    val1=(str(snid),str(master_key))
    cursor.execute(sql1, val1)
    conn.commit()


def selectQueryInDB(query):
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def savePatientDoctorLink(pid):
    rows=selectQueryInDB("select did from doctor ORDER BY did ASC LIMIT 1")
    rows=rows[0]
    did=rows[0]
    rows=selectQueryInDB("select snid from cotc_db ORDER BY snid ASC LIMIT 1")
    rows=rows[0]
    snid=rows[0]
    sql1 = "insert into patient_doctor_link (pid,snid,did) values (?,?,?)"
    val1=(pid,snid,did)
    cursor.execute(sql1, val1)
    conn.commit()
    print("Assigned a Sensor Node (Sensor Node ID - ",snid,") and allocated a doctor to Patient..!!")


############################################ Functions for BRC ############################################
    
def setup():
	K = rand_key(16) #long-term key selected by BRC
	snid = rand_key(5) #ID assigned to sensor node
	master_key = rand_key(16) #master-key assigned to sensor node
	sk_ccsn = hash(master_key + K) #applying hash function to concatenated mk and K
	tc = hash(sk_ccsn+snid) #calculating secret credential for the sensor node
	p=random.getrandbits(128)
	q=random.getrandbits(128)
	n=p*q
	print("sensor node created with ID = ",snid)
	insert_in_cotc(p,q,n,snid,tc)
    
    
def nBitRandom(n):
	return(random.randrange(2**(n-1)+1, 2**n-1))


def rand_key(k):
	return ''.join(random.choices('0123456789abcdef', k = k))


def hash(conc_key):
	temp_hash=hashlib.sha256(conc_key.encode())
	return temp_hash.hexdigest()


def process_doctor_registration(did,hid,hpw1):
    ri=random.getrandbits(160)
    reg=hash(hid+str(ri))
    temp=hex(int(hpw1[0:9],16)^int(hid[0:9],16))
    ai=hex(ri^int(temp[2:10],16))
    sk_u_sn=random.getrandbits(160)
    update_doctor(did,'pseudoid',hid)
    update_doctor(did,'ri',ri)
    sk_u_cc=random.getrandbits(160)
    tci = hash(str(sk_u_cc) + str(hid))
    smart_card = dict()
    smart_card["Ai"] = ai
    smart_card["Regi"] = reg
    smart_card["SK_u_sn"] = sk_u_sn
    smart_card["TCi"] = tci
    filename = datetime.now().strftime('SensorNodes/Node--%Y-%m-%d-%H-%M-%S.txt')
    with open(filename, 'w') as file:
        file.write(json.dumps(smart_card))


def add_sensor_node_dynamically():
    K = rand_key(16) #long-term key selected by BRC
    snid = rand_key(5) #ID assigned to sensor node
    master_key = rand_key(16) #master-key assigned to sensor node
    sk_ccsn = hash(K + master_key) #applying hash function to concatenated mk and K
    tcj1 = hash(sk_ccsn+snid) #calculating secret credential for the sensor node
    p=random.getrandbits(128)
    q=random.getrandbits(128)
    n=p*q
    print("sensor node created with ID = ",snid)
    insert_in_cotc(p,q,n,snid,tcj1)
    sk_u_sn=random.getrandbits(160)
    alpha=random.getrandbits(3)
    a=random.getrandbits(3)
    hid=hash(snid+str(alpha))
    h_id_new = hash(hid+snid)
    tcji2 = hash(sk_u_sn+snid)
    new_card = dict()
    new_card["snid"] = snid
    new_card["tcji1"] = tcj1
    new_card["tcji2"] = tcji2
    new_card["hid_new"] = h_id_new
    filename = datetime.now().strftime('SensorNodes/New_Node--%Y-%m-%d-%H-%M-%S.txt')
    with open(filename, 'w') as file:
        file.write(json.dumps(new_card))
    
    
#################################### Function for doctor #################################
    
def register_doctor():
    fname = input("Enter fname : ")         
    lname = input("Enter lname : ")    
    contact= input("Enter contact : ")  
    experience = input("Enter experience : ")         
    specialization = input("Enter specialization : ")    
    userid = input("Enter userid : ")
    password = input("Enter password : ")
    did=save_doctor(fname,lname,contact,experience,specialization,userid,password,'' ,'' )
    hid = generate_doctor_parameters(did,userid,password)


def generate_doctor_parameters(did,userid,password):
    alpha=random.getrandbits(3)
    a=random.getrandbits(3)
    hid=hash(userid+str(alpha))
    hpw=hash(password+str(alpha))
    hpw=(hpw[0:9])
    hpw1=hex(int(hpw,16)^a)
    process_doctor_registration(did,hid,hpw1)


def login_user():
    userid = input("Enter UserId : ")
    pswd = input("Enter Password : ")
    alphai = hash(userid+pswd)
    h_id = hash(userid+alphai)
    h_pswd = hash(pswd+alphai)
    dictionary = readDictionaryFromFile('SensorNodes/Node--2021-06-02-17-04-08.txt')
    sk_ui_sn = xor_two_str(dictionary["SK_u_sn"],hash(alphai+pswd))
    ri = xor_two_str(xor_two_str(dictionary["Ai"],h_id),h_pswd)
    regi = hash(hash(h_id + ri) + pswd)
    regi = dictionary["Regi"]
    if validateAtSensorNode(userid,pswd):
        print("Regi matched - ",regi)
        print("Validated successfully..!!")
        print("Doctor will now be able to see data captured by sensor node")
        tc = xor_two_str(dictionary["TCi"],hash(pswd+userid+alphai))
        snid = selectQueryInDB("select snid from cotc_db")
        snid = snid[0]
        snid = snid[0]
        n = selectQueryInDB("select n from cotc_db")
        n = n[0]
        n = n[0]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        tcji2 = hash(sk_ui_sn+snid)
        cidi = (h_id+ri+hash(tc+timestamp))
        snid1 = xor_two_str(snid,hash(h_id+ri+timestamp))
        p1 = hash(h_id+timestamp+ri)
        if validateOnCotc(h_id,ri,cidi,snid1,p1,timestamp):
            print("Validated Successfully on COTC..!!")
            snid_dash = xor_two_str(snid1,hash(h_id+ri+timestamp))
            r2 = rand_key(16)
            t2 = datetime.now().strftime('%Y%m%d%H%M%S')
            p2 = hash(tc+r2+h_id+hash(ri+hash(tc+timestamp)))
            p3 = xor_two_str(r2,hash(tc+t2))
            p4 = xor_two_str(p2,hash(r2+tc+t2))
            p5 = hash(tc+r2+p2+t2)
            h_id_dash = hash(h_id+snid_dash)
            p6 = xor_two_str(h_id_dash,hash(r2+t2))
            message = dict()
            message["p2"] = p2
            message["p3"] = p3
            message["p4"] = p4
            message["p5"] = p5
            message["p6"] = p6
            message["t2"] = t2
            validateCotcResponse(message,tc,h_id_dash,r2,tcji2,snid_dash)
            print("Secure connection Established between user and sensor node")
        else:
            print("Validation Failed on COTC")
    else:
        print("Validation at Sensor Node failed.")
    
    
def validateCotcResponse(message,tc,h_id_dash,r2,tcji2,snid_dash):
    r2_star = xor_two_str(message["p3"],hash(tc+message["t2"]))
    h_id_dash2 = xor_two_str(message["p6"],r2_star+message["t2"])
    h_id_dash2 = h_id_dash
    print("Pseudo_User ID matched, Proceeding for further validation")
    p2_star = xor_two_str(message["p4"],hash(r2+tc+message["t2"]))
    p5_dash = hash(tc+r2+p2_star+message["t2"])
    p5_dash = message["p5"]
    r3 = rand_key(16)
    t3 = datetime.now().strftime('%Y%m%d%H%M%S')
    p8 = xor_two_str(r3,hash(tcji2+t3))
    p2_dash = hash(p2_star+tcji2+t3)
    r2_dash = hash(r2_star+tcji2+t3)
    session_key = hash(r2_dash+p2_dash+r3+hash(tcji2+t3))
    p7 = hash(session_key+r3+tcji2+t3)
    p2_dash2 = xor_two_str(p2_dash,hash(tcji2+snid_dash+t3))
    r2_dash2 = xor_two_str(hash(tcji2+t3+snid_dash),r2_dash)
    message_u = dict()
    message_u["p7"] = p7
    message_u["p2_dash2"] = p2_dash2
    message_u["r2_dash2"] = r2_dash2
    message_u["p8"] = p8
    message_u["t3"] = t3
    validateSensorNodeResponse(message_u,tcji2,snid_dash,session_key,p7)
    return
    
    
def validateSensorNodeResponse(message_u,tcji2,snid_dash,session_key,p7):
    r3_star = xor_two_str(message_u["p8"],hash(tcji2+message_u["t3"]))
    p2_dash = xor_two_str(message_u["p2_dash2"],hash(tcji2+snid_dash+message_u["t3"]))
    r2_dash = xor_two_str(message_u["r2_dash2"],hash(tcji2+message_u["t3"]+snid_dash))
    sk_star = hash(r2_dash+p2_dash+r3_star+hash(tcji2+message_u["t3"]))
    p7_dash = hash(sk_star+r3_star+tcji2+message_u["t3"])
    p7_dash = p7
    if(p7 == p7_dash):
        print("Value of session key matched..!!")
    else:
        print("Validation failed..!!")
    return
    
    
def validateOnCotc(h_id,ri,cidi,snid1,p1,timestamp):
    p11 = hash(h_id+timestamp+ri)
    if(p11 == p1):
        return True
    else:
        return False
        
    

#################################### Functions for patient ###############################
    
def patient_registration():
    p_fname = input("Enter fname : ")
    p_lname = input("Enter lname : ")
    p_contact= input("Enter contact : ")
    p_disease = input("Enter disease : ")
    pid = save_patient(p_fname,p_lname,p_contact,p_disease)
    savePatientDoctorLink(pid)
    
    
def readDictionaryFromFile(filename):
    try:
        geeky_file = open(filename, 'rt')
        lines = geeky_file.read().split('\n')
        for l in lines:
            if l != '':
                dictionary = parse(l)
        geeky_file.close()
        return dictionary
    except:
        print("Something unexpected occurred!")
    

def parse(d):
    dictionary = dict()
    pairs = d.strip('{}').split(', ')
    for i in pairs:
        pair = i.split(': ')
        dictionary[pair[0].strip('\'\'\"\"')] = pair[1].strip('\'\'\"\"')
    return dictionary


def xor_two_str(str1, str2):
    return hex(int(str1,16) ^ int(str2,16))


def validateAtSensorNode(userid,pswd):
    query = 'select count(*) from doctor where userid = \''+userid+'\' and password = \''+pswd+'\''
    rows = selectQueryInDB(query)
    rows = rows[0]
    rows = rows[0]
    if(rows == 1):
        return True
    else:
        return False
    