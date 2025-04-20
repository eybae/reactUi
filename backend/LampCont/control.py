import json
import base64, binascii, codecs
from decimal import Decimal
import numpy


def encode(data):    
    base64_message = base64.b64encode(bytes.fromhex(data)).decode()
    return base64_message

def dataTobase64(data):
    base64Data = ""        
    res = ''.join(format(x, '02x') for x in data)
    base64Data = encode(res)
    return base64Data

def autoControl():
    print("auto control")
    
def totalControl(request):
    if request == 1:
        dataArray = [int(0), int(1), int(0), int(3), int(19), int(0), int(5), int(30)]     
            
        data = {'state': '0',
                'dem': '3',
                'onTime': '19:00',
                'offTime': '05:30',
                }           
    else:
        errors = ''    
        data = {'state':'1', 'dem':'3', 'onTime':'19:00', 'offTime':'05:00'}
        dataArray = []

        state = request.form["astate"] 
        dem = request.form["adem1"]        
        ontime = request.form["aonTime"].strip() 
        offtime = request.form["aoffTime"].strip()  

        if not dem or not state or not ontime or not offtime:
            errors = "Please enter all the fields."
            
        if not errors:  
            aon1 = ontime.split(':')
            aoff1 = offtime.split(':')  
            mode = 0                # 0: 상태 , 1: 명령 
            cmd = 1                 # 0: 자동 , 1: 일괄, 2:개별         
            
            dataArray = [int(mode), int(cmd), int(state), int(dem), int(aon1[0]), int(aon1[1]), int(aoff1[0]), int(aoff1[1])]     
            
            data = {'state': state,
                    'dem': dem,
                    'onTime': ontime,
                    'offTime': offtime,
                    }    
               
    return (data, dataArray)

