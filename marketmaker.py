from backtesting import evaluateHist, evaluateIntr
from strategy import Strategy
from order import Order
import numpy as np

class MarketMaker(Strategy):
    def __init__(self):
        self.petr3 = None
        self.usdbrl = None
        self.pbr = None
        self.margem = 1
        self.orders = None

    def calculate_pbr(self, petr3, usdbrl):
        pbr = ((petr3 * 2) / usdbrl) * 1.05
        return pbr

    def push(self, event):
        orders = []
        print('Event: {0} {1}@{2}'.format(event.instrument, event.quantity, event.price))

        if event.instrument == "PETR3":
            self.petr3 = event.price[3]

        if event.instrument == "USDBRL":
            self.usdbrl = event.price[3]

        if self.petr3 and self.usdbrl:
            self.pbr = self.calculate_pbr(self.petr3, self.usdbrl)

            #em que valor comprar e vender

            entrar = self.pbr - self.margem
            sair = self.pbr + self.margem

            #cancela
            if self.orders:
                for orderid in self.orders:
                    self.cancel(self.id, orderid)

            #manda duas novas ordens
            self.orders = []
            orders.append(Order("PBR", 1, entrar))
            orders.append(Order("PBR", -1, sair))
            for order in orders:
                self.orders.append(order.id)

            return orders
        return []

    def fill(self, id,  instrument, price, quantity, status):
        super().fill(id, instrument, price, quantity, status)
        orders = []
        if instrument == "PBR":
            if quantity < 0:
                orders.append(Order("PETR3", 1, self.pbr))
                orders.append(Order("USDBRL", -1, self.pbr))

            elif quantity > 0:
                orders.append(Order("PETR3", -1, self.pbr))
                orders.append(Order("USDBRL", 1, self.pbr))

        return orders

print(evaluateIntr(MarketMaker(), {'USDBRL':'USDBRL.csv', 'PETR3':'PETR3.csv', 'PBR':'PBR.csv'}))


