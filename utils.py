import random
import asyncio
import math 
import config

import database
import utils
import texts
import kb
from misc import bot
from database import User


from aiogram.types import ChatJoinRequest


# BONUS
async def add_bonus(user_id):
    try:
        with database.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            user.bonuses_gotten += 1
            user.bonuses_available += 1
            session.commit()
    except:
         await bot.send_message(user_id, 'Пользователь не найден.\nПожалуйста, войдите по реферальной ссылке')

         
async def up_level(user_id):
    user = await database.get_user(user_id)  
    next_level = (user.level)+1
    restate_require =  math.ceil(250 * database.basecoin) * (2 ** (next_level))
    lead_grace =  math.ceil(250 * database.basecoin) * (2 ** (next_level))
    balance = user.restate + user.grow_wallet + user.liquid_wallet
    # delta = (lead_grace + restate_require) - balance
    # database.gamma[user_id] = lead_grace - (user.grow_wallet+user.liquid_wallet)
    if (restate_require-user.restate) > 0:
        database.gamma[user_id] = lead_grace-(user.grow_wallet + user.liquid_wallet-(restate_require-user.restate)) 
    else:  
         database.gamma[user_id] = lead_grace-(user.grow_wallet + user.liquid_wallet)

    if database.gamma[user_id] > 0:
        database.gamma[user_id] = database.gamma[user_id]/100
        xxx = database.gamma[user_id]
        # await bot.send_message(user_id, f'xxx:{xxx} math.ceil: {math.ceil(xxx)}')
        database.gamma[user_id] = math.ceil(xxx)
        # await bot.send_message(user_id, f'math.ceil: {database.gamma[user_id]}')
        database.gamma[user_id] = database.gamma[user_id]*100

        await bot.send_message(user_id, f'Следующий уровень: {next_level}\n\nRestate: {restate_require} руб\nСпасибо Лиду: {lead_grace} руб\
                               \n\nБаланс: '+ '%.2f' %(balance) + " руб"+ f'\n\nПополните баланс на {database.gamma[user_id]} руб', reply_markup=kb.add_grow)
    else:
        await bot.send_message(user_id, f'Следующий уровень: {next_level}\n\nRestate: {restate_require} руб\nСпасибо Лиду: {lead_grace} руб\
                               \n\nБаланс: '+ '%.2f' %(balance) + " руб", reply_markup=kb.up_me)



async def good_morning_all():
    database.basecoin = database.basecoin * (1 + 0.0005)
    user_count = 0
    for user in await database.get_all_users():
        user_id = user.user_id
        await good_morning(user_id)
        user_count += 1
    await bot.send_message(config.levels_guide_id, f'Всего {user_count} пользователей')


async def good_morning(user_id):
    user = await database.get_user(user_id)
    restate = user.restate
    grow = user.grow_wallet
    add_restate_amount = restate * 0.0006
    add_grow_amount = grow * 0.0005
    await add_grow(user_id, add_grow_amount)
    await add_restate(user_id, add_restate_amount)
    await add_turnover(user_id, add_grow_amount+add_restate_amount)
    text = f'\n+ {add_grow_amount + add_restate_amount} рублей\n\nдоброе утро, {user.user_name} 😄\n\nВ Уровнях мы получаем деньги каждый день\n\nКакая сумма будет комфортна?'
    await bot.send_message(user_id, text)


async def admin_show_all_users():
    user_count = 0
    for user in await database.get_all_users():
        user_count += 1
        user_id = user.user_id
        user_info_text = f"User {user_count}: " + await database.user_info( user_id)
        await bot.send_message(config.levels_guide_id, user_info_text, disable_web_page_preview=True)
            
    
