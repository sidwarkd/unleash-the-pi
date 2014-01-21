import RPi.GPIO as GPIO
import spidev
from time import sleep, localtime, strftime, time
import sys
import smbus
from twython import Twython


def get_temp(bus):
  temp = bus.read_word_data(0x48, 0)
  byte1_mask = 0b0000000011111111
  byte2_mask = 0b1111111100000000
  byte1 = (temp & byte1_mask) << 4
  byte2 = (temp & byte2_mask) >> 12
  temp_c = byte2 | byte1
  temp_c *= .0625
  #print "Celsius: " + str(temp_c)
  temp_f = temp_c*1.80 + 32.00
  #print "Farenheit: " + str(temp_f)
  return temp_f

def spi_send(bus, data):
  xfer_list = []
  if type(data) == str:
    for c in data:
      xfer_list.append(ord(c))
  elif type(data) == list:
    xfer_list += data
  elif type(data) == int:
    xfer_list.append(data)
  else:
    print "Unsupported type passed to spi_send. Must be str, int, or list"

  bus.xfer2(xfer_list, 250000)

def clear_display(bus):
  spi_send(bus, [0x76])

def display_time(bus):
  t = strftime("%H%M", localtime())
  clear_display(bus)
  spi_send(bus, t)
  spi_send(bus, [0x77, 0x10])

def display_temp(bus, temp):
  # Display temp with one decimal of precision
  temp_str = "{:4.1f}f".format(round(temp,1))
  display_val = temp_str.replace('.','')
  clear_display(bus)
  spi_send(bus, display_val)
  # Turn on the decimal and the apostrophe
  spi_send(bus, [0x77, 0x22])

# Set the mode GPIO.BCM or GPIO.BOARD
GPIO.setmode(GPIO.BOARD)

# Setup the LED pin as an output and to have an initial 
# state of high which turns the LED off
GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH)

# Setup the switch pin as an input
GPIO.setup(16, GPIO.IN)

# Setup the button pin as an input
GPIO.setup(18, GPIO.IN)

# Setup spi module
spi = spidev.SpiDev()
spi.open(0,0)

# Setup i2c module
i2c = smbus.SMBus(1)
lastTempReading = time()
currentTemp = get_temp(i2c)

# Setup motion sensor
GPIO.setup(22, GPIO.IN)
system_armed = False
time_armed = None

# Setup Twitter 
# After creating an app via dev.twitter.com you need to enter the 4 keys required below
twitter = Twython("Consumer Key", "Consumer Secret", "Access Token","Access Token Secret")
last_tweet = time()

clock_mode = True
last_display_update = time()
display_time(spi)

try:
  while True:
    if GPIO.input(16) == GPIO.HIGH:
      if not system_armed:
        time_armed = time()
        system_armed = True
    else:
      time_armed = None
      system_armed = False

    if GPIO.input(18) == GPIO.HIGH:
      if clock_mode:
        display_temp(spi, currentTemp)
        clock_mode = False
      else:
        display_time(spi)
        clock_mode = True
      sleep(1)
  
    # Get temp reading every 5 seconds
    if((time() - lastTempReading) >= 5):
      lastTempReading = time()
      currentTemp = get_temp(i2c)

    # Update the display every 10 seconds
    if((time() - last_display_update) >= 10):
      if (clock_mode):
        display_time(spi)
      else:
        display_temp(spi, currentTemp)

      last_display_update = time()

    # If the system is armed check for motion
    if system_armed:
      # Wait 10 seconds so people can leave the room
      if (time() - time_armed) >= 10:
        if GPIO.input(22) == GPIO.HIGH:
          GPIO.output(12, GPIO.LOW)
          if (time() - last_tweet) >= 10:
            statusText = strftime("%X", localtime()) + ": I detected motion. BTW, the current temp is " + str(currentTemp)
            twitter.update_status(status=statusText)
            last_tweet = time()

except KeyboardInterrupt:
  GPIO.output(12, GPIO.HIGH)
  GPIO.cleanup()
  clear_display(spi)
  spi.close()
  sys.exit(1)

except Exception as e:
  GPIO.output(12, GPIO.HIGH)
  GPIO.cleanup()
  clear_display(spi)
  spi.close()
  sys.exit(2)
