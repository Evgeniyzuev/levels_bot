import kb
import texts
import utils
import config
import database #import SessionLocal, User
from database import User

from misc import dp, bot


from aiogram import types, F, Router, flags
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject, StateFilter
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
# from sqlalchemy.sql import func
# from aiogram.methods.get_chat import GetChat
# from aiogram.types import (
#     KeyboardButton,
#     Message,
#     ReplyKeyboardMarkup,
#     ReplyKeyboardRemove,
# )

#     Справочник https://t.me/aiogram/28
#     await callback_query.answer("Как много?",reply_markup=ReplyKeyboardRemove(),)  Всплывающее сообщение и удаление клавиатуры
#      await message.answer("Операция отменена",)  answer высплывает сообщение


# класс состояний
class Form(StatesGroup):
    amount_state = State()
    amount_state_ok = State()
    wait_check = State()
    grow_wallet_up = State()
    restate_up = State()
    # wallet_stack_confirm = State()
    # restate_down = State()
    admin_send_ckeck_state = State()
    user_send_ckeck_state = State()
    requisites_entering_state = State()
    grow_wallet_down = State()
    transfer_to_id = State()
    transfer_sum = State()
    process_transfer_approvement = State()



# START
# @dp.message(Command("start"))
@dp.message(CommandStart(deep_link=True))
async def start_handler( callback_query: types.CallbackQuery, command: CommandObject): #message: Message,
    user_name = callback_query.from_user.full_name
    user_id = callback_query.from_user.id
    user_link = callback_query.from_user.username
    try:
        args = command.args
        referrer_id = decode_payload(args)
        # await bot.send_message(user_id, f'referrer_id: {referrer_id}')
    except:
        await bot.send_message(user_id, text='❗️ Не валидная реферальная ссылка ❗️')
        referrer_id = None
    user = await database.get_or_create_user(user_id, user_name, user_link, referrer_id)
    # await callback_query.answer(f'ваш реферер: {referrer_id}')
    await utils.start_guide_stages(user_id)


@dp.message(Command("start"))
async def start_handler( callback_query: types.CallbackQuery): #message: Message,
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    await bot.send_message(user_id, f"{user_name}, привет!")
    user = await database.get_user(user_id)
    if user:
        await utils.start_guide_stages(user_id)
    else:
        await bot.send_message(user_id, "Используйте реферальную ссылку для регистрации")

@dp.message(Command("equality"))
async def start_handler( callback_query: types.CallbackQuery): #message: Message,
    user_id = callback_query.from_user.id
    if user_id == config.levels_guide_id:
        await bot.send_message(config.levels_guide_id, "🔴 admin panel", reply_markup=kb.admin_panel_buttons_reply_markup) 
        

@dp.callback_query(F.data == "all_users_button")
async def all_users_button(callback_query: types.CallbackQuery):
    await utils.admin_show_all_users()

@dp.callback_query(F.data == "all_users_level_button")
async def all_users_level_button(callback_query: types.CallbackQuery):
    await utils.admin_show_all_users_level()

@dp.callback_query(F.data == "delete_inactive_users_button")
async def delete_inactive_users_button(callback_query: types.CallbackQuery):
    await utils.delete_inactive_users()

@dp.callback_query(F.data == "good_morning_button")
async def good_morning_button(callback_query: types.CallbackQuery):
    await utils.good_morning(config.levels_guide_id)

@dp.callback_query(F.data == "reset_guide_button")
async def reset_guide_button(callback_query: types.CallbackQuery):
    user_id = config.levels_guide_id
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.guide_stage  = 0
        user.bonuses_gotten  = 0
        user.restate  = 0
        user.grow_wallet  = 0
        user.turnover  = 0
        user.sales  = 0
        session.commit()
    await bot.send_message(user_id, "Guide reseted")

@dp.callback_query(F.data == "alter_table_user_button")
async def alter_table_user_button(callback_query: types.CallbackQuery):
    await database.alter_table_user()
    await bot.send_message(config.levels_guide_id, "alter table user")
