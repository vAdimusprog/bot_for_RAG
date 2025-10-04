import asyncio
from bot import bot, dp, scheduler
from start import start_router
# from work_time.time_func import
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands():
    commands = [BotCommand(command='start', description='Меню'),
                BotCommand(command='faq', description='Частые вопросы')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    print("Бот запущен и команды установлены!")

async def main():
    # scheduler.add_job(send_time_msg, 'interval', seconds=10)
    # scheduler.start()
    dp.include_router(start_router)
    await set_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())