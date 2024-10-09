import sys
sys.path.append("./")
from indoorEntity import Door
from indoorEntity import Partition
import matplotlib.pyplot as plt

class IndoorSpace:
    def __init__(self, name, ID, nfloor):
        self.name = name
        self.ID = ID 
        self.nfloor = nfloor

        self.partitions = []
        self.doors = []

    def getPartition(self, ID):
        for par in self.partition:
            if par.ID == ID:
                return par
        
        print("Not Found PartitionID: {}" .format(ID))
        return None
    
    def getDoor(self, ID):
        for door in self.doors:
            if door.ID == ID:
                return door
        print("Not Found DoorID: {}" .format(ID))
        return None
    
    def readPartitions(self, partitionFile):
        print("Start reading partitionfile {}..." .format(partitionFile))

        with open(partitionFile, 'r', encoding='utf-8') as f:
            for line in f:
                tempArr = (line.strip()).split()
                ID = int(tempArr[0])
                x1 = float(tempArr[1])
                x2 = float(tempArr[2])
                y1 = float(tempArr[3])
                y2 = float(tempArr[4])

                if x1 > x2:
                    temp = x1
                    x1 = x2
                    x2 = temp
                if y1 > y2:
                    temp = y1
                    y1 = y2
                    y2 = temp

                floor = int(tempArr[5])
                type = int(tempArr[6])

                par = Partition.Partition(ID, x1, x2, y1, y2, floor, type)

                for i in range(7, len(tempArr)):
                    doorID = tempArr[i]
                    par.addDoor(int(doorID))

                self.partitions.append(par)

    def readDoors(self, doorFile):
        print("Start reading doorfile {}..." .format(doorFile))

        with open(doorFile, 'r', encoding='utf-8') as f:
            for line in f:
                tempArr = (line.strip()).split()
                ID = int(tempArr[0])
                x = float(tempArr[1])
                y = float(tempArr[2])
                floor = int(tempArr[3])

                door = Door.Door(ID, x, y, floor)

                for i in range(4, len(tempArr)):
                    roomID = tempArr[i]
                    door.addRoom(int(roomID))

                self.doors.append(door)

    def printIndoorSpace(self):
        print("IndoorStructure {}: ID={}, nfloor={}, numOfPatitions={}, numOfDoors={},\n partitions={}, \ndoors={}"
              .format(self.name, self.ID, self.nfloor, len(self.partitions), len(self.doors), 
                      [p.ID for p in self.partitions], [d.ID for d in self.doors]))

    def drawIndoorSpace(self):
        fig = plt.figure(figsize=(15, 8))
        plt.axis('off')
        ax = plt.gca()
        ax.xaxis.set_ticks_position('top')
        ax.invert_yaxis()

        plt.title("IndoorStructure {}, ID={}".format(self.name, self.ID),fontsize=20)
        for par in self.partitions:
            par.drawPatition()
        for door in self.doors:
            door.drawDoor()
        # plt.show()
        return fig
    
    def check(self):
        flag = 0
        for par in self.partitions:
            for doorID in par.doors:
                # ensure roomID exist
                if self.getDoor(doorID) == None:
                    print("ERROR: doorID {} not exist.\n" .format(doorID)) 
                    flag = 1 
                if par.ID not in self.getDoor(doorID).rooms:
                    print("ERROR: Partition {} is not in Door {}.rooms".format(par.ID, doorID))
                    flag = 1
        
        for door in self.doors:
            if len(door.rooms)>2:
                print('Door{} connects with more than two patitions.patitionsID={}'.format(door.ID,door.rooms))
                flag = 1
        if flag == 0:
            print('The IndoorStructure has no problem.')
            return True
        elif flag == 1:
            return False