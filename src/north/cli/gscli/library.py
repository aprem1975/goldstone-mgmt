from enum import Enum

import sys
import subprocess
import logging

stdout = logging.getLogger('stdout')

def tabular(diclst, c_name):

    rows=[]
    diclst_1=[]
    rwid=[0]*len(diclst)
    
    for i in diclst:
        d1=i.copy()
        for j in d1:
            if type(d1[j])==type([]):
                for k in range(len(d1[j])):
                    if type(d1[j][k]) != type('1'):
                        d1[j][k]=str(d1[j][k])
            elif type(d1[j])!=type('1'):
                d1[j]=str(d1[j])
        diclst_1.append(d1)

    cwid=[0]*len(c_name)

    for i in range(len(c_name)):
        if cwid[i]<len(c_name):
            cwid[i]=len(c_name[i])

    for i in range(len(diclst_1)):
        ii=0
        for j in diclst_1[i]:
            if type(diclst_1[i][j])==type([]):
                if len(diclst_1[i][j])>rwid[i]:
                    rwid[i]=len(diclst_1[i][j])
                for k in range(len(diclst_1[i][j])):
                    if cwid[ii]<len(diclst_1[i][j][k]):
                        cwid[ii]=len(diclst_1[i][j][k])
            elif cwid[ii]<len(diclst_1[i][j]):
                cwid[ii]=len(diclst_1[i][j])
            ii+=1
    print(rwid)
    cwid=[i+4 for i in cwid]

    row_bod="+"
    for i in range(len(c_name)):
        row_bod=row_bod+'-'*cwid[i]+'+'
    rows=[row_bod]

    row_bod1="+"
    for i in range(len(c_name)):
        row_bod1=row_bod1+'='*cwid[i]+'+'
    rows=[row_bod1]

    rows=[row_bod]

    row_='|'
    for i in range(len(c_name)):
        row_=row_+' '+c_name[i]+' '*(cwid[i]-len(c_name[i])-1)+'|'

    rows.append(row_)
    rows.append(row_bod1)

    for i in range(len(diclst_1)):
        row='|'
        ii=0
        for k in diclst_1[i]:
            if type(diclst_1[i][k])==type([]):
                if len(diclst_1[i][k]) == 0:
                    row=row+' '*cwid[ii]+'|'
                else:
                    row=row+' '+diclst_1[i][k][0]+' '*(cwid[ii]-len(diclst_1[i][k][0])-1)+'|'
            else:
                row=row+' '+diclst_1[i][k]+' '*(cwid[ii]-len(diclst_1[i][k])-1)+'|'
            ii+=1
        rows.append(row)
        for j in range(1,rwid[i]):
            ii=0
            row='|'
            for k in diclst_1[i]:
                if type(diclst_1[i][k])==type([]) and j<len(diclst_1[i][k]):
                    row=row+' '+diclst_1[i][k][j]+' '*(cwid[ii]-len(diclst_1[i][k][j])-1)+'|'
                else:
                    row=row+' '*cwid[ii]+'|'
                ii+=1
            rows.append(row)
        rows.append(row_bod)
    if diclst==[]:
        row='|'
        for k in range(len(c_name)):
            row = row + ' '*cwid[k]+'|'
        rows.append(row)
        rows.append(row_bod)
    return '\n'.join(rows)
