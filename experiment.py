data = {'market': 'KRW-BTC', 'timestamp': 1640755865073, 'total_ask_size': 1.32068208, 'total_bid_size': 4.89289483, 
'orderbook_units': [{'ask_price': 58220000.0, 'bid_price': 58213000.0, 'ask_size': 0.22128832, 'bid_size': 0.07704133},
 {'ask_price': 58221000.0, 'bid_price': 58212000.0, 'ask_size': 0.00335362, 'bid_size': 0.26698425}, 
{'ask_price': 58222000.0, 'bid_price': 58211000.0, 'ask_size': 0.00343513, 'bid_size': 0.00447708},
 {'ask_price': 58223000.0, 'bid_price': 58210000.0, 'ask_size': 0.09720134, 'bid_size': 0.50469193},
 {'ask_price': 58224000.0, 'bid_price': 58209000.0, 'ask_size': 0.11311536, 'bid_size': 0.0181762},
 {'ask_price': 58227000.0, 'bid_price': 58208000.0, 'ask_size': 0.06, 'bid_size': 0.0194651},
 {'ask_price': 58228000.0, 'bid_price': 58207000.0, 'ask_size': 0.00131832, 'bid_size': 0.41391237},
 {'ask_price': 58236000.0, 'bid_price': 58206000.0, 'ask_size': 0.0034343, 'bid_size': 0.85764327},
 {'ask_price': 58240000.0, 'bid_price': 58205000.0, 'ask_size': 0.00302166, 'bid_size': 0.45026119},
 {'ask_price': 58258000.0, 'bid_price': 58202000.0, 'ask_size': 0.002, 'bid_size': 1.27365803},
 {'ask_price': 58259000.0, 'bid_price': 58201000.0, 'ask_size': 0.08324865, 'bid_size': 0.02356901},
 {'ask_price': 58260000.0, 'bid_price': 58200000.0, 'ask_size': 0.00835022, 'bid_size': 0.87115016},
 {'ask_price': 58261000.0, 'bid_price': 58199000.0, 'ask_size': 0.3435, 'bid_size': 0.01908916},
 {'ask_price': 58269000.0, 'bid_price': 58198000.0, 'ask_size': 0.00090902, 'bid_size': 0.07391282},
 {'ask_price': 58270000.0, 'bid_price': 58197000.0, 'ask_size': 0.37650614, 'bid_size': 0.01886293}]}
newpricelist = []
newsizelist = []
for i in range(0,15):
    newpricelist.append(data['orderbook_units'][i]['ask_price'])
    newsizelist.append(data['orderbook_units'][i]['ask_size'])
    
lst = [200,4002,4141,2141]
for i, v in enumerate(lst):
    print(['{:0,.0f}'.format(v)])
