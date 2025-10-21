# import numpy
import numpy as np

a = np.array([[10.2, 21.4, 3.6, 14.8], [0.0, 5.0, 10.0, 15.0]])
bins = np.array([1.0, 1.3, 2.5, 4.0, 10.0])

# using np.digitize() method
gfg = np.digitize(a, bins)

print(gfg)
