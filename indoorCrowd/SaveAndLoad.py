import pickle
def saveVariable(G_list,filename):
    f = open(filename,'wb')          
    pickle.dump(G_list,f)           
    f.close()                       
    return filename

def loadVariable(filename):
    try:
        f = open(filename,'rb+')
        r = pickle.load(f)
        f.close()
        return r
    except EOFError:
        return "file is empty."