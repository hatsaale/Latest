from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
import requests
import m3u8
import json
import subprocess
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
from pyromod import listen
from pyrogram.types import Message
from p_bar import progress_bar
from subprocess import getstatusoutput
from aiohttp import ClientSession
import helper
from logger import logging
import time
import asyncio
from pyrogram.types import User, Message
import sys
import re
import os
import urllib
import urllib.parse
import tgcrypto
import cloudscraper

bot = Client("bot",
             bot_token='add',
             api_id=add,
             api_hash='add')

owner_id = [6530997270]
auth_users = [6530997270]
photo1 = 'https://envs.sh/PQ_.jpg'
getstatusoutput(f"wget {photo1} -O 'photo.jpg'")
photo = "photo.jpg"


token_cp = 'your cp token'

@bot.on_message(filters.command(["start"]) & filters.user(owner_id))
async def account_login(bot: Client, m: Message):
    await m.reply_text(f"**Hello Bruh** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n>>I am TXT file Downloader Bot.\n>>Send me /txt Command And Follow Steps\nIf You Want To Stop Me Just Send /stop to stop me 😎")

@bot.on_message(filters.command("txt"))
async def restart_handler(_, m):
    await m.reply_text("🚦**STOPPED**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["txt"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("**Please Send TXT file for download**")
    input: Message = await bot.listen(editable.chat.id)
    y = await input.download()
    file_name, ext = os.path.splitext(os.path.basename(y))  # Extract filename & extension
    x = y  # No decryption, use the file as is

    path = f"./downloads/{m.chat.id}"

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return

    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Send Me Your Batch Name or send `df` for grabing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == 'df':
        b_name = file_name
    else:
        b_name = raw_text0

    await editable.edit("**Enter resolution** `1080` , `720` , `480` , `360` , `240` , `144`")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080"
        else:
            res = "1280x720"
    except Exception:
        res = "UN"

    await editable.edit("**Now Enter A Caption to add caption on your uploaded file\n\n>>OR Send `df` for use default**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == 'df':
        MR = "Group Admin:)™"
    else:
        MR = raw_text3

    await editable.edit("**If pw mpd links enter working token ! **")
    input11: Message = await bot.listen(editable.chat.id)
    token = input11.text
    await input11.delete(True)

    await editable.edit("Now send the Thumb url For Custom Thumbnail.\nExample » `https://envs.sh/Hlb.jpg` \n Or if don't want Custom Thumbnail send = `no`")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    if len(links) == 1:
        count = 1
    else:
        count = int(raw_text)

    try:
        for i in range(count - 1, len(links)):
            V = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + V

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)
            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])
            elif "classplusapp.com/drm/" in url:
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])
            elif "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth={yourtoken} #yourcwtoken
                url = url.split("bcov_auth")[0]+bcov
            elif "tencdn.classplusapp" in url:
                headers = {'Host': 'api.classplusapp.com', 'x-access-token': f'{token_cp}', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                params = (('url', f'{url}'))
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']
            elif 'videos.classplusapp' in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{token_cp}'}).json()['url']
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url:
                headers = { 'x-access-token': f'{token_cp}',"X-CDN-Tag": "empty"}
                response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                url = response.json()['url']
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]
            elif url.startswith("https://videotest.adda247.com/"):
                if url.split("/")[3] != "demo":
                    url = f'https://videotest.adda247.com/demo/{url.split("https://videotest.adda247.com/")[1]}'
            elif 'master.mpd' in url:
                url = f"{api_url}pw-dl?url={url}&token={token}&authorization={api_token}&q={raw_text2}"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{name1[:60]} 𝐃𝐈𝐋𝐉𝐀𝐋𝐄 ❤️'

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'**╭── ⋆⋅☆⋅⋆ ──╮**\n✦ **{str(count).zfill(3)}** ✦\n**╰── ⋆⋅☆⋅⋆ ──╯**\n\n🎭 **Title:** `{name1} 😎 Admin:)™.mkv`\n🖥️ **Resolution:** [{res}]\n\n📘 **Course:** `{b_name}`\n\n🚀 **Extracted By:** `{MR}`'
                cc1 = f'**╭── ⋆⋅☆⋅⋆ ──╮**\n✦ **{str(count).zfill(3)}** ✦\n**╰── ⋆⋅☆⋅⋆ ──╯**\n\n🎭 **Title:** `{name1} 😎 Admin:)™.pdf`\n\n📘 **Course:** `{b_name}`\n\n🚀 **Extracted By:** `{MR}`'
                cc2 = f'**╭── ⋆⋅☆⋅⋆ ──╮**\n✦ **{str(count).zfill(3)}** ✦\n**╰── ⋆⋅☆⋅⋆ ──╯**\n\n🎭 **Title:** `{name1} 😎 Admin:)™.jpg`\n\n📘 **Course:** `{b_name}`\n\n🚀 **Extracted By:** `{MR}`'
                ccyt = f'**╭── ⋆⋅☆⋅⋆ ──╮**\n✦ **{str(count).zfill(3)}** ✦\n**╰── ⋆⋅☆⋅⋆ ──╯**\n\n🎭 **Title:** `{name1} 😎 Admin:)™.mkv`\n🎬 **Video Link:** {url}\n🖥️ **Resolution:** [{res}]\n\n📘 **Course:** `{b_name}`\n\n🚀 **Extracted By:** `{MR}`'

                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc1)
                        count += 1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif 'pdf*' in url:
                    pdf_key = url.split('*')[1]
                    url = url.split('*')[0]
                    pdf_enc = await helper.download_and_decrypt_pdf(url, name, pdf_key)
                    copy = await bot.send_document(chat_id=m.chat.id, document=pdf_enc, caption=cc1)
                    count += 1
                    os.remove(pdf_enc)
                    continue

                elif ".pdf" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif any(img in url.lower() for img in ['.jpeg', '.png', '.jpg']):
                    try:
                        subprocess.run(['wget', url, '-O', f'{name}.jpg'], check=True)
                        await bot.send_photo(chat_id=m.chat.id, caption=cc2, photo=f'{name}.jpg')
                    except subprocess.CalledProcessError:
                        await m.reply("Failed to download the image. Please check the URL.")
                    except Exception as e:
                        await m.reply(f"An error occurred: {e}")
                    finally:
                        if os.path.exists(f'{name}.jpg'):
                            os.remove(f'{name}.jpg')

                elif "youtu" in url:
                    try:
                        await bot.send_photo(chat_id=m.chat.id, photo=photo, caption=ccyt)
                        count += 1
                    except Exception as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(1)
                        continue

                elif ".ws" in url and url.endswith(".ws"):
                    try:
                        await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}", f"{name}.html")
                        time.sleep(1)
                        await bot.send_document(chat_id=m.chat.id, document=f"{name}.html", caption=cc1)
                        os.remove(f'{name}.html')
                        count += 1
                        time.sleep(5)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        await m.reply_text(str(e))
                        continue

                elif 'encrypted.m' in url:
                    Show = f"✈️ 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 ✈️\n\n┠ 📈 Total Links = {len(links)}\n┠ 💥 Currently On = {str(count).zfill(3)}\n\n**📩 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆 📩**\n\n**🧚🏻‍♂️ Title** : {name}\n├── **Extention** : {MR}\n├── **Resolution** : {raw_text2}\n├── **Url** : `Kya karega URL dekh ke  BSDK 👻👻`\n├── **Thumbnail** : `{input6.text}`\n├── **Bot Made By** : "
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    await asyncio.sleep(1)
                    continue

                elif 'drmcdni' in url or 'drm/wv' in url:
                    Show = f"𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 ✈️\n\n┠ 📈 Total Links = {len(links)}\n┠ 💥 Currently On = {str(count).zfill(3)}\n\n**📩 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆 📩**\n\n**🧚🏻‍♂️ Title** : {name}\n├── **Extention** : {MR}\n├── **Resolution** : {raw_text2}\n├── **Url** : `Kya karega URL dekh ke  BSDK 👻👻`\n├── **Thumbnail** : `{input6.text}`\n├── **Bot Made By** : "
                    prog = await m.reply_text(Show)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    await asyncio.sleep(1)
                    continue

                else:
                    Show = f"✈️ 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 ✈️\n\n┠ 📈 Total Links = {len(links)}\n┠ 💥 Currently On = {str(count).zfill(3)}\n\n**📩 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆 📩**\n\n**🧚🏻‍♂️ Title** : {name}\n├── **Extention** : {MR}\n├── **Resolution** : {raw_text2}\n├── **Url** : `Kya karega URL dekh ke  BSDK 👻👻`\n├── **Thumbnail** : `{input6.text}`\n├── **Bot Made By** : "
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(f"**downloading failed \**\n\n{str(e)}\n\n**Name** - {name}\n**Link** - {url}")
                count += 1
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("**🔥 Sᴜᴄᴄᴇsғᴜʟʟʏ Dᴏᴡɴʟᴏᴀᴅᴇᴅ Aʟʟ Lᴇᴄᴛᴜʀᴇs SIR 🔥**")

bot.run()
