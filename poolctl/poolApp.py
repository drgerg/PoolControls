#!/usr/bin/env python3

# poolApp.py

# Adapted by Greg Sanders August 2019 to run a Elegoo 8 channel relay module to control pool equipment.
#     Adapted from:
#        Inspired by an adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson
#        as modified by Rui Santos
   


import RPi.GPIO as GPIO
import os, pickle, re, time, requests, sys, logging, traceback, subprocess, poolGetSensors,configparser,signal,threading
from collections import OrderedDict
from flask import Flask, render_template, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, BooleanField, StringField, IntegerField, SubmitField, validators
from wtforms.validators import Length, DataRequired, NumberRange
from graph import build_graph
from poolGetSQL import dataGrab

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d341f27d241f27567d241f4b6176a'
#
## Get the HOME environment variable
#
poolAppHome = os.path.abspath(os.path.dirname(__file__))

#
## ConfigParser init area.  Get some info out of 'poolApp.conf'.
#
config = configparser.RawConfigParser()
config.read(poolAppHome + '/poolApp.conf')
#
## End ConfigParser init
#
logger = logging.getLogger(__name__)
logging.basicConfig(filename=poolAppHome + '/poolApp.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
logger.info(" - - - - poolApp.py DATA LOGGING STARTED - - - - ")

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# We have some extra relays.  Pin 17 is Relay1, pin 25 is Relay7, and pin 6 is Relay8.
# We need to set them up, then set them HIGH to turn them off.
GPIO.setup(17, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)
GPIO.output(25, GPIO.HIGH)
GPIO.output(6, GPIO.HIGH)
##
####  PINS PICKLE
##
# Check for a 'CurrentState.pkl' file.  If one exists, load it.
if os.path.isfile(poolAppHome + '/CurrentState.pkl'):
   Spins = pickle.load(open(poolAppHome + '/CurrentState.pkl', 'rb'))
# Otherwise:   
# Create a dictionary called pins to store the pin number, name, and pin state:
else:
   pins = {
       18 : {'sort' : '1', 'name' : 'Pump Step 1', 'state' : GPIO.HIGH},
       22 : {'sort' : '2', 'name' : 'Pump Step 2', 'state' : GPIO.HIGH},
       23 : {'sort' : '3', 'name' : 'Pump Step 3', 'state' : GPIO.HIGH},
       5 : {'sort' : '4', 'name' : 'Pump Override', 'state' : GPIO.HIGH},
       24 : {'sort' : '5', 'name' : 'Pool Lights', 'state' : GPIO.HIGH},
       25 : {'sort' : '6', 'name' : 'WeathPi Reset', 'state' : GPIO.HIGH}
       
       }
   Spins = OrderedDict(sorted(pins.items(), key=lambda kv: kv[1]['sort']))
   
 # Save the current status of all pins to a .pkl file.
   pickle.dump(Spins, open(poolAppHome + '/CurrentState.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)
##
#### SCHEDULE PICKLE
##
if os.path.isfile(poolAppHome + '/CurrentSched.pkl'):
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
else:
   # Create a Schedule times dictionary:
   sched1 = {
      1 : {'name' : 'Pump Step 1', 'time' : '1600', 'action' : 'on'},
      2 : {'name' : 'Pump Step 2', 'time' : '1300', 'action' : 'on'},
      3 : {'name' : 'Pump Step 3', 'time' : '2200', 'action' : 'on'},
      4 : {'name' : 'Pump Override', 'time' : '0000', 'action' : 'on'},
      5 : {'name' : 'Pool Lights', 'time' : '2000', 'action' : 'on'},
      6 : {'name' : 'Pool Lights', 'time' : '0700', 'action' : 'off'}
   }
# Save the current schedule to our .pkl file.
pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)
##
###    WORK WITH CRON TO RUN THE SCHEDULE
# 
##   EDIT /ETC/RSYSLOG.CONF to prevent spamming /var/log/syslog  ##
#
# *.*;auth,authpriv.none     -/var/log/syslog
# to
# *.*;cron,auth,authpriv.none     -/var/log/syslog
# within /etc/rsyslog.conf and then restart syslog
#
##    ADD AN ENTRY TO CRONTAB  "me@mymachine:~ $sudo crontab -e" ##
#
# m h  dom mon dow   command
# * * * * * /usr/bin/curl -X GET http://localhost/cron/run/
#
###
@app.route("/cron/run/", methods=['POST', 'GET'])
def schdCheck():
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   locTime = time.localtime()
   locTimeStr = str(locTime.tm_hour).rjust(2, '0')+str(locTime.tm_min).rjust(2, '0')
#    logger.info("CurrentSched.pkl was opened. locTimeStr is:" + locTimeStr + '.')
   # print(locTimeStr)
   for t in sched1:
      tt = str(sched1[t]['time'])
    #   logger.info(str("t is: " + str(t) + " and tt is: " + tt + '.'))
      if tt == locTimeStr:
         tName = sched1[t]['name']
        #  logger.info('Schedule' + str(sched1[t]) + 'triggered.')
         tAction = sched1[t]['action']
         for p in Spins:
            if Spins[p]['name'] == tName:
               getPin = str(p)
               logger.info(locTimeStr + ": Scheduled action: " + tName + " set to " + tAction + ". Pin " + getPin)
               action(getPin,tAction)
   return "OK", 200

##
####  PINS INITIAL SETUP
##
# Set each pin as an output and make it high (high = off):
for pin in Spins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, Spins[pin]['state'])
#
## THESE BLOCKS THAT START WITH A '@app.route()' LINE ARE CALLED 'VIEWS'
## THIS BLOCK OF CODE DETERMINES WHAT HAPPENS WHEN A BROWSER REQUESTS A CERTAIN URL
## THIS ONE IS FOR THE ROOT, WHAT WE USED TO THINK OF AS 'INDEX.HTML'
#

@app.route('/')
def main():
   # Retrieve previous state settings from the .pkl file.
   Spins = pickle.load(open(poolAppHome + '/CurrentState.pkl', 'rb'))
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in Spins:
      Spins[pin]['state'] = GPIO.input(pin)
   #
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      #'schedTimes' : schedTimes,
      'sched1' : sched1,
      'pins' : Spins
      }
   # 
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)
#
## SET UP FOR THE STATS VIEW
#
@app.route('/stats/')
def stats():
   ## Get the temperature from the 1-Wire probes
   cpuTemp = poolGetSensors.cpuTemp()[1]
   probe1Temp = poolGetSensors.getTemp('probe1')[1]
   probe2Temp = poolGetSensors.getTemp('probe2')[1]
   #probe3Temp = poolGetSensors.getTemp('probe3')[1]
   # 
   # Put the various temps dictionary into the template data dictionary:
   #
   templateData = {
      'cpuTemp' : cpuTemp,
      'probe1Temp' : probe1Temp,
      'probe2Temp' : probe2Temp
    #  'probe3Temp' : probe3Temp
      }
   # 
   # Pass the template data into the template main.html and return it to the user
   return render_template('stats.html', **templateData)
