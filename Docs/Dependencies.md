# Dependencies required to make poolApp.py work

Flask - python3 module.  Flask is a lightweight WSGI web application framework.

>```sudo pip3 install -U Flask```

flask_wtf - Python3 module.  Simple integration of Flask and WTForms, including CSRF, file upload, and reCAPTCHA.

>```sudo pip3 install flask_wtf```

There are more modules that are not yet listed here.  
I'm just now getting this up to date (10/31/19).  Check the 'import' statements for clues.

For the graphing function (still under development), these are needed:

matplotlib - Matplotlib is a Python 2D plotting library which produces publication quality figures in a variety of hardcopy formats.

>```sudo pip3 install matplotlib```

I had issues with numpy, however.  The fix was to uninstall the version matplotlib installed and do it differently.

>```sudo pip3 uninstall numpy```

followed by

>```sudo apt-get install python3-numpy```

That seems to solve that issue.  More data here: [numpy.org](https://numpy.org/devdocs/user/troubleshooting-importerror.html)

That's what I know today.

#### Adafruit DS3231 Precision RTC Breakout [ADA3013]

The blurb says, "This Real Time Clock (RTC) is the most precise you can get in a small, low power package."

I realized the Sunfounder RTC-Nano would eventually have to be replaced because the backup battery is soldered in place.  This clock is apparently much more accurate, and has a replaceable battery, so I'm opting to use this one in my projects from now on.  You can find them on Amazon which saves you shipping if you're a Prime member.  Otherwise, look at Adafruit.com.

