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
    balance = user.restate + user.grow_wallet
    if (restate_require-user.restate) > 0:
        database.gamma[user_id] = lead_grace-(user.grow_wallet -(restate_require-user.restate)) 
    else:  
         database.gamma[user_id] = lead_grace-(user.grow_wallet)

    if database.gamma[user_id] > 0:
        database.gamma[user_id] = database.gamma[user_id]/100
        xxx = database.gamma[user_id]
        database.gamma[user_id] = math.ceil(xxx)
        database.gamma[user_id] = database.gamma[user_id]*100

        await bot.send_message(user_id, f'Следующий уровень: {next_level}\n\nСтек требуется: {restate_require} руб\nЦена: {lead_grace} руб\
                               \n\nБаланс: '+ '%.2f' %(balance) + " руб"+ f'\n\nПополните баланс на {database.gamma[user_id]} руб', reply_markup=kb.show_requisites_markup)
    else:
        await bot.send_message(user_id, f'Следующий уровень: {next_level}\n\nСтек требуется: {restate_require} руб\nЦена: {lead_grace} руб\
                               \n\nБаланс: '+ '%.2f' %(balance) + " руб", reply_markup=kb.up_me)



async def good_morning_all():
    database.basecoin = database.basecoin * (1 + 0.0005)
    user_count = 1
    for user in await database.get_all_users():
        user_id = user.user_id
        try:
            await good_morning(user_id)
            await bot.send_message(config.levels_guide_id, f'GM user {user_count} ')
        except:
            await bot.send_message(config.levels_guide_id, f'GM user {user_count} error')
        user_count += 1
    


async def good_morning(user_id):
    user = await database.get_user(user_id)
    restate = user.restate
    grow = user.grow_wallet
    add_restate_amount = restate * 0.00062
    add_grow_amount = grow * 0.0005
    sum = add_grow_amount+add_restate_amount
    balance_text = await get_balance(user_id)
    await add_grow(user_id, sum)
    # await add_restate(user_id, add_restate_amount)
    await add_turnover(user_id, sum)
    text = f'\n+ {sum} руб'+balance_text+f'\n\nДоброе утро, {user.user_name} 😄\n\nГарантированный ежедневный доход\nКакая сумма будет комфортна?'
    await bot.send_message(user_id, text)


async def admin_show_all_users():
    user_count = 0
    users_text = ''
    for user in await database.get_all_users():
        user_count += 1
        user_id_text = str(user.user_id)
        user_name_text = user.user_name

        users_text += '\n<a href="tg://openmessage?user_id='+user_id_text+'">'+user_name_text+'</a>'#<a href="tg://user?id=123456789">inline mention of a user</a>'   tg://openmessage?user_id=
        # user_info_text = f"User {user_count}: " + await database.user_info( user.user_id)
    await bot.send_message(config.levels_guide_id, f'users: {user_count}' + users_text, disable_web_page_preview=True)

async def admin_show_all_users_level():
    user_count = 1
    for user in await database.get_all_users():
        try:
            if user.level != 0:
                user_info_text = f"User {user_count}: " + await database.user_info( user.user_id)
                await bot.send_message(config.levels_guide_id, user_info_text, disable_web_page_preview=True)
                user_count += 1
        except:
            await bot.send_message(config.levels_guide_id, f'GM user {user_count} error')

async def delete_inactive_users():
    for user in await database.get_all_users():
        if user.turnover == 0:
            await database.delete_user(user.user_id)
            await database.delete_all_refs(user.user_id)
        else: pass
        
                

async def up_me(user_id):
        user = await database.get_user(user_id)
        referrer_id = user.referrer_id
        current_leader = await database.get_user(referrer_id)
        restate_require =(250 * database.basecoin) * (2 ** (user.level+1))
        lead_grace = (250 * database.basecoin) * (2 ** (user.level+1)) 
        if (restate_require-user.restate) > 0:
          database.gamma[user_id] = lead_grace-(user.grow_wallet -(restate_require-user.restate)) 
        else:  
            database.gamma[user_id] = lead_grace-(user.grow_wallet )
        if database.gamma[user_id] > 0:
            await bot.send_message(user_id,  f'Недостаточно средств: {database.gamma[user_id]} руб')
        else:
            balance = current_leader.restate + current_leader.grow_wallet +lead_grace
            balance_text = f'\n\nБаланс: '+ '%.0f' %(balance) +  'руб'
            if restate_require > user.restate:
                await add_grow(user_id, -restate_require+user.restate)
                await add_restate(user_id, restate_require-user.restate)
            await add_grow(user_id, -lead_grace)
            await add_turnover(user_id, lead_grace)               
            await add_level(user_id)
            await add_sales(referrer_id)
            await add_grow(referrer_id, lead_grace)
            await add_turnover(referrer_id, lead_grace)
            await bot.send_message(user_id, f'Поздравляем! Уровень повышен 🔼\n\nВаш уровень: {user.level+1}\n\nСсылки: {database.level_links[user.level]}')
            await bot.send_message(current_leader.user_id, f'Продажа: +{lead_grace} руб'+ balance_text +f'\n\nВаш реферал {user.user_name}: {(user.level)} 🔼 {user.level+1}\
                                \n\n*напоминание: рефералы, достигшие уровня Лида, могут уйти к другому Лиду. Для того, чтобы взять следующий уровень')



