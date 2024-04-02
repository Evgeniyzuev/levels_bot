from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
# menu_buttons = [
#     [InlineKeyboardButton(text="📝\nПрофиль", callback_data="profile"),InlineKeyboardButton(text="🔗\nРесурсы", callback_data="resources")],[InlineKeyboardButton(text="🔼\nУровень", callback_data="level"),
#     InlineKeyboardButton(text="💳\nБаланс", callback_data="balance")],[InlineKeyboardButton(text="💎\nПартнёры", callback_data="partners"), InlineKeyboardButton(text="🎁\nБонусы", callback_data="bonuses")],
#     [InlineKeyboardButton(text="🔎\nИнфо", callback_data="info")]]

menu_button = [InlineKeyboardButton(text="🟢 Menu", callback_data="menu", one_time_keyboard = True)]

profile_button = [InlineKeyboardButton(text="🪪 Профиль", callback_data="profile", one_time_keyboard = True)]
bonus_button = [InlineKeyboardButton(text="🎁 Открыть Бонус", callback_data="open_bonus", one_time_keyboard = True)]
up_level = [InlineKeyboardButton(text="🔼 Поднять уровень", callback_data="up_level", one_time_keyboard = True)]
up_me = [InlineKeyboardButton(text="🔼 Поднять сейчас", callback_data="up_me", one_time_keyboard = True)]
# up_me = [InlineKeyboardButton(text="🔼 Поднять сейчас", callback_data="up_me", one_time_keyboard = True)]
add_grow = [InlineKeyboardButton(text="🔼 Пополнить баланс", callback_data="add_grow", one_time_keyboard = True)]
add_balance_ready = [InlineKeyboardButton(text="Перевод отправлен", callback_data="add_balance_ready", one_time_keyboard = True)]
get_and_open_bonus_button = [InlineKeyboardButton(text="🎁 Получить Бонус", callback_data="get_and_open_bonus", one_time_keyboard = True)]
check_done_button = [[InlineKeyboardButton(text="Готово!", callback_data="check_done_button", one_time_keyboard = True)]]
subscribe_buttons = [[InlineKeyboardButton(text="Подписаться", url='https://t.me/Levels_up')],[InlineKeyboardButton(text="Готово!", callback_data="check_subscribe_button", one_time_keyboard = True)]]
subscribe_buttons2 = [[InlineKeyboardButton(text="Подписаться", url='https://t.me/Levels_up')],[InlineKeyboardButton(text="Готово!", callback_data="check_subscribe_button", one_time_keyboard = True)],[InlineKeyboardButton(text="Продолжить без бонуса 🚫", callback_data="no_subscribtion", one_time_keyboard = True)]]
share_button = [[InlineKeyboardButton(text="🔗 Поделиться", callback_data="share_button", one_time_keyboard = True)]]
# transfer_button = [[InlineKeyboardButton(text=" Перевод", callback_data="transfer", one_time_keyboard = True)]]
# pay_button = [[InlineKeyboardButton(text=" Оплата", callback_data="pay", one_time_keyboard = True)]]

grow_to_liquid = InlineKeyboardButton(text="🌱🔻💧", callback_data="grow_to_liquid", one_time_keyboard = True)
liquid_wallet_down = InlineKeyboardButton(text="💧🔻🔻", callback_data="liquid_wallet_down", one_time_keyboard = True)
grow_wallet_up = InlineKeyboardButton(text="🔼🔼🌱", callback_data="grow_wallet_up", one_time_keyboard = True)
liquid_to_grow = InlineKeyboardButton(text="💧🔼🌱", callback_data="liquid_to_grow", one_time_keyboard = True)
restate_up = InlineKeyboardButton(text="🌱🔼🏡", callback_data="restate_up", one_time_keyboard = True)
restate_down = InlineKeyboardButton(text="🏡🔻🌱", callback_data="restate_down", one_time_keyboard = True)
admin_confirm_payment = InlineKeyboardButton(text="Деньги вижу", callback_data="admin_confirm_payment", one_time_keyboard = True)
admin_payout = InlineKeyboardButton(text="Перевод", callback_data="admin_payout", one_time_keyboard = True)
check_user_payment = InlineKeyboardButton(text="Проверить платеж", callback_data="check_user_payment", one_time_keyboard = True)
admin_change_amount_payment = InlineKeyboardButton(text="Изменить сумму платежа", callback_data="admin_change_amount_payment", one_time_keyboard = True)
changed_amount_payment_confirm = InlineKeyboardButton(text="Подтвердить сумму платежа", callback_data="changed_amount_payment_confirm", one_time_keyboard = True)




profile_buttons = [menu_button]
resources_buttons = [menu_button]
level_buttons = [up_level]
balance_buttons = [menu_button]
partners_buttons = [menu_button] 
info_buttons = [menu_button]
bonus_buttons = [bonus_button, profile_button,]

