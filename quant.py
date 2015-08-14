__author__ = 'William.George'
null_func = lambda *args, **kwargs: (args, kwargs)
log = null_func
log.info = null_func
log.debug = null_func
log.error = null_func
order = null_func
Equity = null_func
Timestamp = null_func
symbols = null_func
order_target_percent = null_func
schedule_function = null_func
date_rules = null_func
date_rules.month_start = null_func
date_rules.every_day = null_func
time_rules = null_func
time_rules.market_open = null_func
time_rules.market_close = null_func

def get_datetime():
    import datetime
    return datetime.datetime.today()

# benchmarks for time:  2000hps in daily, 47hps in minute

from functools import partial
from datetime import datetime
import collections


mydebug = True
mydebug_targets = ['run_time']


def today():
    return get_datetime().date()


def d_log(msg, target='all'):
    if not mydebug:
        return

    if 'all' in mydebug_targets or target in mydebug_targets:
        log.debug(msg)


def run_time_report(context, data):
    if not mydebug:  # don't even run if we're not debugging
        return

    code_run_time = datetime.today() - context.code_start_time
    sim_run_time = get_datetime() - context.sim_start_time


    # seconds of sim_run_time and seconds of code_run_time
    seconds_of_crt = code_run_time.total_seconds()
    seconds_of_srt = int(sim_run_time.total_seconds())

    hours_of_srt = seconds_of_srt / 3600

    srt_hours_per_crt_second = hours_of_srt / seconds_of_crt

    msg = ('\n'
           'code_run_time: \t{0}\n'
           'sim_run_time:  \t{1}\n'
           'sim_hours_per_code_second:\n \t\t {2:.3f}\n'
           ''.format(code_run_time, sim_run_time,
                     srt_hours_per_crt_second)
           )
    d_log(msg, target='run_time')


class EquityWrapperCore(object):
    _instances = []
    limits = {'BUY':(1.01, .30), 'STRONG BUY':(1.05, .7),
              'SELL':(0.995, .20), 'STRONG SELL':(0.975, 1),
              'short_len':25, 'long_len':200}
    max_score_clamping = 0

    def __init__(self, symbol):
        self.symbol = symbol
        self._instances.append(self)
        self.bought_today = None
        self.sold_today = None
        self.last_init = None

    def daily_init(self, short_mavg, long_mavg):
        self.short_mavg = short_mavg
        self.long_mavg = long_mavg

        self.bought_today = False  # can be reset during the day by opposite action
        self.sold_today = False    # can be reset during the day by opposite action

        self.last_init = today()

    @property
    def needs_init(self):
        last = self.last_init
        _today = today()
        d_log('needs_init: {0}: last: {1}, today:{2}'.format(
            self.symbol,
            last,
            _today
        ), target='needs_init')
        if last == _today:
            return False
        return True

    @property
    def s_l_ratio(self):
        try:
            rslt = self.short_mavg / self.long_mavg
        except AttributeError:
            rslt = 0

        return rslt

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

    @property
    def recommendation_limit(self):
        recommendation = self.recommendation
        return self.limits[recommendation]


class EquityWrapper(EquityWrapperCore):
    _instances = []
    portfolio = None

    def __init__(self, equity):
        self.equity = equity
        if self.portfolio is None:
            raise AttributeError('Cannot instantiate EquityWrapper without portfolio')

        d_log('Primary Initialization of EquityWrapper({0})'.format(self.symbol),
              target='__init__')

        EquityWrapperCore.__init__(self, self.symbol)

    def daily_init(self, data):
        equity = self.equity
        s_data = data[equity]
        self.s_data = s_data

        short_mavg = s_data.mavg(self.limits['short_len'])
        long_mavg = s_data.mavg(self.limits['long_len'])

        self.otp = partial(order_target_percent, equity)

        d_log('Daily Initialization of EquityWrapper({0})'.format(self.symbol),
              target='daily_init')
        EquityWrapperCore.daily_init(self, short_mavg=short_mavg, long_mavg=long_mavg)

    @property
    def symbol(self):
        return self.equity.symbol

    @symbol.setter
    def symbol(self, val):
        """
        Silently eat assignments in base class
        """
        pass

    @property
    def amount_to_sell(self):
        recommendation = self.recommendation
        if 'SELL' not in recommendation:
            return 0

        held_amt = self.portfolio.positions[self.equity].amount
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
        """
        Sale decision is based on ONLY this equity, not any broader context
        """
        if amt is None:
            amt = self.amount_to_sell

        if amt > 0:
            amt *= -1
        elif amt == 0:
            return

        order(self.equity, amt)

        self.sold_today = True
        self.bought_today = False
        log.info('Sold {0}: {1}'.format(self.equity, amt))

    def buy(self, amt):
        """
        Buy decision is based on broader context, so we must get amt.
        """
        if amt < 0:
            raise ValueError('Buying negative amount {0} of {1}'.format(amt, self.equity))
        if amt == 0:
            return

        self.sold_today = False
        self.bought_today = True
        order(self.equity, amt)
        log.info('Bought {0}: {1}'.format(self.equity, amt))


# Put any initialization logic here.  The context object will be passed to
# the other methods in your algorithm.
def initialize(context):
    context.code_start_time = datetime.today()
    context.sim_start_time = None  # will give wacky time here

    context.stocks = symbols('XLY',  # XLY Consumer Discrectionary SPDR Fund
                             'XLF',  # XLF Financial SPDR Fund
                             'XLK',  # XLK Technology SPDR Fund
                             'XLE',  # XLE Energy SPDR Fund
                             'XLV',  # XLV Health Care SPRD Fund
                             'XLI',  # XLI Industrial SPDR Fund
                             'XLP',  # XLP Consumer Staples SPDR Fund
                             'XLB',  # XLB Materials SPDR Fund
                             'XLU')  # XLU Utilities SPRD Fund

    EquityWrapper.portfolio = context.portfolio
    context.e_wrappers = {equity.symbol: EquityWrapper(equity)
                          for equity
                          in context.stocks}

    schedule_function(daily_init,
                      date_rules.every_day(),
                      time_rules.market_close())


def daily_init(context, data):
    equities = context.e_wrappers.values()
    for equity in equities:
        equity.daily_init(data)

    run_time_report(context, data)

# Will be called on every trade event for the securities you specify.
def handle_data(context, data):
    if context.sim_start_time is None:
        context.sim_start_time = get_datetime()

    portfolio = context.portfolio
    equities = context.e_wrappers.values()

    for equity in equities:
        if not equity.sold_today:
            equity.sell()  # EquityWrapper.sell decides if appropriate, how much

    # Now we know how much money we have to spend (from selling)

    strong_buys = [equity for equity in equities
                   if (equity.recommendation == 'STRONG BUY')
                       and (not equity.bought_today)]

    buys = [equity for equity in equities
            if (equity.recommendation == 'BUY')
                and (not equity.bought_today)]

    buy_shares(strong_buys, portfolio, all_in=not bool(buys))
    buy_shares(buys, portfolio, all_in=True)


def buy_shares(equity_list, portfolio, all_in=False):
    cash = portfolio.cash

    for equity in equity_list:
        threshold, percent = equity.recommendation_limit

        if all_in:
            percent = 1.0
        percent /= len(equity_list)

        cash_to_spend = cash * percent
        amt = equity.shares_for_price(cash_to_spend)
        equity.buy(amt)