# dp.chat_join_request.register(approve_chat_join_request, F.chat.id == level_2_channel)
async def approve_chat_join_request(chat_join: ChatJoinRequest):
    chat_id = chat_join.chat.id
    chat_name = chat_join.chat.full_name
    user = await database.get_user(chat_join.from_user.id)
    user_name = chat_join.from_user.full_name
    if chat_id in database.level_channels:
        if user.level >= database.level_channels.index(chat_id):
            await bot.send_message(chat_join.from_user.id, f'{user_name}, добро пожаловать в канал {chat_name}')
            await chat_join.approve()
        else: await bot.send_message(chat_join.from_user.id, f'Недостаточный уровнень для доступа в канал {chat_name}')



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
            balance_sum = user.restate+user.grow_wallet

            text1 = '\n🔼 Получено бонусов:     ' + f"{bonuses_gotten}"
            text2 = f"\n🎁 Бонус:         " + '%.2f' %(bonus_size) + " руб" 
            text3 = "\n💳 Баланс:      " + ( '%.2f' %(balance_sum)) + " руб"
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

async def add_turnover(user_id, amount):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.turnover += amount
        session.commit()


async def add_level(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.level += 1
        text = f'\n{user.user_name} теперь на уровне: {user.level}'
        if user.current_leader_id != user.referrer_id :
            await bot.send_message(user.current_leader_id, f'У пользователя{user.user_name} сменился Лид'+ text)
            user.current_leader_id = user.referrer_id
        await bot.send_message(user.current_leader_id, f'Ваш партнер повысил уровень {user.user_name}'+ text) #link to userpage

        for user in await database.get_all_referrals(user_id):
            try:
                # referrals_text += (f"\nreferral {user_count}: " + f'{user.user_name},'+ f' lvl: {user.level}' + f' {user.referral_link}')
                await bot.send_message(user.user_id, text) #link to userpage
            except: pass
        session.commit()

async def add_sales(user_id):
    with database.Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        user.sales += 1
        session.commit()


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

    elif user.guide_stage  == 4:
            # user.guide_stage = 5
            await utils.main_menu(user_id)


async def get_balance(user_id):
    # if await database.get_user(user_id) == False:
    #      await bot.send_message(user_id, "Пользователь не найден. Перезагрузите бота")
    # else:     
        user = await database.get_user(user_id)
        sum = user.restate + user.grow_wallet
        balance_text = "\n💳 Баланс:       " + ( '%.2f' %(sum)) + " руб"
        return balance_text
        
      
# TABS вкладки
#  Вкладки МЕНЮ
async def main_menu(user_id):
     await bot.send_message(user_id, "🟢", reply_markup=kb.menu_buttons_reply_markup) 
     if user_id == config.levels_guide_id:
         await bot.send_message(user_id, "🔴 admin panel", reply_markup=kb.admin_panel_buttons_reply_markup)

# async def admin_panel():
#      await bot.send_message(config.levels_guide_id, "🟢 Кнопки внизу ⬇️", reply_markup=kb.admin_panel_buttons_reply_markup) #

    #  await bot.send_message(user_id, " Все  вкладки  главного  меню  ", reply_markup=kb.menu_markup)

async def profile_tub(user_id):
    user_info_text = await database.user_info( user_id)
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
        await bot.send_message(user_id, f"\nВаш уровень: {level}"+f'\n\nЧто на следующем уровне?: ' + text_next_level, reply_markup=kb.level_markup)
    except:
        await bot.send_message(user_id, f"\nВаш уровень: {level}", reply_markup=kb.level_markup)

async def settings_tub(user_id):
     await bot.send_message(user_id, f"\nНастройки")

async def balance_tub(user_id):
    user = await database.get_user(user_id)
    text1 =   "\n💎Стек:    " + '%.2f' %(user.restate)
    text2 =   "\n💳Счёт:    " + '%.2f' %(user.grow_wallet)
    sum = user.restate + user.grow_wallet
    restate_income = user.restate * 0.00062
    grow_wallet_income = user.grow_wallet * 0.0005
    text0 =   "Баланс:    " + ( '%.2f' %(sum)) + " руб"
    text3 = f"\n\nДоход в день руб:\n💎(25%): {restate_income}\n💳(20%): {grow_wallet_income}"
    balance_text = text0 + text1 + text2 + text3


    try:
        await bot.send_photo(user_id, photo=config.photo_ids_test['restate_grow_liquid'], caption=f'{balance_text}', reply_markup=kb.balance_control_markup)
    except:
        await bot.send_message(user_id, f'{balance_text}', reply_markup=kb.balance_control_markup)

async def partners_tub(user_id):
    # user = await database.get_user(user_id)
    referrals_text = "Рефералы:\n"
    user_count = 0
    for user in await database.get_all_referrals(user_id):
        try:
            referrals_text += (f"\n{user_count}: " + f'{user.user_name},'+ f' lvl: {user.level}' + f' {user.referral_link}')
            user_count += 1
        except:
            pass
    user_count = 0
    referrals_text += "\n\nРефереры:\n"
    for user in await database.get_all_referrers(user_id):        
        try:
             referrals_text += (f"\nreferrer {user_count}: " + f'{user.user_name},'+ f' lvl: {user.level}' + f' {user.referral_link}')
             user_count += 1
        except:
            pass
    await bot.send_message(user_id, referrals_text, disable_web_page_preview=True, reply_markup=kb.partners_markup)
      
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

async def learn_tub(user_id):
    learn_text = texts.learn_text_0
    user = await database.get_user(user_id)
    if user.level > 0:
        learn_text += '\n' + texts.learn_text_1
    await bot.send_message(user_id, learn_text, parse_mode="MarkdownV2", reply_markup=kb.learn_markup)

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
    elif code == "learn":
        await utils.learn_tub(user_id)
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
async def start_guide2(user_id):
    bonus_bottom_text = '%.2f' %(10*database.basecoin)
    bonus_top_text = '%.2f' %(50*database.basecoin)
    await bot.send_message(user_id, f'\nСейчас бонусы от {bonus_bottom_text} до {bonus_top_text} руб.'+texts.start_guide2_text, reply_markup=kb.subscribe_buttons)

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



