# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
import math
from scipy.stats import norm

class Option:
    def __init__(self, parameter_dict):
        pass

class EuropeanOption(Option):
    def __init__(self, parameter_dict):
        pass

    def payoff(self):
        pass

class EuropeanCall(EuropeanOption):
    def __init__(self, parameter_dict):
        self.K = parameter_dict['K']
        self.T = parameter_dict['T']
        self.t = parameter_dict['t']
        self.r = parameter_dict['r']            # annual interest rate

    def payoff(self, ST):
        return max(ST-self.K, 0)

    def PriceByPath(self, path):
        payoff=0
        for i in range(len(path[-1])):
            payoff += self.payoff(path[-1][i])
        return payoff/len(path[-1])*math.exp(-self.r*(self.T-self.t)/252)                           # matching discouting method with divident?

class BarrierOption(Option):
    def __init__(self, parameter_dict):
        pass
    def payoff(self):
        pass

class UpandOutCall(BarrierOption):
    def __init__(self, parameter_dict):
        self.K = parameter_dict['K']
        self.T = parameter_dict['T']
        self.t = parameter_dict['t']
        self.r = parameter_dict['r']
        self.B = parameter_dict['B']            # barrier level

    def payoff(self, ST):
        return max(ST - self.K, 0)

    def PriceByPath(self, path):
        payoff=0
        for i in range(len(path[-1])):
            payoff_i = self.payoff(path[-1][i])
            if payoff_i>0 and max(path[:,i])<self.B:
                payoff += payoff_i
        return payoff/len(path[-1])*math.exp(-self.r*(self.T-self.t)/252)

class PricingModel:
    def __init__(self, option):
        pass

    def path(self):
        pass

class Monte_Carlo(PricingModel):
    def __init__(self, parameter_dict):
        self.n_path = 100000
        self.K = parameter_dict['K']
        self.T = parameter_dict['T']             #expire time (unit: days)
        self.t = parameter_dict['t']             #start time (unit: days)
        self.S0 = parameter_dict['S0']
        self.vol = parameter_dict['vol']
        self.r = parameter_dict['r']
        self.dividend = parameter_dict['dividend']
        self.frequency = parameter_dict['frequency']
        self.path = np.array([[self.S0]*self.n_path])         # row 0: S0

    #def plot_path(self):

    def generate_path_dividend_yield(self):
        # constant vol, r, dividend
        self.path = np.array([[self.S0] * self.n_path])  # row 0: S0
        if type(self.vol)==int or type(self.vol)==float:
            vol = self.vol / math.sqrt(252)                     # convert annual vol to daily vol
            r = self.r/252                                      # convert annual interest rate to daily interest rate
            dividend = self.dividend/252                        # convert annual dividend to daily divident
            for i in range(self.t+1, self.T+1):
                Si = np.array([np.random.lognormal(0, vol*math.sqrt((i-self.t)), self.n_path)*self.S0*math.exp((r-dividend-0.5*vol*vol)*(i-self.t))])     # row i: Si
                self.path = np.r_[self.path, Si]                            # unnecessary copy?
        # array for vol, r, dividend
        else:
            for i in range(self.t+1, self.T+1):
                vol = self.vol   # array
                r = self.r # array
                dividend = self.dividend  # array
                Si = np.array([np.random.lognormal(0, vol[i]*math.sqrt((i-self.t)), self.n_path)*self.S0*math.exp((r[i]-dividend[i]-0.5*vol[i]*vol[i])*(i-self.t))])     # row i: Si
                self.path = np.r_[self.path, Si]
        return self.path

    def generate_path_discrete_cash_dividend(self):
        self.path = np.array([[self.S0] * self.n_path])  # row 0: S0
        # constant vol, r, dividend
        if type(self.vol) == int or type(self.vol) == float:
            vol = self.vol / math.sqrt(252)                     # convert annual vol to daily vol
            r = self.r / 252
            dividend = self.dividend / self.frequency           # cash dividend amount for each dividend payment day
            for i in range(self.t + 1, self.T + 1):
                # dividend paying day
                # fixed dividend paying day?  (i-self.t )%self.frequency==0
                if i%self.frequency==0:
                    dS = self.path[-1]*(np.random.normal(0, vol , self.n_path)+np.ones(self.n_path)*r) - np.ones(self.n_path)*dividend          # daily increment
                # non dividend paying day
                else:
                    dS = self.path[-1]*(np.random.normal(0, vol , self.n_path)+np.ones(self.n_path)*r)             # daily increment
                self.path = np.r_[self.path, np.array([dS+self.path[-1]])]
        return self.path

    def a(self):
        self.path = np.array([[self.S0] * self.n_path])  # row 0: S0
        if type(self.vol) == int or type(self.vol) == float:
            vol = self.vol / math.sqrt(252)  # convert annual vol to daily vol
            r = self.r / 252
            dividend = self.dividend / self.frequency  # dividend percentage for each dividend payment day
            for i in range(self.t + 1, self.T + 1):
                # dividend paying day
                # fixed dividend paying day?  (i-self.t )%self.frequency==0
                if i % self.frequency == 0:
                    dS = self.path[-1] * (np.random.normal(0, vol, self.n_path) + np.ones(self.n_path) * r) - self.path[-1] * dividend  # daily increment
                # non dividend paying day
                else:
                    dS = self.path[-1] * (np.random.normal(0, vol, self.n_path) + np.ones(self.n_path) * r)  # daily increment
                self.path = np.r_[self.path, np.array([dS + self.path[-1]])]
        return self.path

