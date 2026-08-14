def calc_X_t (t,f,a,b):
    if t == 0:
        return a
    elif t == 1:
        return b
    else:
        x_t_2 = a
        x_t_1 = b
        for i in range(t-1):
            x_t = f(x_t_1,x_t_2)
            x_t_2 = x_t_1
            x_t_1 = x_t
        return x_t
# demo
def f(x,y):
    return x - y
a = 2
b = 3
print(calc_X_t(4,f,a,b))


class Consumer:
    # a consumer in this problem is parametrized by their alpha, and consumes some amount x
    def __init__(self, alpha=0.5, gamma=100):
        self.alpha = alpha
        self.gamma = gamma
        self.x = 0.
        self.utility = 0.
    def utility_function(self, x):
        return self.gamma * (x ** self.alpha)

    # now let's describe the process of how a consumer chooses how much to buy at a given price.
    def consume(self, price):  # defined over positive nonzero prices
        x1 = 0
        benefit0 = 0.
        benefit1 = price

        while benefit1 - benefit0 >= price:  # the consumer will purchase until price exceeds marginal benefit
            x1 += 1  # increase the potential purchase amount by 1
            benefit0 = benefit1  # store the benefit at the last level of output
            benefit1 = self.utility_function(x1)  # compare to the utility at the new level

        self.x = x1 - 1
        self.utility = self.utility_function(self.x) - price * self.x
        return self.x

class Firm:
    # a firm in this problem is characterized by a single beta parameter that determines their marginal costs.
    def __init__(self, beta=0.1):
        self.beta = beta
        self.x = 0.
        self.profit = 0.

    # first let's define a cost function for this firm, given their cost parameter beta.
    def cost(self, x):
        return self.beta * (x ** 2)

    # now let's describe how a firm figures out how much they would want to produce at a given price
    def produce(self, price):
        x1 = 0
        profit0 = 0.
        profit1 = 1.

        while profit1 - profit0 >= 0:  # the firm will produce one more good as long as it increases profits
            x1 += 1  # increase potential output by 1
            profit0 = profit1  # store the profit at the last level of output
            profit1 = price * x1 - self.cost(x1)  # compute profit at the new level of output

        # after the loop is finished, we want the last profitable level of x, which would be x-1.
        self.x = x1 - 1
        self.profit = price * self.x - self.cost(self.x)
        return self.x

class Economy:
    def __init__(self, consumer_list, firm):
        self.consumer_list = consumer_list
        self.firm = firm
        self.p = None
        self.qd = None
        self.qs = None

    def equilibrate(self):
        p = 0.1  # choose a small price as the starting point
        qd = 0
        for consumer in self.consumer_list:
            qd += consumer.consume(p)

        qs = self.firm.produce(p)
        while qs < qd:  # check if the market has cleared
            p += 0.1  # add ten cents to the price
            qd = 0
            for consumer in self.consumer_list:
                consumer.consume(p)
                qd += consumer.x
            qs = self.firm.produce(p)
        self.p = p
        self.qd = qd
        self.qs = qs


# class Economy:
#     def __init__(self, consumer, firm):
#         self.consumer = consumer
#         self.firm = firm
#         self.p = None
#         self.qd = None
#         self.qs = None
#
#     def equilibrate(self):
#         p = 0.1  # choose a small price as the starting point
#         qd = self.consumer.consume(p)
#         qs = self.firm.produce(p)
#         while qs < qd:  # check if the market has cleared
#             p += 0.1  # add ten cents to the price
#             qd = self.consumer.consume(p)  # find quantities demanded and supplied at this new price
#             qs = self.firm.produce(p)
#         self.p = p
#         self.qd = qd
#         self.qs = qs
Consumer1=Consumer(alpha = 0.4, gamma=100)
Consumer2=Consumer(alpha = 0.5, gamma=100)
Consumer3=Consumer(alpha = 0.6, gamma=100)
company = Firm(beta = 0.1)
economy1 = Economy([Consumer1,Consumer2,Consumer3], company)
economy1.equilibrate()
print(f"In this toy economy, the market clearing price is {round(economy1.p,2)}. At this price, {economy1.qd} goods are demanded and {economy1.qs} goods are supplied.")






