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
    restate_require = database.ubicoin * (2 ** (next_level))
    lead_grace = database.ubicoin * (2 ** (next_level))
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
    for user in await database.get_all_users():
        user_id = user.user_id
        await good_morning(user_id)


async def good_morning(user_id):
    user = await database.get_user(user_id)
    restate = user.restate
    grow = user.grow_wallet
    add_restate_amount = restate * 0.0006
    add_grow_amount = grow * 0.0005
    await add_grow(user_id, add_grow_amount)
    await add_restate(user_id, add_restate_amount)
    await add_turnover(user_id, add_grow_amount+add_restate_amount)
    text = f'\n+ {add_grow_amount + add_restate_amount} рублей\n\nGood morning, {user.user_name}!\n\nВсе в уровнях получают деньги каждый день\nМожно определить сумму комфортную для себя\nИ дойти до своего уровня дохода\n\n'
    await bot.send_message(user_id, text)


async def up_me(user_id):
    # with database.Session() as session:
        user = await database.get_user(user_id)




        current_leader_id = user.current_leader_id
        current_leader = await database.get_user(current_leader_id)
        restate_require = database.ubicoin * (2 ** (user.level+1))
        lead_grace = database.ubicoin * (2 ** (user.level+1)) 
        if (restate_require-user.restate) > 0:
          database.gamma[user_id] = lead_grace-(user.grow_wallet + user.liquid_wallet-(restate_require-user.restate)) 
        else:  
            database.gamma[user_id] = lead_grace-(user.grow_wallet + user.liquid_wallet)
        if database.gamma[user_id] > 0:
            await bot.send_message(user_id,  f'Недостаточно средств: {database.gamma[user_id]} рублей')
        else:

            balance = current_leader.restate + current_leader.grow_wallet + current_leader.liquid_wallet+lead_grace
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
                    
            balance = current_leader.restate + current_leader.grow_wallet + current_leader.liquid_wallet
            text0 = "\n💳 Баланс: " + ( '%.2f' %(balance)) + " рублей" 

            await bot.send_message(user_id, f'Уровень повышен 🔼: {user.level+1}\n')
            await bot.send_message(current_leader_id, f'Входящий: +{lead_grace} рублей'+ text0 +f'\n\nВаш реферал {user.user_name}: {(user.level)} 🔼 {user.level+1}\
                                \n\n*напоминание: Ваши рефералы могут достичь вашего уровня. Тогда они не смогут взять следующий уровень у вас. И они уйдут к другому Лиду')



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

        text4 = "\nЗдесь пока ничего нет. Куда всё делось? 🤔 \n\nБонусы разыгрываются каждый день! \nМы отправим уведомление, когда придет бонус.\
                \n\nРекомендуем включить всплывающие уведомления в настройках бота🔔 Чтобы не пропустить.\n\n Нажимайте поделиться\n получайте бонус за каждого нового подписчика! 🎁"
          
        if user.bonuses_available >= 1:
            user.bonuses_available-= 1
            bonus_size = float(random.randint(0, 333))
            bonus_size = bonus_size / 100

            bonus_size = bonus_size ** 3
            bonus_size = bonus_size + 10.074 + (random.randint(0, 300))/100
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
                await bot.send_photo(user_id, photo=config.photo_ids_test['travolta'], caption=text4) 
            except:
                await bot.send_message(user_id,'Здесь могло быть наше фото 😄\n' + text4)
            


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


        text1 = "\n\n🏡 Restate(25%):  " + '%.2f' %(user.restate) + ' рублей'
        text2 =   "\n🌱 Grow(20%):      " + '%.2f' %(user.grow_wallet) + ' рублей'
        text3 =   "\n💧 Liquid(0%):       " + '%.2f' %(user.liquid_wallet) + ' рублей'

        sum = user.restate + user.grow_wallet + user.liquid_wallet
        text0 = "💳 Баланс:            " + ( '%.2f' %(sum)) + " рублей"
        balance_text = text0 + text1 + text2 + text3 + texts.accounts_about_text
        return balance_text
        
      
# TABS вкладки
#  Вкладки МЕНЮ
async def main_menu(user_id):

     await bot.send_message(user_id, "🟢 Кнопки внизу 🔢 ⬇️", reply_markup=kb.menu_buttons_reply_markup)

    #  await bot.send_message(user_id, " Все  вкладки  главного  меню  ", reply_markup=kb.menu_markup)

async def profile_tub(user_id):
    user_info_text = "🪪 Профиль\n\n" + await database.user_info( user_id)
    await bot.send_message(user_id, user_info_text, disable_web_page_preview=True, reply_markup=kb.profile_markup)

async def level_tub(user_id):
    user = await database.get_user(user_id)
    level = user.level
    leader_id = user.current_leader_id
    try:
        current_leader = await database.get_user(leader_id)
        leader_name = current_leader.user_name
        leader_level=current_leader.level
        await bot.send_message(user_id, f"\nВаш уровень: {level}"+f'\n\nВаш Лид сейчас:\n{leader_name}\nLevel: {leader_level}', reply_markup=kb.level_markup)
    except:
        await bot.send_message(user_id, f"\nВаш уровень: {level}", reply_markup=kb.level_markup)

async def balance_tub(user_id):
    balance_text = await get_balance(user_id)

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
        

    await bot.send_message(user_id, texts.resurses_text, reply_markup=kb.resources_markup)


