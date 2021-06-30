from matplotlib import pyplot as plt
import numpy as np
import csv

dataPoints = []

# Step 1 Starting low - 40
for x in range(40):
    dataPoints.append(1)
    
# Step 2 Smooth raising - 20
for x in range(20):
    dataPoints.append((25/400) * pow(x, 2) + 1)
    
# Step 3 Send Parabel - 40
for x in np.arange(-20, 20, 1):
    dataPoints.append(-(25/400) * pow(x, 2) + 51)
    
# Step 4 Smooth falling - 20
for x in range(20):
    dataPoints.append((25/400) * pow((x - 20), 2) + 1)
    
# Step 5 Waiting low - 100
for x in range(100):
    dataPoints.append(1)
    
# Step 6 Smooth raising - 10
for x in range(10):
    dataPoints.append((10/100) * pow(x, 2) + 1)
    
# Step 7 Response Parable - 20
for x in range(-10, 10):
    dataPoints.append(-(10/100) * pow(x, 2) + 21)
    
# Step 8 Smooth falling - 10
for x in range(10):
    dataPoints.append((10/100) * pow((x - 10), 2) + 1)
    
# Step 9 Finishing low - 40
for x in range(40):
    dataPoints.append(1)
    
print(dataPoints)
    
dataRange = range(-80, 220)

# Write .csv file
with open('huellcurve_good_Semicolon.csv', mode='w') as file:
    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)   
    writer.writerow(dataRange)
    writer.writerow(dataPoints)
    
plt.plot(dataRange, dataPoints)
plt.show()
