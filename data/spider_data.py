# -*-coding: utf-8 -*-
import os
import pandas as pd
import okx.MarketData as MarketData
from binance.client import Client
from utils.logger import get_logger
from utils.config import OKX_FLAG

logger = get_logger(__name__)
k_type_map = {"15m": "15m", "30m": "30m", "1H": "1h", "2H": "2h"}   # 需要获取的K线类型


def get_okx_klines():
    """
    从 OKX 获取行情数据
    :param
        symbol: 合约品种名；
        k_type: K线周期（如 1m, 15m, 30m, 1h）；
        limit: 获取的K线数量；

    :df
        timestamp: 时间
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        volCcy: 成交量
        volCcyQuote: 成交量
        confirm: K线状态，0表示K线未完结，1代表K线已完结
    """
    try:
        flag = OKX_FLAG
        marketDataAPI = MarketData.MarketAPI(flag=flag)
        for k_type in list(k_type_map.keys()):
            result = marketDataAPI.get_candlesticks(instId="BTC-USDT", bar=k_type, limit=9999)
            df = pd.DataFrame(result["data"], columns=["timestamp", "open", "high", "low", "close", "volume", "volCcy", "volCcyQuote", "confirm"])

            if df.empty:
                logger.error(f"[OKX] - 获取{k_type}数据时为空，准备启用 Binance 数据源...")
                return False

            df["timestamp"] = pd.to_datetime(df["timestamp"].astype("int64"), unit="ms", utc=True)
            df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Shanghai")    # 转换成北京时区
            df = df.sort_values(by="timestamp", ignore_index=True)
            df.to_csv(os.path.join("data", "klines_data", f"BTCUSDT_klines_{k_type}.csv"), index=False)
        return True

    except Exception as e:
        logger.error(f"[OKX] - 获取数据发生未知错误：{e}")
        return False


def get_binance_klines(proxy_address="http://10.17.174.144:7890"):
    """
    从 Binance 获取行情数据
    :param
        symbol: 合约品种名；
        k_type: K线周期（如 Client.KLINE_INTERVAL_1HOUR, Client.KLINE_INTERVAL_1DAY）；
        limit: 获取的K线数量；

    :df
        timestamp: 时间
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        close_time: 结束时间
        quote_asset_volume: 未知
        trades: 未知
        taker_base: 未知
        taker_quote: 未知
        ignore: 未知
    """
    try:
        # 注意：从 Binance 获取行情数据需要挂载代理，且大陆与美国的IP禁止连接，可以使用香港的IP。
        os.environ["http_proxy"] = proxy_address
        os.environ["https_proxy"] = proxy_address

        client = Client()
        for k_type in list(k_type_map.values()):
            klines = client.get_klines(symbol="BTCUSDT", interval=k_type, limit=9999)

            if not klines:
                logger.warning(f"[Binance] - 获取{k_type}数据时为空")
                return False

            df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                               "quote_asset_volume", "trades", "taker_base", "taker_quote", "ignore"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df["open"] = df["open"].astype(float).round(2)
            df["high"] = df["high"].astype(float).round(2)
            df["low"] = df["low"].astype(float).round(2)
            df["close"] = df["close"].astype(float).round(2)
            df.to_csv(os.path.join("data", "klines_data", f"BTCUSDT_klines_{k_type}.csv"), index=False)
        return True

    except Exception as e :
        logger.error(f"[Binance] - 获取数据发生未知错误：{e}")
        return False


def get_klines():
    """
    优先尝试从 OKX 获取数据，失败则使用 Binance 获取
    只需获取最近的 N 条 K 线数据，用于计算信号
    """
    if get_okx_klines():
        return True
    else:
        logger.warning("[OKX] - 数据拉取失败，尝试使用 Binance")
        if get_binance_klines():
            return True
        else:
            logger.error("[Binance] - 数据拉取失败，请检查网络是否正常")
            return False