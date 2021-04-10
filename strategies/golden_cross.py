class Strategy:
    def __init__(self):
        self.history = []
        self.ma_sums = {
            "50": 0,
            "200": 0
        }
        self.ma_history = {
            "50": [],
            "200": []
        }
        self.charts = [
            ["ma", 50, 200]
        ]

    def get_moving_average(self, periods):
        self.ma_sums[str(periods)] += self.history[-1]
        if len(self.history) > periods:
            self.ma_sums[str(periods)] -= self.history[-periods]

        return self.ma_sums[str(periods)]/min(periods, len(self.history))

    def on_data(self, info):

        close_price = info["c"]
        self.history.append(close_price)

        ma_50 = self.get_moving_average(50)
        ma_200 = self.get_moving_average(200)
        self.ma_history["50"].append(ma_50)
        self.ma_history["200"].append(ma_200)

        if ma_50 < ma_200 and self.ma_history["50"][-2] >= self.ma_history["200"][-2]:
            return 1
        elif ma_50 > ma_200 and self.ma_history["50"][-2] <= self.ma_history["200"][-2]:
            return -1

        return 0
