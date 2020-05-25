import numpy as np
import pandas as pd
import math
import csv

class Pair_Trading:
    
    def __init__(self, data, info, BALANCE_IN =100000, STD_BOUNDS= 1.0, CLOSE_SP=0.5, CLOSE_LP=0.5):
        self.data = data
        self.info = info
        self.balance = BALANCE_IN
        self.STD_BOUNDS = STD_BOUNDS
        self.CLOSE_SP = CLOSE_SP
        self.CLOSE_LP = CLOSE_LP


    def open_pos_s(self, pos_bal,i):
        s = pos_bal[-1] / self.data[self.info[0]].iloc[i]
        l = (pos_bal[-1] * self.info[3] * s) / (pos_bal[-1] - self.info[2] * s)
        aux_pos ='u'
        return (s, l, aux_pos)

    def open_pos_l(self, pos_bal,i):
        l = pos_bal[-1] / self.data[self.info[1]].iloc[i]
        s = (pos_bal[-1] * l) / ( pos_bal[-1] * self.info[3] + self.info[2]*l)
        aux_pos ='d'
        return (s, l, aux_pos)

    def close_pos_s(self, pos_bal, i, ps_pl, s_l):
            self.balance = ((ps_pl[-1][0] - self.data[self.info[0]].iloc[i]) * s_l[-1][0] + (self.data[self.info[1]].iloc[i]-ps_pl[-1][1]) * s_l[-1][1]) + pos_bal[-1] - (ps_pl[-1][1] * s_l[-1][1])
            aux_pos ='n'
            return(self.balance, aux_pos)

    def close_pos_l(self,pos_bal,i,ps_pl,s_l):
            self.balance = ((self.data[self.info[0]].iloc[i]-ps_pl[-1][0])* s_l[-1][0] + (ps_pl[-1][1]-self.data[self.info[1]].iloc[i])* s_l[-1][1])+ pos_bal[-1]-(ps_pl[-1][0]* s_l[-1][0])
            aux_pos ='n'
            return (self.balance,aux_pos)

    #### Cashless investment
    def buy_sell(self):
        aux_pos ='n'
        i=0
        z_score = np.zeros(len(self.data[self.info[0]]))
        pos_bal = []
        t_o = []
        t_c = []
        s_l = []
        ps_pl = []
        while i < (len(self.data[self.info[0]])):
            pos_bal.append(self.balance)
            z_score[i] = ((self.data[self.info[0]].iloc[i]-(self.info[2] + (self.info[3] * self.data[self.info[1]].iloc[i])))-self.info[4])/self.info[5]
            # Opens position if in t=0 z_score is above (mean + STD_BOUNDS) or below (mean - STD_BOUNDS)
            if (i == 0 and z_score[i] >= self.info[4] + self.STD_BOUNDS*self.info[5]):
                s, l, aux_pos = self.open_pos_s(pos_bal,i)
                s_l.append((s,l))
                ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                t_o.append(i)
            elif(i==0 and z_score[i] <= self.info[4] - self.STD_BOUNDS*self.info[5]):
                s, l, aux_pos = self.open_pos_l(pos_bal,i)
                s_l.append((s,l))
                ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                t_o.append(i)
            else:
                # Opens position if z_score[i-1] is below mean + STD_BOUND and z_score[i] is above it
                # 2 cases: 1) jumps from below mean -STD_BOUND or 2) from between mean - STD_BOUND and mean + STD_BOUND
                if (z_score[i-1] < (self.info[4] + self.STD_BOUNDS*self.info[5]) and z_score[i]>= (self.info[4] + self.STD_BOUNDS*self.info[5]) and i+1 < len(self.data[self.info[0]])):
                    if aux_pos == 'n':
                        s, l, aux_pos = self.open_pos_s(pos_bal,i)
                        s_l.append((s,l))
                        ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                        t_o.append(i)
                    elif aux_pos =='d':
                        self.balance, aux_pos = self.close_pos_l(pos_bal,i,ps_pl,s_l)
                        ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                        t_c.append(i)
                        pos_bal.append(self.balance)
                        s, l, aux_pos = self.open_pos_s(pos_bal,i)
                        s_l.append((s,l))
                        ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                        t_o.append(i)
                # Opens position if z_score[i-1] is above mean - STD_BOUND and z_score[i] is below it
                # 2 cases: 1) jumps from above (mean + STD_BOUND) or 2) from between mean - STD_BOUND and mean + STD_BOUND        
                elif (z_score[i-1] > (self.info[4] - self.STD_BOUNDS*self.info[5]) and z_score[i] <= (self.info[4] - self.STD_BOUNDS*self.info[5]) and i+1 < len(self.data[self.info[0]])):
                    if aux_pos == 'n':
                        s, l, aux_pos = self.open_pos_l(pos_bal,i)
                        s_l.append((s,l))
                        ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                        t_o.append(i)
                    elif aux_pos =='u':
                        self.balance, aux_pos = self.close_pos_s(pos_bal,i,ps_pl,s_l)
                        ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                        t_c.append(i)
                        pos_bal.append(self.balance)
                        s, l, aux_pos = self.open_pos_l(pos_bal,i)
                        s_l.append((s,l))
                        ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                        t_o.append(i)
                else:
                    # Closes the position if z_score[i-1] is above CLOSE_SP and z_zero[i] is below CLOSE_SP
                    if ((z_score[i-1] > self.info[4] + self.CLOSE_SP*self.info[5] and z_score[i] <= self.info[4] + self.CLOSE_SP*self.info[5]) and i+1 < len(self.data[self.info[0]])):
                        if aux_pos == 'u':
                            self.balance, aux_pos = self.close_pos_s(pos_bal,i,ps_pl,s_l)
                            ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                            t_c.append(i)
                            pos_bal.append(self.balance)
                    # Closes the position if z_score[i-1] is below CLOSE_LP and z_zero[i] is above CLOSE_LP        
                    elif((z_score[i-1] < self.info[4] - self.CLOSE_LP*self.info[5] and z_score[i] >= self.info[4] - self.CLOSE_LP*self.info[5]) and i+1 < len(self.data[self.info[0]])):
                        if aux_pos == 'd':
                            self.balance, aux_pos = self.close_pos_l(pos_bal,i,ps_pl,s_l)
                            ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                            t_c.append(i)
                            pos_bal.append(self.balance)
                    else:
                    # Checks if for the last i a position is needed
                    # Opens and closes the position
                        if(i+1 ==len(self.data[self.info[0]])):
                            if (z_score[i-1] < (self.info[4] + self.STD_BOUNDS*self.info[5]) and z_score[i]>= (self.info[4] + self.STD_BOUNDS*self.info[5])):
                                s, l, aux_pos = self.open_pos_s(pos_bal,i)
                                s_l.append((s,l))
                                ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                                t_o.append(i)
                                self.balance, aux_pos = self.close_pos_s(pos_bal,i,ps_pl,s_l)
                                ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                                t_c.append(i)
                                pos_bal.append(self.balance)
                            elif (z_score[i-1] > (self.info[4] - self.STD_BOUNDS*self.info[5]) and z_score[i] <= (self.info[4] - self.STD_BOUNDS*self.info[5])):
                                s, l, aux_pos = self.open_pos_l(pos_bal,i)
                                s_l.append((s,l))
                                ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                                t_o.append(i)
                                self.balance, aux_pos = self.close_pos_l(pos_bal,i,ps_pl,s_l)
                                ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                                t_c.append(i)
                                pos_bal.append(self.balance)
                            else:
                                if aux_pos == 'u':
                                    self.balance, aux_pos = self.close_pos_s(pos_bal,i,ps_pl,s_l)
                                    ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                                    t_c.append(i)
                                    pos_bal.append(self.balance)
                                elif aux_pos == 'd':
                                    self.balance, aux_pos = self.close_pos_l(pos_bal,i,ps_pl,s_l)
                                    ps_pl.append((self.data[self.info[0]].iloc[i],self.data[self.info[1]].iloc[i]))
                                    t_c.append(i)
                                    pos_bal.append(self.balance)

            i+=1
        return (len(t_o),len(t_c),pos_bal[-1],z_score,t_o,t_c,pos_bal,ps_pl,s_l)    