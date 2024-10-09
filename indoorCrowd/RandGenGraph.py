import random
from Edge import Edge
from door import door
from Vertex import Vertex
from Graph import Graph

def generateGraph(ID, v_num, start, source_num=0, end_num=0,Alpha=random.random(),Beta=1):
    #生成了所有分区都连通的室内拓扑结构以及人群模型，百分百搜得到路径
    e_num = round((v_num-1)*(2+Alpha*(v_num-2)))
    D = []
    V = []
    E = []
    for i in range(v_num):
        v_area = random.randint(1000, 3000)
        v_type = 'R'
        v_startp = random.randint(0, int(v_area*1500/20000))
        V.append(Vertex(i+1,v_area,[],v_type,v_startp))

    v_choice = V.copy()
    graph = [random.choice(v_choice)]#先选两个分区，使之连通
    v_choice.remove(graph[0])
    graph.append(random.choice(v_choice))
    v_choice.remove(graph[1])
    D.append(door(len(D)+1,random.randint(1, 4)))
    E.append(Edge(len(E)+1,D[-1],graph[0],graph[1],random.randint(1, 3)))
    E.append(Edge(len(E)+1,D[-1],graph[1],graph[0],random.randint(1, 3)))
    graph[0].Md2d.append(D[-1])
    graph[1].Md2d.append(D[-1])

    while len(v_choice) != 0:
        #再从剩下的分区里选一个出来，使之既能进入前面两分区组成的整体，也能离开这个整体
        #把这个分区加入到这个整体，继续从剩下的分区中选分区继续上述操作，直至分区用完
        choice0 = random.choice(v_choice)
        choice1 = random.choice(graph)
        if random.random() < Beta:
            choice2 = choice1
        else:
            graph.remove(choice1)
            choice2 = random.choice(graph)
            graph.append(choice1)
        graph.append(choice0)
        v_choice.remove(choice0)
        D.append(door(len(D)+1,random.randint(1, 4)))
        E.append(Edge(len(E)+1,D[-1],choice0,choice1,random.randint(1, 3)))
        choice0.Md2d.append(D[-1])
        choice1.Md2d.append(D[-1])
        if choice1.ID == choice2.ID:
            E.append(Edge(len(E)+1,D[-1],choice1,choice0,random.randint(1, 3)))
        else:
            D.append(door(len(D)+1,random.randint(1, 4)))
            E.append(Edge(len(E)+1,D[-1],choice2,choice0,random.randint(1, 3)))
            choice0.Md2d.append(D[-1])
            choice2.Md2d.append(D[-1])

    v_choice = V.copy()
    while e_num > len(E):#如果还没达到边的下界，继续随机选两分区添加边
        choice1 = random.choice(v_choice)
        v_choice.remove(choice1)
        choice2 = random.choice(v_choice)
        flag = 0
        flag1 = 0
        for e in E:
            if (e.vi.ID == choice1.ID and e.vj.ID == choice2.ID
                ) or (e.vj.ID == choice1.ID and e.vi.ID == choice2.ID):
                flag = 1
                if e.vi.ID == choice1.ID and e.vj.ID == choice2.ID:
                    flag1 = 1
                    samedoor = e.dk
                    break
                else:
                    samedoor = e.dk
                    break
        if flag == 1:
            if flag1 == 1:
                for e in E:
                    if e.vj.ID == choice1.ID and e.vi.ID == choice2.ID:
                        flag = 0
                        break
            else:
                for e in E:
                    if e.vi.ID == choice1.ID and e.vj.ID == choice2.ID:
                        flag = 0
                        break
            if flag == 1:
                if flag1 == 1:
                    E.append(Edge(len(E)+1,samedoor,choice2,choice1,random.randint(1, 3)))
        else:
            if random.random() < Beta:
                D.append(door(len(D)+1,random.randint(1, 4)))
                E.append(Edge(len(E)+1,D[-1],choice1,choice2,random.randint(1, 3)))
                E.append(Edge(len(E)+1,D[-1],choice2,choice1,random.randint(1, 3)))
                choice1.Md2d.append(D[-1])
                choice2.Md2d.append(D[-1])
            else:
                D.append(door(len(D)+1,random.randint(1, 4)))
                E.append(Edge(len(E)+1,D[-1],choice1,choice2,random.randint(1, 3)))
                choice1.Md2d.append(D[-1])
                choice2.Md2d.append(D[-1])
        v_choice.append(choice1)
    
    v_choice = V.copy()
    for _ in range(source_num):#添加人流源
        D.append(door(len(D)+1,random.randint(1, 4)))
        choice = random.choice(v_choice)
        E.append(Edge(len(E)+1,D[-1],None,choice,random.randint(1, 3)))
        choice.Md2d.append(D[-1])
        v_choice.remove(choice)
    v_choice = V.copy()
    for _ in range(end_num):#添加人流终点
        D.append(door(len(D)+1,random.randint(1, 4)))
        choice = random.choice(v_choice)
        E.append(Edge(len(E)+1,D[-1],choice,None,random.randint(1, 3)))
        choice.Md2d.append(D[-1])
        v_choice.remove(choice)

    for elem in V:#把门的距离添加上
        if len(elem.Md2d) == 1:
            elem.Md2d.clear()
        else:
            Md2d = []
            while len(elem.Md2d) != 1:
                di = elem.Md2d.pop()
                for dj in elem.Md2d:
                    dist = random.randint(round(elem.area**0.5/2), round(1.4*elem.area**0.5))
                    Md2d.append([di,dj,dist])
                    Md2d.append([dj,di,dist])
            elem.Md2d = Md2d.copy()
    for elem in V:#从一进一出的分区随机选作Q型分区
        if len(elem.Md2d)==2:
            """ change = random.randint(1,2)
            if change==1:
                elem.type = "Q" """
            elem.type = "Q"
    if len(D)!=D[-1].ID:
        print('{},{}'.format(len(D), D[-1].ID))
        return
    for d in D:
        bit = 0
        for e in E:
            if e.dk.ID==d.ID:
                bit = 1
        if bit == 0:
            print('error')
            return

    G1 = Graph(ID,V,E,start)
    return G1
