#Getting Started
This repository is meant to accompany the Skillshare class **Unleash the Raspberry Pi Through Physical Computing**. For those that follow along with the class project this is the final working code at the end of the project. Note that it is a little different than what you will end up with at the end as I continually maintain this code and change it from time to time but if you have all of the hardware connected as shown in the class, this code will run on your Pi.

##Twitter Integration
To get the Twitter integration working you will need to edit the line of code in monitor.py that contains the 4 keys found in your twitter app dashboard.
```python
twitter = Twython("Consumer Key", "Consumer Secret", "Access Token","Access Token Secret")
```
If you don't want Twitter integration then just comment out the lines of code that attempt to update Twitter status.

##Requirements
  * Python 2.7.3