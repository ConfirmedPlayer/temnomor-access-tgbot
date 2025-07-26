import orjson
import redis.asyncio as redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiomoney import YooMoney
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tools.http import AiohttpClient
from tools.x_ui import XUISession

from .env import env

bot = Bot(
    token=env.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

logger_bot = Bot(token=env.TELEGRAM_LOGGING_BOT_TOKEN)

redis_storage = RedisStorage(
    redis=redis.Redis(host=env.REDIS_HOSTNAME, decode_responses=True),
    json_loads=orjson.loads,
    json_dumps=orjson.dumps,
)

dp = Dispatcher(storage=redis_storage)

http_client = AiohttpClient()

x_ui_session = XUISession(http_client)

scheduler = AsyncIOScheduler()

yoomoney = YooMoney(env.YOOMONEY_ACCESS_TOKEN)
