#Birthday sim
import random
import pandas as pd
df=pd.read_csv('boy_names_2024.csv',header=1)

names={}
for name in df.itertuples():
    print(name[2])
    names[name[2]]=random.randint(1,365)


matches={}
for person in names:
    matches[person]={}
    matches[person][person]=[person,names[person]]
    for other_person in names:
        if not other_person == person:
            if names[other_person] == names[person]:
                matches[person][other_person]=names[other_person]


'''for person in names:
    print(person[0])
    print(person[1])
    print(person[2])'''
print(matches)