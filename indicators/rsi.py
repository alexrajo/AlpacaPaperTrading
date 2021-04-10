class Strategy:
    def __init__(self):
        self.history = []
        self.gain_sum = 0
        self.loss_sum = 0

        self.gain_history = []
        self.loss_history = []

        self.overbought_threshold = 70
        self.oversold_threshold = 30

        self.charts = [
            ["rsi"]
        ]

    def calculate_rsi(self, avg_gain, avg_loss, gain, loss):
        avg_gain = avg_gain != 0 and avg_gain or 1
        avg_loss = avg_loss != 0 and avg_loss or 1

        first_step = 100-(100/(1+avg_gain/avg_loss))
        # final = 100-(100/(1+(avg_gain*13+gain)/-(avg_loss*13+loss)))
        return first_step

    def on_data(self, info):

        close_price = info["c"]
        change_percent = len(self.history) > 0 and (close_price/self.history[-1]-1)*100 or 0

        if change_percent > 0:
            self.gain_sum += abs(change_percent)
            self.gain_history.append(abs(change_percent))
            self.loss_history.append(0)
        else:
            self.loss_sum += abs(change_percent)
            self.loss_history.append(abs(change_percent))
            self.gain_history.append(0)

        if len(self.history) > 13:
            self.gain_sum -= self.gain_history[-14]
            self.loss_sum -= self.loss_history[-14]


        t = max(1, min(len(self.history), 14))
        self.history.append(close_price)

        rsi = self.calculate_rsi(self.gain_sum/t, self.loss_sum/t, change_percent > 0 and change_percent or 0, change_percent < 0 and abs(change_percent) or 0)

        if rsi >= self.overbought_threshold:
            return -1
        elif rsi <= self.oversold_threshold:
            return 1

        return 0
