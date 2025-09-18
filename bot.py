import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Простейший RSI сигнал
def calculate_rsi(prices, period=14):
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [x if x>0 else 0 for x in deltas]
    losses = [-x if x<0 else 0 for x in deltas]
    avg_gain = sum(gains[-period:])/period
    avg_loss = sum(losses[-period:])/period
    rs = avg_gain / (avg_loss + 0.00001)
    rsi = 100 - (100 / (1 + rs))
    return rsi

async def get_signal():
    # Берем исторические цены BTC на CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1&interval=minute"
    data = requests.get(url).json()
    prices = [p[1] for p in data['prices']]
    rsi = calculate_rsi(prices)
    
    if rsi < 30:
        return "BUY", rsi
    elif rsi > 70:
        return "SELL", rsi
    else:
        return "HOLD", rsi

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Я бот для сигналов криптовалют. Пиши /signal чтобы получить рекомендацию.")

@dp.message_handler(commands=['signal'])
async def signal(message: types.Message):
    signal, rsi = await get_signal()
    await message.reply(f"Сигнал: {signal}\nRSI: {rsi:.2f}")

# Фоновая задача каждые 5 минут
async def background():
    while True:
        signal, rsi = await get_signal()
        if signal != "HOLD":
            await bot.send_message(chat_id="YOUR_CHAT_ID", text=f"Сигнал: {signal}\nRSI: {rsi:.2f}")
        await asyncio.sleep(300)  # 5 минут

if __name__ == "__main__":
    dp.loop.create_task(background())
    executor.start_polling(dp, skip_updates=True)