async def info_tub(user_id):
    await bot.send_message(user_id, "🔎 Инфо"+ texts.info_text, reply_markup=kb.info_markup)

async def switch_tubs(code , user_id):
    if code == "menu":
        await utils.main_menu(user_id)
    elif code == "profile":
        await utils.profile_tub(user_id)
    elif code == "resources":
        await utils.resources_tub(user_id)
    elif code == "level":
        await utils.level_tub(user_id)
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

    try:
        await bot.send_photo(user_id, photo=config.photo_ids_test['choose_your_level'],caption=texts.start_guide1_text)
    except:
        await bot.send_message(user_id, texts.start_guide1_text)

    await asyncio.sleep(1)
   
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.guide_stage  = 1
        if user.bonuses_gotten  == 0:
           await utils.add_bonus(user_id)
        elif user.bonuses_gotten  >= 1:
           await bot.send_message(user_id, 'Хм...\nКажется, вы уже получили первый бонус')
        session.commit()
    await bot.send_message(user_id,"Начнем с небольшого бонуса", reply_markup=kb.bonus_button)

# Открывам бонус 1. Про бонусы. Для второго бонуса - подписка на канал
async def start_guide2(user_id):
    await asyncio.sleep(1)
    await bot.send_message(user_id, "Сначала бонусы могут содежать\nот 10 до 50 рублей.\n\nДальше - больше 🔼")
    await asyncio.sleep(1)
    await bot.send_message(user_id, "Можно получить следующий бонус за 2 простых действия:")
    await asyncio.sleep(1)
    await bot.send_message(user_id, "1. Подписка на канал", reply_markup=kb.subscribe_buttons)
    # database.get_user(user_id).guide_stage = 2

    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.guide_stage  = 2
        session.commit()


# Поделиться своей реферальной ссылкой в ТГ.
async def start_guide3(user_id):  
        with database.Session() as session:
            user = session.query(User).filter(User.user_id == user_id).first() 
            user_channel_status = await bot.get_chat_member(chat_id='-1001973511610', user_id=user_id)
            if user_channel_status != 'left':

                # if user_channel_status.status == "creator" or user_channel_status.status == "member" or user_channel_status.status == 'ChatMemberMember':
                if user_channel_status.status in ['creator', 'member', 'ChatMemberMember']:

                    # database.get_user(user_id).guide_stage  = 3
                    user.guide_stage  = 3
                    if user.bonuses_gotten  == 1:
                        await utils.add_bonus(user_id)
                    elif user.bonuses_gotten  >= 2:
                        await bot.send_message(user_id, 'Хм...\nКажется, вы уже получили 2 бонуса')
                    session.commit()
                    await bot.send_message(user_id, 'Спасибо за подписку')
                    await bot.send_message(user_id, '2. Поделиться СВОЕЙ реферальной ссылкой в ТГ.')
                    await asyncio.sleep(2)
                    referral_link = user.referral_link 

                    try:
                        await bot.send_photo(user_id, photo=config.photo_ids_test['bonus_open'],\
                                caption= texts.start_guide3_text_1 +f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n ♻️ 🔁 ❗️РЕПОСТ ТУТ❗️  ➡️  ➡️  ➡️")
                    except:
                        await bot.send_message(user_id, 'Здесь могло быть наше фото 😄\n' + texts.start_guide3_text_1 +f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n ♻️ 🔁 ❗️РЕПОСТ ТУТ❗️  ➡️  ➡️  ➡️")

                    await asyncio.sleep(2)
                    await bot.send_message(user_id, texts.start_guide3_text_2, reply_markup=kb.check_done_button)
                else:
                    await bot.send_message(user_id, 'Нет подписки. Можно продолжить без подписки и потерять следующий бонус 😱', reply_markup=kb.subscribe_buttons2)



# Без подписки на канал нет бонус
async def start_guide3_nosub(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()  
        user.guide_stage  = 3
        if user.bonuses_gotten == 1:
                        user.bonuses_gotten = 2
        session.commit()
    await bot.send_message(user_id, '☹️')
    await bot.send_message(user_id, '2. Поделиться своей реферальной ссылкой в ТГ.')
    await asyncio.sleep(2)
    referral_link = user.referral_link 

    try:
        await bot.send_photo(user_id, photo=config.photo_ids_test['bonus_open'],\
                caption= texts.start_guide3_text_1 + f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n❗️ ♻️ 🔁 РЕПОСТ тут ➡️ ➡️ ➡️")
    except:
        await bot.send_message(user_id, 'Здесь могло быть наше фото 😄\n' + texts.start_guide3_text_1 + f"{referral_link}" + "\n🎁 ⬆️ Бонус здесь ⬆️ 🎁\n\n\n❗️ ♻️ 🔁 РЕПОСТ тут ➡️ ➡️ ➡️")

    await asyncio.sleep(2)



async def start_guide3_1(user_id):
    await bot.send_message(user_id, 'OK')
    await asyncio.sleep(1)
    await bot.send_message(user_id, 'А вот и бонус!', reply_markup=kb.bonus_button)


async def start_guide4(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.guide_stage  = 4
        session.commit()
    await asyncio.sleep(1)
    await bot.send_message(user_id, texts.start_guide4_text, disable_web_page_preview=True)
    await asyncio.sleep(2)
    await bot.send_message(user_id, texts.start_guide4_text_2, reply_markup=kb.menu_button_markup)
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        session.commit()



