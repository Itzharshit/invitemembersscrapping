# -*- coding: utf-8 -*-
# < (c) @xditya , https://xditya.me >
# inviteAllUserBot, 2021.

# Paid source, re-distributing without contacting the code owner is NOT allowed.

import logging
import asyncio
from decouple import config
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon import functions

from telethon.tl.functions.messages import GetFullChatRequest
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
)
from telethon.tl.functions.channels import GetFullChannelRequest

logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)

log = logging.getLogger("inviteAllUserBot")

log.info("\n\nStarting...\n")

# getting the vars
try:
    API_ID = config("API_ID", default=None, cast=int)
    API_HASH = config("API_HASH")
    SESSION = config("SESSION")
    SUDOS = config("SUDOS")
except Exception as e:
    log.warning("Missing config vars {}".format(e))
    exit(1)

SUDOS = [int(i) for i in SUDOS.split(" ")]

# connecting the user client
try:
    client = TelegramClient(
        StringSession(SESSION), api_id=API_ID, api_hash=API_HASH
    ).start()
except Exception as e:
    log.warning(e)
    exit(1)

# start by printing details
async def me_():
    me = await client.get_entity("me")
    print("First Name:", me.first_name)
    print("UserName:", me.username)
    print("User ID:", me.id)
    SUDOS.append(me.id) if me.id not in SUDOS else None


# functions
async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await event.reply("`Invalid channel/group`")
            return None
        except ChannelPrivateError:
            await event.reply(
                "`This is a private channel/group or I am banned from there`"
            )
            return None
        except ChannelPublicGroupNaError:
            await event.reply("`Channel or supergroup doesn't exist`")
            return None
        except (TypeError, ValueError) as err:
            await event.reply("`Invalid channel/group`")
            return None
    return chat_info


def make_mention(user):
    if user.username:
        return f"@{user.username}"
    else:
        return inline_mention(user)


def inline_mention(user):
    full_name = user_full_name(user) or "No Name"
    return f"[{full_name}](tg://user?id={user.id})"


def user_full_name(user):
    names = [user.first_name, user.last_name]
    names = [i for i in list(names) if i]
    return " ".join(names)


# functions end.


@client.on(events.NewMessage(pattern="^.alive$", from_users=SUDOS))
async def alive_resp(event):
    await event.reply("I'm online.\n\n~ @Bots4Sale")


@client.on(events.NewMessage(pattern=r"^.allinvite ?(.*)", from_users=SUDOS))
async def get_users(event):
    sender = await event.get_sender()
    me = await event.client.get_me()
    if sender.id != me.id:
        xx = await event.reply("`processing...`")
    else:
        xx = await event.edit("`processing...`")
    rk1 = await get_chatinfo(event)
    chat = await event.get_chat()
    if event.is_private:
        return await xx.edit("`Sorry, Can add users here`")
    s = f = 0
    error = "None"

    await xx.edit("**TerminalStatus**\n\n`Collecting Users.......`")
    async for user in event.client.iter_participants(rk1.full_chat.id):
        try:
            if error.startswith("Too"):
                return await xx.edit(
                    f"**Terminal Finished With Error**\n(`May Got Limit Error from telethon Please try agin Later`)\n**Error** : \n`{error}`\n\n• Invited `{s}` people \n• Failed to Invite `{f}` people"
                )
            await event.client(
                functions.channels.InviteToChannelRequest(channel=chat, users=[user.id])
            )
            s += 1
            await xx.edit(
                f"**Terminal Running...**\n\n• Invited `{s}` people \n• Failed to Invite `{f}` people\n\n**× LastError:** `{error}`"
            )
        except Exception as e:
            error = str(e)
            f += 1
        await asyncio.sleep(15)  # sleep 15 seconds.
    return await xx.edit(
        f"**Terminal Finished** \n\n• Successfully Invited `{s}` people \n• failed to invite `{f}` people"
    )


client.loop.run_until_complete(me_())
print("\nBot has started.\n(c) @xditya.\n")
client.run_until_disconnected()
