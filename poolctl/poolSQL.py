#!/usr/bin/env python3
#
""" poolSQL.py - Manage poolApp.py data logging.
    2019 - Gregory Allen Sanders"""

import os,sys,configparser,logging,time,signal,mysql.connector,poolGetSensors
from mysql.connector import MySQLConnection, Error
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


def mydb():
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Started the " + funNStr + " function")
    P1 = config.get('Probes','Probe1')
    P2 = config.get('Probes','Probe2')
    P3 = config.get('Probes','Probe3')
    logger.debug("Probes: " + P1 + ", " + P2 + " ," + P3)
    t1C,tP1 = poolGetSensors.getTemp('probe1')
    t2C,tP2 = poolGetSensors.getTemp('probe2')
    t3C,tP3 = poolGetSensors.getTemp('probe3')
    ct1,cpuT = poolGetSensors.cpuTemp()
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
    cursor = mydb.cursor()
    cursor.execute("select database();")
    record = cursor.fetchone()
    logger.debug("Got the database: " + str(record))
    try:
        addRecord = ('INSERT INTO ' + DBdatabase + '.' + DBtable + '' \
            ' (dt,pt1,pt2,cput,aitb)' \
            ' VALUES (%s,%s,%s,%s,%s)')
        addData = (dtNow,t1C,t2C,ct1,t3C)
        logger.debug(addRecord %addData)
        cursor.execute(addRecord,addData)
        cursor.execute("SELECT * FROM " + DBdatabase + '.' + DBtable + " where id=(select max(id) from " + DBdatabase + '.' + DBtable + ")")
        record = cursor.fetchone()
        logger.debug('The last record is number: ' + str(record))
        mydb.commit()
        cursor.close()
        mydb.close()
    except Error as error:
        print(error)
        pass
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Finished the " + funNStr + " function")
    #return record

def SignalHandler(signal, frame):
        
        logger.info("Shutting down gracefully")
        #logger.debug("This is SignalHandler")
        logger.debug("Wrote to log in SignalHandler")
        logger.info("That's all, Goodbye . . . ")
        logger.info(" = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
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
                logging.basicConfig(filename=poolAppHome + '/poolSQL.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("Debugging output enabled")
            else:
                logging.basicConfig(filename=poolAppHome + '/poolSQL.log', format='%(asctime)s - %(message)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing

            signal.signal(signal.SIGINT, SignalHandler)
            logger.debug("Top of try")
            while True:
                logger.info(" = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
                logger.info("Starting poolSQL . . . ")
                freq=config.get('mySQL','LogFreq')
                goTime = time.time() + int(freq)
                while True:
                    if time.time() < goTime:
                        time.sleep(1)
                    else:
                        goTime = time.time() + int(freq)
                        mydb()
                        pass
            logger.info("Bottom of try")

        except Error as error:
            print(error)
            pass
            logger.info("That's all folks.  Goodbye")

