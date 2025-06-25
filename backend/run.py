import asyncio
import uvicorn
from main import app
from bot import start_bot

async def main():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    api_task = asyncio.create_task(server.serve())
    bot_task = asyncio.create_task(start_bot())

    await asyncio.gather(api_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())
