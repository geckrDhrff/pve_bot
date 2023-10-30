import json
import logging
import sys

from proxmoxer import ProxmoxAPI
from proxmoxer.tools import Tasks
from html import escape
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler

import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

bot_token = os.getenv('BOT_TOKEN')
pve_ip = os.getenv('PVE_IP', default="127.0.0.1")
pve_user = os.getenv('PVE_USER', default="root@pam")
pve_pwd = os.getenv('PVE_PWD', default="123456")

pve_token = os.getenv('PVE_TOKEN_NAME')
pve_token_value = os.getenv('PVE_TOKEN_VALUE')

# two ways to login pve
# 1. username and password, the only requirement is to make a request within 2 hours
#    proxmox = ProxmoxAPI(pve_ip, user=pve_user, password=pve_pwd, verify_ssl=False)
# 2. user, token_name and token_value, The API Token allows stateless interaction

proxmox = ProxmoxAPI(
    pve_ip, user=pve_user, token_name=pve_token,
    token_value=pve_token_value, verify_ssl=False
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("\t /start - start \n \
                                    /help - show help \n \
                                    /get_status - get pve cluster status \n \
                                    /get_nodes - get all nodes \n \
                                    /get_resources - get pve cluster resources \n \
                                    /get_vm_status {node} {vmid} - get vm status \n \
                                    /set_vm_start {node} {vmid} - start vm \n \
                                    /set_vm_stop {node} {vmid} - stop vm ")


async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info(sys._getframe().f_code.co_name)
    data = json.dumps(proxmox.cluster.status.get(), indent=4, separators=(',', ':'))
    await update.message.reply_text(data)


async def get_nodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info(sys._getframe().f_code.co_name)
    data = json.dumps(proxmox.nodes.get(), indent=4, separators=(',', ':'))
    await update.message.reply_text(data)


async def get_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info(sys._getframe().f_code.co_name)
    data = json.dumps(proxmox.cluster.resources.get(), indent=4, separators=(',', ':'))
    await update.message.reply_text(data)


async def get_vm_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    nodeid = context.args[0]
    vmid = context.args[1]
    logger.info(sys._getframe().f_code.co_name + " nodeid: " + nodeid + " vmid: " + vmid)

    data = json.dumps(proxmox.nodes(nodeid).qemu(vmid).status.current.get(), indent=4, separators=(',', ':'))
    await update.message.reply_text(data)


async def set_vm_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    nodeid = context.args[0]
    vmid = context.args[1]
    logger.info(sys._getframe().f_code.co_name + " nodeid: " + nodeid + " vmid: " + vmid)

    upid = proxmox.nodes(nodeid).qemu(vmid).status.start.post()
    logger.info(sys._getframe().f_code.co_name + " upid: " + upid)
    res = Tasks.blocking_status(proxmox, upid, timeout=300)
    data = json.dumps(res, indent=4, separators=(',', ':'))
    await update.message.reply_text(data)


async def set_vm_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    nodeid = context.args[0]
    vmid = context.args[1]
    logger.info(sys._getframe().f_code.co_name + " nodeid: " + nodeid + " vmid: " + vmid)

    upid = proxmox.nodes(nodeid).qemu(vmid).status.stop.post()
    logger.info(sys._getframe().f_code.co_name + " upid: " + upid)

    res = Tasks.blocking_status(proxmox, upid, timeout=300)
    data = json.dumps(res, indent=4, separators=(',', ':'))
    await update.message.reply_text(data)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query

    if not query:  # empty query should not be handled
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"<b>{escape(query)}</b>", parse_mode=ParseMode.HTML
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"<i>{escape(query)}</i>", parse_mode=ParseMode.HTML
            ),
        ),
    ]

    await update.inline_query.answer(results)


async def error_handler(update: Update, context: ContextTypes.context):
    logger.error(">>>>>>>>>>>", exc_info=context.error)

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).http_version("1.1").get_updates_http_version("1.1").build()

    # on different commands - answer in Telegram
    # command should be low letter!
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get_status", get_status))
    application.add_handler(CommandHandler("get_nodes", get_nodes))
    application.add_handler(CommandHandler("get_resources", get_resources))
    application.add_handler(CommandHandler("get_vm_status", get_vm_status))
    application.add_handler(CommandHandler("set_vm_start", set_vm_start))
    application.add_handler(CommandHandler("set_vm_stop", set_vm_stop))

    # on inline queries - show corresponding inline results
    application.add_handler(InlineQueryHandler(inline_query))

    application.add_error_handler(error_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