#
## GENERATE THE GRAPHS FROM TEMP DATA
#
@app.route('/graphs/', methods=['POST', 'GET'])
def graphs():
    app.config['WTF_CSRF_ENABLED'] = False
    form = inputGraphDays()
    gsr = config.get('mySQL','LogFreq')
    GD = 0
    if request.method == 'POST' and form.validate():   
      returnGD = request.form.get('graphDays')
      flash("Entry: " + str(returnGD))
      GD = returnGD
    elif request.form.get('graphDays') != None:
      returnGD = request.form.get('graphDays')
      flash(form.graphDays.errors)
      flash("Your entry was: " + str(returnGD))
    pass
    x1 = dataGrab(GD)[0]
    x2 = dataGrab(GD)[1]
    rn = dataGrab(GD)[2]
    lp1t = dataGrab(GD)[3]
    lp2t = dataGrab(GD)[4]
    x3 = dataGrab(GD)[5]
    #laitb = dataGrab(GD)[6]
   
    graph1_url = build_graph(x1, x2, x3)
    #graph2_url = build_graph(x2,y2)
    #graph3_url = build_graph(x3,y3)
    
    return render_template('graphs.html',
    graph1=graph1_url,
    GD=GD,
    x1=x1,
    x2=x2,
    x3=x3,
    rn=rn,
    gsr=gsr,
    lp1t=lp1t,
    lp2t=lp2t,
    form=form)
    #laitb=laitb)
    #graph2=graph2_url,
    #graph3=graph3_url)
 
