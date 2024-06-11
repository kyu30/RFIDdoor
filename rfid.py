#Importing libraries used in the code
import serial
import csv
import pandas as pd
from datetime import datetime as dt
from datetime import time, date, timedelta


#Sets up example csv containing information from one card
data2 = {
    "Card ID": ["84 B8 C8 72"],
    "Permission": ['Owner'],
    "User": ["Owner1"],
    "Last Used": [dt.now()-timedelta(days=20)] #Used this to test last used range for card
}

df = pd.DataFrame(data2) #Creates a dataframe using the example csv
df = df.set_index("Card ID")

def card_check(df): #use to control access
    print("Tap Card")
    ser = serial.Serial('COM4', 9600) #Links to the arduino program's Serial Monitor (info recorded by the Arduino)
    #time.sleep(2)
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip() #Converts info from Serial Monitor (utf-8) to regular English
                    if "UID" in line: #Runs below code if "UID" is in the Serial Monitor output
                        id = str(line.split(": ")[1]).strip().upper() #Takes the second half of the output (the UID of the RFID card)
                        if id in df.index: #Runs below code if the UID is in the given dataframe
                            in_df = True #This variable stores whether or not the UID is in the dataframe or not (True/False)
                            user_info = df.loc[id] #Stores all the information associated with the UID in the user_info variable
                            if (dt.now() - df.loc[id, 'Last Used']).days > 30: #Checks if the last time the card was used was within a month ago
                                print("Card expired") #Card is expired if the last time the card was used was more than a month (30 days) ago
                                time = False #This variable stores whether or not the card expired
                            else:
                                df.loc[id, "Last Used"] = dt.now() #Sets the new Last Used to now, saves all new information/overwrites existing
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
            except serial.SerialException as e:
                break  # Exit the loop and try to reinitialize the serial connection
            '''except Exception as e:
                print(f"Unexpected error: {e}")
                ser.close()'''
    except KeyboardInterrupt: #You can exit the program with ctrl+C
        print("Exiting Program")
    ser.close()

def add_update(df): #Use for adding cards
    print("Tap card")
    ser = serial.Serial('COM4', 9600)
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if "UID" in line:
                        id = str(line.split(": ")[1]).strip().upper() # Same as in the other function
                        if id in df.index:
                            print("Card already in system")
                            answer = input("Update card? (y/n) ") #If the card is already in the dataframe, the user is prompted to choose to update the card or not
                            if answer.lower() == 'y':
                                update = input("Name or Permission").upper() #If user types 'y', they're prompted to choose between updating the name or permission associated with the card
                                if update == "NAME":
                                    df.loc[id, 'User'] = input("New name? ") #If user picks name, they're prompted to type in the new name to be associated with the card
                                    print(df.loc[id]) #Prints updated data for the card
                                    df.to_csv('whitelist.csv') #Adds updated data to the whitelist csv
                                    ser.close()
                                elif update == "PERMISSION":
                                    df.loc[id, 'Permission'] = input("New permissions? ") #If user picks permission, they're prompted to type in the new permission to be associated with the card
                                    print(df.loc[id])
                                    df.to_csv('whitelist.csv')
                                    ser.close()
                                else: 
                                    print("Answer not detected, try again")
                                    break #Ends the program if the user doesn't pick name or permission
                            if answer.lower() == 'n':
                                print("Try different card") #Ends the program if the user doesn't want to update the card
                                break
                        else:
                            print("Card not in system")
                            answer = input("Add card? (y/n) ") #If the card isn't already in the system, the user is prompted to choose to add the card or not
                            if answer.lower() == 'y': #If the user picks 'y', the user is prompted to add name and permission
                                df.loc[id, 'User'] = input("Name? ")
                                df.loc[id, 'Permission'] = input("Permissions? ")
                                df.loc[id, 'Last Used'] = dt.now() #Last used is added automatically
                                print("User " + df.loc[id, 'User'] + " added") #Confirmation message
                                df.to_csv('whitelist.csv')
                                ser.close()
                            elif answer.lower() == 'n':
                                print("OK try something else")
                                break #Ends program if the user doesn't want to add the card
            except serial.SerialException as e:
                break  # Exit the loop and try to reinitialize the serial connection
            '''except Exception as e:
                print(f"Unexpected error: {e}")
                ser.close()'''
    except KeyboardInterrupt:
        print("Exiting Program")
        ser.close()



#Used these to call functions and test them
card_check(df)
#add_update(df)
#df.to_csv('whitelist.csv')