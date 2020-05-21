import logging
import pyodbc
import azure.functions as func
import json 
import os

msg_examples = {
    "board1": {
        "timestamp": "20200518",
        "list_devices": {
            "s8": "28",
            "iphonediNic": "48",
            "etc": "10"
        }
    },
    "board2": {
        "timestamp": "20200518",
        "list_devices": {
            "s8": "58",
            "iphonediNic": "18",
            "etc": "5"
        }
    },
    "board3": {
        "timestamp": "20200518",
        "list_devices": {
        }
    },
    "board4": {
        "timestamp": "20200518",
        "list_devices": {
        }
    },
    "board5": {
        "timestamp": "20200518",
        "list_devices": {
        }
    }
}

'''
detect spostamento da 1 a 2
int tempospeso = now-get.id.getroom1
insert vistid room1=te nella table visits
insert current_timestamp in room2 table currentvisits
'''

def get_distance_other_rooms(msg_examples,board,dev):
    min_ = {}
    for b in msg_examples:
        if b == board:
            continue
        else:
            if dev in msg_examples[b]['list_devices']:
                min_[b] =  msg_examples[b]['list_devices'][dev]
    
    return min_

def get_position_devices():
    positions = {}
    for board in msg_examples:
        for dev in msg_examples[board]['list_devices']:
            if dev not in positions:
                distance_other_rooms = get_distance_other_rooms(msg_examples,board,dev)
                if distance_other_rooms != {}:
                    min_room = min(distance_other_rooms.keys(), key=distance_other_rooms.get)
                    if msg_examples[board]['list_devices'][dev] < msg_examples[min_room]['list_devices'][dev]:
                        positions[dev] = board
    return positions



def find_movements(new_positions, previous_positions,timestamp):
    for dev in new_positions:
        if dev in previous_positions:
            if new_positions[dev] != previous_positions[dev]:
                detected_new_room(dev,new_positions[dev],timestamp)
        else:
            detected_new_visitor()

def detected_new_visitor():
    pass

def get_duration():
    #get timestamp of the previous visit from the currentvisit table
    # do the difference betwewen curr_ts and prev_ts = time spent
    # insert value in visits table
    pass

def detected_new_room(dev,new_pos,timestamp):
    #insert the duration of the previous room in the visits table
    dur = get_duration(dev,new_pos)
    insert_row("dbo.Visits",dev,new_pos,dur)
    #insert row in current visit with timestamp to start the counter of the new room
    insert_row("dbo.CurrentVisits",dev,new_pos,timestamp)

def connect_to_db():
    server = 'webappacc.database.windows.net'
    database = 'NextRoom'
    username = 'luigi'
    password = os.environ.get('dbPWD')
    driver= '{ODBC Driver 17 for SQL Server}'
    logging.info("tryng to coonnect")
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    logging.info("connected")
    return cnxn

def insert_row(table,device,room,value):
    #need to manipulate room parameter EX paramter room=board1 --> room1 etc.
    conn = connect_to_db()
    cursor = conn.cursor()
    insert_string = "INSERT INTO " + table + " (" + room + ") "+ "VALUES (?);"
    cursor.execute(insert_string, value)
    try:
        conn.commit()
    except e:
        logging.info("error", e)
    logging.info("row successfully added")
    conn.close()

def query_db(query_string):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query_string)
    row = cursor.fetchone()
    while row:
        print (str(row[0]) + " " + str(row[1]))
        row = cursor.fetchone()
    conn.close()


