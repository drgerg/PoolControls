### Dependencies required to make poolApp.py work

Flask - python3 module.  Flask is a lightweight WSGI web application framework.

>```pip3 install -U Flask```

flask_wtf - Python3 module.  Simple integration of Flask and WTForms, including CSRF, file upload, and reCAPTCHA.

>```pip3 install flask_wtf```

There are more modules that are not yet listed here.  
I'm just now getting this up to date (10/31/19).  Check the 'import' statements for clues.

For the graphing function (still under development), these are needed:

matplotlib - Matplotlib is a Python 2D plotting library which produces publication quality figures in a variety of hardcopy formats.

>```sudo pip3 install matplotlib```

I'm using python3 on Raspbian Buster.  So for some reason I need to uninstall numpy and reinstall a special version.

>```sudo pip3 uninstall numpy```<br>
>```sudo pip3 install python3-numpy```

That's what I know today.


