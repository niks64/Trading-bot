#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from collections import deque
from enum import Enum
import time
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "HARBORSEALS"

# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy BOND for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!


def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)

    # Send an order for BOND at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.
    order_num = 1
    exchange.send_add_message(order_id=order_num, symbol="BOND", dir=Dir.BUY, price=990, size=1)
    order_num += 1
    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    vale_bid_price, vale_ask_price = None, None
    vale_last_print_time = time.time()

    highestBondBuyPrice = 1000
    lowestBondSellPrice = 1000

    highestVALBZBuyPrice = 0
    lowestVALBZSellPrice = 5000

    highestVALEBuyPrice = 0
    lowestVALESellPrice = 5000

    highestGSBuyPrice = 0
    lowestGSSellPrice = 5000

    highestMSBuyPrice = 0
    lowestMSSellPrice = 5000

    highestWFCBuyPrice = 0
    lowestWFCSellPrice = 5000

    highestXLFBuyPrice = 0
    lowestXLFSellPrice = 5000

    bondPosition = 0
    xlfPosition = 0
    valePosition = 0
    valbzPosition = 0
    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!
    while True:
        message = exchange.read_message()

        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "error":
            print(message)
        elif message["type"] == "reject":
            print(message)
        elif message["type"] == "fill":
            if message["symbol"] == "BOND":
                if message["dir"] == Dir.BUY: bondPosition += message["size"]
                elif message["dir"] == Dir.SELL: bondPosition -= message["size"]
            elif message["symbol"] == "XLF":
                if message["dir"] == Dir.BUY: xlfPosition += message["size"]
                elif message["dir"] == Dir.SELL: xlfPosition -= message["size"]
            elif message["symbol"] == "VALE":
                if message["dir"] == Dir.BUY: valePosition += message["size"]
                elif message["dir"] == Dir.SELL: valePosition -= message["size"]
            elif message["symbol"] == "VALBZ":
                if message["dir"] == Dir.BUY: valbzPosition += message["size"]
                elif message["dir"] == Dir.SELL: valbzPosition -= message["size"]
            print(message)
        elif message["type"] == "book":
            def best_price(side):
                    if message[side]:
                        return message[side][0][0]
            now = time.time()
            if message["symbol"] == "VALE":
                vale_bid_price = best_price("buy")
                vale_ask_price = best_price("sell")
                highestVALEBuyPrice = max(highestVALEBuyPrice, vale_bid_price)
                lowestVALESellPrice = min(lowestVALESellPrice, vale_ask_price)

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "vale_bid_price": vale_bid_price,
                            "vale_ask_price": vale_ask_price,
                        }
                    )
                if lowestVALBZSellPrice < highestVALEBuyPrice - 2:
                    if valbzPosition < 10 and valePosition < 5: 
                        quantity = 10 - valbzPosition
                        exchange.send_add_message(order_id=order_num, symbol="VALBZ", dir=Dir.BUY, price=lowestVALBZSellPrice, size=quantity)
                        order_num += 1
                    if valbzPosition > 5:
                        exchange.send_convert_message(order_id=order_num, symbol="VALE", dir=Dir.BUY, size=valbzPosition)
                        valePosition += valbzPosition
                        valbzPosition = 0
                        order_num += 1
                        sellprice = (highestVALEBuyPrice + lowestVALBZSellPrice) / 2
                        exchange.send_add_message(order_id=order_num, symbol="VALE", dir=Dir.SELL, price=1, size=valePosition)
                        order_num += 1
                    
                    print("CONVERTED VALBZ AT " + str(lowestVALBZSellPrice))
            elif message["symbol"] == "VALBZ":
                valbz_bid_price = best_price("buy")
                valbz_ask_price = best_price("sell")
                highestVALBZBuyPrice = max(highestVALBZBuyPrice, valbz_bid_price)
                lowestVALBZSellPrice = min(lowestVALBZSellPrice, valbz_ask_price)

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "valbz_bid_price": valbz_bid_price,
                            "valbz_ask_price": valbz_ask_price,
                        }
                    )
                if lowestVALBZSellPrice < highestVALEBuyPrice - 2:
                    if valbzPosition < 10 and valePosition < 5: 
                        quantity = 10 - valbzPosition
                        exchange.send_add_message(order_id=order_num, symbol="VALBZ", dir=Dir.BUY, price=lowestVALBZSellPrice, size=quantity)
                        order_num += 1
                    if valbzPosition > 5:
                        exchange.send_convert_message(order_id=order_num, symbol="VALE", dir=Dir.BUY, size=valbzPosition)
                        valePosition += valbzPosition
                        valbzPosition = 0
                        order_num += 1
                        sellprice = (highestVALEBuyPrice + lowestVALBZSellPrice) / 2
                        exchange.send_add_message(order_id=order_num, symbol="VALE", dir=Dir.SELL, price=1, size=valePosition)
                        order_num += 1
                    
                    print("CONVERTED VALBZ AT " + str(lowestVALBZSellPrice))
            elif message["symbol"] == "BOND": 
                bond_bid_price = best_price("buy")
                bond_ask_price = best_price("sell")
                highestBondBuyPrice = max(highestBondBuyPrice, bond_bid_price)
                lowestBondSellPrice = min(lowestBondSellPrice, bond_ask_price)
                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "bond_bid_price": bond_bid_price,
                            "bond_ask_price": bond_ask_price,
                        }
                    )
                if highestBondBuyPrice > 1002: 
                    if bondPosition > 0: 
                        exchange.send_add_message(order_id=order_num, symbol="BOND", dir=Dir.SELL, price=highestBondBuyPrice, size=bondPosition)
                        order_num += 1
                        print("BOUGHT BOND AT " + str(highestBondBuyPrice))
                elif lowestBondSellPrice < 998:
                    if bondPosition < 95: 
                        exchange.send_add_message(order_id=order_num, symbol="BOND", dir=Dir.BUY, price=highestBondBuyPrice, size=5)
                        order_num += 1
                        print("SOLD BOND AT " + str(lowestBondSellPrice))
            elif message["type"] == "GS":
                gs_bid_price = best_price("buy")
                gs_ask_price = best_price("sell")
                highestGSBuyPrice = max(highestGSBuyPrice, gs_bid_price)
                lowestGSSellPrice = min(lowestGSSellPrice, gs_ask_price)
                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "gs_bid_price": gs_bid_price,
                            "gs_ask_price": gs_ask_price,
                        }
                    )
            elif message["type"] == "MS":
                ms_bid_price = best_price("buy")
                ms_ask_price = best_price("sell")
                highestMSBuyPrice = max(highestMSBuyPrice, ms_bid_price)
                lowestMSSellPrice = min(lowestMSSellPrice, ms_ask_price)
                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "ms_bid_price": ms_bid_price,
                            "ms_ask_price": ms_ask_price,
                        }
                    )
            elif message["type"] == "WFC":
                wfc_bid_price = best_price("buy")
                wfc_ask_price = best_price("sell")
                highestWFCBuyPrice = max(highestWFCBuyPrice, wfc_bid_price)
                lowestWFCSellPrice = min(lowestWFCSellPrice, wfc_ask_price)
                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "wfc_bid_price": wfc_bid_price,
                            "wfc_ask_price": wfc_ask_price,
                        }
                    )
            elif message["type"] == "XLF":
                xlf_bid_price = best_price("buy")
                xlf_ask_price = best_price("sell")
                highestXLFBuyPrice = max(highestXLFBuyPrice, xlf_bid_price)
                lowestXLFSellPrice = min(lowestXLFSellPrice, xlf_ask_price)
                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "xlf_bid_price": xlf_bid_price,
                            "xlf_ask_price": xlf_ask_price,
                        }
                    )
                if lowestXLFSellPrice * 10 < 3 * highestBondBuyPrice + 2 * highestGSBuyPrice + 3 * highestMSBuyPrice + 2 * highestWFCBuyPrice - 20:
                    if xlfPosition <= 50:
                        exchange.send_add_message(order_id=order_num, symbol="XLF", dir=Dir.BUY, price=highestBondBuyPrice, size=50)
                        order_num += 1
                        exchange.send_convert_message(order_id=order_num, symbol="XLF", dir=Dir.SELL, size=50)
                        order_num += 1
                        exchange.send_add_message(order_id=order_num, symbol="BOND", dir=Dir.SELL, price=highestBondBuyPrice, size=15)
                        order_num += 1
                        exchange.send_add_message(order_id=order_num, symbol="GS", dir=Dir.SELL, price=highestBondBuyPrice, size=10)
                        order_num += 1
                        exchange.send_add_message(order_id=order_num, symbol="MS", dir=Dir.SELL, price=highestBondBuyPrice, size=15)
                        order_num += 1
                        exchange.send_add_message(order_id=order_num, symbol="WFC", dir=Dir.SELL, price=highestBondBuyPrice, size=10)
                        order_num += 1
        #elif message["type"] == "trade": 
            #print(message)
        elif message["type"] == "ack":
            print(message)
        elif message["type"] == "out":
            print(message)


        
        

            
        

        

        

        
        


# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        self.exchange_socket = self._connect(add_socket_timeout=args.add_socket_timeout)

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.exchange_socket.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
        self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s.makefile("rw", 1)

    def _write_message(self, message):
        json.dump(message, self.exchange_socket)
        self.exchange_socket.write("\n")

        now = time.time()
        self.message_timestamps.append(now)
        if len(
            self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
        team_name != "REPLACEME"
    ), "Please put your team name in the variable [team_name]."

    main()
