from aiogram import F, Bot
from aiogram.types import Message
from aiogram.filters import Filter, BaseFilter
from database.mongobase import kanal, admin_calleks, Free_collecks

channels_collection = kanal['kanallar']
channel_vaqt = kanal['vaqtK']
user_requests = kanal['user_requests']
user_reques = kanal['user_req']

class SubscriptionFilter(Filter):

    async def __call__(self, message: Message, bot: Bot) -> bool:

        user_id = message.from_user.id

        # FREE USER TEKSHIRISH
        free_user = Free_collecks.find_one({"user_id": user_id})

        if free_user:
            # Free user bo'lsa obuna tekshirilmaydi
            return False


        docs = list(channels_collection.find({})) + \
               list(channel_vaqt.find({})) + \
               list(user_requests.find({}))

        for doc in docs:

            username = doc.get('channel_username')
            ctype = doc.get('channel_type', 'public')

            if not username:
                continue


            # PUBLIC KANAL
            if ctype == 'public':

                try:

                    status = await bot.get_chat_member(username, user_id)

                    if status.status in ["member", "administrator", "creator"]:

                        if 'target_subscribers' in doc:

                            current = doc.get('current_subscribers', 0) + 1
                            target = doc.get('target_subscribers')

                            channels_collection.update_one(
                                {"_id": doc["_id"]},
                                {"$set": {"current_subscribers": current}}
                            )

                            print(f"Obunachi: {current}/{target}")

                            if current >= target:
                                channels_collection.delete_one({"_id": doc["_id"]})
                                print(f"Kanal avtomatik o'chirildi: {username}")

                        continue

                    else:
                        return True

                except:
                    return True


            # PRIVATE KANAL
            else:

                docs_private = user_requests.find({})
                doc_names = []

                for d in docs_private:

                    if isinstance(d['channel_name'], list):
                        doc_names.extend(d['channel_name'])
                    else:
                        doc_names.append(d['channel_name'])

                user_names = [
                    req['channel_name']
                    for req in user_reques.find({"user_id": user_id})
                ]

                if not set(doc_names).issubset(set(user_names)):
                    return True


        return False

MAIN_ADMIN_ID =  794530193  # bu yerga sizning IDingiz

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id

        # Bosh admin har doim o‘tadi
        if user_id == MAIN_ADMIN_ID:
            return True

        # Boshqa adminlar bazadan tekshiriladi
        if admin_calleks.find_one({'idsi': user_id}):
            return True

        # Agar admin emas bo‘lsa
        await message.answer("Siz admin emassiz ❌")
        return False

