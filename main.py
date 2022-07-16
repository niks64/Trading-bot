#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from collections import deque
from enum import Enum
from operator import pos
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
    order_num+=1
    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    vale_bid_price, vale_ask_price = None, None
    vale_last_print_time = time.time()

    positions = {"BOND": 0, "VALBZ": 0, "VALE": 0, "GS": 0, "MS": 0, "WFC": 0, "XLF": 0}
    highestBuyPrices = {"BOND": 990, "VALBZ": 0, "VALE": 0, "GS": 0, "MS": 0, "WFC": 0, "XLF": 0}
    lowestSellPrices = {"BOND": 1010, "VALBZ": 999999, "VALE": 999999, "GS": 999999, "MS": 999999, "WFC": 999999, "XLF": 999999}

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

        def best_price(side):
            if message[side]:
                return message[side][0][0]

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
            if message["symbol"] == "VALE":
                if message["dir"] == Dir.BUY: positions["VALE"] += message["size"]
                elif message["dir"] == Dir.SELL: positions["VALE"] -= message["size"]
            elif message["symbol"] == "VALBZ":
                if message["dir"] == Dir.BUY: positions["VALBZ"] += message["size"]
                elif message["dir"] == Dir.SELL: positions["VALBZ"] -= message["size"]
            print(message)
        elif message["type"] == "book":
            if message["symbol"] == "VALE":

                vale_bid_price = best_price("buy")
                vale_ask_price = best_price("sell")

                highestBuyPrices["VALE"] = max(highestBuyPrices["VALE"], vale_bid_price)
                lowestSellPrices["VALE"] = min(lowestSellPrices["VALE"], vale_ask_price)

                now = time.time()

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "vale_bid_price": vale_bid_price,
                            "vale_ask_price": vale_ask_price,
                        }
                    )
                if lowestSellPrices["VALE"] < highestBuyPrices["VALBZ"] - 5 and positions["VALE"] <= 8:
                    exchange.send_add_message(order_id=order_num, symbol="VALE", dir=Dir.BUY, price=lowestSellPrices["VALE"], size=2)
                    order_num += 1
                    exchange.send_convert_message(order_id=order_num, symbol="VALE", dir=Dir.SELL, size=2)
                    positions["VALE"] -= 2
                    positions["VALBZ"] += 2
                    order_num += 1
                    exchange.send_add_message(order_id=order_num, symbol="VALBZ", dir=Dir.SELL, price=highestBuyPrices["VALBZ"] - 5, size=2)

            elif message["symbol"] == "VALBZ": 
                valbz_bid_price = best_price("buy")
                valbz_ask_price = best_price("sell")

                highestBuyPrices["VALBZ"] = max(highestBuyPrices["VALBZ"], valbz_bid_price)
                lowestSellPrices["VALBZ"] = max(lowestSellPrices["VALBZ"], valbz_ask_price)

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "valbz_bid_price": valbz_bid_price,
                            "valbz_ask_price": valbz_ask_price,
                        }
                    )
                if lowestSellPrices["VALBZ"] < highestBuyPrices["VALE"] - 5 and positions["VALBZ"] <= 8:
                    exchange.send_add_message(order_id=order_num, symbol="VALBZ", dir=Dir.BUY, price=lowestSellPrices["VALBZ"], size=2)
                    order_num += 1
                    exchange.send_convert_message(order_id=order_num, symbol="VALBZ", dir=Dir.SELL, size=2)
                    positions["VALBZ"] -= 2
                    positions["VALE"] += 2
                    order_num += 1
                    exchange.send_add_message(order_id=order_num, symbol="VALE", dir=Dir.SELL, price=highestBuyPrices["VALE"] - 5, size=2)

            elif message["symbol"] == "BOND":
                bond_bid_price = best_price("buy") if best_price("buy") else 990
                bond_ask_price = best_price("sell") if best_price("sell") else 1010
                highestBuyPrices["BOND"] = max(highestBuyPrices["BOND"], bond_bid_price)
                lowestSellPrices["BOND"] = max(lowestSellPrices["BOND"], bond_ask_price)
                now = time.time()

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "bond_bid_price": bond_bid_price,
                            "bond_ask_price": bond_ask_price,
                        }
                    )

                if positions["BOND"] >= 0:
                    exchange.send_add_message(order_id=order_num, symbol="BOND", dir=Dir.SELL,
                                                price=1001, size=5 )
                    order_num += 1
                    print("BOUGHT BOND AT " + str(1001))
                if positions["BOND"] < 95:
                    exchange.send_add_message(order_id=order_num, symbol="BOND", dir=Dir.BUY,
                                                price=999, size=5)
                    order_num += 1
                    print("SOLD BOND AT " + str(998))



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