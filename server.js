const { Telegraf } = require('telegraf');
const axios = require('axios');

const bot = new Telegraf(process.env.BOT_TOKEN);
const WEBSITE_URL = process.env.WEBSITE_URL || 'https://vercel-telegram-bot-psi.vercel.app/'; // Set this in Vercel env

// Ping command to check Vercel status
bot.command('ping', async (ctx) => {
  try {
    const startTime = Date.now();
    
    // Ping your Vercel website
    const response = await axios.get(WEBSITE_URL);
    const pingTime = Date.now() - startTime;
    
    const status = response.status === 200 ? '🟢 ONLINE' : '🔴 OFFLINE';
    
    ctx.replyWithMarkdown(`
🚀 *Vercel Status*
🕒 Response Time: *${pingTime}ms*
📊 Status: *${status}*
🌐 Website: [${WEBSITE_URL}](${WEBSITE_URL})
    `);
  } catch (error) {
    ctx.replyWithMarkdown(`
❌ *Error checking status*
🔴 Status: *OFFLINE*
🌐 Website: [${WEBSITE_URL}](${WEBSITE_URL})
💡 Error: ${error.message}
    `);
  }
});

// Default commands
bot.start((ctx) => ctx.reply('Welcome! Use /ping to check server status'));
bot.help((ctx) => ctx.reply('Available commands:\n/ping - Check server status'));

// Webhook handler for Vercel
module.exports = async (req, res) => {
  if (req.method === 'POST') {
    try {
      await bot.handleUpdate(req.body, res);
    } catch (err) {
      console.error('Bot error:', err);
      res.status(500).send('Error processing update');
    }
  } else {
    res.status(200).json({
      status: 'online',
      ping: `${Date.now()}`, 
      message: 'Telegram bot is running on Vercel'
    });
  }
};