def eachControl(request):     
    if request == 1:
        data2Array = {'lamp1': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp2': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp3': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp4': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp5': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp6': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp7': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp8': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp9': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)],
                    'lamp10': [int(0), int(2), int(0), int(3), int(19), int(0), int(6), int(0)]}  
         
        data2 = {'bstate1':'1', 'bdem1': '3', 'bonTime1':"19:00", 'boffTime1': "05:00",
             'bstate2':'1', 'bdem2': '3', 'bonTime2':"19:00", 'boffTime2': "05:00",
             'bstate3':'1', 'bdem3': '3', 'bonTime3':"19:00", 'boffTime3': "05:00",
             'bstate4':'1', 'bdem4': '3', 'bonTime4':"19:00", 'boffTime4': "05:00",
             'bstate5':'1', 'bdem5': '3', 'bonTime5':"19:00", 'boffTime5': "05:00",
             'bstate6':'1', 'bdem6': '3', 'bonTime6':"19:00", 'boffTime6': "05:00",
             'bstate7':'1', 'bdem7': '3', 'bonTime7':"19:00", 'boffTime7': "05:00",
             'bstate8':'1', 'bdem8': '3', 'bonTime8':"19:00", 'boffTime8': "05:00",
             'bstate9':'1', 'bdem9': '3', 'bonTime9':"19:00", 'boffTime9': "05:00",
             'bstate10':'1', 'bdem10': '3', 'bonTime10':"19:00", 'boffTime10': "05:00"}            
           
    else:
        errors = ''         
        data2 = {'bstate1':'1', 'bdem1': '3', 'bonTime1':"19:00", 'boffTime1': "05:00",
             'bstate2':'1', 'bdem2': '3', 'bonTime2':"19:00", 'boffTime2': "05:00",
             'bstate3':'1', 'bdem3': '3', 'bonTime3':"19:00", 'boffTime3': "05:00",
             'bstate4':'1', 'bdem4': '3', 'bonTime4':"19:00", 'boffTime4': "05:00",
             'bstate5':'1', 'bdem5': '3', 'bonTime5':"19:00", 'boffTime5': "05:00",
             'bstate6':'1', 'bdem6': '3', 'bonTime6':"19:00", 'boffTime6': "05:00",
             'bstate7':'1', 'bdem7': '3', 'bonTime7':"19:00", 'boffTime7': "05:00",
             'bstate8':'1', 'bdem8': '3', 'bonTime8':"19:00", 'boffTime8': "05:00",
             'bstate9':'1', 'bdem9': '3', 'bonTime9':"19:00", 'boffTime9': "05:00",
             'bstate10':'1', 'bdem10': '3', 'bonTime10':"19:00", 'boffTime10': "05:00"}  
        data2Array = {}    
    
        bdem1 = request.form["bdem1"]  
        bstate1 = request.form["bstate1"]
        bonTime1 = request.form["bonTime1"].strip()
        boffTime1 = request.form["boffTime1"].strip()
        bdem2 = request.form["bdem2"]  
        bstate2 = request.form["bstate2"]
        bonTime2 = request.form["bonTime2"].strip()
        boffTime2 = request.form["boffTime2"].strip()
        bdem3 = request.form["bdem3"]  
        bstate3 = request.form["bstate3"]
        bonTime3 = request.form["bonTime3"].strip()
        boffTime3 = request.form["boffTime3"].strip()
        bdem4 = request.form["bdem4"]  
        bstate4 = request.form["bstate4"]
        bonTime4 = request.form["bonTime4"].strip()
        boffTime4 = request.form["boffTime4"].strip()
        bdem5 = request.form["bdem5"]  
        bstate5 =  request.form["bstate5"]
        bonTime5 = request.form["bonTime5"].strip()
        boffTime5 = request.form["boffTime5"].strip()
        bdem6 = request.form["bdem6"]  
        bstate6 = request.form["bstate6"]
        bonTime6 = request.form["bonTime6"].strip()
        boffTime6 = request.form["boffTime6"].strip()
        bdem7 = request.form["bdem7"]  
        bstate7 = request.form["bstate7"]
        bonTime7 = request.form["bonTime7"].strip()
        boffTime7 = request.form["boffTime7"].strip()
        bdem8 = request.form["bdem8"]  
        bstate8 = request.form["bstate8"]
        bonTime8 = request.form["bonTime8"].strip()
        boffTime8 = request.form["boffTime8"].strip()
        bdem9 = request.form["bdem9"]  
        bstate9 = request.form["bstate9"]
        bonTime9 = request.form["bonTime9"].strip()
        boffTime9 = request.form["boffTime9"].strip()
        bdem10 = request.form["bdem10"]  
        bstate10 = request.form["bstate10"]
        bonTime10 = request.form["bonTime10"].strip()
        boffTime10 = request.form["boffTime10"].strip()  
        
        if not bdem1 or not bdem2 or not bdem3 or not bdem4 or not bdem5 or not bdem6 or not bdem7 or not bdem8 or not bdem9 or not bdem10:
            errors = "Please enter all the fields."
            
        if not errors:         
            on1 = bonTime1.split(':')
            off1 = boffTime1.split(':')
            on2 = bonTime2.split(':')
            off2 = boffTime2.split(':')
            on3 = bonTime3.split(':')
            off3 = bonTime3.split(':')
            on4 = bonTime4.split(':')
            off4 = boffTime4.split(':')
            on5 = bonTime5.split(':')
            off5 = boffTime5.split(':')
            on6 = bonTime6.split(':')
            off6 = bonTime6.split(':')
            on7 = bonTime7.split(':')
            off7 = boffTime7.split(':')
            on8 = bonTime8.split(':')
            off8 = boffTime8.split(':')
            on9 = bonTime9.split(':')
            off9 = bonTime9.split(':')
            on10 = bonTime10.split(':')
            off10 = bonTime10.split(':')
            mode = 0       # 개별제어
            cmd = 2
            
            data2temp = {'lamp1': [int(mode), int(cmd), int(bstate1), int(bdem1), int(on1[0]), int(on1[1]), int(off1[0]), int(off1[1])],
                        'lamp2': [int(mode), int(cmd), int(bstate2), int(bdem2), int(on2[0]), int(on2[1]), int(off2[0]), int(off2[1])],
                        'lamp3': [int(mode), int(cmd), int(bstate3), int(bdem3), int(on3[0]), int(on3[1]), int(off3[0]), int(off3[1])],
                        'lamp4': [int(mode), int(cmd), int(bstate4), int(bdem4), int(on4[0]), int(on4[1]), int(off4[0]), int(off4[1])],
                        'lamp5': [int(mode), int(cmd), int(bstate5), int(bdem5), int(on5[0]), int(on5[1]), int(off5[0]), int(off5[1])],
                        'lamp6': [int(mode), int(cmd), int(bstate6), int(bdem6), int(on6[0]), int(on6[1]), int(off6[0]), int(off6[1])],
                        'lamp7': [int(mode), int(cmd), int(bstate7), int(bdem7), int(on7[0]), int(on7[1]), int(off7[0]), int(off7[1])],
                        'lamp8': [int(mode), int(cmd), int(bstate8), int(bdem8), int(on8[0]), int(on8[1]), int(off8[0]), int(off8[1])],
                        'lamp9': [int(mode), int(cmd), int(bstate9), int(bdem9), int(on9[0]), int(on9[1]), int(off9[0]), int(off9[1])],
                        'lamp10': [int(mode), int(cmd), int(bstate10), int(bdem10), int(on10[0]), int(on10[1]), int(off10[0]), int(off10[1])]}   
            
            for num in data2temp:
                data2Array[num] = data2temp[num]     
                
            data2 = {
                    'bstate1': bstate1,'bdem1': bdem1,'bonTime1': bonTime1,'boffTime1': boffTime1,   
                    'bstate2': bstate2,'bdem2': bdem2,'bonTime2': bonTime2,'boffTime2': boffTime2,
                    'bstate3': bstate3,'bdem3': bdem3,'bonTime3': bonTime3,'boffTime3': boffTime3,   
                    'bstate4': bstate4,'bdem4': bdem4,'bonTime4': bonTime4,'boffTime4': boffTime4,   
                    'bstate5': bstate5,'bdem5': bdem5,'bonTime5': bonTime5,'boffTime5': boffTime5,   
                    'bstate6': bstate6,'bdem6': bdem6,'bonTime6': bonTime6,'boffTime6': boffTime6,
                    'bstate7': bstate7,'bdem7': bdem7,'bonTime7': bonTime7,'boffTime7': boffTime7,   
                    'bstate8': bstate8,'bdem8': bdem8,'bonTime8': bonTime8,'boffTime8': boffTime8,  
                    'bstate9': bstate9,'bdem9': bdem7,'bonTime9': bonTime9,'boffTime9': boffTime9,   
                    'bstate10': bstate10,'bdem10': bdem10,'bonTime10': bonTime10,'boffTime10': boffTime10,                 
            }      
            
    return (data2, data2Array)