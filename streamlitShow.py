import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime 
import time
import sys
sys.path.append("CAIPPP")
from dataGen.cph.cphCrowdModelGen import generateIndoorCrowd 
from dataGen.cph.cphGen import generateIndoorSpace
# from indoorCrowd.RandGenGraph import generateGraph
from indoorCrowd.SaveAndLoad import *


st.title('Welcome to Our Website on Indoor Crowd Modeling')
st.write('Our website presents the research findings of our project, "Towards Crowd-aware Indoor Path Planning". We are eager to share our results with you and hope you find them informative and insightful.')
st.write('On the left-hand side, you will find several useful functions related to our project. Please click on them to discover more.')

st.set_option('deprecation.showPyplotGlobalUse', False)

functions = ['Homepage','Indoor Geometry','Indoor Crowd-Evolution','Indoor Topology',
            'Time-evolving Population Estimator','Query Processing']



box = st.sidebar.radio("What type of function would you like to explore?", functions)

if box==functions[1]:
    st.write('-----------------------------------------------------------------------')
    st.header('1. Indoor Geometry')
    radio = st.radio('There is a indoor structure named CPH, do you want to draw it to see?', ['No','Yes'])
    if radio=='Yes':
        s = generateIndoorSpace('CPH', 0, 1,
                            'CAIPPP\inputfiles\CPH\RParINFO_diType_1.txt', 
                            'CAIPPP\inputfiles\CPH\RDoorINFO_diType_1.txt')
        saveVariable(s,'CAIPPP\saveVariable\cph.txt')
        fig = s.drawIndoorSpace()
        st.pyplot(fig)

if box==functions[2]:
    st.write('-----------------------------------------------------------------------')
    st.header('2. Indoor Crowd-Evolution')
    st.write('Sorry, this function is not ready.')

if box==functions[3]:
    st.write('-----------------------------------------------------------------------')
    st.header('3. Indoor Topology')
    radio = st.radio('There is a indoor structure named CPH, do you want to generate a indoor crowd model by using it?', ['No','Yes'])
    if radio=='Yes':
        s = loadVariable('CAIPPP\saveVariable\cph.txt')
        G0 = generateIndoorCrowd(s)
        saveVariable(G0,'CAIPPP\saveVariable\G0.txt')
        HtmlFile = G0.drawGraph()
        components.html(HtmlFile,height = 600)
    """  else:
        st.write('You can generate an indoor topology by simply setting the parameters below.')
        num_v = st.selectbox('Enter the number of partitions, ranging from 5 to 16: ', list(range(5, 100)))
        num_source = st.selectbox('Enter the number of population sources, which should not exceed the first parameter:', list(range(0, 100-num_v)))
        num_end = st.selectbox('Enter the number of population endpoints, which should not exceed the first parameter:', list(range(0, 100-num_v-num_source)))
        Alpha = st.number_input('Enter a number ranging from 0 to 1 to determind the density of the network: ')
        Beta = st.number_input('Enter a number ranging from 0 to 1 to determind the proportion of directed edges in the network: ')
        G0 = generateGraph('G0', num_v, '00:00:00',num_source,num_end,Alpha,Beta)
        saveVariable(G0,'CAIPPP\saveVariable\G0.txt')
        HtmlFile = G0.drawGraph() 
        components.html(HtmlFile,height = 600)
 """
if box==functions[4]:
    st.write('-----------------------------------------------------------------------')
    st.header('4. Time-evolving Population Estimator')
    st.write('Before using the time-evolving population estimating function, please make sure to run the third function to generate the G0 model.')
    radio = st.radio('Have you generated the G0 model? If so, would you like to use it for time-evolving population estimating?', ['No','Yes'])
    if radio=='Yes':
        G0 = loadVariable('CAIPPP\saveVariable\G0.txt')
        a = G0.ID
        HtmlFile = G0.drawGraph()
        if st.checkbox("Show the model {}".format(a)):
            components.html(HtmlFile,height = 600)
        kind = st.selectbox("Which time-evolving population estimator would you like to use?", ['global estimator','local estimator'])
        if kind=='global estimator':
            time1 = st.time_input("Enter the time at which you would like to know the population, ranging from G0.start to (G0.start + 10min):",datetime.time(0,15))
            ta = time1.strftime("%H:%M")+':00'
            if st.button('start estimator'):
                time_start = time.time()
                dict = G0.populationGlobal(ta)
                print('the populationGlobal costs {}s.'.format(time.time()-time_start))
                st.write("Here is a dictionary recording the population information for each partition.")
                st.write(dict)
                html = G0.drawPopulationLine()
                components.html(html,width=800,height = 600)
        else:
            vID = st.selectbox("Enter the ID of the partition for which you want to know the population. The ID should be an integer.",list(range(1,len(G0.Vertexes)+1)))
            time1 = st.time_input("Enter the time at which you would like to know the population, ranging from G0.start to (G0.start + 10min):",datetime.time(0,15))
            ta = time1.strftime("%H:%M")+':00'
            if st.button('start estimator'):
                time_start = time.time()
                p = G0.populationLocal(vID,ta)
                print('the populationLocal costs {}s.'.format(time.time()-time_start))
                st.write("The population of v{} at time {} is {}".format(str(vID),ta,p))
                html = G0.drawPopulationLine()
                components.html(html,width=800,height = 600)

if box==functions[5]:
    st.write('-----------------------------------------------------------------------')
    st.header('5. Query Processing')
    st.write("In order to perform query processing, you need to run the third function to generate model G0 if you haven't done so already.")
    radio = st.radio('If you have generated a G0 model, do you want to do query processing on it?', ['No','Yes'])
    if radio=='Yes':
        G0 = loadVariable('CAIPPP\saveVariable\G0.txt')
        a = G0.ID
        HtmlFile = G0.drawGraph()
        if st.checkbox("Show the model {}".format(a),key=1):
            components.html(HtmlFile,height = 600)
        v1ID = st.selectbox("Enter the ID of the partition that contains the first point. The ID should be an integer:", list(range(1, len(G0.Vertexes)+1)))  
        v2ID = st.selectbox("Enter the ID of the partition that contains the second point. The ID should be an integer:", list(range(1, len(G0.Vertexes)+1))) 
        start_time = st.time_input("Enter the time for your query, ensuring that it falls between G0.start and (G0.start + 9 minutes):",datetime.time(0,15)) 
        type = st.radio('Enter the query type: ',['LCPQ','FPQ']) 
        ps, pt = G0.getTwoPoints(v1ID, v2ID)
        tq = start_time.strftime("%H:%M")+':00'
        st.write(tq)
        if st.button('start query processing'):
            time_start = time.time()
            result = G0.search(ps,pt,tq,type)
            print('query processing costs {}s.'.format(time.time()-time_start))
            st.write("{}'s v is v{}, dist:".format(ps.ID,ps.v.ID))
            st.write(pd.DataFrame([['d'+str(dist[0].ID), dist[1]] for dist in ps.dist]))
            
            st.write("{}'s v is v{}, dist:".format(pt.ID,pt.v.ID))
            st.write(pd.DataFrame([['d'+str(dist[0].ID), dist[1]] for dist in pt.dist]))
            if result != None:
                st.write('path: {}'.format(result[0]))
                if len(result[1])==2:
                    st.write('dist: {}m, time: {}s'.format(result[1][0],result[1][1]))
                else:
                    st.write('dist: {}m, time: {}s, contact: {}'.format(result[1][0],result[1][1],result[1][2]))
            else:
                st.write('No path.')
        st.write('------------------------------------------------')