#
## SET UP THE FORM 
#
 
class inputSchedTime1(FlaskForm):
   schedTime1 = StringField(label='sched1', validators=[Length(min=0, max=4, message='Entry can only be exactly four digits.')])
   go1 = SubmitField(label = 'GO', id = '1')

class inputSchedTime2(FlaskForm):
   schedTime2 = StringField(label='sched2', validators=[Length(min=0, max=4, message='Entry can only be exactly four digits.')])
   go2 = SubmitField(label = 'GO', id = '2')
     
class inputSchedTime3(FlaskForm):
   schedTime3 = StringField(label='sched3', validators=[Length(min=0, max=4, message='Entry can only be exactly four digits.')])
   go3 = SubmitField(label = 'GO', id = '3')

class inputSchedTime4(FlaskForm):
   schedTime4 = StringField(label='sched4', validators=[Length(min=0, max=4, message='Entry can only be exactly four digits.')])
   go4 = SubmitField(label = 'GO', id = '4')

class inputSchedTime5(FlaskForm):
   schedTime5 = StringField(label='sched5', validators=[Length(min=0, max=4, message='Entry can only be exactly four digits.')])
   go5 = SubmitField(label = 'GO', id = '5')

class inputSchedTime6(FlaskForm):
   schedTime6 = StringField(label='sched6', validators=[Length(min=0, max=4, message='Entry can only be exactly four digits.')])
   go6 = SubmitField(label = 'GO', id = '6')

class inputGraphDays(FlaskForm):
   graphDays = StringField(label='graphDays', validators=[Length(min=0, max=3)])
   graphGo = SubmitField(label = 'GO', id = '7')
   

@app.route('/2/', methods=['POST', 'GET'])
def page2():
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'sched1' : sched1,
      'pins' : Spins
      }
   
   # Pass the template data into the template main.html and return it to the user
   return render_template('2.html', **templateData)
##
#####  SCHED 1  #####
##
@app.route('/schdChng1/', methods = ['POST', 'GET'])
def schdChng1():
   app.config['WTF_CSRF_ENABLED'] = False
   form = inputSchedTime1()
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   if request.method == 'POST' and form.validate():   
      returnText = request.form.get('schedTime1')
      returnName = request.form.get('selName')
      returnAct = request.form.get('selAct')
      flash("Entry: " + str(returnText) + " : " + str(returnName) + " : " + str(returnAct))
      sched1[1]['time'] = returnText
      sched1[1]['name'] = returnName
      sched1[1]['action'] = returnAct
      logger.info('Schedule slot 1 is now ' + str(returnText) + " : " + str(returnName) + " : " + str(returnAct) + '.')
   elif request.form.get('schedTime1') != None:
      returnText = request.form.get('schedTime1')
      flash(form.schedTime1.errors)
      flash("Your entry was: " + str(returnText))
   pass
   templateData = {
      'sched1' : sched1,
      'pins' : Spins,
      'form' : form
      }
   # Save the current schedule to our .pkl file.
   pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)
   return render_template('schdChng1.html', **templateData)
##
#####  SCHED 2  #####
##   
@app.route('/schdChng2/', methods = ['POST', 'GET'])
def schdChng2():
   app.config['WTF_CSRF_ENABLED'] = False
   form = inputSchedTime2()
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   if request.method == 'POST' and form.validate():   
      returnText = request.form.get('schedTime2')
      returnName = request.form.get('selName')
      returnAct = request.form.get('selAct')
      flash("Entry: " + str(returnText) + " : " + str(returnName) + " : " + str(returnAct))
      sched1[2]['time'] = returnText
      sched1[2]['name'] = returnName
      sched1[2]['action'] = returnAct
      logger.info('Schedule slot 2 is now ' + str(returnText) + " : " + str(returnName) + " : " + str(returnAct) + '.')
   elif request.form.get('schedTime2') != None:
      returnText = request.form.get('schedTime2')
      flash(form.schedTime2.errors)
      flash("Your entry was: " + str(returnText))
   pass
   templateData = {
      'sched1' : sched1,
      'pins' : Spins,
      'form' : form
      }
   # Save the current schedule to our .pkl file.
   pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)   
   return render_template('schdChng2.html', **templateData)
