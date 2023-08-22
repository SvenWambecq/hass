# hass
Home Assistant Configuration 


## Setup

### Install Raspbian

HA works with a recent Raspbian version (it requires python/3.10). Version of raspbian can be found at http://raspbian.raspberrypi.org/raspbian/.
The image then has to be flashed on the SD card using balena etcher (see https://etcher.balena.io/).

Best is to use a full image. I took a smaller OS image, but struggled afterwards because some dependencies had not been installed. 

### Build Python/3.11

Because even the newer versions of raspbian only include python/3.9, we still had to build python/3.11 ourselves. Note that it is important to have the right dependencies installed.

1. Download python/3.11 source code 
2. Make sure the following dependencies are installed:
   1. 
