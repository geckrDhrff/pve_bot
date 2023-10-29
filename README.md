利用telegram bot 监控PVE 主机状态,控制虚拟机

**How to start**
```shell
  git clone XXXXX
  cd pve_bot
  python -m venv venv
  source venv/bin/activate
  pip3 install -r requirements.txt
  #Get from https://t.me/BotFather
  export BOT_TOKEN="your_bot_token"

  export PVE_IP="your_pve_ip"
  #Create api_token in pve management page 
  export PVE_TOKEN_NAME="your_pve_token"
  export PVE_TOKEN_VALUE="your_pve_token_secret"
  python3 bot.py
```
***Requires access to telegram***

参考文档
https://github.com/sshuangliu/Proxmox-VE-api
https://github.com/python-telegram-bot/python-telegram-bot
https://github.com/proxmoxer/proxmoxer/
