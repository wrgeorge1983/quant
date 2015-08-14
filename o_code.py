from functools import partial
import collections

class MASetPrim(object):
    instances = []
    limits = {'BUY':(1.01, .30), 'STRONG BUY':(1.05, .7), 
              'SELL':(0.99, .20), 'STRONG SELL':(0.95, 1), 
              'short_len':25, 'long_len':100}
    max_score_clamping = 0
    
    def __init__(self, short, long, name=''):
        self.short = short
        self.long = long
        self.name = name
        self.instances.append(self)    
        
    @property
    def s_l_ratio(self):
        return (self.short / self.long)
    # 
    # @property
    # def ratio_sum(self):
    #     """
    #     Sum of instance ratios
    #     """
    #     return sum((instance.s_l_ratio for instance in self.instances))
    # 
    # @property
    # def ratio_weight(self):
    #     """
    #     ratio of self.ratio to self.ratio_sum
    #     (in other words, the amount of `ratio_sum` that this instance contributes)
    #     ** NO SHORTING **
    #     """
    #     return self.s_l_ratio / self.ratio_sum
    # 
    # @property
    # def score(self):
    #     ratio = self.s_l_ratio
    #     if ratio < 1:
    #         try:
    #             ratio = -1.0 / ratio
    #         except ZeroDivisionError:
    #             ratio = 0
    #     score = min(max(ratio, -5), 5)
    #     self.max_score_clamping = max((self.max_score_clamping, score - ratio))
    #     return score * -1
    
    @property
    def recommendation(self):
        ss, s, b, sb = [threshold for threshold, percent in (self.limits['STRONG SELL'], 
                                                             self.limits['SELL'], 
                                                             self.limits['BUY'], 
                                                             self.limits['STRONG BUY'])]
        
        ratio = self.s_l_ratio
        if ratio <= ss:
            rslt = 'STRONG SELL'
        elif ratio <= s:
            rslt = 'SELL'
        elif ratio >= sb:
            rslt = 'STRONG BUY'
        elif ratio >= b:
            rslt = 'BUY'
        else:
            rslt = 'HOLD'
        return rslt
    
    # def __getitem__(self, item):
    #     return getattr(self, item)
    # 
    # def __iter__(self):
    #     for x in self.__dict__.keys():
    #         if not x.startswith('_'):
    #             yield x
    #     for x in self.__class__.__dict__.keys():
    #         if not x.startswith('_') and x not in self.__dict__.keys():
    #             yield x
    #     
    # def __len__(self):
    #     return len(tuple(iter(self)))
    
    
class MASet(MASetPrim):
    instances = []
    
    def __init__(self, data, portfolio, stock):
        s_data = data[stock]
        self.s_data = s_data
        self.stock = stock
        self.portfolio = portfolio
        short = s_data.mavg(self.limits['short_len'])
        long = s_data.mavg(self.limits['long_len'])
        
        self.otp = partial(order_target_percent, stock)
        MASetPrim.__init__(self, short, long)
    
    @property
    def amount_to_sell(self):
        recommendation = self.recommendation
        if 'SELL' not in recommendation:
            return 0
        
        held_amt = self.portfolio.positions[self.stock].amount
        threshold, percent = self.limits[recommendation]
        return int(held_amt * percent)
    
    def shares_for_price(self, cash):
        if cash <= 0:
            return 0
        return int(cash/self.s_data.price)
    
    @property
    def amount_to_buy(self, cash=None):
        recommendation = self.recommendation
        if 'BUY' not in recommendation:
            return 0
        
        if cash is None:
            cash = self.portfolio.cash
        
        price = self.s_data.price
        return int(cash/price)

    def sell(self, amt=None):
        if amt is None:
            amt = self.amount_to_sell
        
        if amt > 0:
            amt *= -1
        elif amt == 0:
            return
            
        order(self.stock, amt)
        log.info('Sold {0}: {1}'.format(self.stock, amt))
        
    def buy(self, amt):
        if amt < 0: 
            raise ValueError('Buying negative amount {0} of {1}'.format(amt, self.stock))
        if amt == 0:
            return
        
        order(self.stock, amt)
        log.info('Bought {0}: {1}'.format(self.stock, amt))

# Put any initialization logic here.  The context object will be passed to
# the other methods in your algorithm.
def initialize(context):
    context.stocks = symbols('XLY',  # XLY Consumer Discrectionary SPDR Fund   
                             'XLF',  # XLF Financial SPDR Fund  
                             'XLK',  # XLK Technology SPDR Fund  
                             'XLE',  # XLE Energy SPDR Fund  
                             'XLV',  # XLV Health Care SPRD Fund  
                             'XLI',  # XLI Industrial SPDR Fund  
                             'XLP',  # XLP Consumer Staples SPDR Fund   
                             'XLB',  # XLB Materials SPDR Fund  
                             'XLU')  # XLU Utilities SPRD Fund

# Will be called on every trade event for the securities you specify. 
def handle_data(context, data):
    MASet.instances = []
    MASet.max_score_clamping = 0
    portfolio = context.portfolio
    for stock in context.stocks:
        mas = MASet(data, portfolio, stock)
  
    for mas in MASet.instances:
        mas.sell()  # sell any that want to be sold
    
    strong_buys = [mas for mas in MASet.instances if mas.recommendation == 'STRONG BUY']
    buys = [mas for mas in MASet.instances if mas.recommendation == 'BUY']
    
    buy_shares(strong_buys, portfolio, all_in=bool(buys))   
    buy_shares(buys, portfolio, all_in=True)

    
def buy_shares(share_list, portfolio, all_in=False):
    cash = portfolio.cash
    for mas in share_list:
        recommendation = mas.recommendation
        threshold, percent = mas.limits[recommendation]
        if all_in:
            percent = 1.0
        percent /= len(share_list)
        cash_to_spend = cash * percent
        amt = mas.shares_for_price(cash_to_spend)
        mas.buy(amt)
            
    