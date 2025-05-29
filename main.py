from pyrogram import Client, filters
from pyrogram.types import Message
# from pyromod import listen # Not using listen in this simplified version
import helper # Assuming helper.py is in the same directory and has necessary functions
import logging
import time
import asyncio
import os
import re
import tempfile
from pathlib import Path
import urllib.parse # For URL encoding
import requests # For downloading thumbnail

# --- Environment Variables for Configuration ---
# IMPORTANT: Set these in Render's Environment Variables UI for security
# The default values here are just placeholders and for local testing if env vars are not set.
API_ID = int(os.environ.get("API_ID", "28748671"))
API_HASH = os.environ.get("API_HASH", "f53ec7c41ce34e6d585674ed9ce6167c")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7896165148:AAFKmmxHT01cbgqPcuHpbigHnGETVO4vSk4")
OWNER_ID = int(os.environ.get("OWNER_ID", "1169394017")) # YOUR Telegram User ID
DEFAULT_RESOLUTION = os.environ.get("DEFAULT_RESOLUTION", "720")
DEFAULT_THUMBNAIL_URL = os.environ.get("DEFAULT_THUMBNAIL_URL", "no") # 'no' means auto-generate

CLASSPLUS_KEY_API_URL_TEMPLATE = os.environ.get("CLASSPLUS_KEY_API_URL_TEMPLATE", "") # e.g. "https://drm-api-pradeptech.onrender.com/cp?link="
PW_MPD_API_URL_TEMPLATE = os.environ.get("PW_MPD_API_URL_TEMPLATE", "") # e.g. "https://pw-api.com/dl?url={mpd_url}&token={user_token}&q={quality}"
PW_USER_TOKEN_ENV = os.environ.get("PW_USER_TOKEN", "") # Default token for PW-like API

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, # Set to logging.DEBUG for even more detailed Pyrogram logs if needed
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(funcName)s:%(lineno)d]", # Added funcName and lineno
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING) # Keep Pyrogram's own logs less verbose unless debugging it

logger.info("Logging configured.")
logger.info(f"Attempting to initialize Pyrogram Client with API_ID: {API_ID}, Bot Token (first 5 chars): {BOT_TOKEN[:5] if BOT_TOKEN else 'None'}")

try:
    bot = Client(
        "render_uploader_bot_session", # Session name
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )
    logger.info("Pyrogram Client object initialized.")
except Exception as e_client_init:
    logger.error(f"CRITICAL: Pyrogram Client initialization failed: {e_client_init}", exc_info=True)
    # If client fails to init, the script might exit or bot.run() will fail later.
    # For Render, this might cause the container to crash loop if it's a fatal init error.
    # Consider exiting if bot object is None or critical components are missing
    bot = None # Ensure bot is None if init fails

user_is_processing = {} # Simple flag to prevent concurrent processing by same user (OWNER_ID)

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, m: Message):
    logger.info(f"Received /start command from user_id: {m.from_user.id}")
    if m.from_user.id != OWNER_ID:
        logger.warning(f"Unauthorized /start attempt by user_id: {m.from_user.id}. Expected OWNER_ID: {OWNER_ID}")
        await m.reply_text("You are not authorized to use this bot.")
        return

    if user_is_processing.get(m.from_user.id, False):
        logger.info(f"User {m.from_user.id} sent /start while already processing.")
        await m.reply_text("I am currently busy processing a previous request. Please wait.")
        return

    logger.info(f"/start command from OWNER_ID {m.from_user.id} - providing instructions.")
    await m.reply_text(
        f"Hello [{m.from_user.first_name}](tg://user?id={m.from_user.id})!\n"
        "Ready to process your video links.\n\n"
        "**Send me a `.txt` file.**\n\n"
        "**In the caption of the TXT file, you can optionally specify (each on a new line):**\n"
        "1. Batch Name (e.g., `Physics Lectures`)\n"
        "2. Resolution (e.g., `720`, `1080`, `480` - default: `{DEFAULT_RESOLUTION}`p)\n"
        "3. Thumbnail URL (direct image link, or `no` for auto-gen - default: `{DEFAULT_THUMBNAIL_URL}`)\n"
        "4. Platform Token (if needed for specific MPD links, e.g., a PW token)\n\n"
        "**Example Caption:**\n"
        "```\nMy Course Batch 1\n1080\nhttps://example.com/thumb.jpg\nmytopsecrettoken123\n```"
    )

