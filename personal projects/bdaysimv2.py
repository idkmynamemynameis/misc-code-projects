import matplotlib.pyplot as plt
import numpy.random as rand
batch_len=50
batch_size_per_batch=100
def run_test(size):
    person_ids_to_days={i:rand.randint(1,366) for i in range(size)}
    for id in person_ids_to_days.keys():
        for id2 in person_ids_to_days.keys():
            if not id == id2:
                if person_ids_to_days[id] == person_ids_to_days[id2]:
                    return True
    return False
def run_all_tests(itters,batch_size):
    results={}
    for size in range(batch_size):
        size+=1
        results[size]=0
        for itter in range(itters):
            if run_test(size):
                results[size]+=1
        results[size]/=itters
        print(str(size)+' '+str(results[size]))
    return results
print(run_all_tests(10000,30))



