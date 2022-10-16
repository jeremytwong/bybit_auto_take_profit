from pybit import usdt_perpetual
from pybit import HTTP  # supports inverse perp & futures, usdt perp, spot.
import configparser




class Account():
    def __init__(self):
        self.endpoint='https://api.bybit.com'
        self.domain = 'bytick' 
        self.active_position_list = []
        self.orders = []



        
        config=configparser.ConfigParser()
        config.read('cfg/config.ini')
        
        self.config = config
        self.number_of_positions = self.config['ORDERS']['number_positions']
        self.position_tp_percentage = int(self.config['ORDERS']['percentage_tp_position'])
        self.active_symbol_name = self.config['SYMBOL']['current_symbol']


        self.debug = []
        #connect ws auth app | noauth app | http app
        self._create_ws_auth()
        self._create_http_noauth()
        self._create_ws_noauth()
        self._create_http_auth()

        #get symbol info
        self._get_min_info()
        self._get_current_symbol_position()


    def _create_ws_noauth(self) -> None:
        self.ws_noauth = usdt_perpetual.WebSocket(
            test=False,
            domain='bytick')

    def _create_http_noauth(self) -> None:
        self.http_noauth = usdt_perpetual.HTTP(
            endpoint="https://api-testnet.bybit.com"
        )

    def _create_ws_auth(self) -> None:
        self.ws_auth_client = usdt_perpetual.WebSocket(
            test=False,
            domain=self.domain,
            api_key=self.config['BYBITKEYS']['apikey'],
            api_secret=self.config['BYBITKEYS']['apisecret']
        )


    def _create_http_auth(self) -> None:
        self.http_client = usdt_perpetual.HTTP(
            endpoint=self.endpoint,
            api_key=self.config['BYBITKEYS']['apikey'],
            api_secret=self.config['BYBITKEYS']['apisecret']
        )

    def _get_current_symbol_position(self) -> None:
        try:
            self.active_position_list = self.http_client.my_position(
                symbol = self.active_symbol_name
            )

        except Exception as e:
            self.debug.append(e)
            return
    
    def _get_min_info(self) -> None:
        try:
            query = self.http_noauth.query_symbol()
            if query['ret_msg'] == 'OK':
                for symbol in query['result']:
                    if symbol['name'] == self.active_symbol_name:
                        self.min_step = symbol['price_filter']['tick_size']
                        self.min_price = symbol['lot_size_filter']['min_trading_qty']
                        self.sig_dig = int(symbol['price_scale'])

        except Exception as e:
            self.debug.append(e)
            return

    def _clear_orders(self) -> None:
        self.orders = []

    def set_scaling_tp(account):
        try:
            order_side = None
            if (account.active_position_list['result'][0]['size'] == 0):
                entry = float(account.active_position_list['result'][1]['entry_price'])
                side = account.active_position_list['result'][1]['side']
                size = float(account.active_position_list['result'][1]['size'])
                order_side = 'Buy'
            else:
                entry = float(account.active_position_list['result'][0]['entry_price'])
                side = account.active_position_list['result'][0]['side']
                size = float(account.active_position_list['result'][0]['size'])
                order_side = 'Sell'
            positions = []

            #determine the positions to sell everything
            
            if (side) == 'Buy':
                top = entry * (account.position_tp_percentage / 100 + 1)
                diff = top - entry
                entry = top
                amount_to_increase = diff / int(account.number_of_positions)    
                for i in range(1, int(account.number_of_positions) + 1):
                    entry += amount_to_increase
                    positions.append(round(entry, account.sig_dig))
                
            elif (side) == 'Sell':
                bottom = entry * (float(1 - account.position_tp_percentage / 100))
                diff = entry - bottom
                entry = bottom
                amount_to_increase = diff / int(account.number_of_positions)  
                for i in range(1, int(account.number_of_positions) + 1):
                    entry -= amount_to_increase
                    positions.append(round(entry, account.sig_dig))
            amount_to_sell = round(size / float(account.number_of_positions), account.sig_dig)

            if (amount_to_sell < float(account.min_price)) or (amount_to_increase < float(account.min_step)):
                account.debug.append('increase size or decrease number of positions in config.ini')
                return False
            else:
                for i in range(0, int(account.number_of_positions)):
                    account.orders.append((amount_to_sell, positions[i]))
                    account.http_client.place_active_order(
                        symbol=account.active_symbol_name,
                        side=order_side,
                        order_type='Limit',
                        qty=amount_to_sell,
                        price=positions[i],
                        time_in_force='PostOnly',
                        reduce_only=True,
                        close_on_trigger=True
                    )
        except Exception as e:
            account.debug.append(e)
        return True
