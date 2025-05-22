# LLM Bot
Telegram bot for openrouter api  

# Bot Setup Instructions  

To use the bot, you must be registered at https://openrouter.ai/.  
Then, log in and generate an API key at https://openrouter.ai/settings/keys.  

Edit the code by replacing the following fields:  
```python
# Settings
  TELEGRAM_TOKEN = "*"  # Replace * with your bot token from BotFather
  OPENROUTER_API_KEY = "*"  # Replace * with your generated OpenRouter API key
  MAX_TOKENS = set_max_tokens  # Set the number of tokens for your chosen model (2048, 4096, etc)
  BOT_USERNAME = "@botname"  # Replace with the Telegram username you assigned to your bot
```
Next, on line 103, change ```python model="deepseek/deepseek-chat-v3-0324:free"``` to the desired model from the list available on OpenRouter.
For example, under each model's heading, you will see a line with a button to copy the model name:
![image](https://github.com/user-attachments/assets/3e972921-e1c0-4f30-88af-3d22c40a1006)

After making these changes, the code is ready to run as a bot! :)
# Dependency
1. ```bash
   install python3
   ```

2. ```bash
   install python3-pip
   ```

3. ```bash
   pip install python-telegram-bot openai tiktoken
   ```

      -python-telegram-bot — for working with Telegram API.  
      -openai — for working with OpenAI API.  
      -tiktoken — for text tokenization.  

5. Execute: python3 openrouter_bot.py

# P.S. Start as service
```bash
nano /etc/systemd/system/telegram-bot.service
```  
   
```bash
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
User=user
WorkingDirectory=/home/user/telegram_bot
ExecStart=/home/user/telegram_bot/bot_env/bin/python3 /home/user/telegram_bot/openrouter_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
systemctl daemon-reload
systemctl enable telegram-bot.service
systemctl start telegram-bot.service
```