@bot.on_message(filters.document & filters.private & filters.user(OWNER_ID))
async def handle_document(client: Client, m: Message):
    logger.info(f"Received a document from user_id: {m.from_user.id}. Filename: {m.document.file_name if m.document else 'N/A'}")
    if m.from_user.id != OWNER_ID: # Should be caught by filter, but good practice
        logger.warning(f"Document received from unauthorized user_id: {m.from_user.id}")
        return

    if user_is_processing.get(m.from_user.id, False):
        logger.info(f"User {m.from_user.id} sent document while already processing.")
        await m.reply_text("Still processing a previous batch. Please wait until it's finished.")
        return

    if not m.document or not m.document.file_name.endswith(".txt"):
        logger.info(f"Received document is not a .txt file: {m.document.file_name if m.document else 'N/A'}")
        await m.reply_text("Please send a `.txt` file.")
        return

    user_is_processing[m.from_user.id] = True
    logger.info(f"Processing document: {m.document.file_name} for user_id: {m.from_user.id}")
    editable_msg = await m.reply_text(f"File `{m.document.file_name}` received. Parsing parameters...")

    caption_lines = (m.caption.strip().split('\n') if m.caption else [])
    logger.info(f"Caption lines received: {caption_lines}")
    
    batch_name_user = caption_lines[0].strip() if len(caption_lines) > 0 else None
    quality_user = caption_lines[1].strip() if len(caption_lines) > 1 else DEFAULT_RESOLUTION
    thumb_input_user = caption_lines[2].strip() if len(caption_lines) > 2 else DEFAULT_THUMBNAIL_URL
    platform_token_user = caption_lines[3].strip() if len(caption_lines) > 3 else PW_USER_TOKEN_ENV

    logger.info(f"Parsed params - Batch: {batch_name_user}, Quality: {quality_user}, Thumb: {thumb_input_user}, Token: {platform_token_user}")

    with tempfile.TemporaryDirectory(prefix="bot_dl_") as temp_task_dir_str:
        temp_task_dir = Path(temp_task_dir_str)
        logger.info(f"Created temporary directory: {temp_task_dir}")
        txt_file_path = await m.download(file_name=str(temp_task_dir / m.document.file_name))
        logger.info(f"TXT file downloaded to: {txt_file_path}")
        
        batch_name = batch_name_user if batch_name_user else Path(txt_file_path).stem
        quality = quality_user if quality_user.isdigit() else DEFAULT_RESOLUTION
        
        custom_thumb_dl_path = None
        if thumb_input_user.lower() != "no" and thumb_input_user.startswith("http"):
            custom_thumb_dl_path = temp_task_dir / "custom_thumb.jpg"
            logger.info(f"Attempting to download custom thumbnail from: {thumb_input_user} to {custom_thumb_dl_path}")
            try:
                response = requests.get(thumb_input_user, stream=True, timeout=20)
                response.raise_for_status()
                with open(custom_thumb_dl_path, 'wb') as f_thumb:
                    for chunk in response.iter_content(chunk_size=8192): f_thumb.write(chunk)
                logger.info("Custom thumbnail downloaded successfully.")
                await editable_msg.edit_text("Custom thumbnail downloaded.")
                await asyncio.sleep(1)
            except Exception as e_thumb:
                logger.error(f"Failed to download thumbnail {thumb_input_user}: {e_thumb}", exc_info=True)
                await editable_msg.edit_text(f"Failed to download custom thumbnail. Using default/auto. Error: {str(e_thumb)[:100]}")
                custom_thumb_dl_path = None
                await asyncio.sleep(1)
        
        thumb_to_use_in_helper = str(custom_thumb_dl_path) if custom_thumb_dl_path and custom_thumb_dl_path.exists() else "no"
        logger.info(f"Thumbnail to use in helper: {thumb_to_use_in_helper}")

        try:
            with open(txt_file_path, "r", encoding='utf-8') as f:
                content_lines = [line.strip() for line in f.read().split("\n") if line.strip()]
            logger.info(f"Read {len(content_lines)} lines from TXT file.")
        except Exception as e_read_txt:
            logger.error(f"Error reading TXT file {txt_file_path}: {e_read_txt}", exc_info=True)
            await editable_msg.edit_text(f"Error reading the TXT file: {str(e_read_txt)}")
            user_is_processing[m.from_user.id] = False
            return


        if not content_lines:
            logger.info("TXT file is empty after stripping lines.")
            await editable_msg.edit_text("The .txt file is empty or contains no valid links.")
            user_is_processing[m.from_user.id] = False
            return

        await editable_msg.edit_text(f"Found {len(content_lines)} links in `{Path(txt_file_path).name}`.\nBatch: `{batch_name}`\nQuality: `{quality}p`.\nStarting processing...\nThis message will be updated with progress.")
        
        success_count = 0
        failure_count = 0

        for i, url_line in enumerate(content_lines):
            item_progress_text = f"Batch: `{batch_name}` - Item {i+1}/{len(content_lines)}\n"
            logger.info(f"Processing item {i+1}: {url_line}")
            
            video_name_suggestion = f"video_{i+1}"
            url = url_line.strip()
            if ' ' in url_line:
                possible_url_part = url_line.split(' ')[-1]
                if possible_url_part.startswith("http"):
                    url = possible_url_part
                    video_name_suggestion = ' '.join(url_line.split(' ')[:-1]).strip()
            
            if not video_name_suggestion or video_name_suggestion == url:
                video_name_suggestion = urllib.parse.unquote(Path(url).name.split('?')[0].split('.')[0]) or f"video_{i+1}"

            video_name_sanitized = re.sub(r'[\\/*?:"<>|]', "_", video_name_suggestion)[:50].strip() # Replace invalid chars with underscore
            output_filename_base = f"{str(i+1).zfill(len(str(len(content_lines))))}_{video_name_sanitized if video_name_sanitized else f'item_{i+1}'}"
            logger.info(f"Item base name: {output_filename_base}, URL: {url}")

            status_update_msg_content = item_progress_text + f"Processing: `{output_filename_base}`..."
            try: await editable_msg.edit_text(status_update_msg_content)
            except Exception: pass

            downloaded_file_path = None
            try:
                if CLASSPLUS_KEY_API_URL_TEMPLATE and any(domain in url for domain in ["classplusapp.com/drm/", "cpvod.testbook.com/", "media-cdn.classplusapp.com"]):
                    logger.info(f"Classplus-like link detected: {url}")
                    normalized_url = url
                    if "cpvod.testbook.com/" in url:
                        normalized_url = url.replace("cpvod.testbook.com/", "media-cdn.classplusapp.com/drm/")
                        logger.info(f"Normalized Testbook URL to: {normalized_url}")
                    
                    api_call_url = f"{CLASSPLUS_KEY_API_URL_TEMPLATE}{urllib.parse.quote_plus(normalized_url)}"
                    await editable_msg.edit_text(status_update_msg_content + "\nFetching DRM keys...")
                    mpd_link, keys_list = helper.get_mps_and_keys(api_call_url) # This is a sync function, consider running in executor for async

                    if mpd_link and keys_list:
                        logger.info(f"DRM keys fetched. MPD: {mpd_link}, Keys count: {len(keys_list)}")
                        downloaded_file_path = await helper.decrypt_and_merge_video(
                            mpd_url=mpd_link, keys_list=keys_list,
                            output_dir_str=str(temp_task_dir), output_name_base=output_filename_base, quality=quality,
                            message_to_edit=editable_msg, context_bot=client
                        )
                    else:
                        logger.warning(f"Failed to get MPD/Keys for {url} from API: {api_call_url}")
                        await editable_msg.edit_text(status_update_msg_content + "\nERROR: Failed to get MPD/Keys from API.")
                        failure_count += 1; continue
                
                # Placeholder for PW-like MPD (add specific domain checks and API logic)
                elif PW_MPD_API_URL_TEMPLATE and "master.mpd" in url and "your_pw_platform_domain.com" in url: # Replace with actual domain
                    logger.info(f"PW-like MPD link detected: {url}")
                    await editable_msg.edit_text(status_update_msg_content + "\n(PW-like MPD) Fetching DRM keys... (NOT IMPLEMENTED YET)")
                    # ... (your logic to call PW_MPD_API_URL_TEMPLATE and then helper.decrypt_and_merge_video) ...
                    failure_count += 1; continue

                else:
                    logger.info(f"Using basic download for: {url}")
                    downloaded_file_path = await helper.download_video_basic(
                        url=url, output_name_base=output_filename_base, output_dir_str=str(temp_task_dir), quality=quality,
                        message_to_edit=editable_msg, context_bot=client
                    )

                if downloaded_file_path and Path(downloaded_file_path).exists():
                    logger.info(f"File successfully processed: {downloaded_file_path}")
                    caption_text = f"**Batch:** `{batch_name}`\n**Title:** `{output_filename_base}`\n**Quality:** {quality}p"
                    await helper.send_vid(
                        bot=client, m=m, cc=caption_text,
                        filename_path_str=downloaded_file_path,
                        thumb_path_or_no=thumb_to_use_in_helper,
                        name=f"{output_filename_base}.mp4",
                        prog_msg_id_to_delete=None # send_vid manages its own progress now
                    )
                    success_count += 1
                elif downloaded_file_path is None: # Error occurred and helper should have edited the message
                    logger.warning(f"Download/processing returned None for {output_filename_base}.")
                    failure_count += 1
                else: # Path returned but file doesn't exist (should not happen if helper is correct)
                    logger.error(f"File path {downloaded_file_path} returned but file does not exist for {output_filename_base}.")
                    failure_count += 1


            except Exception as e_loop:
                logger.error(f"Critical error in main processing loop for item {output_filename_base} (URL: {url}): {e_loop}", exc_info=True)
                try: await editable_msg.edit_text(status_update_msg_content + f"\nFATAL ITEM ERROR: {str(e_loop)[:200]}")
                except Exception: pass
                failure_count +=1
            
            logger.info(f"Item {i+1} processing finished. Success: {success_count}, Failures: {failure_count}")
            await asyncio.sleep(1) # Small delay between items

        final_summary = f"**Batch `{batch_name}` Processing Complete!**\n\nSuccessfully Uploaded: {success_count}\nFailed: {failure_count}"
        logger.info(final_summary)
        try: await editable_msg.edit_text(final_summary)
        except Exception: await m.reply_text(final_summary) # If original editable deleted

    # temp_task_dir and its contents are automatically cleaned up when 'with' block exits.
    logger.info(f"Finished processing batch for user_id: {m.from_user.id}")
    user_is_processing[m.from_user.id] = False


