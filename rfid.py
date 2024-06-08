import serial
import csv
import pandas as pd
from datetime import datetime as dt
from datetime import time, date, timedelta
data2 = {
    "Card ID": ["84 B8 C8 72"],
    "Permission": ['Owner'],
    "User": ["Owner1"],
    "Last Used": [dt.now()-timedelta(days=20)]
}

'''with open('whitelist.csv', mode = 'w', newline = '') as file1:
    writer = csv.writer(file1)
    writer.writerows(data)
'''    
df = pd.DataFrame(data2)
df = df.set_index("Card ID")

def update(uid, name, df):
    df.loc[uid, "User"] = name
    
    #df.loc[uid, "Last Used"] = dt.now()
    #print(df.loc[uid, "User"] + " added")
    df.to_csv('whitelist.csv')

update("84 B8 C8 72", "Keith Yu", df)

def card_check(df): #use to control access
    print("Tap Card")
    ser = serial.Serial('COM4', 9600)
    #time.sleep(2)
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if "UID" in line:
                        id = str(line.split(": ")[1]).strip().upper()
                        if id in df.index:
                            in_df = True
                            user_info = df.loc[id]
                            if (dt.now() - df.loc[id, 'Last Used']).days > 30:
                                print("Card expired")
                                time = False
                            else:
                                df.loc[id, "Last Used"] = dt.now()
                                df.to_csv('whitelist.csv')
                                print(user_info.to_string() + "\nCard recognized, access granted")
                                time = True
                        else:
                            in_df = False
                            print("Card not recognized")
                        if (in_df == True) and (time == True):
                            ser.write(b"ACCESS GRANTED\n")
                        else:
                            ser.write(b"ACCESS DENIED\n")
            except serial.SerialException as e:
                #print(f"Serial communication error: {e}")
                break  # Exit the loop and try to reinitialize the serial connection
            except Exception as e:
                print(f"Unexpected error: {e}")
                ser.close()
    except KeyboardInterrupt:
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
                        id = str(line.split(": ")[1]).strip().upper()
                        if id in df.index:
                            print("Card already in system")
                            answer = input("Update card? (y/n) ")
                            if answer.lower() == 'y':
                                update = input("Name or Permission").upper()
                                if update == "NAME":
                                    df.loc[id, 'User'] = input("New name? ")
                                    print(df[id])
                                    ser.close()
                                elif update == "PERMISSION":
                                    df.loc[id, 'Permission'] = input("New permissions? ")
                                    print(df[id])
                                    ser.close()
                                else: 
                                    print("Answer not detected, try again")
                                    break
                            if answer.lower() == 'n':
                                print("Try different card")
                                break
                        else:
                            print("Card not in system")
                            answer = input("Add card? (y/n) ")
                            if answer.lower() == 'y':
                                df.loc[id, 'User'] = input("Name? ")
                                df.loc[id, 'Permission'] = input("Permissions? ")
                                df.loc[id, 'Last Used'] = dt.now()
                                print("User " + df.loc[id, 'User'] + " added")
                                ser.close()
                            elif answer.lower() == 'n':
                                print("OK try something else")
            except serial.SerialException as e:
                #print(f"Serial communication error: {e}")
                break  # Exit the loop and try to reinitialize the serial connection
            except Exception as e:
                print(f"Unexpected error: {e}")
                ser.close()
    except KeyboardInterrupt:
        print("Exiting Program")
        ser.close()



#while True:
card_check(df)
#add_update(df)
#df.to_csv('whitelist.csv')