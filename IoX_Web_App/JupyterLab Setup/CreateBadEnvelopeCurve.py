from matplotlib import pyplot as plt
import numpy as np
import math
import csv

dataPoints = []

# Step 1 Starting low - 40
for x in range(40):
    dataPoints.append(1)
    
# Step 2 Smooth raising - 20
for x in range(20):
    dataPoints.append((25/400) * pow(x, 2) + 1)
    
# Step 3 Send Parabel (half) - 20
for x in np.arange(-20, 0, 1):
    dataPoints.append(-(25/400) * pow(x, 2) + 51)
    
# Step 4 Falling with Sinus - 115
for x in range(115):
    dataPoints.append(2 * math.sin((0.25 * (x + 2))) + -(49/120) * x + 50)
    
# Step 5 Smoothen Sinus end - 5
for x in range(-5, 0):
    dataPoints.append((1/25) * pow(x, 2) + 1)  

# Step 6     
for x in range(120):
    dataPoints.append(1)
    
# Step 6 Smooth raising - 10
for x in range(10):
    dataPoints.append((8/225) * pow(x, 2) + 1)
    
# Step 7 Response Parable - 20
for x in range(-10, 10):
    dataPoints.append(-(8/225) * pow(x, 2) + 8)
    
# Step 8 Smooth falling - 10
for x in range(10):
    dataPoints.append((8/225) * pow((x - 10), 2) + 1)
    
# Step 9 Finishing low - 40
for x in range(40):
    dataPoints.append(1)
    
print(dataPoints)
    
dataRange = range(-80, 320)

# Write .csv file
with open('huellcurve_bad_Semicolon.csv', mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)   
    writer.writerow(dataRange)
    writer.writerow(dataPoints)
    
plt.plot(dataRange, dataPoints)
plt.show()
