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



