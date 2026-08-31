
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as rand
p1s=rand.randint(1,11,1000)
p2s=rand.randint(1,11,1000)
pts=[p1s[i]+p2s[i] for i in range(1000)]
rang=list(range(1000))
numtot={i:0 for i in range(21)}
for item in pts:
    numtot[int(item)]+=1
print(numtot)


plt.bar(list(numtot.keys()),list(numtot.values()))

plt.show()