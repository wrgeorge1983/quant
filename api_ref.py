__author__ = 'William.George'
equity_list = [
               Equity(19662, symbol='XLY',
                      asset_name='CONSUMER DISCRETIONARY SELECT SECTOR SPDR FUND',
                      exchange='NYSE ARCA EXCHANGE',
                      start_date=Timestamp('1998-12-21 00:00:00+0000', tz='UTC'),
                      end_date=Timestamp('2015-08-14 00:00:00+0000', tz='UTC'),
                      first_traded=None),
               Equity(19656, symbol='XLF',
                      asset_name='FINANCIAL SELECT SECTOR SPDR FUND',
                      exchange='NYSE ARCA EXCHANGE',
                      start_date=Timestamp('1998-12-21 00:00:00+0000', tz='UTC'),
                      end_date=Timestamp('2015-08-14 00:00:00+0000', tz='UTC'),
                      first_traded=None),
               Equity(19658, symbol='XLK',
                      asset_name='TECHNOLOGY SELECT SECTOR SPDR FUND',
                      exchange='NYSE ARCA EXCHANGE',
                      start_date=Timestamp('1998-12-21 00:00:00+0000', tz='UTC'),
                      end_date=Timestamp('2015-08-14 00:00:00+0000', tz='UTC'),
                      first_traded=None),
               Equity(19655, symbol='XLE',
                      asset_name='ENERGY SELECT SECTOR SPDR FUND',
                      exchange='NYSE ARCA EXCHANGE',
                      start_date=Timestamp('1998-12-21 00:00:00+0000', tz='UTC'),
                      end_date=Timestamp('2015-08-14 00:00:00+0000', tz='UTC'),
                      first_traded=None)
              ]


AlgorithmContext({
    'account': Account({
        'day_trades_remaining': inf, 'leverage': 0.0, 'regt_equity': 1000000.0, 'regt_margin': inf, 'available_funds': 1000000.0, 'maintenance_margin_requirement': 0.0, 'equity_with_loan': 1000000.0, 'buying_power': inf, 'initial_margin_requirement': 0.0, 'excess_liquidity': 1000000.0, 'settled_cash': 1000000.0, 'net_liquidation': 1000000.0, 'cushion': 1.0, 'total_positions_value': 0.0, 'net_leverage': 0.0, 'accrued_interest': 0.0
    }),
    'portfolio': Portfolio({
        'portfolio_value': 1000000.0, 'positions_exposure': 0.0, 'cash': 1000000.0, 'starting_cash': 1000000.0, 'returns': 0.0, 'capital_used': 0.0, 'pnl': 0.0, 'positions': {}, 'positions_value': 0.0, 'start_date': Timestamp('2015-08-10 00:00:00+0000', tz='UTC')
    }),
    'security': [Equity(
        24, symbol='AAPL', asset_name='APPLE INC', exchange='NASDAQ GLOBAL SELECT MARKET', start_date=Timestamp('1993-01-04 00:00:00+0000', tz='UTC'), end_date=Timestamp('2015-08-14 00:00:00+0000', tz='UTC'), first_traded=None)],
    'first_run': True})