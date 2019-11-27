#### Setup nginx and gunicorn 

These instruction assume Flask is already installed and configured.  I am condensing instructions I found on the web here: [www.e-tinkers.com](https://www.e-tinkers.com/2018/08/how-to-properly-host-flask-application-with-nginx-and-guincorn/)

```sudo apt-get update```

If you have anything using port 80, you'll want to stop it.  I had my existing poolctl.service running with Flask and 