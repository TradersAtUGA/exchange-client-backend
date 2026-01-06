"""
This is a demo file to ensure that the exchange
can receive orders from a demo broker such as this 
file
"""
import quickfix as fix
import time
from datetime import datetime
import order as ord

SOH = chr(1)
VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT"]
VALID_TIF = ["DAY", "FOK", "IOC"]

SIDE_MAP = {
    "BUY": fix.Side_BUY, 
    "SELL": fix.Side_SELL
}

ORDER_TYPE_MAP = {
    "MARKET": fix.OrdType_MARKET,
    "LIMIT": fix.OrdType_LIMIT
}

TIF_MAP = {
    "DAY": fix.TimeInForce_DAY,
    "FOK": fix.TimeInForce_FILL_OR_KILL,
    "IOC": fix.TimeInForce_IMMEDIATE_OR_CANCEL
}
    
def check_valid_order_args(side: str, order_type: str, tif: str, 
                            ticker: str, qty: int, price: float) -> bool:
    if side not in VALID_SIDES: return False
    if order_type not in VALID_ORDER_TYPES: return False
    if tif not in VALID_TIF: return False
    if qty < 0 or price < 0: return False


class Application(fix.Application):
    sessionID = "BROKER1"
    cl_ord_id = int(time.time() * 1e6)

    def onCreate(self, sessionID):
        print("onCreate", sessionID)

    def onLogon(self, sessionID):
        self.sessionID = sessionID
        print("LOGON", sessionID)

    def onLogout(self, sessionID):
        print("LOGOUT", sessionID)

    def toAdmin(self, message, sessionID):
        print("ADMIN S >>", message.toString().replace(SOH, "|"))

    def fromAdmin(self, message, sessionID):
        print("ADMIN R <<", message.toString().replace(SOH, "|"))

    def toApp(self, message, sessionID):
        print("APP   S >>", message.toString().replace(SOH, "|"))

    def fromApp(self, message, sessionID):
        print("APP   R <<", message.toString().replace(SOH, "|"))

    def nextClOrdID(self):
        """
        This generates the broker side order id number 
        this is not used internally by the exchange 
        """
        self.cl_ord_id += 1
        return str(self.cl_ord_id)

    def send_new_order(self): # testing method dont use for production 
        if not self.sessionID:
            print("Not logged on yet")
            return

        msg = fix.Message()
        header = msg.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))  # 35=D

        msg.setField(fix.ClOrdID(self.nextClOrdID()))             # 11
        msg.setField(fix.Symbol("MSFT"))                          # 55
        msg.setField(fix.Side(fix.Side_BUY))                      # 54
        msg.setField(fix.OrderQty(100))                           # 38
        msg.setField(fix.OrdType(fix.OrdType_LIMIT))              # 40
        msg.setField(fix.Price(100.25))                           # 44
        msg.setField(fix.TimeInForce(fix.TimeInForce_DAY))        # 59

        tx_time = fix.TransactTime()
        tx_time.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
        msg.setField(tx_time)                                     # 60

        fix.Session.sendToTarget(msg, self.sessionID)

    # TODO(vikas) add a API endpoint that calls this method so users can place 
    # orders to the exchange
    def create_and_send_order(self, side: str, order_type: str, 
                              tif: str, ticker: str, qty: int, 
                              price: float) -> None:
        if check_valid_order_args(
            side, order_type, tif, ticker, qty, price
            ):
                msg = fix.Message()
                header= msg.getHeader()
                header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))

                msg.setField(fix.ClOrdID(self.nextClOrdID()))
                msg.setField(fix.Symbol(ticker)) # exchange will validate ticker 
                msg.setField(fix.OrderQty(qty))
                msg.setField(fix.Price(price))
                msg.setField(fix.Side(SIDE_MAP[side]))
                msg.setField(fix.OrdType(ORDER_TYPE_MAP[order_type]))
                msg.setField(fix.TimeInForce(TIF_MAP[tif]))

                tx_time = fix.TransactTime()
                tx_time.setString(datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
                msg.setField(tx_time) 

                fix.Session.sendToTarget(msg, self.sessionID)
        else:
            pass # TODO:(vikas) reject order here and inform user if fields are invalid 
            # negative qty, invalid ticker, etc. 

# sets up broker side server 
# NOTE: this server should be run on a separate thread in parallel with the 
# fast API server 
def main():
    # change PATH if necessary 
    settings = fix.SessionSettings("initiator.cfg")

    app = Application()
    store = fix.FileStoreFactory(settings)
    log = fix.FileLogFactory(settings)

    initiator = fix.SocketInitiator(app, store, settings, log)

    initiator.start()
    print("Initiator started")

    try:
        while True:
            cmd = input("1 = send order, q = quit: ")
            if cmd == "1":
                app.send_new_order()
            elif cmd == "q":
                break
    finally:
        initiator.stop()
        print("exit")

if __name__ == "__main__":
    main()