# @dp.callback_query(F.data == "drop_table_referrals_button")
# async def drop_table_referrals_button(callback_query: types.CallbackQuery):
#     await database.drop_table_referrals()
#     await bot.send_message(config.levels_guide_id, "Table referrals dropped")


# # добавление пользователя в канал
dp.chat_join_request.register(utils.approve_chat_join_request)
 

# Нажатие кнопки открыть бонус
@dp.callback_query(F.data == "open_bonus")
async def process_open_bonus_button(callback_query: types.CallbackQuery): #message: Message, 
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    # chat_id =  await bot.get_chat()
    user = await database.get_user(user_id)
    bonuses_gotten = user.bonuses_gotten
    bonuses_available = user.bonuses_available
    if user.guide_stage == 1:
        await callback_query.message.delete()
    if user.guide_stage == 3:
        await callback_query.message.delete()

        
    if bonuses_available > 0:
        if bonuses_gotten-bonuses_available == 1:
            try:
                current_leader_id = user.current_leader_id
                await bot.send_message(current_leader_id, text= f"Ваш реферал: {user_name}(ID: {user_id}) открыл второй бонус.", reply_markup=kb.get_and_open_bonus_button)
            except:
                await bot.send_message(user_id, text="не получилось")   
    await utils.open_bonus(user_id)
    if user.guide_stage == 1:
        await utils.start_guide2(user_id)  
    elif user.guide_stage == 3:
        await utils.start_guide4(user_id)



