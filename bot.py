from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters , ContextTypes
import logging
import chess
from chess_generator import draw_board_with_pieces
import re
from io import BytesIO


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


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    board_img = draw_board_with_pieces(ongoing_games[chat_id]['board'])
    with BytesIO() as output:
        board_img.save(output, format="PNG")
        output.seek(0)
        await context.bot.send_photo(chat_id=chat_id, photo=output)

    await update.message.reply_text('New game started! Send your moves in standard algebraic notation.\n')
# Function to join an existing game
async def join(update, context):
    chat_id = update.message.chat_id
    if chat_id not in ongoing_games:
        await update.message.reply_text('Unable to join: no game to join.')
        return
    
    user_id = update.message.from_user.id
    # Check if the user is already playing in this game
    if 'black' in ongoing_games[chat_id]['players']:
        if ongoing_games[chat_id]['players']['black'] == user_id:
            await update.message.reply_text('You are already playing as Black.')
        else:
            await update.message.reply_text('The game is already full.')
        return
    elif 'white' in ongoing_games[chat_id]['players'] and ongoing_games[chat_id]['players']['white'] == user_id:
        # Allow the user to join as Black if they are already White
        ongoing_games[chat_id]['players']['black'] = user_id
        await update.message.reply_text('You are now playing as both White and Black! It’s your turn.')
    else:
        # Assign the second player (Black) to the game if it's a different user
        ongoing_games[chat_id]['players']['black'] = user_id
        await update.message.reply_text('You have joined the game as Black! Wait for White to make their move.')


async def handle_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not is_move_format(text):
        return

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    game = ongoing_games.get(chat_id)

    # Ensure there is an ongoing game and the user is part of it
    if not game or user_id not in game['players'].values():
        await update.message.reply_text("You're not part of an ongoing game in this chat.")
        return

    board = game['board']

    # Check if it's the correct turn for the player
    # This is adjusted to allow a user playing both sides to make moves consecutively
    player_color = 'white' if game['players']['white'] == user_id else 'black'
    if (board.turn == chess.WHITE and player_color != 'white') and (board.turn == chess.BLACK and game['players'].get('black') != user_id):
        await update.message.reply_text("It's not your turn.")
        return
    
    # Before sending a new board image, delete the previous one if it exists
    if 'last_board_msg_id' in game:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=game['last_board_msg_id'])
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
    try:
        move = board.parse_san(text)
        if move in board.legal_moves:
            board.push(move)
            # Generate and send the updated board image
            board_img = draw_board_with_pieces(board)
            with BytesIO() as output:
                board_img.save(output, format="PNG")
                output.seek(0)
                await context.bot.send_photo(chat_id=chat_id, photo=output)

            # Store the message ID of the new board image
            game['last_board_msg_id'] = update.message.message_id
        else:
            await update.message.reply_text("Illegal move. Try again.")
    except ValueError:
        await update.message.reply_text("Could not understand the move. Please use Standard Algebraic Notation (SAN).")

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

    # Adding handlers for play and join
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("join", join))

    # Handler for making moves - catches all non-command text messages
    app.add_handler(MessageHandler(filters.ALL, handle_move))

    # Start the Bot
    app.run_polling()


if __name__ == '__main__':
    main()
