# -*-coding: utf-8 -*-
import os
import pandas as pd

# sar策略


class SARCalculator:
    def __init__(self, af=0.02, mf=0.2):
        self.af = af    # 加速因子
        self.mf = mf    # 最大加速因子
        self.sar_values = []


    def calc_sar(self, high_values, low_values):
        """
        计算 SAR 指标
        """
        sar_values = []
        trend = 1   # 1：上升趋势，-1：下降趋势
        ep = high_values[0]     # 极点，初始值为第一个高点
        sar = low_values[0]     # 初始SAR值为第一个周期最低价
        af = self.af            # 初始加速因子

        for i in range(1, len(high_values)):
            # 计算当前周期的SAR值
            sar = sar + af * (ep - sar)
            sar_values.append(sar)

            # 判断趋势反转
            if trend == 1:  # 上升趋势
                if low_values[i] < sar: # 如果当前周期的最低价低于SAR值，反转为下降趋势
                    trend = -1
                    sar = ep    # 反转时SAR值设置为极端点
                    ep = low_values[i]  # 更新极端点为当前周期的最低价
                    af = self.af    # 重置加速因子为初始值
                else:
                    if high_values[i] > ep: # 创新高时，更新极点为当前周期最高价
                        ep = high_values[i]
                        af = min(af + self.af, self.mf) # 更新加速因子

            elif trend == -1:       # 下降趋势
                if high_values[i] > sar:    # 如果当前周期的最高价高于SAR值，反转为上升趋势
                    trend = 1
                    sar = ep    # 反转时SAR值设置为极端点
                    ep = high_values[i] # 更新极端点为当前周期的最高价
                    af = self.af    # 重置加速因子为初始值
                else:
                    if low_values[i] < ep:  # 更新极端点为当前周期的最低价
                        ep = low_values[i]
                        af = min(af + self.af, self.mf)

        return sar_values


df = pd.read_csv(os.path.join("..", "data", "klines_data", "BTCUSDT_klines_30m.csv"))
high_values = df["high"]
low_values = df["low"]

sar_calculator = SARCalculator()
sar_values = sar_calculator.calc_sar(high_values, low_values)
print(sar_values)