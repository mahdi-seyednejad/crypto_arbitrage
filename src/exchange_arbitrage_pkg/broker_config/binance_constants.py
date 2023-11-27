SYMBOL_TYPE_SPOT = 'SPOT'
ORDER_STATUS_NEW = 'NEW'
ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
ORDER_STATUS_FILLED = 'FILLED'
ORDER_STATUS_CANCELED = 'CANCELED'
ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
ORDER_STATUS_REJECTED = 'REJECTED'
ORDER_STATUS_EXPIRED = 'EXPIRED'
KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'
KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'
KLINE_INTERVAL_1WEEK = '1w'
KLINE_INTERVAL_1MONTH = '1M'
SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'
ORDER_TYPE_LIMIT = 'LIMIT'
ORDER_TYPE_MARKET = 'MARKET'
ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'
TIME_IN_FORCE_GTC = 'GTC'
TIME_IN_FORCE_IOC = 'IOC'
TIME_IN_FORCE_FOK = 'FOK'
ORDER_RESP_TYPE_ACK = 'ACK'
ORDER_RESP_TYPE_RESULT = 'RESULT'
ORDER_RESP_TYPE_FULL = 'FULL'
# For accessing the data returned by Client.aggregate_trades().
AGG_ID = 'a'
AGG_PRICE = 'p'
AGG_QUANTITY = 'q'
AGG_FIRST_TRADE_ID = 'f'
AGG_LAST_TRADE_ID = 'l'
AGG_TIME = 'T'
AGG_BUYER_MAKES = 'm'
AGG_BEST_MATCH = 'M'
WEBSOCKET_DEPTH_5 = '5'
WEBSOCKET_DEPTH_10 = '10'
WEBSOCKET_DEPTH_20 = '20'

SYMBOL_PAIRS = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT', 'BNBUSDT', 'ETHBTC', 'BNBBTC', 'LTCBTC',
                'ADAUSDT', 'BATUSDT', 'ETCUSDT', 'XLMUSDT', 'ZRXUSDT', 'BTCBUSD', 'DOGEUSDT', 'ATOMUSDT', 'NEOUSDT',
                'VETUSDT', 'QTUMUSDT', 'ONTUSDT', 'BNBBUSD', 'ETHBUSD', 'ADABTC', 'KNCUSDT', 'VTHOUSDT', 'COMPUSDT',
                'MKRUSDT', 'ONEUSDT', 'BANDUSDT', 'STORJUSDT', 'UNIUSDT', 'SOLUSDT', 'LINKBTC', 'EGLDUSDT', 'PAXGUSDT',
                'OXTUSDT', 'ZENUSDT', 'BTCUSDC', 'FILUSDT', 'AAVEUSDT', 'GRTUSDT', 'SHIBUSDT', 'CRVUSDT', 'AXSUSDT',
                'SOLBTC', 'AVAXUSDT', 'CTSIUSDT', 'DOTUSDT', 'YFIUSDT', '1INCHUSDT', 'FTMUSDT', 'USDCUSDT', 'ETHUSDC',
                'MATICUSDT', 'MANAUSDT', 'ALGOUSDT', 'LINKUSDT', 'EOSUSDT', 'ZECUSDT', 'ENJUSDT', 'NEARUSDT', 'OMGUSDT',
                'SUSHIUSDT', 'LRCUSDT', 'LPTUSDT', 'MATICBTC', 'NMRUSDT', 'SLPUSDT', 'ANTUSDT', 'CHZUSDT', 'OGNUSDT',
                'GALAUSDT', 'TLMUSDT', 'SNXUSDT', 'AUDIOUSDT', 'ENSUSDT', 'AVAXBTC', 'WBTCBTC', 'REQUSDT', 'APEUSDT',
                'FLUXUSDT', 'COTIUSDT', 'VOXELUSDT', 'RLCUSDT', 'BICOUSDT', 'API3USDT', 'BNTUSDT', 'IMXUSDT',
                'FLOWUSDT', 'GTCUSDT', 'THETAUSDT', 'TFUELUSDT', 'OCEANUSDT', 'LAZIOUSDT', 'SANTOSUSDT', 'ALPINEUSDT',
                'PORTOUSDT', 'RENUSDT', 'CELRUSDT', 'SKLUSDT', 'VITEUSDT', 'WAXPUSDT', 'LTOUSDT', 'FETUSDT', 'BONDUSDT',
                'LOKAUSDT', 'ICPUSDT', 'TUSDT', 'OPUSDT', 'ROSEUSDT', 'CELOUSDT', 'KDAUSDT', 'KSMUSDT', 'ACHUSDT',
                'DARUSDT', 'RNDRUSDT', 'SYSUSDT', 'RADUSDT', 'ILVUSDT', 'LDOUSDT', 'RAREUSDT', 'LSKUSDT', 'DGBUSDT',
                'REEFUSDT', 'ALICEUSDT', 'FORTHUSDT', 'ASTRUSDT', 'BTRSTUSDT', 'GALUSDT', 'SANDUSDT', 'BALUSDT',
                'GLMUSDT', 'CLVUSDT', 'TUSDUSDT', 'QNTUSDT', 'STGUSDT', 'AXLUSDT', 'KAVAUSDT', 'APTUSDT', 'MASKUSDT',
                'BOSONUSDT', 'PONDUSDT', 'SOLUSDC', 'ADAUSDC', 'MXCUSDT', 'JAMUSDT', 'TRACUSDT', 'PROMUSDT', 'DIAUSDT',
                'BTCDAI', 'ETHDAI', 'ADAETH', 'DOGEBTC', 'LOOMUSDT', 'STMXUSDT', 'USDTUSD', 'POLYXUSDT', 'IOSTUSDT',
                'MATICETH', 'SOLETH', 'ARBUSDT', 'FLOKIUSDT', 'XECUSDT', 'BLURUSDT', 'ANKRUSDT', 'DAIUSDT', 'DASHUSDT',
                'HBARUSDT', 'ICXUSDT', 'IOTAUSDT', 'RVNUSDT', 'WAVESUSDT', 'XNOUSDT', 'XTZUSDT', 'ZILUSDT', 'ORBSUSDT']

