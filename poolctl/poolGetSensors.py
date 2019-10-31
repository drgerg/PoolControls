#!/usr/bin/env python3

""" poolGetSensors.py - (Pool Controls) Query and return the status of the specified sensors.
    2019 - Gregory Allen Sanders"""

import os,sys,argparse,logging,time,signal,configparser


## ConfigParser init area.  Get some info out of 'poolApp.conf'.
#
#poolAppHome = os.getcwd()
poolAppHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.RawConfigParser()
config.read(poolAppHome + '/poolApp.conf')
#
## End ConfigParser init

logger = logging.getLogger(__name__)

logger.debug("\nStart GPIO Setup")

def getTemp(probe):
    #print(probe)
    probeSerial = config['Probes'][probe]
    #print(probeSerial)
    probeName = config['ProbeNames'][probe + 'Name']
    probeAdjust = config['ProbeAdjust'][probe + 'Adjust']
    f = open('/sys/bus/w1/devices/' + probeSerial + '/w1_slave', 'r')
    line = f.readline() # read 1st line
    crc = line.rsplit(' ',1)
    crc = crc[1].replace('\n', '')
    if crc=='YES':
        line = f.readline() # read 2nd line
        gettemp = line.rsplit('t=',1)
        gettemp = gettemp[1]
    else:
        gettemp = 99999
    f.close()
    tempC = (int(gettemp)/1000) + float(probeAdjust)
    tempF = '{:.2f}'.format(float(9/5 * tempC + 32.00))
    probeTemp = probeName +': ' + str(tempC) + '°C' + ' (' + str(tempF) + '°F)'
    #print('Temp: ' + str(tempC))
    return tempC,probeTemp
    #####

def cpuTemp():
# Return CPU temperature as a character string
    ct = os.popen('vcgencmd measure_temp').readline()
    cpuRtn = ct.replace("temp=","").replace("'C\n","")
    temp1=float(cpuRtn)
    temp2= '{:.2f}'.format(float(9/5 * temp1 + 32.00))
    cpuTemp = "CPU: " + str(temp1) + "C" + " (" + str(temp2) + "F)"
    logger.debug(cpuTemp)
    #functionNameAsString = sys._getframe().f_code.co_name
    #logger.debug("Finished the " + functionNameAsString + " function")
    return temp1,cpuTemp


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
        parserGS = argparse.ArgumentParser()
        parserGS.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
        argsGS = parserGS.parse_args()
        if argsGS.debug:
            logging.basicConfig(filename= poolAppHome + '/poolGetSensors.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
            logging.info("Debugging output enabled")
        else:
            logging.basicConfig(filename= poolAppHome + '/poolGetSensors.log', format='%(asctime)s - %(message)s in %(name)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
        #
        ## End Command line arguments parsing

        signal.signal(signal.SIGINT, SignalHandler)
        logger.debug("Top of try")
        logger.info("\n = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =\nStarting up . . . ")
        while True:
            getTemp()
            #main()
        pass
        logger.info("Bottom of try")

    except:
        pass
        logger.info("That's all folks.  Goodbye")

