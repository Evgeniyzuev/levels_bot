import asyncio
import database
import config
from misc import dp, bot
from aiogram import Bot, types
from aiogram.utils.deep_linking import create_start_link
# from aiogram.dispatcher import Dispatcher
# from aiogram.utils import executor
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, DateTime, FLOAT,DATETIME
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from sqlalchemy import select, update
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


# url_object = URL.create("/data/bot.db")
db_url = 'sqlite://'+ config.db_url  
engine = create_engine(db_url)
# engine = create_engine("sqlite:////data/bot.db")

Base = declarative_base()
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Association table for the many-to-many relationship between users and referrers
# user_referrer = Table('user_referrer', Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True),
#     Column('referrer_id', Integer, ForeignKey('users.user_id'), primary_key=True))
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    user_link = Column(String)
    referral_link = Column(String, unique=True)
    referrer_id = Column(Integer, ForeignKey("users.user_id"))
    registration_time = Column(DateTime)
    level = Column(Integer, index=True)
    restate = Column(FLOAT)
    grow_wallet = Column(FLOAT)
    liquid_wallet = Column(FLOAT)
    turnover = Column(FLOAT)
    sales = Column(Integer)
    bonuses_available = Column(Integer)
    bonuses_gotten = Column(Integer)
    guide_stage = Column(Integer)
    current_leader_id = Column(Integer, index=True)
    referrers = Column(String)
    referrals = Column(String)
    bonus_cd_time = Column ( DateTime)

class Referral(Base):
    __tablename__ = "referals"
    referrer_id = Column(Integer,  ForeignKey("users.user_id"), primary_key=True)
    referral_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    # primary_key = Column(String, primary_key=True)

Base.metadata.create_all(bind=engine)

# db = SQLAlchemy(app)
# database.db = database.SessionLocal()

async def get_or_create_user(user_id, user_name, user_link, referrer_id):   # user = await db.query(User).filter(User.id == user_id).first()

    with Session(expire_on_commit=False) as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
                # await bot.send_message(user_id, f'user.referrer_id: {user.referrer_id} referrer_id: {referrer_id}')
                if int(user.referrer_id) != int(referrer_id) and int(user.user_id) != int(referrer_id):
                    user.referrer_id = referrer_id
                    session.commit()
                    # await bot.send_message(user_id, 'Реферер изменился')
                # else:
                #     await bot.send_message(user_id, 'Реферер не изменился')
                try:
                    # referral = session.query(Referral).filter(Referral.referrer_id == referrer_id).filter(Referral.referral_id == user_id).first()
                    referral = Referral(referrer_id=referrer_id, referral_id=user_id)
                    session.add(referral)
                    session.commit()
                except: pass
        try:
            user_info_text = await database.user_info( referrer_id)
        except:
            user_info_text = 'Пользователь не найден'
        await bot.send_message(user_id, 'Реферер: ' + user_info_text, disable_web_page_preview=True)
    if not user:
        referral_link = await create_start_link(bot,str(user_id), encode=True)
        await bot.send_message(referrer_id, text= f"По вашей ссылке зашел пользователь:\n{user_name}\nВы получите бонус 🎁 когда пользователь откроет два бонуса.")
        with Session(expire_on_commit=False) as session:
            # await bot.send_message(user_id, "регистрация нового пользователя")
            now = datetime.now()
            # referrers_text = ''
            # referrers_text += f'{referrer_id}'
            if user_id == 6251757715: level = 100
            else: level = 0
            user = User(user_id=user_id, user_name=user_name, user_link=user_link, referral_link=referral_link, referrer_id=referrer_id, registration_time=now, level=level,
                restate=0, grow_wallet=0, liquid_wallet=0, turnover=0, sales=0, bonuses_available=0, bonuses_gotten=0, guide_stage=0,
                current_leader_id=referrer_id, referrers='', referrals = '', bonus_cd_time = now )
            referral = Referral(referrer_id=referrer_id, referral_id=user_id)
            session.add(referral)
            session.add(user)
            session.commit()
    return user 

async def alter_table_user():
    with Session() as session:
        session.execute("ALTER TABLE users ADD COLUMN user_link TEXT")
        session.commit()

async def get_user(user_id):
    with Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
    return user

async def drop_table_referrals():
    with Session() as session:
        session.execute("DROP TABLE referals")
        session.commit()

async def delete_user(user_id):
    with Session() as session:
        session.query(User).filter(User.user_id == user_id).delete()
        session.commit()
    
async def delete_all_refs(user_id):
    with Session() as session:
        session.query(Referral).filter(Referral.referrer_id == user_id).delete()
        session.query(Referral).filter(Referral.referral_id == user_id).delete()

async def get_all_refs():
    with Session() as session:
        refs = session.query(Referral).all()
        return refs

async def user_info(user_id):
    user = await get_user(user_id)
    # registration_time = user.registration_time.strftime('%Y-%m-%d %H:%M:%S')   # [user_id]
    # bonus_cd_time = user.bonus_cd_time.strftime('%Y-%m-%d %H:%M:%S') # [user_id]
    user_info = (f"{user.user_name}\nУровень: {user.level}\n@{user.user_link}\n{user.referral_link}\nОборот: {user.turnover}\nБонусов получено: {user.bonuses_gotten}\nID: {user.user_id}\nЛид: {user.current_leader_id}\nРеферер: {user.referrer_id}")
    return user_info
    # except:
    #     await bot.send_message(user_id, "Бот не обновляется♻️\nПерезайдите по реф.ссылке или попробуйте позднее") 


async def get_all_users():
    with Session() as session:
        users = session.query(User).all()
        return users

