# Lab2: Adversarial Localization
## Team 2: Natalia Kisanga, Cho Yin Kong, Lucy Newman

## Summary
In this lab, we collected RSS data traces from 3 locations as robotic cars moved along marked trajectories near a hidden WiFi camera. Our goal is to use the location of the car and the RSS data form the refeiver to find an algorithm that predicts the location of the WiFi transmitter.

First, we parsed the data and stored each data trace into a log class. Then, we further classified each trace into a mac class, based on the 4 different mac addresses given to us. For each mac class, we calculated the absolute x and y locations of the receiver by computing the average speed of the car between the two points for all the points, and using that speed to compute the x and y coordinates at each time, to find the absolute location. We used this list of (x,y) coordinates and the RSS values to do our model fitting.

## Algorithm

We used the *scipy curve_fit function*  which uses non-linear least squares to fit our function to the data we collected. The equation we use is:

> RSS = c - g * log(distance((rxx, txx),(rxy, txy))

The known values are the RSS data points and the corresponding receiver x and y locations. We used these values to train our model to predict the four unknown parameters for each trace: c, g, and the location of the transmitter.


## Results

For the two locations we know, our model predicts these locations:

~~~~
8c:85:90:16:0a:a4 = (1.7424648579719106, 2.9145329936775437)
Average error: 7.66881981109
Results error: 6.37773592822

ac:9e:17:7d:31:e8 = (-1.4514753389253363, 9.3428035016914865)
Average error: 4.25368568235
Results error: 0.5912737598
~~~~

These are our predictions for the two unknown Mac Address locations:

~~~~
d8:c4:6a:50:e3:b1 = (2.3336365498565548, 3.9552350511118233)

f8:cf:c5:97:e0:9e = (1.8629801623605156, 4.8234596645366947)
~~~~
