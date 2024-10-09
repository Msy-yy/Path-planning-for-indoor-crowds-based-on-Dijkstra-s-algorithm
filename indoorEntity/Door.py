import matplotlib.pyplot as plt

class Door:
    def __init__(self, ID, x, y, floor):
        self.ID = ID
        self.x = x
        self.y = y
        self.floor = floor
        self.rooms = []

    def addRoom(self, roomID):
        if roomID not in self.rooms:
            self.rooms.append(roomID)

    def printDoor(self):
        print("Door {}: x={}, y={}, floor={}, rooms={}"
              .format(self.ID, self.x, self.y, self.floor, self.rooms))
        
    def drawDoor(self):
        plt.scatter(self.x, self.y, marker = '.', color="red")
