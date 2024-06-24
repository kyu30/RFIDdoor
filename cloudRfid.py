#Importing libraries used in the code
import serial
import csv
import pandas as pd
from datetime import datetime as dt
from datetime import time, date, timedelta
import requests

API_URL = "https://api2.arduino.cc/iot/v2/things"
CLIENT_ID = "lJh6ANFahQkawhN3nwwy4S5c08kS8PxR"
CLIENT_SECRET = "Dg0OMPPrK3pE4EUqGARTEasWHgky1fqkAhU5CwBuYR2KuCNYJMGyHXIqIccZJJn7"
THING_ID = "d2b0b304-850a-4fa0-82c4-20266a966f74"
PROPERTY_ID = "4d8f01bb-9b77-43d7-b8e2-30078fe11405"
TOKEN_URL = "https://api2.arduino.cc/iot/v1/clients/token"

#Sets up example csv containing information from one card
data2 = {
    "UID": ["84 B8 C8 72"],
    "Permission": ['Owner'],
    "User": ["Owner1"],
    "LastUsed": [dt.now()-timedelta(days=20)] #Used this to test LastUsed range for card
}

df = pd.DataFrame(data2) #Creates a dataframe using the example csv
df = df.set_index("UID")

def get_access_token(client_id, client_secret):
    response = requests.post(TOKEN_URL, data ={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'audience': 'https://api2.arduino.cc/iot'
    })
    return response.json()['access_token']

def set_access(access_token, thing_id, property_id, state):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }
    data = {'value': state}
    url = f"{API_URL}/things/{thing_id}/properties/{property_id}/publish"
    response = requests.put(url, json=data, headers = headers)
    return response.json

def card_check(df): #use to control access
    print("Tap Card")
    ser = serial.Serial('COM5', 9600) #Links to the arduino program's Serial Monitor (info recorded by the Arduino)
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    #time.sleep(2)
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip() #Converts info from Serial Monitor (utf-8) to regular English
                    if "UID" in line: #Runs below code if "UID" is in the Serial Monitor output
                        id = str(line.split(": ")[1]).strip().upper() #Takes the second half of the output (the UID of the RFID card)
                        print(id)
                        if id in df.index: #Runs below code if the UID is in the given dataframe
                            in_df = True #This variable stores whether or not the UID is in the dataframe or not (True/False)
                            user_info = df.loc[id] #Stores all the information associated with the UID in the user_info variable
                            if (dt.now() - df.loc[id, 'LastUsed']).days > 30: #Checks if the last time the card was used was within a month ago
                                print("Card expired") #Card is expired if the last time the card was used was more than a month (30 days) ago
                                time = False #This variable stores whether or not the card expired
                            else:
                                df.loc[id, "LastUsed"] = dt.now() #Sets the new LastUsed to now, saves all new information/overwrites existing
                                                                    #info into a csv/spreadsheet
                                df.to_csv('whitelist.csv')
                                print(user_info.to_string() + "\nCard recognized, access granted") #Writes message to user
                                time = True
                        else:
                            in_df = False
                            print("Card not recognized")
                        if (in_df == True) and (time == True):
                            ser.write(b"ACCESS GRANTED\n") #Tells Arduino to let cardholder if the card isn't expired and is in the dataframe
                        else:
                            ser.write(b"ACCESS DENIED\n")
                        break
            except serial.SerialException as e:
                break  # Exit the loop and try to reinitialize the serial connection
            '''except Exception as e:
                print(f"Unexpected error: {e}")
                ser.close()'''
    except KeyboardInterrupt: #You can exit the program with ctrl+C
        print("Exiting Program")
    ser.close()

#Used these to call functions and test them
card_check(df)
#add_update(df)
#df.to_csv('whitelist.csv')
