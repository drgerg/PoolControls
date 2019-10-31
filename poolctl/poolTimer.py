#!/usr/bin/env python3
#
""" poolTimer.py - Perform desired functions at desired intervals.
    2019 - Gregory Allen Sanders"""

import os,sys,time,logging,signal,configparser

#
## ConfigParser init area.  Get some info out of working.conf.
#
poolAppHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.RawConfigParser()
config.read(poolAppHome + '/poolApp.conf')
#
## End ConfigParser init

logger = logging.getLogger(__name__)

def timer():
    funNStr = sys._getframe().f_code.co_name
    logger.debug("Started the " + funNStr + " function")
    #site = config.get('Network','Address')
    while True:
        #os.system('wget -O/dev/null -q http://%s/cron/run/'%site)
        #logger.debug('Sent the URL to %s.'%site)
        os.system('wget -O/dev/null -q http://127.0.0.1/cron/run/')
        logger.debug('Sent the URL to 127.0.0.1')
        time.sleep(30)
    return

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
                logging.basicConfig(filename=poolAppHome + '/poolTimer.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("Debugging output enabled")
            else:
                logging.basicConfig(filename=poolAppHome + '/poolTimer.log', format='%(asctime)s - %(message)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing

            signal.signal(signal.SIGINT, SignalHandler)
            logger.info("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
            logger.info("Starting poolTimer . . . ")            
            logger.debug("Top of try")
            timer()
            logger.info("Bottom of try")

        except  ValueError as errVal:
            print(errVal)
            pass
        logger.info("That's all folks.  Goodbye")

