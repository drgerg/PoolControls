# 2020 Rebuild Process Documentation

In Mid-June we got nailed by lightning again.  This time it took out both the Pi and the SD card.
It is, of course, in moments like this that you discover you failed yet again to document changes you've made incrementally to the system.

So, this time (at least) I'm going to document the steps it takes to get from where my last Filezilla copies left me to where I need to be.  

Let's begin:

- Download Raspberry Pi Imager for Windows
  - <https://www.raspberrypi.org/downloads/>
- Install Imager on Windows machine
- Run Imager and write selected OS to SD card
- Start following the steps I wrote out at: <https://github.com/casspop/ohd/blob/master/SetupRaspianForOhd.md>
- Insert SD card and boot Pi
  - Login - username: pi, password: raspberry
- Run "sudo raspi-config" at command prompt
        Make changes to Network, Hostname, localization, timezone, enable SSH
- Reboot.
- Install pip3
- Install RPi.GPIO module for Python
- Change default user/group and password
  - Create root user password
  - ```$ sudo passwd root```
  - log out and back in as root
  - change user name
  - ```$ usermod -l newname pi```
  - change user group
  - ```$ groups```
  - followed by
  - ```$ usermod -g newGroup -G newname,comma,delimited,list,of,groups,from,the,last,step```
  - 
  - ```$ usermod -m -d /home/newname newname```
  - ```$ passwd```
  - ```$ sudo apt-get update```
  - ```$ sudo passwd -l root```
