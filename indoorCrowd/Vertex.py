import numpy as np
from datetime import datetime, timedelta

MAXDENSITY = 1          #人群密度的上界，实际上可能超出

class Vertex():
    def __init__(self, ID, area, Md2d, type, start,
                 maxDensity = MAXDENSITY): 
        self.ID = ID
        self.area = area 
        self.Md2d = Md2d#[[d1,d2,5],[d2,d1,5]]
        self.type = type
        self.population = []#[[0,'10:01:01'],[1,'10:06:11']]
        self.population.append([start, '00:00:00'])
        #P的这个初始时间会被G类的实例化的全局初始时间更改
        self.maxDensity = maxDensity
        #默认初始的人数随机

    def getDensity(self, tc):
        tc = datetime.strptime(tc, '%H:%M:%S')
        tmax = datetime.strptime(self.population[-1][1], '%H:%M:%S')
        t0 = datetime.strptime(self.population[0][1], '%H:%M:%S')
        if tc > tmax or tc < t0:
            return None
        elif tc == tmax:
            return self.population[-1][0]/self.area
        else:
            for i in range(len(self.population)-1):
                ti = datetime.strptime(self.population[i][1], '%H:%M:%S')
                tii = datetime.strptime(self.population[i+1][1], '%H:%M:%S')
                if tc >= ti and tc < tii:
                    return self.population[i][0]/self.area
            
    def laggingCoefficient(self, tc):
        if self.getDensity(tc) == None:
            return None
        a = self.getDensity(tc)/self.maxDensity
        if self.type == 'Q':
            #print('laggingCoefficient({}) = {}'.format(tc, 1+np.exp(a)))
            return 1 + np.exp(a)
        else:
            #print('laggingCoefficient({}) = {}'.format(tc, 1+np.exp(np.power(a,2))))
            return 1 + np.exp(np.power(a,2))

    def printVertex(self):
        print('---------------------------------------------------')
        print("v{}'s area is {}, type: {}, ".format(self.ID, self.area,
                                                   self.type), end='')
        print("Md2d: [", end='')
        for i in range(len(self.Md2d)):
            print('[d{}, d{}, {}]'.format(self.Md2d[i][0].ID,
                                      self.Md2d[i][1].ID,
                                      self.Md2d[i][2]), end='') 
            if i != len(self.Md2d)-1:
                print(', ', end='')
        print(']')
        print("time and population: {}".format(self.population))
        print('---------------------------------------------------')