# Creatd by this function: def get_top_k_cryptos(api_key, api_secret, is_testnet, k=10, base_assets=None)
TOP_SYMBOL_PAIRS_TESTNET = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'LTCUSDT', 'XRPUSDT', 'TRXUSDT']

TOP_SYMBOL_PAIRS = ['BTCUSDT', 'ETHUSDT', 'NMRUSDT', 'GALAUSDT', 'XRPUSDT', 'FETUSDT', 'SHIBUSDT', 'BCHUSDT',
                    'DOGEUSDT', 'BNBUSDT', 'SOLUSDT', 'XLMUSDT', 'ADAUSDT', 'MATICUSDT', 'ZILUSDT', 'VETUSDT',
                    'ONEUSDT', 'FTMUSDT', 'LTCUSDT', 'AVAXUSDT', 'KDAUSDT', 'LINKUSDT', 'NEARUSDT', 'ALGOUSDT',
                    'HBARUSDT', 'WAVESUSDT', 'DOTUSDT', 'MKRUSDT', 'ACHUSDT', 'ATOMUSDT', 'SANTOSUSDT', 'OPUSDT',
                    'UNIUSDT', 'RADUSDT', 'SANDUSDT', 'IOTAUSDT', 'VTHOUSDT', 'JAMUSDT', 'GRTUSDT', 'SNXUSDT',
                    'OCEANUSDT', 'ZENUSDT', 'QNTUSDT', 'FLOKIUSDT', 'FORTUSDT', 'ICXUSDT', 'OXTUSDT', 'WAXPUSDT',
                    'BONDUSDT', 'APEUSDT', 'BNTUSDT', 'XECUSDT', 'KAVAUSDT', 'IMXUSDT', 'PROMUSDT', 'ZECUSDT',
                    'AAVEUSDT', 'ENJUSDT', 'RNDRUSDT', 'APTUSDT', 'ANTUSDT', 'ENSUSDT', 'STMXUSDT', 'RLCUSDT',
                    'LPTUSDT', 'COMPUSDT', 'CRVUSDT', 'ICPUSDT', 'ZRXUSDT', 'ARBUSDT', 'MANAUSDT', 'TRACUSDT',
                    'BALUSDT', 'CUDOSUSDT', 'FILUSDT', 'SYSUSDT', 'THETAUSDT', 'XNOUSDT', 'EGLDUSDT', 'VOXELUSDT',
                    'MASKUSDT', 'BATUSDT', 'BANDUSDT', 'ONTUSDT', 'ETCUSDT', 'FLOWUSDT', 'CHZUSDT', 'OGNUSDT',
                    'QTUMUSDT', 'AUDIOUSDT', 'NEOUSDT', 'POLYXUSDT', 'STORJUSDT', 'EOSUSDT', 'BOSONUSDT', 'XTZUSDT',
                    'DGBUSDT', 'FLUXUSDT', 'LDOUSDT', 'RENUSDT', 'DASHUSDT', 'AXSUSDT', 'FORTHUSDT', 'ADXUSDT',
                    'SLPUSDT', 'TUSDT', 'SUSHIUSDT', 'RVNUSDT', 'DAIUSDT', 'LOKAUSDT', 'COTIUSDT', 'ROSEUSDT',
                    'ASTRUSDT', 'REEFUSDT', 'TLMUSDT', 'CTSIUSDT', 'ORBSUSDT', 'TFUELUSDT', 'LOOMUSDT', 'CELRUSDT',
                    'KSMUSDT', 'VITEUSDT', 'CELOUSDT', 'STGUSDT', 'SKLUSDT', 'ANKRUSDT', 'OMGUSDT', 'ALPINEUSDT',
                    'LRCUSDT', 'LAZIOUSDT', 'LTOUSDT', 'YFIUSDT', 'REQUSDT', 'ALICEUSDT', 'ILVUSDT', 'PORTOUSDT',
                    'BICOUSDT', 'IOSTUSDT', 'KNCUSDT', 'HNTUSDT', 'PAXGUSDT', 'POLYUSDT', 'TRXUSDT', 'USTUSDT',
                    'SPELLUSDT', 'JASMYUSDT', 'GTCUSDT', 'DARUSDT', 'RAREUSDT', 'LSKUSDT', 'SRMUSDT', 'BTRSTUSDT',
                    'GALUSDT', 'GLMUSDT', 'CLVUSDT', 'AXLUSDT', 'PONDUSDT', 'MXCUSDT', 'DIAUSDT', 'BLURUSDT']


Binance_Quote_Currencies = ['USDT', 'BTC', 'ETH', 'BNB', 'XRP']

