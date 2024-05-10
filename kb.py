from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


profile_button = [InlineKeyboardButton(text="😃 Профиль", callback_data="profile", one_time_keyboard = True)]
bonus_button = InlineKeyboardButton(text="🎁 Открыть Бонус", callback_data="open_bonus", one_time_keyboard = True)
up_level = InlineKeyboardButton(text="🔼 Поднять уровень", callback_data="up_level", one_time_keyboard = True)
up_me = [InlineKeyboardButton(text="🔼 Поднять сейчас", callback_data="up_me", one_time_keyboard = True)]
# up_me = [InlineKeyboardButton(text="🔼 Поднять сейчас", callback_data="up_me", one_time_keyboard = True)]
# add_grow = [InlineKeyboardButton(text="🔼 Пополнить баланс", callback_data="add_grow", one_time_keyboard = True)]
add_balance_ready = [InlineKeyboardButton(text="✅ Перевод отправлен", callback_data="add_balance_ready", one_time_keyboard = True)]
get_and_open_bonus_button = [InlineKeyboardButton(text="🎁 Получить Бонус", callback_data="get_and_open_bonus", one_time_keyboard = True)]
check_done_button = [[InlineKeyboardButton(text="Готово!", callback_data="check_done_button", one_time_keyboard = True)]]
subscribe_buttons = [[InlineKeyboardButton(text="Подписаться", url='https://t.me/Levels_up')],[InlineKeyboardButton(text="Готово!", callback_data="check_subscribe_button", one_time_keyboard = True)]]
# subscribe_buttons2 = [[InlineKeyboardButton(text="Подписаться", url='https://t.me/Levels_up')],[InlineKeyboardButton(text="Готово!", callback_data="check_subscribe_button", one_time_keyboard = True)],[InlineKeyboardButton(text="Продолжить без бонуса 🚫", callback_data="no_subscribtion", one_time_keyboard = True)]]
share_button = [[InlineKeyboardButton(text="🔗 Поделиться", callback_data="share_button", one_time_keyboard = True)]]
# transfer_button = [[InlineKeyboardButton(text=" Перевод", callback_data="transfer", one_time_keyboard = True)]]
# pay_button = [[InlineKeyboardButton(text=" Оплата", callback_data="pay", one_time_keyboard = True)]]
show_requisites  = InlineKeyboardButton(text="ПО СБП  ", callback_data="show_requisites" , one_time_keyboard = True)
show_requisites2 = InlineKeyboardButton(text="TONCOIN ", callback_data="show_requisites2", one_time_keyboard = True)
show_requisites3 = InlineKeyboardButton(text="USDT TON", callback_data="show_requisites3", one_time_keyboard = True)

grow_wallet_down = InlineKeyboardButton(text="💳 🔻", callback_data="grow_wallet_down", one_time_keyboard = True)
grow_wallet_up = InlineKeyboardButton(text="💳 🔼", callback_data="grow_wallet_up", one_time_keyboard = True)
transfer_button = InlineKeyboardButton(text="💳 Перевод", callback_data="transfer", one_time_keyboard = True)
restate_up = InlineKeyboardButton(text="💳 ➡️ ✨", callback_data="restate_up", one_time_keyboard = True)
restate_down = InlineKeyboardButton(text="✨ ➡️ 💳", callback_data="restate_down", one_time_keyboard = True)
admin_confirm_payment = InlineKeyboardButton(text="Деньги вижу", callback_data="admin_confirm_payment", one_time_keyboard = True)
admin_payout = InlineKeyboardButton(text="Перевод", callback_data="admin_payout", one_time_keyboard = True)
check_user_payment = InlineKeyboardButton(text="Проверить платеж", callback_data="check_user_payment", one_time_keyboard = True)
admin_change_amount_payment = InlineKeyboardButton(text="Изменить сумму платежа", callback_data="admin_change_amount_payment", one_time_keyboard = True)
changed_amount_payment_confirm = InlineKeyboardButton(text="Подтвердить сумму платежа", callback_data="changed_amount_payment_confirm", one_time_keyboard = True)
next_button = InlineKeyboardButton(text="далее", callback_data="next", one_time_keyboard = True)





profile_buttons = []
resources_buttons = []
balance_buttons = []
partners_buttons = [] 
learn_buttons = []

balance_control_buttons = [[restate_up, transfer_button, grow_wallet_up], [restate_down, grow_wallet_down]]
# balance_control_buttons2 = [restate_down, liquid_to_grow, liquid_wallet_down]



