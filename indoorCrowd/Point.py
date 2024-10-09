class Point:#点
    def __init__(self, ID, v, dist):
        self.ID = ID
        self.v = v
        self.dist = dist#[[d1, 3],[d2, 4],[p1, 1]]

    def printPoint(self):
        print('---------------------------------------------------')
        print("p{}'s v is v{},".format(self.ID,self.v.ID))
        print("dist: ", end='')
        print([['d'+str(dist[0].ID), dist[1]] for dist in self.dist])
        print('---------------------------------------------------')