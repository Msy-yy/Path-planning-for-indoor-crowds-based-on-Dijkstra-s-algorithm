import matplotlib.pyplot as plt
import sys
sys.path.append("CAIPPP")
from indoorEntity import IndoorSpace

def generateIndoorSpace(name, ID, nfloor, patitionFlie, doorFile):
    print('Start generate indoor framework map...')

    s = IndoorSpace.IndoorSpace(name, ID, nfloor)
    s.readPartitions(patitionFlie)
    s.readDoors(doorFile)

    for par in s.partitions:
        par.printPartition()
    for door in s.doors:
        door.printDoor()

    s.printIndoorSpace()

    return s

def main():
    cph = generateIndoorSpace('CPH', 0, 1, 
                              'CAIPPP\inputfiles\CPH\RParINFO_diType_1.txt', 
                              'CAIPPP\inputfiles\CPH\RDoorINFO_diType_1.txt')
    cph.check()
    print('Start drawing indoor framework map...')
    cph.drawIndoorSpace()
    plt.show()

if __name__ == '__main__':
    main()