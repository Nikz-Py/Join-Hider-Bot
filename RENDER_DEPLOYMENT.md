# Deploy Telegram Bot to Render

## Prerequisites
- Render account (free tier available)
- Your Telegram bot token
- Git repository with your code

## Step 1: Create requirements.txt
Since the pyproject.toml is configured, create a requirements.txt file with:
```
flask>=3.1.1
python-telegram-bot[webhooks]==20.7
```

## Step 2: Deploy to Render

1. **Connect Repository**
   - Go to https://render.com/
   - Click "New" → "Web Service"
   - Connect your Git repository

2. **Configure Service**
   - Name: `telegram-bot`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

3. **Set Environment Variables**
   Add these in Render dashboard:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
   - `WEBHOOK_URL`: `https://your-app-name.onrender.com/webhook` (replace with actual URL)
   - `SUPPORT_GROUP_URL`: Your support group link (optional)
   - `PORT`: `5000`

## Step 3: Update Bot Configuration

After deployment, get your Render URL and:

1. Set webhook URL in your bot:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-app-name.onrender.com/webhook
   ```

2. Test the webhook:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
   ```

## Step 4: Verify Deployment

- Check Render logs for any errors
- Test `/start` command with your bot
- Add bot to a test group to verify join message

## Files Created for Deployment:
- `render.yaml`: Render service configuration
- `Procfile`: Process configuration
- `runtime.txt`: Python version specification

## Important Notes:
- Free tier on Render may have cold starts
- Bot will automatically handle both polling and webhook modes
- Make sure webhook URL matches your Render domain exactly