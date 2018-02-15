# Lab2: Adversarial Localization
## Team 2: Natalia Kisanga, Cho Yin Kong, Lucy Newman

## Summary
In this lab, we collected RSS data traces from 3 locations as robotic cars moved along marked trajectories near a hidden WiFi camera. Our goal is to use the location of the car and the RSS data form the refeiver to find an algorithm that predicts the location of the WiFi transmitter.

First, we parsed the data and stored each data trace into a log class. Then, we further classified each trace into a mac class, based on the 4 different mac addresses given to us. For each mac class, we calculated the absolute x and y locations of the receiver by computing the average speed of the car between the two points and using that speed to compute the x and y coordinates at each time. We used this list of (x,y) coordinates and the RSS values to do our model fitting.

## Algorithm

We used the *scipy curve_fit function*  which uses non-linear least squares to fit our function to the data we collected. The equation we use is:

RSS = c - g * log(distance((rxx, txx),(rxy, txy))

The known values are the RSS data points and the corresponding receiver x and y locations. We used these values to train our model to predict the four unknown parameters for each trace: c, g, and the location of the transmitter.


## Results

For the two locations we know, our model predicts these locations:

8c:85:90:16:0a:a4  = (1.748, 2.914) 
Error =  0.591  


ac:9e:17:7d:31:e8  = (x,y) 
Error =  6.373


These are our predictions for the two unknown Mac Address locations:

d8:c4:6a:50:e3:b1 = (1.990, 3.479) 
f8:cf:c5:97:e0:9e = (1.862, 4.822)

