from typing import List
from schemas import Order


class StockExchange:
    def __init__(self):
        self.buy_orders:List[Order] = []
        self.sell_orders:List[Order]= []
        self.last_traded_price = None  # 用于存储最后的成交价格

    def add_order(self, order: Order):
        if order.action == 'buy':
            self.buy_orders.append(order)
            self.buy_orders.sort(key=lambda x: x.price, reverse=True)
        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(key=lambda x: x.price)

    def match_orders(self):
        matches = []

        while self.buy_orders and self.sell_orders:
            best_buy = self.buy_orders[0]
            best_sell = self.sell_orders[0]

            if best_buy.price >= best_sell.price:
                traded_shares = min(best_buy.share, best_sell.share)
                matches.append((best_buy, best_sell, traded_shares))

                # 更新最后的成交价格
                self.last_traded_price = best_sell.price

                if best_buy.share > best_sell.share:
                    self.buy_orders[0] = Order(
                        uid=best_buy.uid, 
                        action=best_buy.action, 
                        price=best_buy.price, 
                        share=best_buy.share - traded_shares)
                    self.sell_orders.pop(0)
                elif best_buy.share < best_sell.share:
                    self.sell_orders[0] = Order(
                        uid=best_sell.uid,
                        action= best_sell.action, 
                        price=best_sell.price, 
                        share=best_sell.share - traded_shares)
                    self.buy_orders.pop(0)
                else:
                    self.buy_orders.pop(0)
                    self.sell_orders.pop(0)
            else:
                break

        return matches


    