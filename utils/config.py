# -*-coding: utf-8 -*-
import os
from dotenv import load_dotenv


load_dotenv()   # 加载 utils/.env 文件

OKX_FLAG: str | None = os.getenv('OKX_FLAG')
OKX_API_KEY: str | None = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY: str | None = os.getenv("OKX_SECRET_KEY")