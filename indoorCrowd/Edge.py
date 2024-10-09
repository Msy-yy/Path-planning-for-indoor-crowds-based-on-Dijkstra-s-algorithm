import numpy as np

class Edge():
    def __init__(self, ID, dk, vi=None, vj=None,  
                 Lambda = np.random.randint(0, 4)):
        self.ID = ID
        self.vi = vi
        self.vj = vj
        self.dk = dk
        self.flow = {}#记录时间点的人流{'10:01:01': 0}
        self.Lambda = Lambda#默认lambda在0到3随机变化
    
    def printEdge(self):
        print('---------------------------------------------------')
        print("e{}'s vi is v{}, vj is v{}, dk is d{}, flow is {}, Lambda is {}."
              .format(self.ID, self.vi.ID if self.vi!=None else None,
                      self.vj.ID if self.vj!=None else None, self.dk.ID,
                      self.flow, self.Lambda))
        print('---------------------------------------------------')