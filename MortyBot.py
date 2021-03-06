import pywaves as pw
import datetime
import time
import os
import sys
import random
try:
	import configparser
except ImportError:
	import ConfigParser as configparser

class MortyBot:
    def __init__(self):
        self.log_file = "bot.log"
        self.node = "https://privatenode2.blackturtle.eu"
        self.chain = "turtlenetwork"
        self.matcher = "https://privatematcher.blackturtle.eu"
        self.datafeed = "https://bot.blackturtle.eu"
        self.order_fee = int(0.04 * 10 ** 8)
        self.order_lifetime = 1 * 86400  # 1 days
        self.private_key = ""
        self.amount_asset_id = ""
        self.amount_asset = pw.WAVES
        self.price_asset_id = "4LHHvYGNKJUg5hj65aGD5vgScvCBmLpdRFtjokvCjSL8" # BTC
        self.price_asset = pw.Asset(self.price_asset_id)  
        self.price_step = 0.05
        self.min_amount = 10000
        self.seconds_to_sleep = 5
        self.strategy = "grid"
        self.grid = ["-"]
        self.grid_levels = 20
        self.grid_tranche = 10000000000
        self.grid_base = "LAST"
        self.grid_flexibility = 20
        self.grid_type = "SYMMETRIC"
        self.grid_basePrice = 0
        self.can_buy = ""
        self.can_sell = ""
        self.uptr_profitmargin = 0.05
        self.uptr_stoploss = 0.01
        self.uptr_stoploss_current = 0
        self.buy_orderid = ""
        self.sell_orderid = ""
        self.filled_type = ""
        self.filled_price = ""

    def log(self, msg):
        timestamp = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
        s = "[{0}]:{1}".format(timestamp, msg)
        print(s)
        try:
            f = open(self.log_file, "a")
            f.write(s + "\n")
            f.close()
        except OSError:
            pass

    def read_config(self, cfg_file):
        if not os.path.isfile(cfg_file):
            self.log("Missing config file")
            self.log("Exiting.")
            exit(1)

        try:
            self.log("Reading config file '{0}'".format(cfg_file))
            config = configparser.RawConfigParser()
            config.read(cfg_file)
            self.node = config.get('network', 'node')
            self.chain = config.get('network', 'network')
            self.matcher = config.get('network', 'matcher')
            self.datafeed = config.get('network', 'datafeed')
            self.order_fee = config.getint('network', 'order_fee')
            
            self.order_lifetime = config.getint('main', 'order_lifetime')
            self.strategy = config.get('main', 'strategy').lower()
            self.seconds_to_sleep = config.getint('main', 'sleeptimer')

            self.private_key = config.get('account', 'private_key')

            self.amount_asset_id = config.get('market', 'amount_asset')
            self.amount_asset = pw.Asset(self.amount_asset_id)

            self.price_asset_id = config.get('market', 'price_asset')
            self.price_asset = pw.Asset(self.price_asset_id)

            self.price_step = config.getfloat('grid', 'interval')
            self.grid_tranche = config.getint('grid', 'tranche_size')
            self.grid_flexibility = config.getint('grid', 'flexibility')
            self.grid_levels = config.getint('grid', 'grid_levels')
            self.grid_base = config.get('grid', 'base').upper()
            self.grid_type = config.get('grid', 'type').upper()
        
            self.uptr_profitmargin = config.getfloat('uptrend', 'profitmargin')
            self.uptr_stoploss = config.getfloat('uptrend', 'stoploss')

            self.log_file = config.get('logging', 'logfile')
        except OSError:
            self.log("Error reading config file")
            self.log("Exiting.")
            exit(1)

    def grid_price(self, level):
        return int(self.grid_basePrice * (1 + self.price_step) ** (level - self.grid_levels / 2))

