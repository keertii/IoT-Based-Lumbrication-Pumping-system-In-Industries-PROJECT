import wiotp.sdk.device
from datetime import datetime
import time
import random
import json
import ibm_boto3
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1
from ibmcloudant import CouchDbSessionAuthenticator
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator


authenticator = BasicAuthenticator("apikey-v2-1x76tp54wlzxvziy003n0hhrvo0art1l5zj7amwvt6u2","01ecd22c6e9b02ae338e4e07956a29f2")

service = CloudantV1(authenticator=authenticator)

service.set_service_url('https://apikey-v2-1x76tp54wlzxvziy003n0hhrvo0art1l5zj7amwvt6u2:01ecd22c6e9b02ae338e4e07956a29f2@cc4dc272-85d7-450a-a536-30c09d73a555-bluemix.cloudantnosqldb.appdomain.cloud')









myConfig = { 
    "identity": {
        "orgId": "d7luey",
        "typeId": "IOTPumpSystem",
        "deviceId":"5684"
    },
    "auth": {
        "token": "0123456789"

    }
}


lubricationlevel = 100
lubinpump = 100
activity = ""
msgadmin = ""
error = None

def lubricant_in_pump(a,b,c):
    x = a-(c-b)
    return x

def myCommandCallback(cmd):
    global lubricationlevel
    global lubinpump
    global error
    global msgadmin
    m = cmd.data['command']
    if(m == "fill pump"):
        lubinpump = 100
        recentactpublish("PUMP IS FILLED WITH LUBRICANT")
        publishdata()
    elif(isinstance(m, int)):
        if(m<=lubricationlevel):
            error = "The desired lubrication level is less than the actual lubrication level"
            publishdata()
        elif(m>=0 and m<=100):
            publishdata()
            lubinpump = lubricant_in_pump(lubinpump,lubricationlevel,m)
            time.sleep(2)
            lubricationlevel = m
            xyz = "machine is lubricated upto "+ str(m) + "  % "
            recentactpublish(xyz)
            publishdata() 
            #print("Message received from IBM IoT Platform: %s" % cmd.data['command'])

    elif(m.isdigit()):
        if(int(m)<=lubricationlevel):
            error = " The desired lubrication level is less than the actual lubrication level"
            publishdata()
        elif(int(m)>=0 and int(m)<=100):
            publishdata()
            lubinpump = lubricant_in_pump(lubinpump,lubricationlevel,int(m))
            time.sleep(2)
            lubricationlevel = int(m)
            xyz = "machine is lubricated upto "+ m + "  % "
            recentactpublish(xyz)
            publishdata()
        
    else:
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        msgadmin = date_time + '  '+m
        publishdata()

    
def publishdata():
    global stats
    if(lubricationlevel>=80):
        stats = "HIGH"
    elif(lubricationlevel>=50 and lubricationlevel<80):
        stats = "FINE"
    elif(lubricationlevel>=20 and lubricationlevel<50):
        stats = "LOW"
    elif(lubricationlevel<20):
        stats = "VERY LOW"
        
    myData = {'Lubricationlevel':lubricationlevel,'Pumplevel':lubinpump,'Stats':stats,'Recentactiv':activity,'msgfromadmin':msgadmin,'er':error}
    response = service.post_document(db='lubrication_pump_data', document=myData).get_result()
    client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=None)
    print("Published data Successfully: ", myData)
    




def recentactpublish(recact):
    global msg
    global activity
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    msg = recact
    activity = date_time+" -> "+msg
    
    
    
    

        
client = wiotp.sdk.device.DeviceClient(config=myConfig, logHandlers=None)
client.connect()

while True:
    client.commandCallback = myCommandCallback
    publishdata()
    time.sleep(10)
    lubricationlevel = random.randint(0,100)
    error = None

    

client.disconnect()
       
    
    