# menu_markup = InlineKeyboardMarkup(inline_keyboard=menu_buttons, one_time_keyboard = True, resize_keyboard=True)
# menu_button_markup = InlineKeyboardMarkup(inline_keyboard=[menu_button], one_time_keyboard = True)
profile_markup = InlineKeyboardMarkup(inline_keyboard=profile_buttons, one_time_keyboard = True)
resources_markup = InlineKeyboardMarkup(inline_keyboard=resources_buttons, one_time_keyboard = True)
level_markup = InlineKeyboardMarkup(inline_keyboard=[[up_level]], one_time_keyboard = True)
balance_markup = InlineKeyboardMarkup(inline_keyboard=balance_buttons, one_time_keyboard = True)
partners_markup = InlineKeyboardMarkup(inline_keyboard=partners_buttons, one_time_keyboard = True)
bonuses_markup = InlineKeyboardMarkup(inline_keyboard=[[bonus_button]], one_time_keyboard = True)
learn_markup = InlineKeyboardMarkup(inline_keyboard=learn_buttons, one_time_keyboard = True)
balance_control_markup = InlineKeyboardMarkup(inline_keyboard=balance_control_buttons, one_time_keyboard = True) # one_time_keyboard = True, 
# balance_control_markup = InlineKeyboardMarkup(inline_keyboard=balance_control_buttons, one_time_keyboard = True) 

# single button markups
bonus_button = InlineKeyboardMarkup(inline_keyboard=[[bonus_button]], one_time_keyboard = True)
get_and_open_bonus_button = InlineKeyboardMarkup(inline_keyboard=[get_and_open_bonus_button], one_time_keyboard = True)
check_done_button = InlineKeyboardMarkup(inline_keyboard=check_done_button, one_time_keyboard = True)
subscribe_buttons = InlineKeyboardMarkup(inline_keyboard=subscribe_buttons, one_time_keyboard = True)

admin_confirm_payment = InlineKeyboardMarkup(inline_keyboard=[[admin_confirm_payment],[admin_change_amount_payment]], one_time_keyboard = True)
admin_payout = InlineKeyboardMarkup(inline_keyboard=[[admin_payout]], one_time_keyboard = True)
next_button = InlineKeyboardMarkup(inline_keyboard=[[next_button]], one_time_keyboard = True)
# admin_change_amount_payment = InlineKeyboardMarkup(inline_keyboard=[[admin_change_amount_payment]], one_time_keyboard = True)

changed_amount_payment_confirm = InlineKeyboardMarkup(inline_keyboard=[[changed_amount_payment_confirm]], one_time_keyboard = True)
check_user_payment = InlineKeyboardMarkup(inline_keyboard=[[check_user_payment]], one_time_keyboard = True)
# next_button = InlineKeyboardMarkup(inline_keyboard=[[next_button]])
# no subscribe button markup
# subscribe_buttons2 = InlineKeyboardMarkup(inline_keyboard=subscribe_buttons2, one_time_keyboard = True)
share_button = InlineKeyboardMarkup(inline_keyboard=share_button)
up_me = InlineKeyboardMarkup(inline_keyboard=[up_me]) 
# add_grow = InlineKeyboardMarkup(inline_keyboard=[add_grow])
show_requisites_markup = InlineKeyboardMarkup(inline_keyboard=[[show_requisites],[show_requisites2],[show_requisites3]])
add_balance_ready = InlineKeyboardMarkup(inline_keyboard=[add_balance_ready])

# transfer_button = InlineKeyboardMarkup(inline_keyboard=transfer_button)
# pay_button = InlineKeyboardMarkup(inline_keyboard=pay_button)

"1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣0️⃣"


# button101 = KeyboardButton(text="🟢\nМеню")

button1 = KeyboardButton(text="😃\nПрофиль")
button2 = KeyboardButton(text="🔼\nУровень")
button3 = KeyboardButton(text="💳\nБаланс")
button4 = KeyboardButton(text="⚙️\nНастрой")
button5 = KeyboardButton(text="🤝\nПартнеры")
button6 = KeyboardButton(text="🔗\nРесурсы")
button7 = KeyboardButton(text="🎁\nБонусы")
button8 = KeyboardButton(text="❓\nДоходы")


menu_buttons_reply_markup = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3, button4], [button5, button6, button7, button8]], resize_keyboard=True)

all_users_button = InlineKeyboardButton(text="all users", callback_data="all_users_button", one_time_keyboard = True)
good_morning_button = InlineKeyboardButton(text="good morning", callback_data="good_morning_button", one_time_keyboard = True)
# alter_table_user_button = InlineKeyboardButton(text="alter table user", callback_data="alter_table_user_button", one_time_keyboard = True)
# all_users_level_button = InlineKeyboardButton(text="all users level", callback_data="all_users_level_button", one_time_keyboard = True)
reset_guide_button = InlineKeyboardButton(text="reset guide", callback_data="reset_guide_button", one_time_keyboard = True)
# drop_table_referrals_button = InlineKeyboardButton(text="drop table referrals", callback_data="drop_table_referrals_button", one_time_keyboard = True)
delete_inactive_users_button = InlineKeyboardButton(text="delete inactive users", callback_data="delete_inactive_users_button", one_time_keyboard = True)

admin_panel_buttons_reply_markup = InlineKeyboardMarkup(inline_keyboard=[[all_users_button,], [good_morning_button],[reset_guide_button,],[delete_inactive_users_button,]], resize_keyboard=True)





# builder = InlineKeyboardBuilder()
# for i in range(15):
#     builder.button(text=f”Кнопка {i}”, callback_data=f”button_{i}”)
# builder.adjust(2)
# await msg.answer(“Текст сообщения”, reply_markup=builder.as_markup())

