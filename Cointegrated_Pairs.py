import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from scipy import stats

class Cointegrated_Pairs:
    def __init__(self, data_ins, P_VALUE):
        self.data_ins = data_ins
        self.P_VALUE = P_VALUE    

    def adf_check(self, time_series, var):
        """
            Checks if the time series is stationary (0) or non-stationary (1)
            Augmented Dicky-Fuller Test
        """

        result = adfuller(time_series, maxlag= None, regression = var ,autolag = 'AIC', store= False)
        # result = (adf, pvalue, usedlag, nobs, critical_values, icbest, resstore)
        # Condition to check stationarity -> we are looking for those non-stationary so return =1
        if result[1] <= self.P_VALUE and result[0]<= result[4]['1%']:
            return 0
        else:
            return 1

    def insacoint_pairs(self):
        """
            Obtains the pairs of stocks for insample/training period with their corresponding values 
            for the onsample/testing period
            1) Checks that the series are non-stationary
            2) Calculates the possible pairs of stocks from the non-stationary series
            3) Checks that the pairs are cointegrated by looking for stationarity in the residuals 
               of the linear combination
            4) Calculates the mean and the std deviation of the residuals for each pair of stocks
            5) Returns a tuple with the folowing values:
               (sy, sx, intercept, slope, mean_ce, std_ce)

        """
        # Runs the adf_check and keeps only those that are non-stationary
        for s_c in self.data_ins:
            if self.adf_check(self.data_ins[s_c],'ct') ==0:
                self.data_ins.drop(s_c,axis=1,inplace=True)
        
        # Creates a list of all possible pairs of those series that are non-stationary
        pairs = []
        for s1 in self.data_ins:
            for s2 in self.data_ins:
                if s1 != s2:
                    pairs.append((s1,s2))

        # Checks which pairs are cointegrated
        coint_pairs = []
        for (sy,sx) in pairs:
            slope, intercept, _, _, _ = stats.linregress(self.data_ins[sx],self.data_ins[sy])
            res = ( self.data_ins[sy] - (intercept + slope * self.data_ins[sx]))
            ## Check if the slope is negative and only consider those that have a positive slope Pl = alfa*(Ps)
            if slope >0:
                ### Check if the residuals are stationary using the ADF test -> if they are stationary it means the pair is cointegrated
                if self.adf_check(res,'c') == 0:
                    #result = adfuller(res, maxlag = None, regression = 'ct', store= False)
                    #print("{}-{}".format(sy,sx))
                    #print(result)

                    # Calculates the mean and the std deviation for the cointegrated pairs
                    mean_ce = (self.data_ins[sy]-(intercept + (slope * self.data_ins[sx]))).mean()
                    std_ce =0
                    for i in range(len(self.data_ins[sy])):
                        std_ce = std_ce + ((self.data_ins[sy].iloc[i]-(intercept + slope * self.data_ins[sx].iloc[i])) - mean_ce)**2

                    std_ce = (std_ce / len(self.data_ins[sy]))**.5
                    coint_pairs.append((sy,sx,intercept,slope,mean_ce,std_ce))

        # Returns a list of tuples with (sy, sx, intercept, slope, mean_ce, std_ce)              
        return coint_pairs
