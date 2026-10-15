import numpy as np
import numpy.random as rand
import matplotlib.pyplot as plt
numbers=rand.randint(1,4,100)
numbers2=rand.randint(1,4,100)
numbers3=rand.randint(1,4,100)
points=[]
points_counted={}
for num1 in numbers:
    for num2 in numbers2:
        for num3 in numbers3:
            num=int(num1+num2+num3)

            try:  
                if points_counted[str(num)] :
                    points_counted[str(num)]+=1
            except:
                points_counted[str(num)]=1

plt.plot(list(points_counted.values()))

plt.show()