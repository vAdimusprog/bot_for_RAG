from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from all_kb import main_kb
from aiogram.filters import CommandStart, Command, CommandObject
from inline_kbs import ease_link_kb
from aiogram.types import CallbackQuery
from create_bot import  create_qst_inline_kb, questions
import asyncio
from aiogram.utils.chat_action import ChatActionSender
from bot import bot, admins, txt
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from RAG import RAGSystem

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "⚙️ Я ТОКАРЬ СТЭТХЭМ. ПОКАЖУ КАК МУЖИКИ ТОЧАТ ДЕТАЛИ. 💪\n\n"
        "Никаких соплей, только сталь и результат. Выбирай, что нужно:",
        reply_markup=main_kb(message.from_user.id)
    )


class QuestionState(StatesGroup):
    waiting_for_question = State()


@start_router.message(F.text == 'Задать вопрос')
async def get_inline_btn_link(message: Message, state: FSMContext):
    await message.answer(
        '🔧 <b>Задайте ваш вопрос:</b>\n\n'
        'Просто напишите его в чат, а я постараюсь помочь! '
        'Не забудьте добавить вопросительный знак "?"',
        parse_mode='HTML',
        reply_markup=types.ReplyKeyboardRemove()  # Убираем клавиатуру на время вопроса
    )
    await state.set_state(QuestionState.waiting_for_question)


@start_router.message(QuestionState.waiting_for_question)
async def handle_question(message: Message, state: FSMContext):
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action="typing"):
        """Обработчик вопроса в состоянии ожидания"""
        if message.text and "?" in message.text:
            try:
                rag = RAGSystem(txt)
                answer = rag.ask_question(message.text)

                await message.answer(
                    f"💡 <b>Ответ на ваш вопрос:</b>\n\n{answer}",
                    parse_mode='HTML'
                )

            except Exception as e:
                await message.answer(
                    "❌ Произошла ошибка при обработке вопроса. Попробуйте позже."
                )
            finally:
                # Возвращаем основное меню после ответа
                await message.answer(
                    "Возвращаю в главное меню:",
                    reply_markup=main_kb(message.from_user.id)
                )
                await state.clear()

        else:
            # Если сообщение без вопросительного знака
            await message.answer(
                "❓ Пожалуйста, задайте вопрос с вопросительным знаком '?'\n\n"
                "Или нажмите /cancel для отмены"
            )
@start_router.message(Command('cancel'))
@start_router.message(F.text.lower() == 'отмена')
async def cancel_question(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Ввод вопроса отменен.",
        reply_markup=main_kb(message.from_user.id)
    )



@start_router.message(F.text == 'Давай инлайн!')
async def get_inline_btn_link(message: Message):
    await message.answer('Вот тебе инлайн клавиатура со ссылками!', reply_markup=ease_link_kb())

@start_router.message(F.text == '📖 Кто я')
async def get_inline_btn_link(message: Message):
    await message.answer(
        "<tg-spoiler>⚙️ Я ТОКАРЬ СТЭТХЭМ</tg-spoiler>\n\n"
        "Покажу как мужики точат детали. Без компромиссов.\n\n",
            reply_markup = main_kb(message.from_user.id)
    )

@start_router.message(F.text == "👤 Что смогу в будущем?")
async def get_inline_btn_link(message: Message):
    await message.answer(
        "Научусь получать от тебя текст",
            reply_markup = main_kb(message.from_user.id)
    )



@start_router.callback_query(F.data == 'back_home')
async def get_home(call: CallbackQuery):
    await call.answer('Иду домой', show_alert=False)
    await call.message.answer(
        "Добро пожаловать домой! 🏠",
        reply_markup=main_kb(call.from_user.id)
    )

@start_router.message(Command('faq'))
async def cmd_start_2(message: Message):
    await message.answer('Сообщение с инлайн клавиатурой с вопросами', reply_markup=create_qst_inline_kb(questions))

@start_router.callback_query(F.data.startswith('qst_'))
async def cmd_start(call: CallbackQuery):
    await call.answer()
    qst_id = int(call.data.replace('qst_', ''))
    qst_data = questions[qst_id]
    msg_text = f'Ответ на вопрос {qst_data.get("qst")}\n\n' \
               f'<b>{qst_data.get("answer")}</b>\n\n' \
               f'Выбери другой вопрос:'
    async with ChatActionSender(bot=bot, chat_id=call.from_user.id, action="typing"):
        await asyncio.sleep(2)
        await call.message.answer(msg_text, reply_markup=create_qst_inline_kb(questions))

@start_router.message(Command(commands=["settings", "about"]))
async def univers_cmd_handler(message: Message, command: CommandObject):
    command_args: str = command.args
    command_name = 'settings' if 'settings' in message.text else 'about'
    response = f'Была вызвана команда /{command_name}'
    if command_args:
        response += f' с меткой <b>{command_args}</b>'
    else:
        response += ' без метки'
    await message.answer(response)



@start_router.message(F.text.lower().contains('подписывайся'), IsAdmin(admins))
async def process_find_word(message: Message):
    await message.answer('О, админ, здарова! А тебе можно писать подписывайся.')


@start_router.message(F.text.lower().contains('подписывайся'))
async def process_find_word(message: Message):
    await message.answer('В твоем сообщении было найдено слово "подписывайся", а у нас такое писать запрещено!')


@start_router.message(Command('test_edit_msg'))
async def cmd_start(message: Message, state: FSMContext):
    # Бот делает отправку сообщения с сохранением объекта msg
    msg = await message.answer('Отправляю сообщение')

    # Достаем ID сообщения
    msg_id = msg.message_id

    # Имитируем набор текста 2 секунды и отправляеВ коде оставлены комментарии. Единственное, на что нужно обратить внимание, — строка:

#м какое-то сообщение
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action="typing"):
        await asyncio.sleep(2)
        await message.answer('<tg-spoiler>Новое сообщение</tg-spoiler>')

    # Делаем паузу ещё на 2 секунды
    await asyncio.sleep(2)

    # Изменяем текст сообщения, ID которого мы сохранили
    await bot.edit_message_text(text='<b>Отправляю сообщение!!!</b>', chat_id=message.from_user.id, message_id=msg_id)