def Price(option_name, parameters, model):
    optionA = option_name(parameters)
    if parameters['type']=='dividend yield':
        return optionA.PriceByPath(model(parameters).generate_path_dividend_yield())
    elif parameters['type']=='discrete cash dividend':
        return optionA.PriceByPath(model(parameters).generate_path_discrete_cash_dividend())
    # discrete proportional dividend
    else:
        return optionA.PriceByPath(model(parameters).generate_path_discrete_proportional_dividend())



parameter1 = {'S0': 100, 'K': 100, 'T': 252, 't': 0, 'vol': 0.1, 'r': 0.01, 'dividend': 0.01, "type": 'dividend yield', 'frequency': 252}    # annual dividend rate (compounded)
parameter2 = {'S0': 100, 'K': 100, 'T': 252, 't': 0, 'vol': 0.1, 'r': 0.01, 'dividend': 1, "type": 'discrete cash dividend', 'frequency': 126}      # annual dividend amount, semi-annual dividend
parameter3 = {'S0': 100, 'K': 100, 'T': 252, 't': 0, 'vol': 0.1, 'r': 0.01, 'dividend': 0.01, "type": 'discrete proportional dividend', 'frequency': 126}    # annual dividend rate (proportional)
print("European call with divident yield : ", Price(EuropeanCall, parameter1, Monte_Carlo))
print("European call with discrete cash dividend: ", Price(EuropeanCall, parameter2, Monte_Carlo))
print("European call with discrete proportional dividend: ", Price(EuropeanCall, parameter3, Monte_Carlo))

parameter4 = {'S0': 100, 'K': 100, 'T': 252, 't': 0, 'vol': 0.1, 'r': 0.01, 'dividend': 0.01, "B": 130, "type": 'dividend yield', 'frequency': 252}    # annual dividend rate (compounded)
parameter5 = {'S0': 100, 'K': 100, 'T': 252, 't': 0, 'vol': 0.1, 'r': 0.01, 'dividend': 1, "B": 130, "type": 'discrete cash dividend', 'frequency': 126}      # annual dividend amount, semi-annual dividend
parameter6 = {'S0': 100, 'K': 100, 'T': 252, 't': 0, 'vol': 0.1, 'r': 0.01, 'dividend': 0.01, "B": 130, "type": 'discrete proportional dividend', 'frequency': 126}    # annual dividend rate (proportional)
print("Up-and-out call with divident yield : ", Price(UpandOutCall, parameter4, Monte_Carlo))
print("Up-and-out call with discrete cash dividend: ", Price(UpandOutCall, parameter5, Monte_Carlo))
print("Up-and-out call with discrete proportional dividend: ", Price(UpandOutCall, parameter6, Monte_Carlo))

