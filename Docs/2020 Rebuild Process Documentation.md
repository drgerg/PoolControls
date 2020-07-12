# 2020 Rebuild Process Documentation

In Mid-June we got nailed by lightning again.  This time it took out both the Pi and the SD card.
It is, of course, in moments like this that you discover you failed yet again to document changes you've made incrementally to the system.

So, this time (at least) I'm going to document the steps it takes to get from where my last Filezilla copies left me to where I need to be.  

Let's begin:

- Download Raspberry Pi Imager for Windows
  - <https://www.raspberrypi.org/downloads/>
- Install Imager on Windows machine
- Run Imager and write selected OS to SD card
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
  - Log out and back in as root
  - ```$ logout```
  - Change user name
  - ```$ usermod -l newname pi```
  - Change user group.  Start by finding out what groups the oldname belongs to.
  - ```$ groups oldname```
  - Change all the Secondary groups at once by:  (leave off the first one, which was 'pi')
  - ```$ usermod -G comma,delimited,list,of,groups,from,the,last,step newname```
  - Edit /etc/group manually to change 'pi' to 'newname'.  This changes newname's primary group.
  - ```$ sudo nano /etc/group```
  - Create a new /home/directory and move newuser's files over there.
  - ```$ usermod -m -d /home/newname newname```
  - Log out of root's account and into the newname account
  - ```$ logout```
  - Change newname's password
  - ```$ passwd```
  - Run apt-get update to verify sudo permissions are working.
  - ```$ sudo apt-get update```
  - Remove the root password.  You really don't need it now.
  - ```$ sudo passwd -l root```

- Set a static IP address.
  - ```$ sudo nano /etc/dhcpcd.conf```
    - Edit the hostname at the top of the file to match your hostname.
    - Read the examples, the add something like these lines to the bottom:
        > interface eth0<br>
        > static ip_address 192.168.1.###/24  (### is your number)<br>
        > static routers=192.168.1.###  (### is your router's number)<br>
        > static domain_name_servers=192.168.1.### #.#.#.# (typically your router and your other favorite)<br>

  - Save and reboot.  You should see the new IP address.  If not, do:
  - ```$ ip addr```

- Change the SSH port
  - ```$ sudo nano /etc/sshd/sshd_config```
  - You will get an warning message when you log in. That's normal. Read, follow, fix.

- Log in using SSH and do the rest of this more comfortably.
- Log back out, and set up key-based login (only if you already have this working. Otherwise, you have to set that up first.)
  - ```$ ssh-copy-id newname@pi-hostname -p portNumber```
- Edit .bashrc in /home/newname to add the 'll' alias. (Not using sudo. .bashrc is your file.)
  - ```$ nano .bashrc```
    - Add ```alias ll='ls -la'``` under the other 'alias' lines.

- Edit /boot/config.txt:
  - ```$ sudo nano /boot/config.txt```
    - Add these lines to the bottom of the file.

        > dtoverlay=i2c-rtc,ds3231<br>
        > dtoverlay w1-gpio,gpiopin=26,pullup=0<br>
        > dtoverlay w1-gpio,gpiopin=19,pullup=0<br>

    -This sets up the Pi to use the 1-wire thermometers we have.<br><br>
- Prep the system for using the Adafruit DS3231 Real-Time Clock (ADA3013)
  - ```$ sudo apt-get install python-smbus i2c-tools```
  - ```$ sudo i2cdetect -y 1```
  - The number 68 should be in the resulting table.  If not, reboot and try again.
    - 68 is the i2c address for the RTC module.
  - ```$ sudo apt-get -y remove fake-hwclock```
  - ```$ sudo update-rc.d -f fake-hwclock remove```
  - ```$ sudo nano /lib/udev/hwclock-set```
  - Comment out these lines so it looks like this: (ONLY the 3 lines that read exactly this. You supply the pound signs (hashes).)<br>
         ```# if [ -e /run/systemd/system ] ; then```<br>
         ```#    exit 0```<br>
         ```# fi```<br>
- Reboot (just for safety's sake)
- Check the date and time.
  - ``$ date``
  - If it's good, set the hardware clock (RTC).
    - ``$ sudo hwclock -w``
  - Read it to see if all went well.
    - ``$ sudo hwclock -r``


- Follow ['Dependencies required to make poolApp.py work'](https://github.com/casspop/PoolControls/blob/master/Dependencies.md)
- Follow ['Setup nginx and gunicorn'](https://github.com/casspop/PoolControls/blob/master/Setup%20nginx%20and%20gunicorn.md)


