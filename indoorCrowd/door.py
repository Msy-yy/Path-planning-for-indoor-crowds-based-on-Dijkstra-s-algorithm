class door:#门
    def __init__(self, ID, n = 1):
        self.ID = ID
        if n not in [1, 2, 3, 4]:
            print('n is invalid.')
            return
        self.n = n
        self.reportTimes = []#报道时间['10:01:01','10:01:06','10:01:11']
    
    def getReportTimes(self,RT):
        self.reportTimes = RT.copy()

    def printdoor(self):
        print("d{}'s n={}, reportTimes={}".format(self.ID,self.n,self.reportTimes))