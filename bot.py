from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters , ContextTypes
import logging
import chess
from chess_utils import board_to_unicode
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store ongoing games. Key: chat_id, Value: game state
ongoing_games = {}

# Telegram bot token from BotFather
TOKEN = 'Your token'


def is_move_format(text):
    # Simple pattern: letter followed by number, e.g., e4, Nf3. This pattern can be adjusted for more complexity.
    return re.match("^[a-hA-H][1-8]$", text) or re.match("^[NBRQK][a-hA-H][1-8]$", text)


async def new_chess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in ongoing_games:
        await update.message.reply_text('A game is already in progress in this chat.')
        return
    # Set up a new game
    ongoing_games[chat_id] = {
        'board': chess.Board(),
        'players': {'white': update.message.from_user.id},  # First player who started the game
        'turn': chess.WHITE
    }
    await update.message.reply_text('New game started! Send your moves in standard algebraic notation.\n'
                               + board_to_unicode(ongoing_games[chat_id]['board']))
# Function to join an existing game
async def join(update, context):
    chat_id = update.message.chat_id
    if chat_id not in ongoing_games or len(ongoing_games[chat_id]['players']) >= 2:
        await update.message.reply_text('Unable to join: no game to join or game is full.')
        return
    if 'black' in ongoing_games[chat_id]['players']:
        await update.message.reply_text('The game is already full.')
        return
     # Assign the second player (Black) to the game
    ongoing_games[chat_id]['players']['black'] = update.message.from_user.id
    await update.message.reply_text('You have joined the game as Black! Wait for White to make their move.')

async def handle_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if not is_move_format(text):
        return
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    game = ongoing_games.get(chat_id)
    if not game or user_id not in game['players'].values():
        await update.message.reply_text("You're not part of an ongoing game in this chat.")
        return

    board = game['board']
    is_white_turn = board.turn == chess.WHITE
    player_color = 'white' if game['players']['white'] == user_id else 'black'
    
    if (is_white_turn and player_color != 'white') or (not is_white_turn and player_color != 'black'):
        await update.message.reply_text("It's not your turn.")
        return

    try:
        move = board.parse_san(update.message.text)
        if move in board.legal_moves:
            board.push(move)
            await update.message.reply_text("Move made:\n" + board_to_unicode(board))
            # Toggle turn
            game['turn'] = chess.BLACK if game['turn'] == chess.WHITE else chess.WHITE
        else:
            await context.bot.send_message(chat_id=chat_id, text="Illegal move.")
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="Could not understand the move. Please use Standard Algebraic Notation (SAN).")

async def start(update:Update, context: ContextTypes.DEFAULT_TYPE): 
    """Send a message when the command /start is issued."""
    await update.message.reply_text(text ='Welcome to ChessBot! Send /play to start a game.')

async def help_command(update:Update, context: ContextTypes.DEFAULT_TYPE): 
    """Send a message when the command /help is issued."""
    await update.message.reply_text(text ='Help!')
async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.type
    text: str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')


def main():
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    # On different commands - answer in Telegram
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Adding handlers for new_chess_game and join
    app.add_handler(CommandHandler("new_chess_game", new_chess_game))
    app.add_handler(CommandHandler("join", join))

    # Handler for making moves - catches all non-command text messages
    app.add_handler(MessageHandler(filters.ALL, handle_move))

    # Start the Bot
    app.run_polling()


if __name__ == '__main__':
    main()
