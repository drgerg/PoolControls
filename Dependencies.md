### Dependencies required to make poolApp.py work

Flask - python3 module.  Flask is a lightweight WSGI web application framework.

>```sudo pip3 install -U Flask```

flask_wtf - Python3 module.  Simple integration of Flask and WTForms, including CSRF, file upload, and reCAPTCHA.

>```sudo pip3 install flask_wtf```

There are more modules that are not yet listed here.  
I'm just now getting this up to date (10/31/19).  Check the 'import' statements for clues.

For the graphing function (still under development), these are needed:

matplotlib - Matplotlib is a Python 2D plotting library which produces publication quality figures in a variety of hardcopy formats.

>```sudo pip3 install matplotlib```

That's what I know today.

#### RTC-Nano Real-time Clock module

[Sunfounder Wiki](http://wiki.sunfounder.cc/index.php?title=RTC-Nano )

The RTC-Nano is a small very inexpensive RealTime Clock for the RPi.  I consider it a requirement, as it keeps the clock honest amid random reboots.  [Amazon link](https://www.amazon.com/gp/product/B00HF4NUSS/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)

The module plugs on the first 5 pins of the 40-pin header.  [Here's a graphic](./Pics/Rtc_raspberry.png) from the Sunfounder wiki. The pins are 3.3V, (2) I2C pins, GPIO 4, and GND.  Follow the wiki to get everything in place to support this little guy.

#### Adafruit DS3231 Precision RTC Breakout [ADA3013]

The blurb says, "This Real Time Clock (RTC) is the most precise you can get in a small, low power package."

I realized the RTC-Nano would eventually have to be replaced because the backup battery is soldered in place.  This clock is apparently much more accurate, and has a replaceable battery, so I'm opting to use this one in my projects from now on.  You can find them on Amazon which saves you shipping if you're a Prime member.  Otherwise, look at Adafruit.com.

