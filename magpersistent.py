import sqlite3 as lite
import sys
import os
##import MySQLdb as mdb

class MagDB:

    def createAllTables(self):
        raise NotImplementedError( "Should have implemented this" )

    def setInfoStation(self,user,psw,ipaddr,staid,name,lon,lat,alti):
        raise NotImplementedError( "Should have implemented this" )

    def getInfoStation(self):
        raise NotImplementedError( "Should have implemented this" )
    
    def close(self):
        raise NotImplementedError( "Should have implemented this" )

class MagclDB(MagDB):
    def __init__(self):
        if not os.path.isdir('db'):
            os.makedirs('db')
        self.conn = lite.connect('db/magdb.db')

    def close(self):
        self.conn.close()
        
    def createAllTables(self):
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS magclstation")
        cur.execute("CREATE TABLE magclstation(staid INTEGER, kode TEXT, nama TEXT,ipaddr TEXT,bujur INTEGER,lintang INTEGER, alti REAL)")
        cur.execute("DROP TABLE IF EXISTS magclstatus")
        cur.execute("CREATE TABLE magclstatus(waktu DATETIME,file TEXT,status INTEGER)")

    def getInfoStation(self):
        pass
    
    def setInfoStation(self,user,psw,ipaddr,staid,name,lon,lat,alti):
        pass

class MagsrvDB(MagDB):
    def __init__(self):
        pass

    def close(self):
        self.conn.close()
        
    def createAllTables(self):
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS stations")
        cur.execute("CREATE TABLE stations(staid INTEGER, kode TEXT, nama TEXT, ipaddr TEXT, bujur INTEGER, lintang INTEGER, alti REAL)")
        cur.execute("DROP TABLE IF EXISTS status")
        cur.execute("CREATE TABLE status(waktu DATETIME,staid INTEGER,file TEXT,status INTEGER)")

    
##con = None
##
##try:
##    con = lite.connect('test.db')
##    
##    cur = con.cursor()    
##    cur.execute('SELECT SQLITE_VERSION()')
##    
##    data = cur.fetchone()
##    
##    print "SQLite version: %s" % data                
##    
##except lite.Error, e:
##    
##    print "Error %s:" % e.args[0]
##    sys.exit(1)
##    
##finally:
##    
##    if con:
##        con.close()