# Flask app for Render's web service type (to keep it alive)
from flask import Flask
flask_app = Flask(__name__)
logger.info("Flask app object created.")

@flask_app.route('/')
def route_index():
    # logger.info("Flask / health check route hit.") # Can be very noisy
    return 'Telegram Bot is alive and running!'

def run_flask():
    port = int(os.environ.get('PORT', 8080)) # Render sets PORT env var
    logger.info(f"Flask app attempting to start on host 0.0.0.0, port {port}...")
    try:
        flask_app.run(host='0.0.0.0', port=port)
        logger.info("Flask app run() method has exited.") # Should not happen if running continuously
    except Exception as e_flask_run:
        logger.error(f"Flask app run() failed: {e_flask_run}", exc_info=True)

if __name__ == "__main__":
    logger.info("Script execution started in __main__ block (main.py).")
    if not bot:
        logger.critical("Pyrogram Client (bot object) is None. Cannot start bot. Check initialization errors.")
    else:
        from threading import Thread
        logger.info("Attempting to start Flask thread...")
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Flask thread start() called. Flask should be running in background.")

        logger.info("Giving Flask a moment to bind port...")
        time.sleep(3) # Give Flask a few seconds to start up before bot takes over main thread

        logger.info(f"OWNER_ID for bot operations: {OWNER_ID}")
        logger.info(f"CLASSPLUS_KEY_API_URL_TEMPLATE: {CLASSPLUS_KEY_API_URL_TEMPLATE if CLASSPLUS_KEY_API_URL_TEMPLATE else 'Not Set'}")

        try:
            logger.info("Attempting bot.run() to start Pyrogram client...")
            bot.run() # This will block until the bot is stopped
            logger.info("Pyrogram client (bot.run()) has finished or been stopped.")
        except Exception as e_bot_run:
            logger.error(f"CRITICAL ERROR during bot.run(): {e_bot_run}", exc_info=True)
        finally:
            logger.info("Exiting __main__ block. Bot process is terminating.")
            if OWNER_ID in user_is_processing: # Check if key exists before deleting
                 user_is_processing[OWNER_ID] = False
