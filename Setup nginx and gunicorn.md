# Setup nginx and gunicorn 

These instruction assume Flask is already installed and configured.  Flask comes with a development WSGI server built-in, but it will complain if you are using it to run your app on port 80.
I am condensing instructions I found on the web here: [www.e-tinkers.com](https://www.e-tinkers.com/2018/08/how-to-properly-host-flask-application-with-nginx-and-guincorn/)

```sudo apt-get update```

If you have anything using port 80, you'll want to stop it.  I had my existing poolctl.service running with Flask and Werkzeug, its built-in WSGI application library.  I kept getting errors at the end of the 'apt-get install nginx' process until I finally stopped long enough to read the screen and realize that systemctl was trying to start nginx and port 80 was in use by my poolctl app.

So . . . I needed to use this:

```sudo systemctl stop poolctl```

Once I did that, port 80 was released and the installation of nginx could complete.

#### Continue installing the packages

```sudo apt-get install ngnix```

```sudo apt-get install gunicorn```

#### Makes edits to /etc/nginx/nginx.conf

```sudo nano /etc/nginx/nginx.conf```

Once in there, look for these various entries and make them look like this, character for character, no # in front:  (All this comes from e-tinkers linked above.)

    multi_accept on;
    keepalive_timeout 30;
    server_tokens off; 
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 5;
    gzip_http_version 1.1;

Add a line just before the <b>gzip_types</b> line that says this: 

    gzip_min_length 256;

Honestly, I don't know if this is necessary, but it was in the instructions, and I can say it didn't hurt anything, so, plug this in just below the # gzip_types ... line that is there. (Yes, you can just use this to replace the existing line.)

    gzip_types
       application/atom+xml 
       application/javascript 
       application/json 
       application/rss+xml 
       application/vnd.ms-fontobject 
       application/x-font-ttf 
       application/x-web-app-manifest+json 
       application/xhtml+xml 
       application/xml 
       font/opentype 
       image/svg+xml 
       image/x-icon 
       text/css 
       text/plain 
       text/x-component 
       text/javascript 
       text/xml;

Save your file and exit.

Now we need to create a 'sites-available' file pointing to our app.

```sudo nano /etc/nginx/sites-available/poolApp```

    server {
            listen 80 default_server;
            listen [::]:80;
            root /var/www/html;
                server_name poolpi;
                location /static {
                alias /var/www/html;
            }

            location / {
                try_files $uri @wsgi;
            }

            location @wsgi {
               # proxy_pass http://unix:/tmp/gunicorn.sock;
                proxy_pass http://unix:/home/greg/poolctl/gunicorn.sock;
                include proxy_params;
            }

            location ~* .(ogg|ogv|svg|svgz|eot|otf|woff|mp4|ttf|css|rss|atom|js|jpg|jpeg|gif|png|ico|zip|tgz|gz|rar|bz2|doc|xls|exe|ppt|tar|mid|midi|wav|bmp|rtf)$ {
                access_log off;
                log_not_found off;
                expires max;
            }
    }

Notice that in the 'proxy_pass' line, I have the .sock file placed in my app's home folder.

Once we have the 'sites-available' file created, we want to make it the default run by nginx.  To do that, we need to replace the 'sites-enabled' default with our new file.

```cd /etc/nginx/sites-enabled```

```sudo rm default```

```sudo ln -s /etc/nginx/sites-available/poolApp .```

I alway list the directory to make sure it's there.  It should look like this:

    greg@Poolpi:/etc/nginx/sites-enabled $ ll
    total 8
    drwxr-xr-x 2 root root 4096 Nov 27 09:57 .
    drwxr-xr-x 8 root root 4096 Nov 27 09:40 ..
    lrwxrwxrwx 1 root root   34 Nov 27 09:57 poolApp -> /etc/nginx/sites-available/poolApp
    greg@Poolpi:/etc/nginx/sites-enabled $

Now test the nginx configuration:

```sudo nginx -t```

If it returns successful, continue by typing:

```sudo systemctl restart nginx  (or 'sudo service nginx reload' . . . I'm just used to using 'systemctl restart'.)```

That's all for nginx.  Now for gunicorn.

### Setup Gunicorn

We installed gunicorn earlier.  Really all that's necessary at this point is to create a systemctl file for it.

```sudo nano /lib/systemd/system/poolApp.service```

That file should look like this when you're done:

    [Unit]
    Description=Sanders Pool Controls  poolctl.service
    After=network-online.target

    [Service]
    Type=simple
    ExecStart=/usr/local/bin/gunicorn --bind=unix:/home/greg/poolctl/gunicorn.sock --threads=8 poolApp:app
    WorkingDirectory=/home/greg/poolctl/
    StandardOutput=syslog
    StandardError=syslog
    User=greg
    Group=www-data
    #ExecStop = /bin/kill -2 $MAINPID
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    Restart=on-abort

    [Install]
    WantedBy=multi-user.target

Note that I am running this as my user 'greg' and www-data is the group.

### Ensure the python app has the correct port listed at the bottom

When you are running in the development server in Flask (Werkzeug), it is intended that you would be using some port other than 80.  So, when you set up a production WSGI server like gunicorn, you'll want to change that at the bottom of your Flask app.  Are there other ways this is done?  I have no idea.  This is the only way I've seen it done in my limited experience.  So I report it here.  

#### From the bottom of poolApp.py:

    if __name__ == "__main__":
        app.run(host='0.0.0.0')
        #app.run(host='0.0.0.0', port=5000, debug=True)

```sudo systemctl daemon-reload```

```sudo systemctl restart poolctl```

That's it.  Those are the steps I took to get poolApp.py running on nginx and gunicorn.