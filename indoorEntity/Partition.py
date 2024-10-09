import matplotlib.pyplot as plt

class Partition:
    def __init__(self, ID, x1, x2, y1, y2, floor, type):
        self.ID = ID
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.floor = floor
        self.type = type
        self.doors = []

    def addDoor(self, doorID):
        if doorID not in self.doors:
            self.doors.append(doorID)

    def printPartition(self):
        print("Patition {}: x1={}, y1={}, x2={}, y2={}, floor={}, type={}, doors={}"
              .format(self.ID, self.x1, self.y1, self.x2, self.y2, self.floor, self.type, self.doors))
        
    def drawPatition(self):
        plt.plot([self.x1, self.x2, self.x2, self.x1, self.x1], 
                 [self.y1, self.y1, self.y2, self.y2, self.y1], 
                 linewidth=1, color='black')
        plt.fill([self.x1, self.x2, self.x2, self.x1, self.x1], 
                 [self.y1, self.y1, self.y2, self.y2, self.y1], 
                 linewidth=1, color=(218/255, 227/255, 243/255) if self.type==0 else 'white')
        plt.text((self.x1+self.x2)/2, (self.y1+self.y2)/2, 'P'+str(self.ID),color='black', fontsize=10)
        
    