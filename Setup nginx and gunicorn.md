# Setup nginx and gunicorn 

These instruction assume Flask is already installed and configured.  Flask comes with a development WSGI server built-in, but it will complain if you are using it to run your app on port 80.
I am condensing instructions I found on the web here: [www.e-tinkers.com](https://www.e-tinkers.com/2018/08/how-to-properly-host-flask-application-with-nginx-and-guincorn/)

```sudo apt-get update```

If you have anything using port 80, you'll want to stop it.  I had my existing poolctl.service running with Flask and Werkzeug, it's built-in WSGI application library.  I kept getting errors at the end of the 'apt-get install nginx' process until I finally stopped long enough to read the screen and realize that systemctl was trying to start nginx and port 80 was in use by my poolctl app.

So . . . I needed to use this:

```sudo systemctl stop poolctl```

Once I did that, port 80 was released and the installation of nginx could complete.

#### Continue installing the packages

```sudo apt-get install ngnix```

```sudo apt-get install gunicorn```

#### Makes edits to /etc/nginx/nginx.conf

```sudo nano /etc/nginx/nginx.conf```

Once in there, look for these entries and make them look like this, character for character, no # in front:  (All this comes from e-tinkers linked above.)

    multi_accept on;
    keepalive_timeout 30;
    server_tokens off; 
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 5;