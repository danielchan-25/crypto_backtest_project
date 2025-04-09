# -*-coding: utf-8 -*-
import os
import pandas as pd
from okx import MarketData
from binance.client import Client
from utils.logger import get_logger

logger = get_logger(__name__)

folders = [os.path.join("data", "raw"), os.path.join("data", "processed")]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)


def get_okx_klines(k_type) -> pd.DataFrame:
    """
    从 OKX 获取行情数据
    :param
        symbol: 合约品种名；
        k_type: K线周期（如 1m, 5m, 15m, 30m, 1h）；
        limit: 获取的K线数量；

    :df
        timestamp: 时间
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        ?: 未知
        ?: 未知
        confirm: K线状态，0表示K线未完结，1代表K线已完结
    """
    try:
        market_api = MarketData.MarketAPI()
        result = market_api.get_candlesticks(instId="BTC-USDT", bar=k_type, limit=9999)
        df = pd.DataFrame(result["data"], columns=["timestamp", "open", "high", "low", "close", "volume", "?", "?", "confirm"])

        if df.empty:
            return pd.DataFrame()

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Shanghai")    # 转换成北京时区
        df = df.sort_values(by="timestamp", ignore_index=True)
        return df

    except Exception as e:
        logger.error(e)
        return pd.DataFrame()


def get_binance_klines(k_type, proxy_address="http://127.0.0.1:7890") -> pd.DataFrame:
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

        # 因 Binance 的K线写法与普通的不同，用字典匹配更方便
        kline_interval_map = {
            "1m": Client.KLINE_INTERVAL_1MINUTE,
            "5m": Client.KLINE_INTERVAL_5MINUTE,
            "15m": Client.KLINE_INTERVAL_15MINUTE,
            "30m": Client.KLINE_INTERVAL_30MINUTE,
            "1h": Client.KLINE_INTERVAL_1HOUR,
            "1d": Client.KLINE_INTERVAL_1DAY,
        }
        k_type = kline_interval_map.get(k_type, Client.KLINE_INTERVAL_1MINUTE)

        client = Client()
        klines = client.get_klines(symbol="BTCUSDT", interval=k_type, limit=9999)

        if not klines:
            return pd.DataFrame()

        df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
                                           "quote_asset_volume", "trades", "taker_base", "taker_quote", "ignore"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df["open"] = df["open"].astype(float).round(2)
        df["high"] = df["high"].astype(float).round(2)
        df["low"] = df["low"].astype(float).round(2)
        df["close"] = df["close"].astype(float).round(2)
        return df

    except Exception as e:
        logger.error(e)
        return pd.DataFrame()


def get_klines(k_type):
    """
    优先尝试从 OKX 获取数据，失败则使用 Binance 获取
    """
    logger.info(f"开始尝试从 OKX 获取数据")
    df = get_okx_klines(k_type)

    if df.empty:
        logger.warning("OKX 数据拉取失败，尝试使用 Binance")
        df = get_binance_klines(k_type)

    df.to_csv(os.path.join("data", "raw", "BTCUSDT_klines.csv"), index=False)
