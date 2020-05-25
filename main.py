import numpy as np
import pandas as pd
from Cointegrated_Pairs import Cointegrated_Pairs
from Pair_Trading import Pair_Trading


""""
    P_VALUE -> the p-value chosen for the ADF test to check for stationarity and non-stationarity
    BALANCE_IN -> Balance available to invest in each cointegrated pair (Mexican Pesos)
    MIN_INS -> Minimum revenue that a cointegrated pair needs to obtain in the insample period to be considered in the testing/onsample period (Mexican Pesos)
    STD_BOUNDS -> # of standard deviations needed to open a position (long and short)
    CLOSE_SP -> # of standard deviations from the mean to close the short position
    CLOSE_LP -> # of standard deviations from the mean to close the long position

    DATA:
        - file_ins -> stocks from the Mexican Price Consumer Index for the insample/training period
        - file_out -> stocks from the Mexican Price Consumer Index for the onsample/testing period
        -----> Only those stocks in the Index with more than 230 records for the onsample period are considered
        Obtained from Bloomberg and Yahoo Finance
""""

values = {'P_VALUE' : 0.01, 'BALANCE_IN' : 100000,'MIN_INS' : 20000, 'STD_BOUNDS': 1, 'CLOSE_SP': 0.5, 'CLOSE_LP': 0.5}

file_ins = ['2006_insample.xls','2007_insample.xls','2008_insample.xls','2009_insample.xls','2010_insample.xls','2011_insample.xls']
file_out = ['2006_onsample.xls','2007_onsample.xls','2008_onsample.xls','2009_onsample.xls','2010_onsample.xls','2011_onsample.xls']
i=0

while i <len(file_ins):
    data_ins = pd.read_excel('Data csv'+'/'+file_ins[i],index_col ='Date', parse_dates=True)
    data_out = pd.read_excel('Data csv'+'/'+file_out[i],index_col ='Date', parse_dates=True)
    pcp = Cointegrated_Pairs(data_ins, values['P_VALUE'])

    # balance_ins_vec[] is where the balance at the end of the insample period is saved with the info for the cointegrated pair
    # that has a minimum revenue in the insample/training period of MIN_INS
 
    balance_ins_vec = []
    for info in pcp.insacoint_pairs():
        aux_1 = Pair_Trading(data_ins, info)
        if aux_1.buy_sell()[2]>= values['MIN_INS']:
            ins_info =(info, aux_1.buy_sell())
            balance_ins_vec.append(ins_info)
    print(len(balance_ins_vec))            

    # balance_out_vec[] es donde guardo el balance al final del onsample y la info
    # de la pareja cointegrada
    balance_out_vec = []
    profit = 0
    c = 0
    for in_info in balance_ins_vec:
        if(in_info[0][0] and in_info[0][1]) in data_out.columns:
            aux_2 = Pair_Trading(data_out, in_info[0])
            out_info =(in_info[0], aux_2.buy_sell())
            balance_out_vec.append(out_info)
            if out_info[1][2]!=values['BALANCE_IN']:
                profit = profit + out_info[1][2]
                c+=1

    year= 2006+i
    print("Cointegrated Pairs {}".format(year))
    print("Total Profit:{}".format(profit))
    for b in balance_out_vec:
        print("{} y {}: {} - ({} + {} * {})".format(b[0][0],b[0][1],b[0][0],b[0][2],b[0][3],b[0][1]))
        print("Open Positions: {}".format(b[1][0]))
        print("Profit: $ {}".format(b[1][2]))
    i+=1