# Нажатие кнопки получать бонус за реферала
@dp.callback_query(F.data == "get_and_open_bonus")
async def process_get_and_open_bonus(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.edit_message_reply_markup(user_id, message_id=callback_query.message.message_id, reply_markup=None )
    await utils.add_bonus(user_id)
    await bot.send_message(user_id, text="+🎁 Бонус получен!\nОткройте его на вкладке Бонусы")


@dp.callback_query(F.data == "up_level")
async def process_up_level(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = await database.get_user(user_id)
    try:
        referrer = await database.get_user(user.referrer_id)
        ref_lvl = referrer.level
    except:
        referrer = None
        ref_lvl = 0
        await bot.send_message(user_id, 'Не найден реферал')
    # try:
    #     current_leader = await database.get_user(user.current_leader_id)
    # except:
    #     current_leader = None
    if ref_lvl > user.level:
            await utils.up_level(user_id)
    else:
        try:
            current_leader = await database.get_user(user.current_leader_id)
            await bot.send_message(user_id, text=f'У реферера нет следующего уровня\nВаш Лид: {current_leader.user_name}\nуровень: {current_leader.level}\n{current_leader.referral_link}')
        except:
            await bot.send_message(user_id, text=f'No current leader')
             

@dp.callback_query(F.data == "up_me") 
async def process_up_me(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await utils.up_me(user_id)


# Выдаёт реквизиты №1 для пополнения grow_wallet
@dp.callback_query(F.data == 'show_requisites')
async def process_add_grow(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.send_message(user_id, f'Перевести на grow_wallet:\n + {database.gamma[user_id]} рублей'+ texts.requisites_text_1, reply_markup=kb.add_balance_ready)

@dp.callback_query(F.data == 'show_requisites2')
async def process_add_grow(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    sum = database.gamma[user_id] / database.ton_rub
    sum = (round(sum, 4))
    caption_text = f'Перевести на grow_wallet:\n + {sum} Toncoin'+ texts.requisites_text_2
    await bot.send_photo(user_id, photo=config.photo_ids_test['requisites_Toncoin'], caption=caption_text, reply_markup=kb.add_balance_ready)
    # await bot.send_message(user_id, f'Перевести на grow_wallet:\n + {database.gamma[user_id]} рублей'+ texts.requisites_text_2, reply_markup=kb.add_balance_ready)

@dp.callback_query(F.data == 'show_requisites3')
async def process_add_grow(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    sum = database.gamma[user_id] / database.usdt_rub
    sum = (round(sum, 2))
    caption_text = f'Перевести на grow_wallet:\n + {sum} USDT TON'+ texts.requisites_text_3
    await bot.send_photo(user_id, photo=config.photo_ids_test['requisites_USDT'], caption=caption_text, reply_markup=kb.add_balance_ready)
    # await bot.send_message(user_id, f'Перевести на grow_wallet:\n + {database.gamma[user_id]} рублей'+ texts.requisites_text_3, reply_markup=kb.add_balance_ready)

# Передаёт запрос на пополнение админу
@dp.callback_query(F.data == "add_balance_ready")
async def process_add_balance_ready(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    database.payment_to_check_user_id = user_id
    await bot.edit_message_reply_markup(user_id, message_id=callback_query.message.message_id, reply_markup=None )
    # await utils.add_balance_ready(user_id)
    # database.payment_to_check=database.gamma[user_id]
    await bot.send_message(config.levels_guide_id, text= f":Запрашивают подтверждение пополнения баланса. USER (amount;ID)  Пришла?")
    await bot.send_message(config.levels_guide_id, text= f"{database.gamma[user_id]};{user_id}", reply_markup=kb.admin_confirm_payment)
    await state.set_state(Form.user_send_ckeck_state)
    await bot.send_message(user_id, f'Платеж: {database.gamma[user_id]} рублей - ожидает подтверждения\n\nОтправьте боту чек 📎↘️')


@dp.message(StateFilter(Form.user_send_ckeck_state))
async def process_user_send_ckeck_state(message: Message, state: FSMContext) -> None:
    await message.send_copy(config.levels_guide_id)
    await state.set_state(None)
    await bot.send_message(message.from_user.id, f'Платеж в процессе 💤')


# # Изменить сумму платежа вручную
@dp.callback_query(F.data == "admin_change_amount_payment")
async def process_confirm_payment_button(callback_query: types.CallbackQuery, state: FSMContext) -> None: #message: Message, callback_query: types.CallbackQuery, 
    text = callback_query.message.text
    splitted = str(text).split(';')
    user_id = splitted[1]
    user_id = int(user_id)
    database.payment_to_check_user_id = user_id
    await state.set_state(Form.amount_state)
    # await bot.edit_message_reply_markup(config.levels_guide_id, message_id=callback_query.message.message_id, reply_markup=None )
    # await bot.send_message(config.levels_guide_id, "введите сумму", reply_markup=kb.changed_amount_payment_confirm )
    await callback_query.answer("Как много?",reply_markup=ReplyKeyboardRemove(),)

# пополняет по кнопке  ("Деньги вижу")
@dp.callback_query(F.data == "admin_confirm_payment")
async def process_confirm_payment_button(callback_query: types.CallbackQuery): #message: Message, callback_query: types.CallbackQuery, 
    text = callback_query.message.text

    splitted = str(text).split(';')
    user_id = splitted[1]
    amount = splitted[0]
    user_id = int(user_id)
    amount = int(amount)

    await utils.add_grow(user_id, amount)
    await bot.edit_message_reply_markup(config.levels_guide_id, message_id=callback_query.message.message_id, reply_markup=None )
    await bot.send_message(user_id, f'Пополнение Счета:\n + {amount} рублей' )
    await bot.send_message(config.levels_guide_id, f'User: {user_id} \nПополнение grow_wallet:\n + {amount} рублей' )

# Подтвердить введенную сумму?
@dp.message(StateFilter(Form.amount_state))
async def process_amount(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.amount_state_ok)
    await state.update_data(amount=message.text)
    database.payment_to_check_amount = int(message.text)
    await message.answer(f'Пополнить Счет:\n + {message.text} рублей\n\nUser ID: {database.payment_to_check_user_id}',reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Yes"),KeyboardButton(text="No"),]],resize_keyboard=True,),)


# Подтвердить введенную сумму - да
@dp.message(Form.amount_state_ok, F.text.casefold() == "yes")
async def process_amount_state_ok(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    user_id = database.payment_to_check_user_id
    amount = database.payment_to_check_amount
    await utils.add_grow(user_id, amount)
    await bot.send_message(user_id, f'Пополнение grow_wallet:\n + {amount} рублей' )
    await bot.send_message(config.levels_guide_id, f'User: {user_id} \nПополнение grow_wallet:\n + {amount} рублей' )
    await utils.main_menu(config.levels_guide_id)
    # await message.answer("Готово",reply_markup=ReplyKeyboardRemove())


# Отменить введенную сумму (нет)
@dp.message(Form.amount_state_ok, F.text.casefold() == "no")
async def process_amount_state_ok(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.amount_state)
    await callback_query.answer("Как много?",) # reply_markup=ReplyKeyboardRemove(),



#движения по счетам  --------------------------------> кнопки
# @dp.callback_query(F.data == "grow_wallet_down")
# async def process_grow_wallet_down(callback_query: types.CallbackQuery, state: FSMContext) -> None:
#     user_id = callback_query.from_user.id
#     user = await database.get_user(user_id)
#     await state.set_state(Form.grow_wallet_down)
#     # await utils.up_liquid(user_id)
#     await bot.send_message(user_id, f'\nGrow -> Liquid\nКомиссия за срочность 1%\nДоступно Grow: {user.grow_wallet} \nВведите сумму:')

# @dp.message(StateFilter(Form.grow_wallet_down))
# async def process_amount(message: Message, state: FSMContext) -> None:
#     user_id = message.from_user.id
#     user = await database.get_user(user_id)
#     await state.update_data(amount=message.text)
#     try:
#         amount = int(message.text)
#         if amount < 0: amount = -1*amount
#         if user.grow_wallet < int(amount):
#             await message.answer(f'Недостаточно средств')
#         else:
#             await utils.add_grow(user_id, (-1)*int(amount))
#             await utils.add_liquid(user_id, (0.99)*int(amount))
#             await message.answer(f'\nGrow -> Liquid:\n{amount} рублей')
#     except:
#         await message.answer('Введите целое число')
#     await state.set_state(None)


@dp.callback_query(F.data == "grow_wallet_down")
async def process_grow_wallet_down(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    user = await database.get_user(user_id)
    await state.set_state(Form.grow_wallet_down)
    # await utils.up_liquid(user_id)
    await bot.send_message(user_id, f'💳Счёт: {user.grow_wallet}\nВывод от 100 руб\nНапишите сумму:')

@dp.message(StateFilter(Form.grow_wallet_down))
async def process_amount(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = await database.get_user(user_id)
    await state.update_data(amount=message.text)
    try:
        amount = int(message.text)
        if amount < 0: amount = -1*amount
        if user.grow_wallet < amount:
            await message.answer(f'Недостаточно средств')
            await state.set_state(None)
        elif amount < 100:
            await message.answer(f'Вывод от 100 рублей без комиссии')
            await state.set_state(None)
        else:
            database.payout[user_id] = amount
            await state.set_state(Form.requisites_entering_state)
            await bot.send_message(user_id, f'\nВывод на TON кошелек +лучший курс\nУкажите номер телефона и адрес кошелька в сети ❗️TON❗️\
                           \n❗️Внимание❗️\nИспользование адреса в другой сети приведет к потере средств❗️\n\nПеревод по СБП без комиссии\nУкажите номер телефона и банк')
    except:
        await message.answer('Введите целое число')
        await state.set_state(None)
    

@dp.message(StateFilter(Form.requisites_entering_state))
async def process_requisites_entering_state(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.update_data(requisites=message.text)
    try:
        requisites = (message.text)
        await bot.send_message(config.levels_guide_id, text= f"Реквизиты: {requisites}")
        await bot.send_message(config.levels_guide_id, text= f"Отправить перевод USER (amount;ID)")
        await bot.send_message(config.levels_guide_id, text= f"{database.payout[user_id]};{user_id}", reply_markup=kb.admin_payout)
        await bot.send_message(user_id, f'Перевод: {database.payout[user_id]} рублей в процессе')
    except:
        await message.answer('Введите валидные реквизиты')
    await state.set_state(None)

@dp.callback_query(F.data == "admin_payout")
async def process_confirm_payment_button(callback_query: types.CallbackQuery, state: FSMContext) -> None: #message: Message, callback_query: types.CallbackQuery, 
    text = callback_query.message.text
    splitted = str(text).split(';')
    user_id = splitted[1]
    amount = splitted[0]
    user_id = int(user_id)
    database.payment_to_check_user_id = user_id
    amount = int(amount)
    await utils.add_grow(user_id,(-1)*amount)
    await bot.send_message(config.levels_guide_id, text= f"прикрепляем чек USER (amount;ID)")
    await bot.edit_message_reply_markup(config.levels_guide_id, message_id=callback_query.message.message_id, reply_markup=None )
    await bot.send_message(user_id, f'Перевод исполнен:\n {amount} рублей' )
    await state.set_state(Form.admin_send_ckeck_state)

@dp.message(StateFilter(Form.admin_send_ckeck_state))
async def process_admin_send_ckeck_state(message: Message, state: FSMContext) -> None:
    await message.send_copy(database.payment_to_check_user_id)
    await state.set_state(None)


@dp.callback_query(F.data == "grow_wallet_up")
async def process_wallet_up(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    user = await database.get_user(user_id)
    await state.set_state(Form.grow_wallet_up)
    await bot.send_message(user_id, f'💳Счёт: {user.grow_wallet} \nПополнение от 100 руб\nНапишите сумму:')

@dp.message(StateFilter(Form.grow_wallet_up))
async def process_amount(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.update_data(amount=message.text)
    try:
        amount = int(message.text)
        if amount < 0: amount = -1*amount
        await state.set_state(None)
    except:
        await message.answer('Введите целое число')
    database.gamma[user_id] = amount
    await message.answer(f'Пополнить grow_wallet:\n + {amount} рублей', reply_markup=kb.show_requisites_markup)

@dp.callback_query(F.data == "transfer")
async def process_transfer(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    user = await database.get_user(user_id)
    await state.set_state(Form.transfer_to_id)
    await bot.send_message(user_id, f'💳Счёт: {user.grow_wallet} \nПеревод пользователю\nНапишите id пользователя:')

@dp.message(StateFilter(Form.transfer_to_id))
async def process_amount(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.update_data(user_to_id=message.text)
    try:
        user_to_id = int(message.text)
        transfer_user = await database.get_user(user_to_id)
        await bot.send_message(user_id, f'Перевод пользователю: {transfer_user.user_name}\nНапишите сумму:')
        await state.set_state(Form.transfer_sum)
    except:
        await message.answer('Пользователь не найден')
        await state.set_state(None)
    transfer = database.Transfer()
    transfer.user_to_id = user_to_id
    database.transfers[user_id] = transfer
    
@dp.message(StateFilter(Form.transfer_sum))
async def process_amount(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    
    await state.update_data(amount=message.text)
    try:
        amount = float(message.text)
    except:
        await message.answer('Некорректная сумма')
        await state.set_state(None)
    if amount < 0: amount = -1*amount
    user = await database.get_user(user_id)
    if amount > user.grow_wallet:
        await message.answer(f'Недостаточно средств')
        await state.set_state(None)
    else:
        transfer = database.transfers[user_id]
        transfer.amount = amount
        database.transfers[user_id] = transfer
        user_recipient = await database.get_user(transfer.user_to_id)
        # reply_markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Перевести", callback_data="transfer_approve"))#.add(InlineKeyboardButton(text="Отменить", callback_data="transfer_cancel"))
        transfer_approvement_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Перевести", callback_data="transfer_approve")],[InlineKeyboardButton(text="Отменить", callback_data="transfer_cancel")]], resize_keyboard=True)
        await bot.send_message(user_id, f'Перевод пользователю: {user_recipient.user_name}\nСумма: {amount} рублей', reply_markup=transfer_approvement_markup)
        await state.set_state(Form.process_transfer_approvement)

@dp.callback_query(StateFilter(Form.process_transfer_approvement))
async def process_transfer_approve(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    if callback_query.data == "transfer_cancel":
        user_id = callback_query.from_user.id
        database.transfers[user_id] = None
        await bot.send_message(user_id, f'Отменено')
        await state.set_state(None)

    if callback_query.data == "transfer_approve":
        user_id = callback_query.from_user.id
        user = await database.get_user(user_id)
        transfer = database.transfers[user_id]
        user_recipient = await database.get_user(transfer.user_to_id)
        
        if transfer.amount <= user.grow_wallet:
            await utils.add_grow(user_id, -transfer.amount)
            await utils.add_grow(transfer.user_to_id, transfer.amount)
            balance_text = await utils.get_balance(user_id)
            balance_recipient_text = await utils.get_balance(transfer.user_to_id)
            await bot.send_message(user_id, f'Переведено: {user_recipient.user_name}\nСумма: {transfer.amount} рублей' + balance_text)
            await bot.send_message(transfer.user_to_id, f'Перевод от: {user.user_name}\nID: {user.user_id}\nСумма: {transfer.amount} рублей' + balance_recipient_text)
        else:
            await bot.send_message(user_id, f'Недостаточно средств')
        database.transfers[user_id] = None
        await state.set_state(None)


# Markdown:
# [User link](tg://user?id=111111)

# HTML:
# <a href="tg://user?id=111111">User link</a>

@dp.callback_query(F.data == "referrals")
async def process_referrals(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    referrals_text = "Рефералы:"
    user_count = 1
    user_id = callback_query.from_user.id
    for user in await database.get_all_referrals(user_id):
        try:
            # chat_link = f'<a href="tg://user?id={user.user_id}">{user.user_name}</a>'
            ref_link = f'<a href="{user.referral_link}"> Reflink</a>'
            chat_link = f'{user.user_name}.'
            if user.user_link: chat_link = f'<a href="t.me/{user.user_link}">{user.user_name}</a>.'
            chat_link += '<a href="tg://openmessage?user_id='+ f'{user.user_id}' +'">'+ ' 🤖' +'</a>.'
            chat_link += '<a href="https://t.me/@id'+ f'{user.user_id}' +'">'+ ' 🍏' +'</a>.'
                # chat_link += f' <a href="t.me/{user.user_link}"> @</a>.'
            # username_link = f't.me/{user.user_link}'
            referrals_text += (f"\n{user_count}:"+ ' '  + f' Lvl {user.level}.' + chat_link + ref_link)
            user_count += 1
        except:
            pass
    await bot.send_message(user_id, referrals_text, disable_web_page_preview=True)

@dp.callback_query(F.data == "other_partners")
async def process_other_partners(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_count = 1
    other_partners_text = "Партнеры:"
    user_id = callback_query.from_user.id
    for user in await database.get_all_referrers(user_id):        
        try:
            ref_link = f'<a href="{user.referral_link}"> Reflink</a>'
            chat_link = f'{user.user_name}.'
            if user.user_link: chat_link = f'<a href="t.me/{user.user_link}">{user.user_name}</a>.'
            chat_link += '<a href="tg://openmessage?user_id='+ f'{user.user_id}' +'">'+ ' @' +'</a>.'
            other_partners_text += (f"\n{user_count}:"+ ' '    + f' Lvl {user.level}.' + chat_link + ref_link)
            user_count += 1
        except:
            pass
    await bot.send_message(user_id, other_partners_text, disable_web_page_preview=True)

@dp.callback_query(F.data == "restate_up")
async def process_grow_to_restate(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    user = await database.get_user(user_id)
    await state.set_state(Form.restate_up)
    await bot.send_message(user_id, f'\n💳Счёт -> ✨Стек\n\nДоступно: ' + '%.2f' %(user.grow_wallet) + ' рублей\nВведите сумму:') 

@dp.message(StateFilter(Form.restate_up))
async def process_amount(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = await database.get_user(user_id)
    try:
        await state.update_data(amount=message.text)
        database.payment_to_check_amount = int(message.text)
        amount = int(message.text)
        if amount < 0: amount = -1*amount
        if amount > user.grow_wallet:
            await message.answer(f'Недостаточно средств')
        else:
            await message.answer(f'Пополненить ✨Стек:\n + {message.text} рублей\n\n❗️Внимание!\nДля продажи ✨Стека в дальнейшем потребуется подтверждение личности', 
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Да", callback_data="wallet_stack_confirm"),InlineKeyboardButton(text="Нет", callback_data="wallet_stack_cancel")]], resize_keyboard=True,))
    except:
        await message.answer('Введите целое число')
    await state.set_state(None)
    
# Подтвердить введенную сумму - да
@dp.callback_query(F.data == "wallet_stack_confirm")
async def process_wallet_stack_confirm(message: Message, state: FSMContext) -> None:

    user_id = message.from_user.id
    user = await database.get_user(user_id)
    amount = database.payment_to_check_amount
    if amount <= user.grow_wallet and amount > 0:
        await utils.add_grow(user_id, int(-1*amount))
        await utils.add_restate(user_id, int(amount))
        await bot.send_message(user_id, f'💳Счёт пополнен:\n + {amount} рублей' )
    else:
        await bot.send_message(user_id, f'Недостаточно средств')
    database.payment_to_check_amount = 0
    # await message.answer("Готово",reply_markup=ReplyKeyboardRemove())


# Отменить введенную сумму (нет)
@dp.callback_query(F.data == "wallet_stack_cancel")
async def process_wallet_stack_cancel(message: Message, state: FSMContext) -> None:
    database.payment_to_check_amount = 0
    user_id = message.from_user.id
    await bot.send_message(user_id, f'Операция отменена')



    
@dp.callback_query(F.data == "restate_down")
async def process_restate_to_grow(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    user = await database.get_user(user_id)
    if user.level < 1:
        await bot.send_message(user_id, 'Продажа ✨Стека недоступна на уровне 0')
    else:
        # await state.set_state(Form.restate_down)
        restate_require =(250 * database.basecoin) * (2 ** (user.level))
        await bot.send_message(user_id, f'✨Стек -> 💳Счёт\nДоступно:'+ '%.2f' % (user.restate) + ' рублей\n\n❗️Внимание!\nДля продажи ✨Стека в требуется подтверждение личности')

# @dp.message(StateFilter(Form.restate_down))
# async def process_amount(message: Message, state: FSMContext) -> None:
#     user_id = message.from_user.id
#     user = await database.get_user(user_id)
#     await state.update_data(amount=message.text)
#     restate_require =(250 * database.basecoin) * (2 ** (user.level))
#     text = f'Требование уровня по недвижимости: {restate_require} рублей\nНедвижимость ниже требования \
#                             приведет к заморозке уровня и дохода\nЗаморозка доступна с уровня 5\nДоступно к продаже: {user.restate - restate_require} рублей\n'
#     try:
#         amount = int(message.text)
#         if amount < 0: amount = -1*amount
#         if (user.restate - restate_require) < int(message.text):
#             await message.answer(text)
#         else:
#             await utils.add_restate(user_id, (-1)*int(amount))
#             await utils.add_grow(user_id, (0.9)*int(amount))
#             await message.answer(f'Вывод из restate:\n + {amount} рублей')
#     except:
#         await message.answer('Введите целое число')
        
#     await state.set_state(None)

    
@dp.message(F.photo)
async def photo_handler(message: Message):
    photo_data = message.photo[-1]
    await bot.send_message(message.from_user.id, f'photo_data: {photo_data}')



@dp.callback_query(F.data == "check_subscribe_button")
async def check_subs(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        user_channel_status = await bot.get_chat_member(chat_id=config.levels_channel_id, user_id=user_id)
        if user_channel_status != 'left' and user_channel_status.status in ['creator', 'member', 'ChatMemberMember']:
               await callback_query.message.delete()
               await utils.start_guide3(user_id)   
        else: await callback_query.answer("Вы не подписаны на канал")
    
# @dp.callback_query(F.data == "no_subscribtion")
# async def check_subs(callback_query: types.CallbackQuery):
#     user_id = callback_query.from_user.id
#     user = await database.get_user(user_id)
#     if user.guide_stage == 2:
#         await utils.start_guide3_nosub(user_id) 

@dp.callback_query(F.data == "check_done_button")
async def check_done(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = await database.get_user(user_id)
    if user.guide_stage == 3:
        await bot.send_message(user_id, 'А вот и бонус!', reply_markup=kb.bonus_button)
    if user.guide_stage == 4:
        # message_id = callback_query.message.message_id
        # await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=texts.start_guide4_text_2)
        # await bot.send_message(user_id, texts.start_guide4_text_2)
        file = types.InputMediaPhoto(media=config.photo_ids_test['choose_your_level'], caption=texts.start_guide4_text_2)
        await callback_query.message.edit_media(file)
        await utils.main_menu(user_id)
        



# @dp.callback_query_handler(text="update_photo")
# async def photo_update(query: types.CallbackQuery):
#     # file_path = "files/foods/pelmeni.png"
#     reply_markup = InlineKeyboardMarkup().add(
#         InlineKeyboardButton(text="Updated button", callback_data="dont_click_me")
#     )
#     file = types.InputMediaPhoto(media=types.InputFile(config.photo_ids_test['bonus_open']), caption="Updated caption :)")

#     await query.message.edit_media(file, reply_markup=reply_markup)

# @dp.message(F.data == "next")
# async def next(callback_query: types.CallbackQuery):
#     await bot.send_message(user_id, "works")
#     user_id = callback_query.from_user.id
#     message_id = callback_query.message.message_id
#     await callback_query.message.delete()
#     # await bot.edit_message_text(user_id, message_id, texts.start_guide4_text_2)
#     await bot.send_message(user_id, texts.start_guide4_text_2)
#     await utils.main_menu(user_id)


# SWITCH TABS

switch_tabs_data =      ["profile"   , "resources"   , "level", "settings" , "balance"  , "partners"  , "bonuses"   , "income"     ] 
switch_tabs_text=      ["Профиль"   , "Ресурсы"     , "Уровень"  , "Настрой"  , "Баланс"     , "Партнеры"    , "Бонусы"    , "Доходы"     ]
switch_tabs_emoji_text=["😃\nПрофиль", "🔗\nРесурсы", "🔼\nУровень", "⚙️\nНастрой", "💳\nБаланс", "🤝\nПартнеры", "🎁\nБонусы", "❓\nДоходы"]
switch_tabs_commands = ["/profile"  , "/resources"    , "/level"     , "/settings"   , "/balance"   , "/partners"   , "/bonuses"    , "/income"    ]

@dp.callback_query(F.data)
async def swith_menu_tubs(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data in switch_tabs_data:
        await utils.switch_tubs(data, user_id=callback_query.from_user.id)

@dp.message(F.text == '/menu') 
async def main_menu(msg: Message):
    await utils.main_menu(user_id=msg.from_user.id)

@dp.message(F.data == "menu")
async def main_menu(callback_query: types.CallbackQuery):
    await utils.main_menu(user_id=callback_query.from_user.id)



       
@dp.message(F.text)  
async def swith_menu_tubs(msg: Message):
    if msg.text in switch_tabs_emoji_text:
        index = switch_tabs_emoji_text.index(msg.text)
        data = switch_tabs_data[index]
        await utils.switch_tubs(data, user_id=msg.from_user.id)
    elif msg.text in switch_tabs_text:
        index = switch_tabs_text.index(msg.text)
        data = switch_tabs_data[index]
        await utils.switch_tubs(data, user_id=msg.from_user.id)
    elif msg.text in switch_tabs_commands:
        index = switch_tabs_commands.index(msg.text)
        data = switch_tabs_data[index]
        await utils.switch_tubs(data, user_id=msg.from_user.id)
    # await bot.answer_callback_query(callback_query.id)
        

# push please
