import random
from tqdm import tqdm

import sys
sys.path.append("CAIPPP")
from indoorCrowd.door import door
from indoorCrowd.Edge import Edge
from indoorCrowd.Vertex import Vertex
from indoorCrowd.Graph import Graph
from dataGen.cph.cphGen import generateIndoorSpace 

def generateIndoorCrowd(indoorSpace):
    GID = indoorSpace.ID
    V = []
    D = []
    E = []
    startTime = '00:00:00'
    for p in tqdm(indoorSpace.partitions, ncols=100):
        ID = p.ID
        area = (p.x2-p.x1)*(p.y2-p.y1)      
        type = "R"
        start = random.randint(0, int(area*1500/20000))

        Md2d = []
        doors = []
        for d in indoorSpace.doors:
            doors.append(d)
        d1 = doors.pop()
        while len(doors)!=0:
            for d2 in doors:
                dist = int(((d1.x-d2.x)**2+(d1.y-d2.y)**2)**0.5)
                Md2d.append([d1.ID,d2.ID,dist])
                Md2d.append([d2.ID,d1.ID,dist])
            d1 = doors.pop()    
        V.append(Vertex(ID,area,Md2d,type,start))

    def getV(vID):
        for vi in V:
            if vi.ID == vID:
                return vi

    for di in indoorSpace.doors:
        ID = di.ID
        n = random.randint(1, 4)
        d = door(ID,n)
        D.append(d)
        for i in range(len(di.rooms)-1):
            for j in range(i+1,len(di.rooms)):
                e = Edge(len(E), d, getV(di.rooms[i]), getV(di.rooms[j]),random.randint(1, 3))
                E.append(e)
                e = Edge(len(E), d, getV(di.rooms[j]), getV(di.rooms[i]),random.randint(1, 3))
                E.append(e)

    def getDoorFromD(dID):
        for d in D:
            if d.ID == dID:
                return d

    for vi in tqdm(V, ncols=100):
        for item in vi.Md2d:
            d1 = getDoorFromD(item[0])
            d2 = getDoorFromD(item[1])
            item[0] = d1
            item[1] = d2
    g = Graph(GID,V,E,startTime)
    return g

def main():
    s = generateIndoorSpace('CPH', 0, 1,
                            'CAIPPP\inputfiles\CPH\RParINFO_diType_1.txt', 
                            'CAIPPP\inputfiles\CPH\RDoorINFO_diType_1.txt')
    g = generateIndoorCrowd(s)
    g.drawGraph()
        
if __name__ == "__main__":
    main()