async def up_me(user_id):
        user = await database.get_user(user_id)
        current_leader_id = user.current_leader_id
        current_leader = await database.get_user(current_leader_id)
        restate_require =(250 * database.basecoin) * (2 ** (user.level+1))
        lead_grace = (250 * database.basecoin) * (2 ** (user.level+1)) 
        if (restate_require-user.restate) > 0:
          database.gamma[user_id] = lead_grace-(user.grow_wallet + user.liquid_wallet-(restate_require-user.restate)) 
        else:  
            database.gamma[user_id] = lead_grace-(user.grow_wallet + user.liquid_wallet)
        if database.gamma[user_id] > 0:
            await bot.send_message(user_id,  f'Недостаточно средств: {database.gamma[user_id]} рублей')
        else:
            balance = current_leader.restate + current_leader.grow_wallet + current_leader.liquid_wallet+lead_grace
            balance_text = f'\n\nБаланс: '+ '%.0f' %(balance) +  'рублей'
            if restate_require > user.restate:
                # user.grow_wallet-=(restate_require-user.restate)
                await add_grow(user_id, -restate_require+user.restate)
                # user.restate=restate_require
                await add_restate(user_id, restate_require-user.restate)
            # user.grow_wallet-=lead_grace 
            await add_grow(user_id, -lead_grace)
            # user.turnover+=lead_grace
            await add_turnover(user_id, lead_grace)               
            # user.level += 1
            await add_level(user_id)
            await add_sales(current_leader_id)
            # current_leader.grow_wallet+=lead_grace
            await add_grow(current_leader_id, lead_grace)
            # current_leader.turnover+=lead_grace
            await add_turnover(current_leader_id, lead_grace)
            await if_grow_wallet_is_negative(user_id)
                    
            # balance = current_leader.restate + current_leader.grow_wallet + current_leader.liquid_wallet
            # text0 = await get_balance(current_leader_id)

            await bot.send_message(user_id, f'Поздравляем! Уровень повышен 🔼\n\nВаш уровень: {user.level+1}\n\nСсылки: {database.level_links[user.level]}')
            await bot.send_message(current_leader_id, f'Продажа: +{lead_grace} рублей'+ balance_text +f'\n\nВаш реферал {user.user_name}: {(user.level)} 🔼 {user.level+1}\
                                \n\n*напоминание: рефералы, достигшие уровня Лида, могут уйти к другому Лиду. Для того, чтобы взять следующий уровень')



# dp.chat_join_request.register(approve_chat_join_request, F.chat.id == level_2_channel)
async def approve_chat_join_request(chat_join: ChatJoinRequest):
    chat_id = chat_join.chat.id
    chat_name = chat_join.chat.full_name
    user = await database.get_user(chat_join.from_user.id)
    user_name = chat_join.from_user.full_name
    if chat_id == database.level_1_channel:
        if user.level >= 1:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_2_channel:
        if user.level >= 2:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_3_channel:
        if user.level >= 3:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_4_channel:
        if user.level >= 4:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_5_channel:
        if user.level >= 5:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_6_channel:
        if user.level >= 6:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_7_channel:
        if user.level >= 7:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_8_channel:
        if user.level >= 8:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_9_channel:
        if user.level >= 9: 
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_10_channel:
        if user.level >= 10:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_11_channel:
        if user.level >= 11:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_12_channel:
        if user.level >= 12:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_13_channel:
        if user.level >= 13:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_14_channel:
        if user.level >= 14:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_15_channel:
        if user.level >= 15:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_16_channel:
        if user.level >= 16:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_17_channel:
        if user.level >= 17:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_18_channel:
        if user.level >= 18:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_19_channel:
        if user.level >= 19:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')
    if chat_id == database.level_20_channel:
        if user.level >= 20:
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_id}')


async def get_bonuses_available(user_id):
    user = await database.get_user(user_id)
    # bonuses_available = user.bonuses_available
    return user.bonuses_available

async def get_bonuses_gotten(user_id):
    user = await database.get_user(user_id) 
    return user.bonuses_gotten


