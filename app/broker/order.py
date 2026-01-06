"""
Class for orders
"""
import quickfix as fix

VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT"]
VALID_TIF = ["DAY", "FOK", "IOC"]

class Order():
    def __init__(
                self,
                side: str, 
                order_type: str, 
                tif: str, 
                ticker: str, 
                qty: int, 
                price: float, 
                ):
        self.broker_id = 1 # broker specific
        self.client_id = 1 # client id is not sent to the exchange only for internal use
        self.set_side(side)
        self.set_order_type(order_type)
        self.set_tif(tif)
        self.symbol = ticker
        self.set_qty(qty)
        self.set_price(price)
        
    def set_side(self, side: str) -> None:
        """
        Set side of an order, return sentinel value
        on ill formed orders
        """
        if side not in VALID_SIDES:
            self.side = "INVALID"
        self.side = side

    def set_order_type(self, order_type: str) -> None:
        """
        Set order type of an order, return sentinel 
        value on ill formed orders
        """
        if order_type not in VALID_ORDER_TYPES:
            self.order_type = "INVALID"
        self.order_type = order_type

    def set_tif(self, tif: str) -> None:
        """
        Set tif of an order, return sentinel value
        on ill formed orders
        """
        if tif not in VALID_TIF:
            self.tif = "INVALID"
        self.tif = tif

    def set_qty(self, qty: int) -> None:
        """
        Set qty of an order, return sentinel value
        on ill formed orders
        """
        if qty < 0:
            self.qty = -1
        self.qty = qty

    def set_price(self, price: float) -> None:
        """
        Set price of an order, return sentinel value
        on ill formed orders
        """
        if price < 0:
            self.price = -1.0
        self.price = price 

    def check_valid(self) -> bool:
        """Checks if a order is properly formed"""
        if self.tif == "INVALID": return False
        if self.order_type == "INVALID": return False
        if self.side == "INVALID": return False
        if self.price <= 0 or self.qty <= 0: return False

