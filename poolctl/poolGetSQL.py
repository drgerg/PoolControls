#!/usr/bin/env python3
#
""" poolGetSQL.py - Retrieve poolApp.py logged data.
    Maybe this needs to be incorporated into poolSQL.py, I don't know.  Right now it's stand-alone.
    2019 - Gregory Allen Sanders"""

#import os,sys,configparser,logging,time,signal,mysql.connector,poolGetSensors

import os,sys,time,logging,signal,configparser,mysql.connector
from mysql.connector import MySQLConnection, Error
import numpy as np

#
## ConfigParser init area.  Get some info out of working.conf.
#
#poolAppHome = os.getcwd()
poolAppHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.RawConfigParser()
config.read(poolAppHome + '/poolApp.conf')
#
## End ConfigParser init

logger = logging.getLogger(__name__)

def dataGrab():
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Started the " + funNStr + " function")
    dtNow = time.strftime('%Y-%m-%d %H:%M:%S')
    DBhost=config.get('mySQL','Address')
    DBuser=config.get('mySQL','User')
    DBpasswd=config.get('mySQL','Password')
    DBdatabase=config.get('mySQL','Database')
    DBtable=config.get('mySQL','Table')
    mydb = mysql.connector.connect(
        host=DBhost,
        user=DBuser,
        passwd=DBpasswd,
        database=DBdatabase
    )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("select database();")
    dbName = cursor.fetchone()
    logger.debug("Got the database: " + str(dbName))
    ## Grab the last row and get the probe temps AND convert to farenheit.
    cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
    record = cursor.fetchone()
    logger.debug('The last record is number: ' + str(record['id']))
    #print(record['id'])
    lastPt1 = float("{pt1:.2f}".format(pt1=(9/5 * float(record['pt1']) + 32.00)))
    lastPt2 = float("{pt2:.2f}".format(pt2=(9/5 * float(record['pt2']) + 32.00)))
    #lastAir = float("{aitb:.2f}".format(aitb=(9/5 * float(record['aitb']) + 32.00)))
    #print(lastPt1, lastPt2)
    cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where DATE_SUB(CURDATE(), INTERVAL 1 DAY) <= dt")
    recList1 = []
    recList2 = []
    recList3 = []
    for row in cursor:
        recList1.append(float("{pt1:.2f}".format(pt1=(9/5 * float(row['pt1']) + 32.00))))
        recList2.append(float("{pt2:.2f}".format(pt2=(9/5 * float(row['pt2']) + 32.00))))
     #   recList3.append(float("{aitb:.2f}".format(aitb=(9/5 * float(row['aitb']) + 32.00))))
    recNum = cursor.rowcount
    cursor.close()
    mydb.close()
    return recList1, recList2, recNum, lastPt1, lastPt2, recList3 #, lastAir


def SignalHandler(signal, frame):
        logger.info("Cleaning up . . . \n = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
        logger.info("Shutting down gracefully")
        logger.debug("This is SignalHandler")
        logger.info("Displayed .info and .debug in SignalHandler")
        logger.info("Shutdown initiated")
        logger.debug("Wrote to log in SignalHandler")
        sys.exit(0)


if __name__ == "__main__":
        try:
            import argparse

            ## Command line arguments parsing
            #
            parsersm = argparse.ArgumentParser()
            parsersm.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
            argssm = parsersm.parse_args()
            if argssm.debug:
                logging.basicConfig(filename=poolAppHome + '/Test.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("Debugging output enabled")
            else:
                logging.basicConfig(filename=poolAppHome + '/Test.log', format='%(asctime)s - %(message)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing

            signal.signal(signal.SIGINT, SignalHandler)
            logger.debug("Top of try")
            dataGrab()
            logger.info("Bottom of try")

        except  ValueError as errVal:
            print(errVal)
            pass
        logger.info("That's all folks.  Goodbye")