##
#####  SCHED 3  #####
##   
@app.route('/schdChng3/', methods = ['POST', 'GET'])
def schdChng3():
   app.config['WTF_CSRF_ENABLED'] = False
   form = inputSchedTime3()
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   if request.method == 'POST' and form.validate():   
      returnText = request.form.get('schedTime3')
      returnName = request.form.get('selName')
      returnAct = request.form.get('selAct')
      flash("Entry: " + str(returnText) + " : " + str(returnName) + " : " + str(returnAct))
      sched1[3]['time'] = returnText
      sched1[3]['name'] = returnName
      sched1[3]['action'] = returnAct
      logger.info('Schedule slot 3 is now ' + str(returnText) + " : " + str(returnName) + " : " + str(returnAct) + '.')
   elif request.form.get('schedTime3') != None:
      returnText = request.form.get('schedTime3')
      flash(form.schedTime3.errors)
      flash("Your entry was: " + str(returnText))
   pass
   templateData = {
      'sched1' : sched1,
      'pins' : Spins,
      'form' : form
      }
   # Save the current schedule to our .pkl file.
   pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)   
   return render_template('schdChng3.html', **templateData)
##
#####  SCHED 4  #####
##   
@app.route('/schdChng4/', methods = ['POST', 'GET'])
def schdChng4():
   app.config['WTF_CSRF_ENABLED'] = False
   form = inputSchedTime4()
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   if request.method == 'POST' and form.validate():   
      returnText = request.form.get('schedTime4')
      returnName = request.form.get('selName')
      returnAct = request.form.get('selAct')
      flash("Entry: " + str(returnText) + " : " + str(returnName) + " : " + str(returnAct))
      sched1[4]['time'] = returnText
      sched1[4]['name'] = returnName
      sched1[4]['action'] = returnAct
      logger.info('Schedule slot 4 is now ' + str(returnText) + " : " + str(returnName) + " : " + str(returnAct) + '.')
   elif request.form.get('schedTime4') != None:
      returnText = request.form.get('schedTime4')
      flash(form.schedTime4.errors)
      flash("Your entry was: " + str(returnText))
   pass
   templateData = {
      'sched1' : sched1,
      'pins' : Spins,
      'form' : form
      }
   # Save the current schedule to our .pkl file.
   pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)   
   return render_template('schdChng4.html', **templateData)
##
#####  SCHED 5  #####
##   
@app.route('/schdChng5/', methods = ['POST', 'GET'])
def schdChng5():
   app.config['WTF_CSRF_ENABLED'] = False
   form = inputSchedTime5()
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   if request.method == 'POST' and form.validate():   
      returnText = request.form.get('schedTime5')
      returnName = request.form.get('selName')
      returnAct = request.form.get('selAct')
      flash("Entry: " + str(returnText) + " : " + str(returnName) + " : " + str(returnAct))
      sched1[5]['time'] = returnText
      sched1[5]['name'] = returnName
      sched1[5]['action'] = returnAct
      logger.info('Schedule slot 5 is now ' + str(returnText) + " : " + str(returnName) + " : " + str(returnAct) + '.')
   elif request.form.get('schedTime5') != None:
      returnText = request.form.get('schedTime5')
      flash(form.schedTime5.errors)
      flash("Your entry was: " + str(returnText))
   pass
   templateData = {
      'sched1' : sched1,
      'pins' : Spins,
      'form' : form
      }
   # Save the current schedule to our .pkl file.
   pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)   
   return render_template('schdChng5.html', **templateData)