balance_control_buttons = [[restate_up, grow_wallet_up, liquid_to_grow], [restate_down, grow_to_liquid, liquid_wallet_down]]
# balance_control_buttons2 = [restate_down, liquid_to_grow, liquid_wallet_down]



# menu_markup = InlineKeyboardMarkup(inline_keyboard=menu_buttons, one_time_keyboard = True, resize_keyboard=True)
menu_button_markup = InlineKeyboardMarkup(inline_keyboard=[menu_button], one_time_keyboard = True)
profile_markup = InlineKeyboardMarkup(inline_keyboard=profile_buttons, one_time_keyboard = True)
resources_markup = InlineKeyboardMarkup(inline_keyboard=resources_buttons, one_time_keyboard = True)
level_markup = InlineKeyboardMarkup(inline_keyboard=level_buttons, one_time_keyboard = True)
balance_markup = InlineKeyboardMarkup(inline_keyboard=balance_buttons, one_time_keyboard = True)
partners_markup = InlineKeyboardMarkup(inline_keyboard=partners_buttons, one_time_keyboard = True)
bonuses_markup = InlineKeyboardMarkup(inline_keyboard=bonus_buttons, one_time_keyboard = True)
info_markup = InlineKeyboardMarkup(inline_keyboard=info_buttons, one_time_keyboard = True)
balance_control_markup = InlineKeyboardMarkup(inline_keyboard=balance_control_buttons, one_time_keyboard = True) # one_time_keyboard = True, 
# balance_control_markup = InlineKeyboardMarkup(inline_keyboard=balance_control_buttons, one_time_keyboard = True) 

# single button markups
bonus_button = InlineKeyboardMarkup(inline_keyboard=[bonus_button], one_time_keyboard = True)
get_and_open_bonus_button = InlineKeyboardMarkup(inline_keyboard=[get_and_open_bonus_button], one_time_keyboard = True)
check_done_button = InlineKeyboardMarkup(inline_keyboard=check_done_button, one_time_keyboard = True)
subscribe_buttons = InlineKeyboardMarkup(inline_keyboard=subscribe_buttons, one_time_keyboard = True)

admin_confirm_payment = InlineKeyboardMarkup(inline_keyboard=[[admin_confirm_payment],[admin_change_amount_payment]], one_time_keyboard = True)
admin_payout = InlineKeyboardMarkup(inline_keyboard=[[admin_payout]], one_time_keyboard = True)
# admin_change_amount_payment = InlineKeyboardMarkup(inline_keyboard=[[admin_change_amount_payment]], one_time_keyboard = True)

changed_amount_payment_confirm = InlineKeyboardMarkup(inline_keyboard=[[changed_amount_payment_confirm]], one_time_keyboard = True)
check_user_payment = InlineKeyboardMarkup(inline_keyboard=[[check_user_payment]], one_time_keyboard = True)
# no subscribe button markup
subscribe_buttons2 = InlineKeyboardMarkup(inline_keyboard=subscribe_buttons2, one_time_keyboard = True)
share_button = InlineKeyboardMarkup(inline_keyboard=share_button)
up_me = InlineKeyboardMarkup(inline_keyboard=[up_me]) 
add_grow = InlineKeyboardMarkup(inline_keyboard=[add_grow])
add_balance_ready = InlineKeyboardMarkup(inline_keyboard=[add_balance_ready])
# transfer_button = InlineKeyboardMarkup(inline_keyboard=transfer_button)
# pay_button = InlineKeyboardMarkup(inline_keyboard=pay_button)

"1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣0️⃣"


button1 = KeyboardButton(text="🟢\nМеню")

button2 = KeyboardButton(text="🪪\nПрофиль")
button3 = KeyboardButton(text="🔼\nУровень")
button4 = KeyboardButton(text="💳\nБаланс")
button5 = KeyboardButton(text="💎\nПартнеры")
button6 = KeyboardButton(text="🔗\nРесурсы")
button7 = KeyboardButton(text="🎁\nБонусы")
button8 = KeyboardButton(text="🔎\nИнфо")

switch_tabs_emoji_text=["🟢\nМеню", "🪪\nПрофиль", "🔗\nРесурсы", "🔼\nУровень", "💳\nБаланс", "💎\nПартнеры", "🎁\nБонусы", "🔎\nИнфо"]


menu_buttons_reply_markup = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3, button4], [button5, button6, button7, button8]], resize_keyboard=True)





# builder = InlineKeyboardBuilder()
# for i in range(15):
#     builder.button(text=f”Кнопка {i}”, callback_data=f”button_{i}”)
# builder.adjust(2)
# await msg.answer(“Текст сообщения”, reply_markup=builder.as_markup())