def give_price(price):
    newprice = int(price / 100) * 100
    newprice = round(newprice / 10 ** (PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals)), 8)
    newprice = float(str(newprice))

    mewprice = (round(price / pow(10, PAIR2.asset2.decimals - PAIR2.asset1.decimals)) * pow(10, PAIR2.asset2.decimals - PAIR2.asset1.decimals))
    mewprice = mewprice / pow(10, 8 + PAIR2.asset2.decimals - PAIR2.asset1.decimals)

    return newprice

def grid_place_order(bot, order_type, level):
    if 0 <= level < bot.grid_levels and (bot.grid[level] == "" or bot.grid[level] == "-"):
        price = bot.grid_price(level)
        showprice = price / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))
        price = (round(price / pow(10, PAIR2.asset2.decimals - PAIR2.asset1.decimals)) * pow(10, PAIR2.asset2.decimals - PAIR2.asset1.decimals))
        price = price / pow(10, 8 + PAIR2.asset2.decimals - PAIR2.asset1.decimals)

        try:
            balance_amount, balance_price = my_address.tradableBalance(PAIR)
            tranche_size = bot.grid_tranche 
            tranche_size = int(tranche_size * (1 - (bot.grid_flexibility / float(200)) + (random.random() * bot.grid_flexibility / float(100))))

            if order_type == "buy":
                if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
                    required_amount = ((tranche_size * price) + bot.order_fee) 
                else:
                    bid_amount = (tranche_size * price) * pow(10, PAIR2.asset2.decimals)
                    required_amount = (tranche_size * price)

                if balance_price >= required_amount:
                    bot.can_buy = "yes"
            
                    o = my_address.buy(PAIR2, tranche_size, price, maxLifetime=bot.order_lifetime, matcherFee=bot.order_fee)
                    try:
                        id = o.orderId
                        bot.log(">> [{0}] {1} order  price: {2}, amount:{3}".format(level, order_type.upper(), showprice, float(tranche_size) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
                    except:
                        id = ""
                    
                else:
                    if bot.can_buy != "no":
                        bot.log(">> Insufficient funds for BUY order")

                        bot.can_buy = "no"
                    id = ""
            elif order_type == "sell":
                if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
                    required_amount = tranche_size 
                else: 
                    required_amount = tranche_size - bot.order_fee 
                
                balance_amount, balance_price = my_address.tradableBalance(PAIR)
                if balance_amount >= required_amount:
                    bot.can_sell = "yes"
    
                    o = my_address.sell(PAIR2, tranche_size, price, maxLifetime=bot.order_lifetime, matcherFee=bot.order_fee)
                    try:
                        id = o.orderId
                        bot.log(">> [{0}] {1} order  price: {2}, amount:{3}".format(level, order_type.upper(), showprice, float(tranche_size) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
                    except:
                        id = ""
                else:
                    if bot.can_sell != "no":
                        bot.log(">> Insufficient funds for SELL order")

                        bot.can_sell = "no"
                    id = ""

        except Exception as e:
            print(str(e))
            id = ""

        bot.grid[level] = id

def get_last_price():
    try:
        last_trade_price = int(round(float(float(PAIR.trades(1)[0]['price']) * pow(10, 8 + PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
    except Exception as e:
        print("Exception ")
        print(str(e))
        last_trade_price = 0
    return last_trade_price

def check_order(bot, orderid):
    #check if order has been filled
    # attempt to retrieve order history from matcher
    try:
        history = my_address.getOrderHistory(PAIR)
    except:
        history = []

    if history:
        order = [item for item in history if item['id'] == orderid]
        status = order[0].get("status") if order else ""
        if status == "Filled":
            my_address.deleteOrderHistory(PAIR)
            bot.filled_price = order[0].get("price")
            bot.filled_type = order[0].get("type")

        return status
    else:
        return "no_history"

def initialize_grid(bot):
    # initialize grid
    try:
        if bot.grid_base.isdigit():
            bot.grid_basePrice = int(bot.grid_base)
        elif bot.grid_base == "LAST":
            bot.grid_basePrice = get_last_price()
        elif bot.grid_base == "BID":
            bot.grid_basePrice = PAIR.orderbook()['bids'][0]['price']
        elif bot.grid_base == "ASK":
            bot.grid_basePrice = PAIR.orderbook()['asks'][0]['price']
            bot.log(">> GRID_BASE: "+str(bot.grid_basePrice))
    except:
        bot.grid_basePrice = 0
    if bot.grid_basePrice == 0:
        bot.log("Invalid BASE price")
        bot.log("Exiting.")
        exit(1)

    bot.log(">> Grid initialisation [base price : %.*f]" % (PAIR2.asset2.decimals, float(bot.grid_basePrice) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))

    last_level = int(bot.grid_levels / 2)

    if bot.grid_type == "SYMMETRIC" or bot.grid_type == "BIDS":
        for n in range(last_level - 1, -1, -1):
            grid_place_order(bot, "buy", n)
    if bot.grid_type == "SYMMETRIC" or bot.grid_type == "ASKS":
        for n in range(last_level + 1, bot.grid_levels):
            grid_place_order(bot, "sell", n)

def check_moving_grid(bot, n):
    #check if we need to reinitialize the grid
    if bot.strategy == "moving_grid":
        if n == bot.grid_levels - 1:
            return True
    else:
        return False


def go_grid(bot):
    #grid strategy main procedure
    # delete order history on the specified pair
    bot.log(">> Deleting order history...")
    my_address.deleteOrderHistory(PAIR)
    bot.log("")

    # grid list with GRID_LEVELS items. item n is the ID of the order placed at the price calculated with this formula
    bot.grid = ["-"] * bot.grid_levels

    # initialize grid
    initialize_grid(bot)
    
    last_level = int(bot.grid_levels / 2)

    check = 0
    # loop forever
    while True:
        check = check + 1
        if check == 360: #every 35 minutes
            bot.log(">> No orders hit - bot is still running")
            check = 0
        
        # loop through all grid levels
        # first all ask levels from the lowest ask to the highest -> range(grid.index("") + 1, len(grid))
        # then all bid levels from the highest to the lowest -> range(grid.index("") - 1, -1, -1)
        for n in list(range(last_level + 1, len(bot.grid))) + list(range(last_level - 1, -1, -1)):

            # find the order with id == grid[n] in the history list
            status = check_order(bot, bot.grid[n])
            if status == "Filled":
                last_price = get_last_price()
                bot.grid[n] = ""
                last_level = n
                check = 0

                bot.log("## [%03d] %s%-4s Filled %18.*f%s" % (n, "", bot.filled_type.upper(), PAIR2.asset2.decimals, float(bot.filled_price) / 10 ** (PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals)), ""))

                if bot.filled_type == "buy":
                    if bot.filled_price >= last_price:
                        grid_place_order(bot, "sell", n + 1)
                    else:
                        grid_place_order(bot, "buy", n)
                elif bot.filled_type == "sell":
                    if bot.filled_price <= last_price:
                        #check if we need to move the grid
                        if check_moving_grid(bot, n):
                            initialize_grid(bot)
                        else:
                            grid_place_order(bot, "buy", n - 1)
                    else:
                        grid_place_order(bot, "sell", n)
            # attempt to place again orders for empty grid levels or cancelled orders
            elif (status == "" or status == "Cancelled") and bot.grid[n] != "-":
                bot.grid[n] = ""
                if n > last_level:
                    grid_place_order(bot, "sell", n)
                elif n < last_level:
                    grid_place_order(bot, "buy", n)

        time.sleep(bot.seconds_to_sleep)

def go_scalp(bot):
    #scalp strategy main procedure
    while True:
        balance_amount, balance_price = my_address.tradableBalance(PAIR)
        order_book = PAIR.orderbook()
        best_bid = order_book["bids"][0]["price"]
        best_ask = order_book["asks"][0]["price"]
        spread_mean_price = ((best_bid + best_ask) // 2) #* 10 ** (PAIR2.asset2.decimals - PAIR2.asset1.decimals)
        bid_price = spread_mean_price * (1 - bot.price_step)
        ask_price = spread_mean_price * (1 + bot.price_step)
        if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
            bid_amount = int(((balance_price - bot.order_fee) / bid_price) * pow(10, PAIR2.asset2.decimals)) 
        else:
            bid_amount = int((balance_price / bid_price) * pow(10, PAIR2.asset2.decimals))

        if bid_amount >= bot.min_amount:
            bot.log("Best_bid: {0}, best_ask: {1}, spread mean price: {2}".format(best_bid, best_ask, spread_mean_price))
            price = give_price(bid_price)
            bot.log("Post buy order with price: {0}, amount:{1}".format(price, float(bid_amount) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
            my_address.buy(assetPair=PAIR2, amount=bid_amount, price=price, matcherFee=bot.order_fee, maxLifetime=bot.order_lifetime)

        balance_amount, balance_price = my_address.tradableBalance(PAIR)
        if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
            ask_amount = balance_amount
        else:
            ask_amount = balance_amount - bot.order_fee #int(((balance_amount - bot.order_fee) / ask_price) * pow(10, PAIR2.asset2.decimals))

        if ask_amount >= bot.min_amount:
            bot.log("Best_bid: {0}, best_ask: {1}, spread mean price: {2}".format(best_bid, best_ask, spread_mean_price))
            price = give_price(ask_price)
            bot.log("Post sell order with price: {0}, ask amount: {1}".format(price, float(ask_amount) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
            my_address.sell(assetPair=PAIR2, amount=ask_amount, price=price, matcherFee=bot.order_fee, maxLifetime=bot.order_lifetime)

        #bot.log("Sleep {0} seconds...".format(bot.seconds_to_sleep))
        time.sleep(bot.seconds_to_sleep)

def set_stoploss(bot, price):
    #set stoploss price
    bot.uptr_stoploss_current = price
    bot.log(">> Stoploss set at: {0}".format(give_price(bot.uptr_stoploss_current)))

def fill_stoploss(bot):
    #stoploss hit, liquidate asset
    balance_amount, balance_price = my_address.tradableBalance(PAIR)
    order_book = PAIR.orderbook()
    best_bid = order_book["bids"][0]["price"]
    price = give_price(best_bid)

    #get current amount
    if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
        ask_amount = int(balance_amount)
    else:
        ask_amount = int(((balance_amount - bot.order_fee) / price) * pow(10, PAIR2.asset2.decimals))

    #check if there's anything to sell
    if ask_amount > 1000:
        bot.log(">> Stoploss hit: Post sell order with price: {0}, amount: {1}".format(price, ask_amount))

        #sell until completely liquidated
        while ask_amount > 1000:                
            order_book = PAIR.orderbook()
            best_bid = order_book["bids"][0]["price"]
            price = give_price(best_bid)

            #sell for current buy price
            my_address.sell(assetPair=PAIR2, amount=ask_amount, price=price, matcherFee=bot.order_fee, maxLifetime=bot.order_lifetime)
        
            time.sleep(bot.seconds_to_sleep)

        #check if everything is sold
            balance_amount, balance_price = my_address.tradableBalance(PAIR)
            if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
                ask_amount = int(balance_amount)
            else:
                ask_amount = int(((balance_amount - bot.order_fee) / price) * pow(10, PAIR2.asset2.decimals))

        bot.log(">> Stoploss filled: all assets liquidated")
        exit(1)

def go_uptrend(bot):
    #uptrend strategy main procedure
    #first initialization
    balance_amount, balance_price = my_address.tradableBalance(PAIR)
    order_book = PAIR.orderbook()
    #get current bids
    best_bid = order_book["bids"][0]["price"]
    best_ask = order_book["asks"][0]["price"]
    spread_mean_price = ((best_bid + best_ask) // 2)
    bid_price = best_ask 
    #calculate sell price
    ask_price = spread_mean_price * (1 + bot.uptr_profitmargin)

    #set stoploss price
    if bot.uptr_stoploss_current == 0:
        set_stoploss(bot, bid_price * (1 - bot.uptr_stoploss))

    #calculate max buy amount
    if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
        bid_amount = int(((balance_price - bot.order_fee) / bid_price) * pow(10, PAIR2.asset2.decimals)) 
    else:
        bid_amount = int((balance_price / bid_price) * pow(10, PAIR2.asset2.decimals))

    #buy for current sell price
    if bid_amount >= bot.min_amount:
        price = give_price(bid_price)
        bot.log(">> Post buy order with price: {0}, amount: {1}".format(price, float(bid_amount) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
        o = my_address.buy(assetPair=PAIR2, amount=bid_amount, price=price, matcherFee=bot.order_fee, maxLifetime=bot.order_lifetime)
        try:
            bot.buy_orderid = o.orderId
        except:
            bot.buy_orderid = ""
    
    #calculate max sell amount
    balance_amount, balance_price = my_address.tradableBalance(PAIR)
    if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
        ask_amount = balance_amount
    else:
        ask_amount = balance_amount #int(((balance_amount - bot.order_fee) / ask_price) * pow(10, PAIR2.asset2.decimals))
    
    #post sell order
    if ask_amount >= bot.min_amount:
        price = give_price(ask_price)
        bot.log(">> Post sell order with price: {0}, amount: {1}".format(price, float(ask_amount) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
        o = my_address.sell(assetPair=PAIR2, amount=ask_amount, price=price, matcherFee=bot.order_fee, maxLifetime=bot.order_lifetime)
        try:
            bot.sell_orderid = o.orderId
        except:
            bot.sell_orderid = ""

    #loop forever
    while True:
        balance_amount, balance_price = my_address.tradableBalance(PAIR)
        order_book = PAIR.orderbook()
        #get current bids
        best_bid = order_book["bids"][0]["price"]
        best_ask = order_book["asks"][0]["price"]
        spread_mean_price = ((best_bid + best_ask) // 2)
        bid_price = best_ask 
        #calculate sell price
        ask_price = spread_mean_price * (1 + bot.uptr_profitmargin)

        #check stoploss
        if best_bid <= bot.uptr_stoploss_current:
            my_address.cancelOpenOrders(PAIR)
            balance_amount, balance_price = my_address.tradableBalance(PAIR)

            fill_stoploss(bot)

        status = ""
        #check buyorder
        if bot.buy_orderid != "":
            status = check_order(bot, bot.buy_orderid)

        if status == "Filled":
            bot.buy_orderid = ""
            bot.log("## {0} order Filled at: {1}".format(bot.filled_type.upper(), float(bot.filled_price) / 10 ** (PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))

            #reset stoploss
            set_stoploss(bot, bot.filled_price * (1 - bot.uptr_stoploss))

            #calculate max sell amount
            balance_amount, balance_price = my_address.tradableBalance(PAIR)
            if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
                ask_amount = balance_amount
            else:
                ask_amount = balance_amount #int(((balance_amount - bot.order_fee) / ask_price) * pow(10, PAIR2.asset2.decimals))
    
            #post sell order
            #if ask_amount >= bot.min_amount:
            price = give_price(ask_price)
            bot.log(">> Post sell order with price: {0}, amount: {1}".format(price, float(ask_amount) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
            o = my_address.sell(assetPair=PAIR2, amount=ask_amount, price=price, matcherFee=bot.order_fee, maxLifetime=bot.order_lifetime)
            try:
                bot.sell_orderid = o.orderId
            except:
                bot.sell_orderid = ""
    
        #check sellorder
        if bot.sell_orderid != "":
            status = check_order(bot, bot.sell_orderid)

        if status == "Filled":
            bot.sell_orderid = ""
            bot.log("## {0} order Filled at: {1}".format(bot.filled_type.upper(), float(bot.filled_price) / 10 ** (PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))

            #reset stoploss
            set_stoploss(bot, bid_price * (1 - bot.uptr_stoploss))

            #calculate max buy amount
            if (bot.chain == "turtlenetwork" and bot.price_asset_id == "TN") or (bot.chain != "turtlenetwork" and bot.price_asset_id == "WAVES"): 
                bid_amount = int(((balance_price - bot.order_fee) / bid_price) * pow(10, PAIR2.asset2.decimals)) 
            else:
                bid_amount = int((balance_price / bid_price) * pow(10, PAIR2.asset2.decimals))

            #buy for current sell price
            #if bid_amount >= bot.min_amount:
            price = give_price(bid_price)
            bot.log(">> Post buy order with price: {0}, amount: {1}".format(price, float(bid_amount) / pow(10, PAIR2.asset2.decimals + (PAIR2.asset2.decimals - PAIR2.asset1.decimals))))
            o = my_address.buy(assetPair=PAIR2, amount=bid_amount, price=price, matcherFee=bot.order_fee, maxLifetime=bot.order_lifetime)
            try:
                bot.buy_orderid = o.orderId
            except:
                bot.buy_orderid = ""

        #bot.log("Sleep {0} seconds...".format(bot.seconds_to_sleep))
        time.sleep(bot.seconds_to_sleep)
    

def main():
    global my_address
    global PAIR
    global PAIR2

    #initialisation
    bot = MortyBot()

    CFG_FILE = "bot.cfg"

    if len(sys.argv) >= 2:
        CFG_FILE = sys.argv[1]

    if not os.path.isfile(CFG_FILE):
        bot.log("Missing config file")
        bot.log("Exiting.")
        exit(1)

    bot.read_config(CFG_FILE)
    pw.setMatcher(node=bot.matcher)
    pw.setDatafeed(wdf=bot.datafeed)
    
    if bot.chain == "turtlenetwork":
        pw.setNode(bot.node, bot.chain, 'L')
        PAIR = pw.AssetPair(pw.Asset(bot.amount_asset_id), pw.Asset(bot.price_asset_id))
        PAIR2 = PAIR
        if bot.price_asset_id == 'TN':
            PAIR2 = pw.AssetPair(pw.Asset(bot.amount_asset_id), pw.Asset('WAVES'))
        elif bot.amount_asset_id == 'TN':
            PAIR2 = pw.AssetPair(pw.Asset('WAVES'), pw.Asset(bot.price_asset_id))
    else:
        pw.setNode(bot.node, bot.chain)
        PAIR = pw.AssetPair(pw.Asset(bot.amount_asset_id), pw.Asset(bot.price_asset_id))
        PAIR2 = PAIR
        if bot.price_asset_id == 'WAVES':
            PAIR2 = pw.AssetPair(pw.Asset(bot.amount_asset_id), pw.WAVES)
        elif bot.amount_asset_id == 'WAVES':
            PAIR2 = pw.AssetPair(pw.WAVES, pw.Asset(bot.price_asset_id))
    
    my_address = pw.Address(privateKey=bot.private_key)

    bot.log("-" * 80)
    bot.log("          Address : {0}".format(my_address.address))
    bot.log("  Amount Asset ID : {0} ({1})".format(bot.amount_asset_id, PAIR2.asset1.name))
    bot.log("   Price Asset ID : {0} ({1})".format(bot.price_asset_id, PAIR2.asset2.name))
    bot.log("Strategy selected : {0}".format(bot.strategy.upper()))
    bot.log("-" * 80)
    bot.log("")

    # cancel all open orders on the specified pair
    bot.log(">> Cancelling open orders...")
    my_address.cancelOpenOrders(PAIR)

    #grid trading
    if bot.strategy.lower() == "grid" or bot.strategy.lower() == "moving_grid":
        go_grid(bot)
    elif bot.strategy.lower() == "scalp":
        go_scalp(bot)
    elif bot.strategy.lower() == "uptrend":
        bot.seconds_to_sleep = 1
        go_uptrend(bot)


if __name__ == "__main__":
    main()
                        