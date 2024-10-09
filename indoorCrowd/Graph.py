from datetime import datetime, timedelta
from pyecharts import options as opts
from pyecharts.charts import Graph as graph
from pyecharts.charts import Line
import random
import sys
sys.path.append("CAIPPP")
from indoorCrowd.SaveAndLoad import loadVariable
from indoorCrowd.Point import Point
from indoorCrowd.door import door

BUFFERWIDTH = 1         #人的缓冲宽度
UTI = 5
WALKINGSPEED = 1      #默认行走速度

class Graph():#人群模型
    def __init__(self, ID, Vertexes, Edges, startTime):
        self.ID = ID
        self.Vertexes = Vertexes
        self.Edges = Edges   
        self.startTime = startTime

        self.doors = []#门集合
        for e in self.Edges:
            if e.dk not in self.doors:
                self.doors.append(e.dk)

        def initReportTimes(startTime, n): #门报道时间初始化
            t = []
            ti = startTime
            #从全局初始时间持续十分钟的报道时间
            while (datetime.strptime(ti, '%H:%M:%S')-
                   datetime.strptime(startTime, '%H:%M:%S')).seconds < 1200:
                ti = datetime.strptime(ti, '%H:%M:%S')   
                ti = datetime.strftime(ti+timedelta(seconds=n*UTI), '%H:%M:%S')
                t.append(ti)
            return t #报道时间['10:01:01','10:01:06','10:01:11']
        for d in self.doors: #初始化每个门的报道时间
            d.getReportTimes(initReportTimes(startTime, d.n))
        for v in self.Vertexes:
            v.population[0][1] = startTime #更改每个分区的初始时间

        self.UTG = [] #去重且有序的门报道时间集合
        t = []
        for d in self.doors:
            for ti in d.reportTimes:
                t.append(ti)
        t = list(set(t))#去重        
        for i in range(1, len(t)):#排序
            for j in range(0, len(t)-i):
                t1 = datetime.strptime(t[j], '%H:%M:%S')
                t2 = datetime.strptime(t[j+1], '%H:%M:%S')
                if t1 > t2:
                    t[j], t[j+1] = t[j+1], t[j]
        self.UTG = t

    def printGraph(self):   
        for d in self.doors:
            d.printdoor()
        for v in self.Vertexes:
            v.printVertex()    
        for e in self.Edges:
            e.printEdge()   
    
    def drawPopulationLine(self):
        time = [p[1] for p in self.Vertexes[0].population]
        # print(len(time))
        line=Line(init_opts=opts.InitOpts(width='750px', height='400px'))
        line.add_xaxis(xaxis_data=time)
        vp = []
        for i in range(len(self.Vertexes)):
            vp.append([p[0] for p in self.Vertexes[i].population])
            # print(len(self.Vertexes[i].population))
            line.add_yaxis(series_name=f'v{i+1}',
                           y_axis=vp[i],
                           label_opts=opts.LabelOpts(is_show=False),
                           is_symbol_show=True,
                           is_smooth=False)
        line.set_global_opts(title_opts=opts.TitleOpts(title="vk's population",
                                                       pos_left="center",
                                                       pos_top="top"),
                            legend_opts=opts.LegendOpts(type_="scroll", 
                                                        pos_left="0%", 
                                                        pos_top="7%"),
                                                       toolbox_opts=opts.ToolboxOpts()
                     )
        return line.render_embed()     
    
    def drawGraph(self):
        nodes = []
        for v in self.Vertexes:
            nodes.append({'name': 'v'+str(v.ID),'symbolSize':v.area/100})
        flag = 0
        flag1 = 0
        for e in self.Edges:
            if e.vi == None:
                flag = 1
            if e.vj == None:
                flag1 = 1
        if flag==1:
            nodes.append({'name': 's','symbolSize':10})
        if flag1==1:
            nodes.append({'name': 'e','symbolSize':10})
        links = []
        for e in self.Edges:
            if e.vi!=None and e.vj!=None:
                links.append({'source': 'v'+str(e.vi.ID),'target':'v'+str(e.vj.ID),'value':'d'+str(e.dk.ID)})
            elif e.vi==None and e.vj!=None:
                links.append({'source': 's','target':'v'+str(e.vj.ID),'value':'d'+str(e.dk.ID)})    
            elif e.vi!=None and e.vj==None:
                links.append({'source': 'v'+str(e.vi.ID),'target':'e','value':'d'+str(e.dk.ID)})
        G = graph(init_opts=opts.InitOpts(width='900px', height='500px'))
        G.add(
            edge_symbol=['arrow'],
            layout="force",
            is_rotate_label=True,
            series_name='',
            nodes=nodes,
            links=links,
            repulsion=4000,
            edge_label=opts.LabelOpts(is_show=True, position='middle',formatter='{c}'),
            linestyle_opts=opts.LineStyleOpts(curve=0.1),
        )
        G.set_global_opts(title_opts=opts.TitleOpts(title="G0's directed graph"))
        # G.render('g.html')
        return G.render_embed()

    def P2Eout(self, v):#找到从分区出去的边
        edges = []
        for e in self.Edges:
            if e.vi!=None and e.vi.ID == v.ID:
                edges.append(e)
        return edges 

    def P2Ein(self, v):#找到能进分区的边
        edges = []
        for e in self.Edges:
            if e.vj!=None and e.vj.ID == v.ID:
                edges.append(e)
        return edges  
    
    def P2D(self, v):
        doors = []
        for e in self.P2Eout(v):
            if e.dk not in doors:
                doors.append(e.dk)
        for e in self.P2Ein(v):
            if e.dk not in doors:
                doors.append(e.dk)
        return doors      
    
    def D2Pout(self, d):#找到能通过门d出去的分区
        v = []
        for e in self.Edges:
            if e.dk.ID == d.ID:
                if e.vi!=None:
                    v.append(e.vi)
        return v
            
    def D2Pin(self, d):#找到能通过门d进去的分区
        v = []
        for e in self.Edges:
            if e.dk.ID == d.ID:
                if e.vj!=None:
                    flag = 0
                    for vi in v:
                        if vi.ID == e.vj.ID:
                            flag = 1
                            break
                    if flag == 0:
                        v.append(e.vj)
        if len(v)>2:
            print('D2Pin(): error1')
            print([v[i].ID for i in range(len(v))])
        elif len(v)==2:
            if v[0].ID==v[1].ID:
                print('D2Pin(): error2')
                for e in self.Edges:
                    if e.dk.ID == d.ID:
                        if e.vj!=None:
                            e.eprint()
        return v  

    def D2D(self, di, dj):
        if di.ID == dj.ID:
            return 0, None
        else:
            for v1 in self.D2Pout(dj):
                for v2 in self.D2Pin(di):
                    if v1.ID == v2.ID:
                        for m in v1.Md2d:              
                            if m[0].ID == dj.ID:
                                return m[2], v1
            for v1 in self.D2Pout(di):
                for v2 in self.D2Pin(dj):
                    if v1.ID == v2.ID:
                        for m in v1.Md2d:              
                            if m[0].ID == di.ID:
                                return m[2], v1         
            return None
    
    def getEuclideanDist(self, p1, p2):#p1和p2至少一个是点
        if isinstance(p1, Point):
            for dist in p1.dist:
                if dist[0].ID == p2.ID:
                    return dist[1], p1.v
        elif isinstance(p2, Point):
            for dist in p2.dist:
                if dist[0].ID == p1.ID:
                    return dist[1], p2.v
        else:
            return None

    def getTwoPoints(self, v1ID=None, v2ID=None):#随机获得两个在不同分区的点
        if v1ID==None:
            v1 = random.choice(self.Vertexes)
        else:
            flag = 0
            for v in self.Vertexes:
                if v.ID==v1ID:
                    v1 = v
                    flag = 1
            if flag==0:
                print('no such a patition.')
                return
        ps = Point('ps', v1, [])
        for d in self.P2D(v1):
            dist = random.randint(0, round(1.4*v1.area**0.5))
            ps.dist.append([d,dist])
            v1.Md2d.append([d,ps,dist])
            v1.Md2d.append([ps,d,dist])
        if v2ID==None:
            v2 = random.choice(self.Vertexes)
        else:
            flag = 0
            for v in self.Vertexes:
                if v.ID==v2ID:
                    v2 = v
                    flag = 1
            if flag==0:
                print('no such a patition.')
                return 
        pt = Point('pt', v2, [])
        for d in self.P2D(v2):
            dist = random.randint(0, round(1.4*v2.area**0.5))
            pt.dist.append([d,dist])
            v2.Md2d.append([d,pt,dist])
            v2.Md2d.append([pt,d,dist])
        return ps, pt    

    def passingTime(self, pi, pj, vk, tc, walkingSpeed = WALKINGSPEED):
        if vk.laggingCoefficient(tc) == None:
            return None
        if isinstance(pi, door) and isinstance(pj, door):
            if self.D2D(pi, pj) == None or self.D2D(pi, pj)[1] == None:
                return None
            if self.D2D(pi, pj)[1].ID != vk.ID:
                return None
            time = self.D2D(pi, pj)[0]/walkingSpeed
        else:
            if self.getEuclideanDist(pi, pj) == None:
                return None
            else:
                if self.getEuclideanDist(pi, pj)[1].ID != vk.ID:
                    return None
                else:
                    time = self.getEuclideanDist(pi, pj)[0]/walkingSpeed
        return round(time*vk.laggingCoefficient(tc))#单位为秒，四舍五入了
    
    def passingContact(self, pi, pj, vk, tc):
        if vk.getDensity(tc) == None:
            return None
        if isinstance(pi, door) and isinstance(pj, door):
            if self.D2D(pi, pj) == None or self.D2D(pi, pj)[1] == None:
                return None
            if self.D2D(pi, pj)[1].ID != vk.ID:
                return None
            distance = self.D2D(pi, pj)[0]
        else:
            if self.getEuclideanDist(pi, pj) == None:
                return None
            else:
                if self.getEuclideanDist(pi, pj)[1].ID != vk.ID:
                    return None
                else:
                    distance = self.getEuclideanDist(pi, pj)[0]
        if vk.type == 'R':
            return round(distance*BUFFERWIDTH*vk.getDensity(tc),3)
        else:
            if distance == 0:
                return 0
            else:
                return round(BUFFERWIDTH*vk.getDensity(tc)*vk.area/distance,3)
        
    def populationGlobal(self, ta):
        """ 由门的报道时间及门流来更新分区的时间戳和人数
        就是由一系列d.reportTimes和lambda来计算出分区一系列新的时间tc对应的人数
        tc就来源于d.reportTimes，但是得>G上次更新的时间，
        并且<=这次要更新到的时间ta(基于人为规定4.)
        """
        # print('Function populationGlobal({}) is called.'.format(ta))
        t = []#所有分区的最新人口的时间
        for v in self.Vertexes:
            t.append(v.population[-1][1])
        for i in range(1, len(t)):#排序
            for j in range(0, len(t)-i):
                t1 = datetime.strptime(t[j], '%H:%M:%S')
                t2 = datetime.strptime(t[j+1], '%H:%M:%S')
                if t1 > t2:
                    t[j], t[j+1] = t[j+1], t[j]
        tGl = t[-1]#所有分区的最新人口的时间的最大值

        tGl = datetime.strptime(tGl, '%H:%M:%S')
        ta = datetime.strptime(ta, '%H:%M:%S')
        if ta <= tGl:
            print('populationGlobal(): param error.')
            return 
        A = []
        for tc in self.UTG:
            tc1 = datetime.strptime(tc, '%H:%M:%S')
            if tc1 > tGl and tc1 <= ta:
                A.append(tc)
        if len(A) == 0:
            print('no data to update population.')
            return
        for tc in A:
            for e in self.Edges:
                if tc in e.dk.reportTimes:                  
                    # e.flow[tc] = int(np.random.poisson(lam=e.Lambda, size=1)[0])
                    e.flow[tc] = e.Lambda
                else:
                    e.flow[tc] = 0
            out = []  
            In = []      
            for i in range(len(self.Vertexes)):
                out.append(0)
                In.append(0)
            for i in range(len(self.Vertexes)):
                for e in self.P2Eout(self.Vertexes[i]):
                    out[i] += e.flow[tc]
                if self.Vertexes[i].population[-1][0] < out[i]:#修正门流
                    outNew = 0
                    for e in self.P2Eout(self.Vertexes[i]):
                        e.flow[tc] = int(e.flow[tc]*self.Vertexes[i].population[-1][0]/out[i])
                        outNew += e.flow[tc]
                    out[i] = outNew
            for i in range(len(self.Vertexes)):
                for e in self.P2Ein(self.Vertexes[i]):
                    In[i] += e.flow[tc]
                Ptc = self.Vertexes[i].population[-1][0] - out[i] + In[i]
                self.Vertexes[i].population.append([Ptc, tc]) 
        vp = {}
        for v in self.Vertexes:
            vp[v.ID] = v.population[-1][0]
        return vp

    def populationLocal(self, vID, ta):
        # print('Function populationLocal(v{}, {}) is called.'.format(vID,
        #                                                             ta))
        for v in self.Vertexes:
            flag = 0
            if v.ID == vID:
                vi = v
                flag = 1
                break
        if flag==0:
            print("vID is not exist.")
            return
        tl = vi.population[-1][1]
        tl = datetime.strptime(tl, '%H:%M:%S')
        ta = datetime.strptime(ta, '%H:%M:%S')
        if ta <= tl:
            print('populationLocal(): param error.')
            return 
        A = []
        for tc in self.UTG:
            tc1 = datetime.strptime(tc, '%H:%M:%S')
            if tc1 > tl and tc1 <= ta:
                A.append(tc)
        if len(A)==0:
            print('no data to update population.')
            return
        tc = A[-1]
        A.pop()
        if len(A) == 0:
            Pitl = vi.population[-1][0]
        else:
            Pitl = self.populationLocal(vi.ID,A[-1])
        out = 0    
        for e in self.P2Eout(vi):  #此处修改了原算法
            if tc in e.dk.reportTimes:      #为了最终结果和全局估计算法一致而改
                # e.flow[tc] = int(np.random.poisson(lam=e.Lambda, size=1)[0])
                e.flow[tc] = e.Lambda 
            else:                  #确保只有在本门的报道时间边才有人流
                e.flow[tc] = 0        #不改的话其他门的报道时间该边也有人流
            out += e.flow[tc]
        if Pitl < out:
            outNew = 0
            for e in self.P2Eout(vi):
                e.flow[tc] = int(e.flow[tc]*Pitl/out)
                outNew += e.flow[tc]
            out = outNew
        In = 0
        for e in self.P2Ein(vi):
            if tc not in e.flow.keys():
                if e.vi!=None:
                    self.populationLocal(e.vi.ID,tc)
                else:#人流源
                    etl = e.flow.popitem()
                    e.flow[etl[0]] = etl[1]
                    ts = []
                    for t in self.UTG:
                        if t > etl[0] and t <= tc:
                            ts.append(t)
                    for t in ts:
                        if t in e.dk.reportTimes:
                            e.flow[t] = e.Lambda
                            # e.flow[t] = int(np.random.poisson(lam=e.Lambda, size=1)[0])
                        else:
                            e.flow[t] = 0
            In += e.flow[tc]
        Pitc = Pitl - out + In
        vi.population.append([Pitc, tc])
        return vi.population[-1][0]
    
    def cost(self, p1, p2, vk, ta, QT):
        # door1 = door(1,2)
        # print('{},{},{},{}'.format(isinstance(p1, Point),isinstance(p2, Point),isinstance(p1,type(door1)),isinstance(p2,type(door1))))
        if isinstance(p1, door) and isinstance(p2, door):
            if self.D2D(p1, p2) == None or self.D2D(p1, p2)[1] == None:
                print('dist1')
                dist = None
            elif self.D2D(p1, p2)[1].ID != vk.ID:
                print('dist2')
                dist = None
            else:
                dist = self.D2D(p1, p2)[0]
        else:
            if self.getEuclideanDist(p1, p2) != None:
                dist = self.getEuclideanDist(p1, p2)[0]
            else:
                print('dist3')
                # print('{},{}'.format(isinstance(p1, door), isinstance(p2, door)))
                # print(type(p1),type(p2))
                p1.printdoor()
                p2.printdoor()
                dist = None
        time = self.passingTime(p1, p2, vk, ta)
        if QT == 'LCPQ':
            contact = self.passingContact(p1, p2, vk, ta)
            print("cost({}, {}, {}, '{}', '{}') = ({}, {}, {})"
                  .format(p1.ID,p2.ID,vk.ID,ta,QT,dist,time,contact))                  
            return dist, time, contact
        else:
            print("cost({}, {}, {}, '{}', '{}') = ({}, {})"
                  .format(p1.ID,p2.ID,vk.ID,ta,QT,dist,time))
            return dist, time
    
    def addcost(self, c1, c2):
        if len(c1) != len(c2):
            return None
        c = ()
        for i in range(len(c1)):
            if c1[i] == None or c2[i] == None:
                return None
            else:
                if i==2:
                    c += (round(c1[i] + c2[i],3), )
                else:
                    c += (c1[i] + c2[i], )
        return c

    def sortQ(self, Q, QT):
        if QT == 'LCPQ':
            for q in Q:
                q[1] = (q[1][2], q[1][0], q[1][1])
            for i in range(1, len(Q)):
                for j in range(0, len(Q)-i):
                    if Q[j][1] > Q[j+1][1]:
                        Q[j], Q[j+1] = Q[j+1], Q[j]
            for q in Q:
                q[1] = (q[1][1], q[1][2], q[1][0])
        else:
            for q in Q:
                q[1] = (q[1][1], q[1][0])
            for i in range(1, len(Q)):
                for j in range(0, len(Q)-i):
                    if Q[j][1] > Q[j+1][1]:
                        Q[j], Q[j+1] = Q[j+1], Q[j]
            for q in Q:
                q[1] = (q[1][1], q[1][0])
        return Q    

    def expand(self, p1, p2, v, ta, Si, QT, As, Q, prev):
        costc = self.addcost(Si[1], self.cost(p1, p2, v, ta, QT))
        if costc == None:
            return
        if p2.ID not in As.keys():
            costpre = None
        else:
            costpre = As[p2.ID][1]   
        if costpre == None:
            S = [p2, costc]
            Q.append(S)
            # print(Q)
            Q = self.sortQ(Q, QT)
            # print(Q)
            As[p2.ID] = S
            prev[p2.ID] = p1
        else:
            if QT == 'LCPQ':
                costc1 = (costc[2],costc[0],costc[1])
                costpre1 = (costpre[2],costpre[0],costpre[1])
            else:
                costc1 = (costc[1],costc[0])
                costpre1 = (costpre[1],costpre[0])
            if costc1 < costpre1:
                # print('{}<{}'.format(costc,costpre))
                S = [p2, costc]
                Q.append(S)
                # print(Q)
                Q = self.sortQ(Q, QT)
                # print(Q)
                As[p2.ID] = S
                prev[p2.ID] = p1

    def getPath(self, pt, prev, ps):
        """ print('{',end='')
        for key, value in prev.items():
            if value != None:
                print("{}:{}, ".format(key,value.ID),end='')
            else:
                print("{}:{}, ".format(key,value),end='')
        print('}') """
        path = [pt.ID]
        p = pt
        while p.ID != ps.ID:
            p = prev[p.ID]
            if isinstance(p,door):
                path.append('d'+str(p.ID))
            else:
                path.append(p.ID)
        path.reverse()
        return path

    def search(self, ps, pt, tq, QT):
        Q = []#优先级队列
        prev = {}#记录每个节点的前驱
        for d in self.doors:
            prev[d.ID] = None
        prev[ps.ID] = None
        prev[pt.ID] = None
        """ A = []
        tq = datetime.strptime(tq, '%H:%M:%S')
        for tc in self.UTG:
            tc1 = datetime.strptime(tc, '%H:%M:%S')
            if tc1 <= tq:
                A.append(tc)
        tl = A[-1] """#算法这部分我觉得是错误的，我给他改为下面这部分
        #################################################
        t = []#所有分区的最新人口的时间
        for v in self.Vertexes:
            t.append(v.population[-1][1])
        for i in range(1, len(t)):#排序
            for j in range(0, len(t)-i):
                t1 = datetime.strptime(t[j], '%H:%M:%S')
                t2 = datetime.strptime(t[j+1], '%H:%M:%S')
                if t1 > t2:
                    t[j], t[j+1] = t[j+1], t[j]
        tl = t[-1]#所有分区的最新人口的时间的最大值
        #################################################
        ta = ''#到达时间，随着路径扩展逐渐扩大
        if QT == 'LCPQ':
            cost0 = (0, 0, 0)
        else:
            cost0 = (0, 0)
        S0 = [ps, cost0]
        As = {}#记录成本
        As[ps.ID] = S0
        Q.append(S0)
        mark = {}#存放标记
        for d in self.doors:
            mark[d.ID] = 0
        mark[ps.ID] = 0
        mark[pt.ID] = 0

        while len(Q) != 0:
            Si = Q[0]#优先级高的在队列头
            del Q[0]
            di = Si[0]
            if di.ID == pt.ID:
                return self.getPath(pt, prev, ps), Si[1]
            if di.ID == ps.ID:
                v = ps.v
            else:
                v = self.D2Pin(di)
                if prev[di.ID] != None:
                    ppre = []
                    p = di
                    while p.ID != ps.ID:
                        ppre.append(p)
                        p = prev[p.ID]
                    ppre.append(ps)
                    ppre = list(reversed(ppre))
                    """ for pi in ppre:
                        print(pi.ID,end=' ') """
                    for i in range(len(ppre)-1):
                        if self.D2D(ppre[i], ppre[i+1]) != None:  
                            for vk in v:
                                if vk.ID == self.D2D(ppre[i], ppre[i+1])[1].ID:
                                    v.remove(vk)
                        elif self.getEuclideanDist(ppre[i], ppre[i+1]) != None:
                            for vk in v:
                                if vk.ID == self.getEuclideanDist(ppre[i], ppre[i+1])[1].ID:
                                    v.remove(vk)
                if len(v) == 1:
                    v = v[0]
                elif len(v) == 0:
                    continue
                else:#这部分是以防万一排查bug的，正常不会运行
                    vID = []
                    print(len(v))
                    for i in range(len(v)):
                        print(type(v[i]))
                        vID.append(v[i].ID)
                    print('vID:', vID)
                    print(di.ID)
                #v = v[0]

            mark[di.ID] = 1
            T = []
            if isinstance(tq, str):
                tq = datetime.strptime(tq, '%H:%M:%S')
            #print(datetime.strftime(tq + timedelta(seconds = Si[1][1]), '%H:%M:%S'))
            for t in self.UTG:
                t1 = datetime.strptime(t, '%H:%M:%S')
                if t1 <= tq + timedelta(seconds = Si[1][1]):
                    T.append(t)
            ta = T[-1]
            if (datetime.strptime(ta, '%H:%M:%S') > 
                datetime.strptime(tl, '%H:%M:%S')):       
                self.populationGlobal(ta)
                tl = ta
            doors = [self.P2Ein(pt.v)[i].dk for i 
                     in range(len(self.P2Ein(pt.v)))]
            if di in doors:
                self.expand(di, pt, v, ta, Si, QT, As, Q, prev)
            doors1 = [self.P2Eout(v)[i].dk for i 
                      in range(len(self.P2Eout(v)))]
            for dj in doors1:
                if mark[dj.ID] == 0:
                    self.expand(di, dj, v, ta, Si, QT, As, Q, prev)
    
def main():
    g = loadVariable('cphG0.txt')
    g.printGraph()

if __name__ == "__main__":
    main()

    