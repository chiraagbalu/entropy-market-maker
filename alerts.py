from discord.ext import tasks
import os
import discord
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv()


db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')


stale_time = 86400
max_leverage = 200
channel = os.getenv('CHANNEL')


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0

        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        channel = self.get_channel(channel)
        await channel.send('hi')

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def my_background_task(self):
        channel = self.get_channel(channel)  # channel ID goes here

        dbstring = (
            f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
        sqlconn = create_engine(dbstring).connect()
        table = 'ec2_data'
        mmData = pd.read_sql_table(table, sqlconn)
        await channel.send(f'using table: {table}')
        df = mmData
        markets = df.marketName.unique()
        for market in markets:
            lastData = np.array(df[df.marketName == market]
                                ['time'].sort_values(ascending=False))[0]
            lastPrice = np.array(
                df[df.marketName == market]['oraclePrice'].sort_values(ascending=False))[0]
            lastDataTime = lastData.timestamp()
            now = pd.to_datetime('now').timestamp()
            timesincelastdata = now-lastDataTime
            print(f'info for: {market}')
            print(f'last data: {lastData}')
            print(f'now: {pd.to_datetime("now")}')
            print(f'hours since last data: {(timesincelastdata)/3600}')
            if timesincelastdata > stale_time:
                await channel.send(
                    f'stale data warning for {market}: hours since last data: {(timesincelastdata)/3600}')
            else:
                await channel.send(f'{market} data up to date!')
            lastBasePos = np.array(
                df[df.marketName == market]['basePos'].sort_values(ascending=False))[0]
            lastNotionalDelta = lastBasePos * lastPrice
            lastLeverage = np.array(
                df[df.marketName == market]['leverage'].sort_values(ascending=False))[0]
            print(f'last notional delta: {lastNotionalDelta}')
            print(f'last leverage: {lastLeverage}%')
            if abs(lastLeverage) > max_leverage:
                await channel.send(
                    f'leverage warning for {market}: current leverage: {lastLeverage}%')
            else:
                await channel.send(f'{market} leverage is within bounds!')
            print('='*35)

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = MyClient()
client.run(os.getenv('BOT_KEY'))
