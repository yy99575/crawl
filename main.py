import asyncio
import aiohttp
from bs4 import BeautifulSoup
from db.connection import db_config

print("数据库配置：", db_config)
print("✅ 所有导入成功，环境准备就绪！")