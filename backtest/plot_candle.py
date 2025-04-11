# -*-coding: utf-8 -*-
import numpy as np
import pandas as pd
import mplfinance as mpf


# 绘制K线图函数


def plot_candlechart(df, title="BTC-USDT", volume_panel=True, avg=False, ma_panel=True, add_plot=None):
    """
    绘制K线图，并可选地添加其他自定义图形（例如技术指标）。

    :param title:
    :param df: pd.DataFrame, 必须包含以下列：
        - timestamp: 时间戳（通常是交易的时间点）
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量

    :param volume_panel: 是否添加成交量面板，默认为 True。

    :param avg_plot_avg: 是否添加均线。默认为False，如果为True，则会绘制累积均值线。

    :param add_plot: 用于添加自定义的额外图形（例如技术指标），可以是单个对象或对象列表。
                      如果不传递，默认为 None。

    :return: None, 直接在图形界面显示K线图。
    """
    # 重命名列，mplfinance 需要指定的列名才能显示
    df = df.rename(columns={"timestamp": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    # 累积均值线
    if avg:
        df["avg"] = df["Close"].expanding(1).mean()
        add_plot_avg = mpf.make_addplot(
            data=df["avg"],
            type="line",
            color="yellow"
        )
    else:
        add_plot_avg = None

    # 成交量图
    if volume_panel:
        volume_colors = np.where(df["Close"] > df["Open"], "red", "green")  # 成交量柱颜色
        add_plot_volume = mpf.make_addplot(
            data=df["Volume"],
            panel=1,  # panel=1 表示在第二个面板（主图是 panel=0）
            type="bar",
            ylabel="Volume",
            color=volume_colors
        )
    else:
        add_plot_volume = None

    # 合并附加图形
    addplot_list = []
    if add_plot:
        if isinstance(add_plot, list):
            addplot_list.extend(add_plot)
        else:
            addplot_list.append(add_plot)

    if add_plot_avg:
        addplot_list.append(add_plot_avg)
    if add_plot_volume:
        addplot_list.append(add_plot_volume)

    mpf_params = {
        "data": df,
        "title": title,
        "type": "candle",
        "style": "default",
        "addplot": addplot_list,
        "volume": False,
        "panel_ratios": (3, 1),
        "figratio": (16, 8),
        "tight_layout": True,
        "figscale": 1.2,
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "xrotation": 10,
    }


    # 主图
    if ma_panel:
        mpf_params["mav"] = (5, 15, 30)
        mpf_params["mavcolors"] = ["orange", "blue", "red"]

    mpf.plot(**mpf_params)
    mpf.show()