async def open_bonus(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()


        if user.bonuses_available >= 1:
            user.bonuses_available-= 1
            bonus_size = float(random.randint(0, 333))
            bonus_size = bonus_size / 100

            bonus_size = bonus_size ** 3
            bonus_size = bonus_size + 10.074 + (random.randint(0, 300))/100
            bonus_size = bonus_size * database.basecoin * (1 + (user.level)/10)
            await add_restate(user_id, bonus_size)
            await add_turnover(user_id, bonus_size)

            session.commit()
            bonuses_gotten = user.bonuses_gotten
            balance_sum = user.restate+user.grow_wallet+user.liquid_wallet

            text1 = '\n🔼 Получено бонусов:     ' + f"{bonuses_gotten}"
            text2 = f"\n🎁 Бонус:         " + '%.2f' %(bonus_size) + " рублей" 
            text3 = "\n💳 Баланс:      " + ( '%.2f' %(balance_sum)) + " рублей"
            try:
                await bot.send_photo(user_id, photo=config.photo_ids_test['bonus_open'], caption=text1 + text2 + text3)
            except:
                await bot.send_message(user_id,'Здесь могло быть наше фото 😄\n' + text1 + text2 + text3)
        else:
            try:
                await bot.send_photo(user_id, photo=config.photo_ids_test['travolta'], caption=texts.bonuses_none)
            except:
                await bot.send_message(user_id,'Здесь могло быть наше фото 😄\n' + texts.bonuses_none)
            


async def add_restate(user_id, amount):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.restate += amount
        session.commit()

async def add_grow(user_id, amount):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.grow_wallet += amount
        session.commit()

async def add_liquid(user_id, amount):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.liquid_wallet += amount
        session.commit()

async def add_turnover(user_id, amount):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.turnover += amount
        session.commit()


async def add_level(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.level += 1
        session.commit()

async def add_sales(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.sales += 1
        session.commit()

async def if_grow_wallet_is_negative(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user.grow_wallet < 0:
            # user.liquid_wallet+=user.grow_wallet
            await add_liquid(user_id, user.grow_wallet)
            # user.grow_wallet=0
            await add_grow(user_id, -user.grow_wallet)


# START Guide Stages
async def start_guide_stages(user_id):
    user = await database.get_user(user_id)

    if user.guide_stage  == 0:
        await utils.start_guide1(user_id)

    elif user.guide_stage  == 1:
        await utils.start_guide2(user_id)

    elif user.guide_stage == 2:
        await utils.start_guide3(user_id)

    elif user.guide_stage  == 3:
        await utils.start_guide4(user_id)

    elif user.guide_stage  >= 4:
            await utils.main_menu(user_id)


async def get_balance(user_id):
    # if await database.get_user(user_id) == False:
    #      await bot.send_message(user_id, "Пользователь не найден. Перезагрузите бота")
    # else:     
        user = await database.get_user(user_id)
        sum = user.restate + user.grow_wallet + user.liquid_wallet
        balance_text = "\n💳 Баланс:            " + ( '%.2f' %(sum)) + " рублей"
        return balance_text
        
      
# TABS вкладки
#  Вкладки МЕНЮ
async def main_menu(user_id):
     await bot.send_message(user_id, "🟢 Кнопки внизу ⬇️", reply_markup=kb.menu_buttons_reply_markup) #

# async def admin_panel():
#      await bot.send_message(config.levels_guide_id, "🟢 Кнопки внизу ⬇️", reply_markup=kb.admin_panel_buttons_reply_markup) #

    #  await bot.send_message(user_id, " Все  вкладки  главного  меню  ", reply_markup=kb.menu_markup)

async def profile_tub(user_id):
    user_info_text = "Профиль\n\n" + await database.user_info( user_id)
    await bot.send_message(user_id, user_info_text, disable_web_page_preview=True)

async def level_tub(user_id):
    user = await database.get_user(user_id)
    level = user.level
    leader_id = user.current_leader_id
    try:
        if level == 0:
            text_next_level = 'https://t.me/Levels_info/38'
        else:
            text_next_level = f'\n\n x2'
        current_leader = await database.get_user(leader_id)
        leader_name = current_leader.user_name
        leader_level=current_leader.level
        await bot.send_message(user_id, f"\nВаш уровень: {level}"+f'\n\nВаш Лид сейчас:\n{leader_name}\nУровень {leader_level}\n\nЧто на следующем уровне?: ' + text_next_level, reply_markup=kb.level_markup)
    except:
        await bot.send_message(user_id, f"\nВаш уровень: {level}", reply_markup=kb.level_markup)

async def settings_tub(user_id):
     await bot.send_message(user_id, f"\nНастройки")

async def balance_tub(user_id):
    user = await database.get_user(user_id)


    text1 = "\n\n🏡 Restate(25%):  " + '%.2f' %(user.restate) + ' рублей'
    text2 =   "\n🌱 Grow(20%):      " + '%.2f' %(user.grow_wallet) + ' рублей'
    text3 =   "\n💧 Liquid(0%):       " + '%.2f' %(user.liquid_wallet) + ' рублей'

    sum = user.restate + user.grow_wallet + user.liquid_wallet
    text0 = "💳 Баланс:            " + ( '%.2f' %(sum)) + " рублей"
    balance_text = text0 + text1 + text2 + text3 + texts.accounts_about_text


    try:
        await bot.send_photo(user_id, photo=config.photo_ids_test['restate_grow_liquid'], caption=f'{balance_text}', reply_markup=kb.balance_control_markup)
    except:
        await bot.send_message(user_id, f'{balance_text}', reply_markup=kb.balance_control_markup)

async def partners_tub(user_id):
    user = await database.get_user(user_id)
    referrals = user.referrals 
    leader_id = user.current_leader_id
    try:
        current_leader = await database.get_user(leader_id)
        leader_name = current_leader.user_name
        leader_level=current_leader.level
        await bot.send_message(user_id, "💎 Партнеры" +f'\n\nВаш Лид сейчас:\n{leader_name}\nLevel: {leader_level} ' 
        + "\n\nНаставники доступны: " + f"\n\nВаши рефералы: {referrals}", reply_markup=kb.partners_markup)
    except:
        await bot.send_message(user_id, "💎 Партнеры" +f'\n\nВаш Лид не найден' 
            + f"\n\n\nВаши рефералы: {referrals}", reply_markup=kb.partners_markup)
        
async def resources_tub(user_id):
    await bot.send_message(user_id, texts.resurses_text)


async def bonuses_tub(user_id):
    try:
        user = await database.get_user(user_id) 
        bonuses_available = user.bonuses_available
        bonuses_gotten = user.bonuses_gotten
        referral_link = user.referral_link 
        text2 = f"\n\nВаша личная реф ссылка:\n{referral_link}"
        await bot.send_message(user_id, texts.bonuses_tub_text1 + text2 + texts.bonuses_tub_text2 + f"{bonuses_gotten}"\
                                + "\nДоступно бонусов: " + f"{bonuses_available}", reply_markup=kb.bonuses_markup)
    except:
        await bot.send_message(user_id, "Пользователь не найден. Перезагрузите бота")

async def info_tub(user_id):
    await bot.send_message(user_id, "🔎 Инфо"+ texts.info_text, reply_markup=kb.info_markup)

async def switch_tubs(code , user_id):
    if code == "profile":
        await utils.profile_tub(user_id)
    elif code == "resources":
        await utils.resources_tub(user_id)
    elif code == "level":
        await utils.level_tub(user_id)
    elif code == "settings":
        await utils.settings_tub(user_id)
    elif code == "balance":
        await utils.balance_tub(user_id)
    elif code == "partners":
        await utils.partners_tub(user_id)
    elif code == "bonuses":
        await utils.bonuses_tub(user_id)
    elif code == "info":
        await utils.info_tub(user_id)
# Guide
# Про Уровни. Даем первый бонус. Открывайте.
async def start_guide1(user_id):

    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.guide_stage  = 1
        if user.bonuses_gotten  == 0:
           await utils.add_bonus(user_id)
        # elif user.bonuses_gotten  >= 1:
        #    await bot.send_message(user_id, 'Хм...\nКажется, вы уже получили первый бонус')
        session.commit()

    user = await database.get_user(user_id)
    user_name = user.user_name
    try:
        await bot.send_photo(user_id, photo=config.photo_ids_test['nivelisha_hello'],  caption= f'Привет, {user_name} !' +texts.start_guide1_text, reply_markup=kb.bonus_button)
    except:
        await bot.send_message(user_id, f'Привет, {user_name} 😊' + texts.start_guide1_text, reply_markup=kb.bonus_button)
    # await bot.send_message(user_id,"Начнем с небольшого бонуса", reply_markup=kb.bonus_button)

# Открывам бонус 1. Про бонусы. Для второго бонуса - подписка на канал
async def start_guide2(user_id, query):
    bonus_bottom_text = '%.2f' %(10*database.basecoin)
    bonus_top_text = '%.2f' %(50*database.basecoin)
    await bot.send_message(user_id, f'\nСейчас бонусы от {bonus_bottom_text} до {bonus_top_text} рублей.'+texts.start_guide2_text, reply_markup=kb.subscribe_buttons)
    # file = await bot.get_file(config.photo_ids_test['bonus_open'])
    # await query.message.edit_media(file, reply_markup=reply_markup)
    # message = await query.message.edit_text(texts.start_guide2_text, reply_markup=kb.subscribe_buttons)
    # await bot.edit_message_media(media=config.photo_ids_test['bonus_open'] ,chat_id=user_id, message_id=query. texts.start_guide2_text, reply_markup=kb.subscribe_buttons)

    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.guide_stage  = 2
        session.commit()


# Поделиться своей реферальной ссылкой в ТГ.
async def start_guide3(user_id):  
        with database.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first() 
            user.guide_stage  = 3
            if user.bonuses_gotten  == 1:
                await utils.add_bonus(user_id)
            elif user.bonuses_gotten  >= 2:
                await bot.send_message(user_id, 'Хм...\nКажется, вы уже получили 2 бонуса')
            session.commit()
            await bot.send_message(user_id, '❗️2. Поделиться СВОЕЙ реферальной ссылкой в ТГ ⬇️')
            referral_link = user.referral_link 
            # try:
            await bot.send_photo(user_id, photo=config.photo_ids_test['bonus_open'],caption= texts.start_guide3_text_1 +f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n🔁 ❗️РЕПОСТ ТУТ❗️ ➡️ ➡️ ➡️ ➡️", reply_markup=kb.check_done_button)
            # except:
            # await bot.send_message(user_id, 'Здесь могло быть наше фото 😄\n' + texts.start_guide3_text_1 +f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n🔁 ❗️РЕПОСТ ТУТ❗️ ➡️ ➡️ ➡️ ➡️", reply_markup=kb.check_done_button)
            # await bot.send_message(user_id, texts.start_guide3_text_2, reply_markup=kb.check_done_button)



# Без подписки на канал нет бонус
# async def start_guide3_nosub(user_id):
#     with database.Session() as session:
#         user = session.query(User).filter(User.user_id == user_id).first()  
#         user.guide_stage  = 3
#         if user.bonuses_gotten == 1:
#                         user.bonuses_gotten = 2
#         session.commit()
#     await bot.send_message(user_id, '☹️')
#     await bot.send_message(user_id, '❗️2. Поделиться своей реферальной ссылкой в ТГ ⬇️')

#     referral_link = user.referral_link 

#     # try:
#     #     await bot.send_photo(user_id, photo=config.photo_ids_test['bonus_open'],\
#     #             caption= texts.start_guide3_text_1 + f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n🔁 ❗️РЕПОСТ ТУТ❗️ ➡️ ➡️ ➡️ ➡️")
#     # except:
#         await bot.send_message(user_id, 'Здесь могло быть наше фото 😄\n' + texts.start_guide3_text_1 + f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n🔁 ❗️РЕПОСТ ТУТ❗️ ➡️ ➡️ ➡️ ➡️")


# async def start_guide3_1(user_id):
#     await bot.send_message(user_id, 'А вот и бонус!', reply_markup=kb.bonus_button)


async def start_guide4(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.guide_stage  = 4
        session.commit()

    # await bot.send_message(user_id, texts.start_guide4_text, disable_web_page_preview=True, reply_markup=kb.check_done_button)
    await bot.send_photo(user_id, photo=config.photo_ids_test['money_fountain'], caption=texts.start_guide4_text, reply_markup=kb.check_done_button)


    # await bot.send_message(user_id, 'Проверьте баланс ⬇️')
    # with database.Session() as session:
    #     user = session.query(User).filter(User.user_id == user_id).first()
    #     session.commit()