async def get_all_referrals(user_id):
    with Session() as session:
        referrals = session.query(Referral).filter(Referral.referrer_id == user_id).all()
        users = []
        for referral in referrals:
            user = await get_user(referral.referral_id)
            users.append(user)
        return users


async def get_all_referrers(user_id):
    with Session() as session:
        referrers = session.query(Referral).filter(Referral.referral_id == user_id).all()
        users = []
        for referrer in referrers:
            user = await get_user(referrer.referrer_id)
            users.append(user)
        return users



level_channels = []
level_channels.append(-1000000000000) # комментарии в канале или кейсы уровней или 
level_channels.append(-1002128672686)
level_channels.append(-1002083788701)
level_channels.append(-1002095901143)
level_channels.append(-1002051825111)
level_channels.append(-1002055692741)
level_channels.append(-1002005520032)
level_channels.append(-1002081701051)
level_channels.append(-1002114431064)
level_channels.append(-1002084433490)
level_channels.append(-1002060493521)
level_channels.append(-1002009023699)
level_channels.append(-1002065971215)
level_channels.append(-1002130407802)
level_channels.append(-1002089355929)
level_channels.append(-1001939317640)
level_channels.append(-1002112588451)
level_channels.append(-1002022917818)
level_channels.append(-1002125464843)
level_channels.append(-1002124444687)
level_channels.append(-1002040773959)

# level_1_channel = -1002128672686
# level_2_channel = -1002083788701
# level_3_channel = -1002095901143
# level_4_channel = -1002051825111
# level_5_channel = -1002055692741
# level_6_channel = -1002005520032
# level_7_channel = -1002081701051
# level_8_channel = -1002114431064
# level_9_channel = -1002084433490
# level_10_channel = -1002060493521
# level_11_channel = -1002009023699
# level_12_channel = -1002065971215
# level_13_channel = -1002130407802
# level_14_channel = -1002089355929
# level_15_channel = -1001939317640
# level_16_channel = -1002112588451
# level_17_channel = -1002022917818
# level_18_channel = -1002125464843
# level_19_channel = -1002124444687
# level_20_channel = -1002040773959
# level_1_channel_link = 'https://t.me/+mfZCEAzD49AxNzUy'
# level_2_channel_link = 'https://t.me/+_OWQU1CpS7xhOGJi'
# level_3_channel_link = 'https://t.me/+ENbYbjFKxyg1NzUy'
# level_4_channel_link = 'https://t.me/+izMLp0OaimhhM2Vi'
# level_5_channel_link = 'https://t.me/+pvQrvKRLQGw1NjEy'
# level_6_channel_link = 'https://t.me/+oqxA8yMvsbUxNTJi'
# level_7_channel_link = 'https://t.me/+scnpUSREb6IxNjcy'
# level_8_channel_link = 'https://t.me/+_DBX496A2rc5ZmQy'
# level_9_channel_link = 'https://t.me/+cyJ4IQpQlnY4Yzky'
# level_10_channel_link = 'https://t.me/+C6ItnmbbRKk1Njcy'
# level_11_channel_link = 'https://t.me/+qMoE-7AH3rs2M2Qy'
# level_12_channel_link = 'https://t.me/+k-2R_rKgu7xjMmMy'
# level_13_channel_link = 'https://t.me/+yYbBroNs2ttiNzdi'
# level_14_channel_link = 'https://t.me/+yaBuo2sNk6UxNmRi'
# level_15_channel_link = 'https://t.me/+WUXrIIi04ScyMzJi'
# level_16_channel_link = 'https://t.me/+GzKigNIttWEyYWJi'
# level_17_channel_link = 'https://t.me/+ZKKCiZEacFgxNzgy'
# level_18_channel_link = 'https://t.me/+BNqLnBJ2YdlkODFi'
# level_19_channel_link = 'https://t.me/+ad73g-MNUYw0Yjk6'
# level_20_channel_link = 'https://t.me/+wO5a1f6vPb4xN2My'


level_links=[]
level_links.append('https://t.me/+mfZCEAzD49AxNzUy')
level_links.append('https://t.me/+_OWQU1CpS7xhOGJi')
level_links.append('https://t.me/+ENbYbjFKxyg1NzUy')
level_links.append('https://t.me/+izMLp0OaimhhM2Vi')
level_links.append('https://t.me/+pvQrvKRLQGw1NjEy')
level_links.append('https://t.me/+oqxA8yMvsbUxNTJi')
level_links.append('https://t.me/+scnpUSREb6IxNjcy')
level_links.append('https://t.me/+_DBX496A2rc5ZmQy')
level_links.append('https://t.me/+cyJ4IQpQlnY4Yzky')
level_links.append('https://t.me/+C6ItnmbbRKk1Njcy')
level_links.append('https://t.me/+qMoE-7AH3rs2M2Qy')
level_links.append('https://t.me/+k-2R_rKgu7xjMmMy')
level_links.append('https://t.me/+yYbBroNs2ttiNzdi')
level_links.append('https://t.me/+yaBuo2sNk6UxNmRi')
level_links.append('https://t.me/+WUXrIIi04ScyMzJi')
level_links.append('https://t.me/+GzKigNIttWEyYWJi')
level_links.append('https://t.me/+ZKKCiZEacFgxNzgy')
level_links.append('https://t.me/+BNqLnBJ2YdlkODFi')
level_links.append('https://t.me/+ad73g-MNUYw0Yjk6')
level_links.append('https://t.me/+wO5a1f6vPb4xN2My')



# local_users = {}
basecoin = 1
usdt_rub = 93
ton_rub = 600
gamma = {}
transfers = {}
payment_to_check = {}

payout = {}
payment_to_check_user_id = 0
payment_to_check_amount = 0
# users = {}


class Transfer:
    user_to_id = 0
    amount = 0