import sqlite3
import time
import datetime
import sys
import os

myConnection = None
myCursor = None
msgType = ["INFO","ERROR"]

dbName = "allData"
dbTable = "allData"  #messedupSomewhere!

# current time for logging
def getTime():
    ts = time.time()
    dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d|%H:%M:%S|%f')
    return dt

def msg(type,method,message):
    print(getTime()+"|"+msgType[type]+"|"+str(os.getpid())+"|"+method+"|"+message) 

# intiate DB connection
# returns 1 for success and 0 for failure
def startConnection():
    global myCursor, myConnection
    isSuccess = 0;
    msg(0,"START_DB","Creating connection to " + dbName + "." + dbTable)
    try:
        myConnection = sqlite3.connect('db/' + dbName)
        myCursor = myConnection.cursor()
        isSuccess = 1
        msg(0,"START_DB","Successful connected to " + dbName + "." + dbTable)
    except:
        msg(1,"START_DB","Failed to connected to " + dbName + "." + dbTable)

    return isSuccess


# stopping DB connection
# returns 1 for success and 0 for failure
def stopConnection():
    global myCursor, myConnection
    opType="STOP_DB"
    isClosed = 0;
    msg(0,opType,"Closing connection to " + dbName + "." + dbTable)
    try:
        myConnection.close()
        myConnection = None
        myCursor = None
        isClosed = 1
        msg(0,opType,"Connection closed to " + dbName + "." + dbTable)
    except:
        msg(1,opType,"Failed to close connection to " + dbName + "." + dbTable)
    return isClosed


# get the value of a given key
# returns retFlags,values
# retFlags
# 	0  - if key present
# 	1  - if key not present
# 	-1 - failure
def get(key):
    global myCursor, myConnection
    retFlag = 0
    opType="GET"
    if not myCursor:
        startConnection()
    value = ''
    try:
        myCursor.execute("SELECT value from " + dbTable + " where key = '" + key + "'")
        d = myCursor.fetchone()
        if d:
            value = d[0]
            retFlag = 0
            msg(0,opType,"key='" + key + "' found!")
        else:
            retFlag = 1
            msg(0,opType,"key='" + key + "' not found!")
    except:
        retFlag = -1
        print sys.exec_info()
        msg(1,opType,"operation failed for key='" + key + "'!")

    return retFlag, value

# INCOMPLETE
def getAll():
    global myCursor, myConnection

    retFlag = -1
    if not myCursor:
        startConnection()
    value = ''
    #try:
    myCursor.execute("SELECT key,value from " + dbTable)
    print [int(record[0]) for record in myCursor.fetchall()]
    #d = myCursor.fetchone()
    #print d


# inserts/updates the value of a given key
# returns retFlags,oldV
# retFlags
# 	0  - if key present hence updated
# 	1  - if key not present hence inserted
# 	-1 - failure
def put(key, value):
    global myCursor, myConnection
    opType="PUT"
    retFlag = -1
    if not myCursor:
        startConnection()
    try:
        msg(0,opType,"adding key='" + key + "' & value='"+value+"'")
        retFlag, oldV = get(key)
        if retFlag == -1:
            raise
        elif retFlag == 1:
            myCursor.execute("INSERT INTO " + dbTable + " VALUES ('" + key + "','" + value + "')")
            msg(0,opType,"value='"+value+"' insert!")
        else:
            myCursor.execute("UPDATE " + dbTable + " SET value='" + value + "' where key='" + key + "'")
            msg(0,opType,"value updated from '"+oldV+"' to '"+value+"'")
        myConnection.commit()
        msg(0,opType,"successful")
    except:
        msg(1,opType,"failed!")

    return retFlag, oldV


# deletes a key-value pair if found
# returns retFlags,oldV
# retFlags
#       0  - if key present hence deleted
#       1  - if key not present hence not deleted
#       -1 - failure
def delete(key):
    global myCursor, myConnection
    opType="DELETE"
    retFlag=-1
    if not myCursor:
        startConnection()
    try:
        msg(0,opType,"deleting key='" + key + "'")
        retFlag, oldV = get(key)
        if retFlag == -1:
            raise
        elif retFlag == 0:
            myCursor.execute("DELETE FROM " + dbTable + " WHERE key='" + key + "'")
            msg(0,opType,"value='"+oldV+"' deleted!")
        else:
            msg(0,opType,"key to be deleted not found.")
        myConnection.commit()
        msg(0,opType,"successful")
    except:
        msg(1,opType,"failed!")

    return retFlag, oldV

def unit_test():
    #UNIT TEST BELOW!
    print ""
    print "*****      TEST 0 START: starting connection"
    startConnection();
    print "*****      TEST 0 END"
    testKey = getTime()
    print ""
    print "*****      TEST 1 START: adding an new value"
    res, oldV = put(testKey, "newValue")
    print "*****      OUTPUT: ", res
    print "*****      TEST 1 END"
    print ""
    print "*****      TEST 2 START: adding an old value"
    res, oldV = put(testKey, "newValue")
    print "*****      OUTPUT: ", res
    print "*****      TEST 2 END"
    print ""
    print "*****      TEST 3 START: get an value that exist"
    res, value = get("1")
    print("*****      Value for Key=1 is " + value)
    print "*****      OUTPUT: ", res
    print "*****      TEST 3 END"
    print ""
    print "*****      TEST 4 START: get an value that does not exist"
    res, value = get("IdontExist")
    print("*****      Value for Key=IdontExist is " + value)
    print "*****      OUTPUT: ", res
    print "*****      TEST 4 END"
    print ""
    print "*****      TEST 5 START: delete a value that does not exist"
    res, value = delete("IdontExist")
    print("*****      Old Value for Key=IdontExist is " + value)
    print "*****      OUTPUT: ", res
    print "*****      TEST 5 END"
    print ""    
    print "*****      TEST 6 START: delete a value that exists"
    res, value = delete(testKey)
    print("*****      Old Value for Key="+testKey+" is " + value)
    print "*****      OUTPUT: ", res
    print "*****      TEST 6 END"
    print ""  
    print "*****      TEST 7 START: close connection"
    stopConnection();
    print "*****      TEST 7 END"
    print ""
    print "*****      TEST 8 START: get an value that exist with connection closed!"
    res, value = get("1")
    print("*****      Value for Key=1 is " + value)
    print "*****      OUTPUT: ", res
    stopConnection();
    print "*****      TEST 8 END"
    print ""


if __name__ == '__main__':
    unit_test()
