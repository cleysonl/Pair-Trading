import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Cointegrated_Pairs import Cointegrated_Pairs
from Pair_Trading import Pair_Trading


values = {'P_VALUE' : 0.01, 'BALANCE_IN' : 100000,'MIN_INS' : 20000, 'STD_BOUNDS': 1, 'CLOSE_SP': 0.5, 'CLOSE_LP': 0.5}
""""
    P_VALUE -> the p-value chosen for the ADF test to check for stationarity and non-stationarity
    BALANCE_IN -> Balance available to invest in each cointegrated pair (Mexican Pesos)
    MIN_INS -> Minimum revenue that a cointegrated pair needs to obtain in the insample period to be considered in the testing/onsample period (Mexican Pesos)
    STD_BOUNDS -> # of standard deviations needed to open a position (long and short)
    CLOSE_SP -> # of standard deviations from the mean to close the short position
    CLOSE_LP -> # of standard deviations from the mean to close the long position
""""

# Files corresponding to the year we want to focus to graph a particular pair of stocks
# To change the year just change 'XXXX_insample.xls" and 'XXXX_onsample.xls" where XXXX is the year
file_ins = ['2008_insample.xls']
file_out = ['2008_onsample.xls']
i=0
while i <len(file_ins):
    data_ins = pd.read_excel('Data csv'+'/'+file_ins[i],index_col ='Date', parse_dates=True)
    data_out = pd.read_excel('Data csv'+'/'+file_out[i])
    data_out['Date'] = pd.to_datetime(data_out['Date'])
    index_data = data_out['Date']
    data_out.set_index('Date',inplace=True)
    pcp = Cointegrated_Pairs(data_ins, values['P_VALUE'])
    
# balance_ins_vec[] is where the balance at the end of the insample period is saved with the info for the cointegrated pair
    balance_ins_vec = []
    for info in pcp.insacoint_pairs():
        aux_1 = Pair_Trading(data_ins, info)
        ins_info =(info, aux_1.buy_sell())
        balance_ins_vec.append(ins_info)

# Pair of stocks to be used for the graph
    y = 'GFNO'
    x = 'ALSE'

    balance_out_vec = []
    profit = 0
    c = 0
    for in_info in balance_ins_vec:
        if(in_info[0][0] == y and in_info[0][1]== x):
            aux_2 = Pair_Trading(data_out, in_info[0])
            out_info =(in_info[0], aux_2.buy_sell())
            balance_out_vec.append(out_info)
            print(len(data_out))
            print("t_o: {}".format(out_info[1][4]))
            print("t_c: {}".format(out_info[1][5]))
            print("pos_bal: {}".format(out_info[1][6]))
            print("ps_pl: {}".format(out_info[1][7]))
            print("s_l: {}".format(out_info[1][8]))
            print("{} y {} 2008: {} - ({} + {} * {})".format(y,x,y,out_info[0][2],out_info[0][3],x))
            upper_band = np.zeros(len(data_out[x]))+(out_info[0][4] + values['STD_BOUNDS']*out_info[0][5])
            lower_band = np.zeros(len(data_out[x]))+(out_info[0][4] - values['STD_BOUNDS']*out_info[0][5])
            s_pos = np.zeros(len(data_out[x]))+(out_info[0][4] + values['CLOSE_SP']*out_info[0][5])
            l_pos = np.zeros(len(data_out[x]))+(out_info[0][4] - values['CLOSE_LP']*out_info[0][5])
            z_score = out_info[1][3]

            ###Graph z(t), upper_band = mean + STD_BOUNDS* std , lower_band = mean - STD_BOUNDS* std
            ### Lines to close the short position (s_pos) and long position (l_pos)
            graf_table = pd.DataFrame({'upper_band'u: upper_band,'lower_band': lower_band, 's_pos':s_pos,'l_pos':l_pos,'z_score':z_score,'Date' : index_data})
            graf_table['Date'] = pd.to_datetime(graf_table['Date'])
            graf_table.set_index('Date',inplace=True)
            graf_table[['Upper_band','lower_band','s_pos','l_pos','z_score']].plot(figsize = (16,6))
            plt.xlabel('Dates')
            plt.ylabel('z(t)')
            plt.title("{} y {} 2008: {} - ({} + {} * {})".format(y,x,y,out_info[0][2],out_info[0][3],x))
            plt.show()
    i+=1
