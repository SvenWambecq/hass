# hass
Home Assistant Configuration 


## Setup

### Install Raspbian

HA works with a recent Raspbian version (it requires python/3.10). Version of raspbian can be found at http://raspbian.raspberrypi.org/raspbian/.
The image then has to be flashed on the SD card using balena etcher (see https://etcher.balena.io/).

Best is to use a full image. I took a smaller OS image, but struggled afterwards because some dependencies had not been installed. 

### Build Python/3.11

Because even the newer versions of raspbian only include python/3.9, we still had to build python/3.11 ourselves. Note that it is important to have the right dependencies installed.
More information can be found at the following locations: 

- https://aruljohn.com/blog/python-raspberrypi/
- https://stackoverflow.com/questions/41328451/ssl-module-in-python-is-not-available-when-installing-package-with-pip3

I struggled with the SSL module. The library was not installed on my RPi, but the python build did not complain about this. Python was built correctly, but I could not install packages using pip because I didn't have the SSL library.

### Install HASS

Follow the steps as described in 
- https://www.home-assistant.io/installation/raspberrypi#install-home-assistant-core

After installing HASS, it can be started as described in the above webpage and you can browse to the interface using a webbrowser. 

### Interfacing

#### Internal access

I configured the raspberry pi to get a fixed internal address on our LAN. (192.168.68.102). 

#### External access

To access HA from the outside is a bit more difficult to setup. 
The basic idea is as follows: 

1. We will use a DynDNS such that the real IP address can be accessed using a logical IP address. To do this, we use DuckDNS.org. A domain was requested for this (sveneniris.duckdns.org).
2. HA listens by default to port 8123. Opening this port, without encryption is not wise, but also not possible within the proximus network. A lot of ports are blocked by default by proximus.
3. We will therefore access HA using https from the external world. Accesses are then made over port 443, and we have to configure the modem (and also the deco on the internal network) to forward port 443 to the raspberry pi.
4. To use https, we need to setup a certificate. We did this using the explanation at https://community.home-assistant.io/t/installing-tls-ssl-using-lets-encrypt/196975.

##### Renew certificate

1. To check until when it is valid: 
   ```
      ssl-cert-check -b -c /etc/letsencrypt/live/sveneniris.duckdns.org/cert.pem
   ```
3. Update certificate:
   ```sudo systemctl stop nginx
      sudo certbot renew --cert-name sveneniris.duckdns.org --preferred-challenges http-01
      sudo systemctl start nginx
   ```

### Create service
https://community.home-assistant.io/t/autostart-using-systemd/199497