##
#####  SCHED 6  #####
##   
@app.route('/schdChng6/', methods = ['POST', 'GET'])
def schdChng6():
   app.config['WTF_CSRF_ENABLED'] = False
   form = inputSchedTime6()
   sched1 = pickle.load(open(poolAppHome + '/CurrentSched.pkl', 'rb'))
   if request.method == 'POST' and form.validate():   
      returnText = request.form.get('schedTime6')
      returnName = request.form.get('selName')
      returnAct = request.form.get('selAct')
      flash("Entry: " + str(returnText) + " : " + str(returnName) + " : " + str(returnAct))
      sched1[6]['time'] = returnText
      sched1[6]['name'] = returnName
      sched1[6]['action'] = returnAct
      logger.info('Schedule slot 6 is now ' + str(returnText) + " : " + str(returnName) + " : " + str(returnAct) + '.')
   elif request.form.get('schedTime6') != None:
      returnText = request.form.get('schedTime6')
      flash(form.schedTime6.errors)
      flash("Your entry was: " + str(returnText))
   pass
   templateData = {
      'sched1' : sched1,
      'pins' : Spins,
      'form' : form
      }
   # Save the current schedule to our .pkl file.
   pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'wb+'), pickle.HIGHEST_PROTOCOL)   
   return render_template('schdChng6.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   deviceName = Spins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin low. Toggle low pins high to keep only one low:
      if changePin == 5:
         GPIO.output(18, GPIO.HIGH)
         GPIO.output(22, GPIO.HIGH)
         GPIO.output(23, GPIO.HIGH)
         GPIO.output(5, GPIO.LOW)
      if changePin == 18:
         GPIO.output(5, GPIO.HIGH)
         GPIO.output(22, GPIO.HIGH)
         GPIO.output(23, GPIO.HIGH)
         GPIO.output(18, GPIO.LOW)
      if changePin == 22:
         GPIO.output(18, GPIO.HIGH)
         GPIO.output(5, GPIO.HIGH)
         GPIO.output(23, GPIO.HIGH)
         GPIO.output(22, GPIO.LOW)
      if changePin == 23:
         GPIO.output(18, GPIO.HIGH)
         GPIO.output(22, GPIO.HIGH)
         GPIO.output(5, GPIO.HIGH)
         GPIO.output(23, GPIO.LOW)
      if changePin == 24:
         GPIO.output(24, GPIO.LOW)
      message = "Turned " + deviceName + " on."

   if action == "off":
      GPIO.output(changePin, GPIO.HIGH)
      message = "Turned " + deviceName + " off."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in Spins:
      Spins[pin]['state'] = GPIO.input(pin)
   logger.info(deviceName + ' set to ' + action + '.')
   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      #'schedTimes' : schedTimes,
      'message' : message,
      'sched1' : sched1,
      'pins' : Spins
   }
   pickle.dump(Spins, open(poolAppHome + '/CurrentState.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
   # Save the current schedule to our .pkl file.
   pickle.dump(sched1, open(poolAppHome + '/CurrentSched.pkl', 'ab+'), pickle.HIGHEST_PROTOCOL)
   return render_template('main.html', **templateData)

#
## WeatherPi Reset using Pin 25 (relay 7)
#
@app.route('/reset/', methods=['POST', 'GET'])
def reset():
    GPIO.output(25, GPIO.LOW)
    time.sleep(.5)
    GPIO.output(25, GPIO.HIGH)
    message = 'Performed hard reset of WeatherPi.'
    logger.info('Performed hard reset of WeatherPi.')
#    templateData = {
#        'message' : message
#    }
    return message
#    return render_template('reset.html', **templateData)

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    else:
        sigStr = str(signal)
    logger.info("SignalHandler invoked by signal: " + sigStr + '.')
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - poolApp.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system  


if __name__ == "__main__":
#    app.run(host='0.0.0.0')
   #app.run(host='0.0.0.0', port=5010, debug=True)
   #app.run(host='192.16.1.10', port=80)


    # if argsTest.debug:
    #     logging.basicConfig(filename=TestHome + '/test.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    #     logging.info("Debugging output enabled")
    # else:
    #     logging.basicConfig(filename=TestHome + '/test.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - poolApp.py STARTED FROM COMMANDLINE WITH DATA LOGGING- - - - ")
    print('Logger info')
    # #
    # signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    # signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
        app.run(host='0.0.0.0')
        pass
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - poolApp.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")