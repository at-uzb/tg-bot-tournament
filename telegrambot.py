from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
API_TOKEN = ''

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

AUTHORIZED_USERNAMES = ['abdulaziz_codes']
async def is_authorized_user(message: Message):
    # Check if the user's username is in the authorized list
    return message.from_user.username in AUTHORIZED_USERNAMES
# Data storage for the tournament
tournament_data = {
    "players": {},  # Format: {"player_name": {"goals": 0, "status": "🔴"}}
    "leaderboard_message_id": None,  # ID of the leaderboard message to edit
    "wish_list" : {},
}

# Command handler for /turnir
@dp.message(Command("turnir"))
async def create_tournament(message: Message):
    if message.from_user.username not in AUTHORIZED_USERNAMES:
        await message.answer("Siz @abdulaziz_codes emassiz)")
        return
    # Check if the command is issued in a group
    if message.chat.type not in ['group', 'supergroup']:
        await message.answer("This command only works in groups.")
        return

    # Parse player names from the command
    args = message.text.split()[1:]  # Extract player names
    if not args:
        await message.answer("Usage: /turnir player1 player2 player3 ...")
        return
    
    # Initialize tournament data with the provided players
    tournament_data["players"] = {
        player: {"goals": 0, "status": "🔴"} for player in args
    }
    tournament_data["leaderboard_message_id"] = None

    # Post the initial leaderboard
    leaderboard_text = generate_leaderboard()
    sent_message = await message.answer(leaderboard_text)  # Removed parse_mode="Markdown"
    tournament_data["leaderboard_message_id"] = sent_message.message_id

    await message.answer("Turnir boshlandi !!!")

@dp.message(Command("update"))
async def update_player_goals(message: Message):
    if message.from_user.username not in AUTHORIZED_USERNAMES:
        await message.answer("Siz @abdulaziz_codes emassiz)")
        return
    # Check if the command is issued in a group
    if message.chat.type not in ['group', 'supergroup']:
        await message.answer("This command only works in groups.")
        return

    # Parse the command arguments
    try:
        # Expected format: /update player_name goals
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer("Usage: /update player_name goals")
            return

        player_name = args[1]
        goals = int(args[2])

        # Check if the player exists in the tournament
        if player_name not in tournament_data["players"]:
            await message.answer(f"Player '{player_name}' not found in the tournament.")
            return

        # Update player goals
        tournament_data["players"][player_name]["goals"] = goals

        # Refresh the leaderboard
        leaderboard_text = generate_leaderboard()
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=tournament_data["leaderboard_message_id"],
            text=leaderboard_text,
            parse_mode="HTML"  # Use HTML parse mode for <pre> tags
        )
        await message.answer(f"{player_name} {goals} urdi!")
    except ValueError:
        await message.answer("Invalid goals. Please provide a valid number.")
    except Exception as e:
        await message.answer(f"Failed to update player stats: {e}")

@dp.message(Command("add"))
async def add_to_wishlist(message: Message):
    if message.from_user.username not in AUTHORIZED_USERNAMES:
        await message.answer("Siz @abdulaziz_codes emassiz)")
        return
    # Check if the command is issued in a group
    if message.chat.type not in ['group', 'supergroup']:
        await message.answer("This command only works in groups.")
        return

    # Parse the command arguments
    try:
        # Expected format: /add player_name its_ovr
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer("Usage: /add player_name its_ovr")
            return

        player_name = args[1]
        ovr = args[2]

        # Add player to the wishlist
        tournament_data["wish_list"][player_name] = ovr
        leaderboard_text = generate_leaderboard()
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=tournament_data["leaderboard_message_id"],
            text=leaderboard_text,
            parse_mode="HTML"  # Use HTML parse mode for <pre> tags
        )
        await message.answer(f"{player_name} ({ovr} OVR) yashil zonaga qo'shildi!")
    except Exception as e:
        await message.answer(f"Failed to add player to wishlist: {e}")

# Helper function to generate the leaderboard
def generate_leaderboard():
    # Sort players by goals (descending)
    sorted_players = sorted(
        tournament_data["players"].items(),
        key=lambda x: x[1]["goals"],
        reverse=True
    )
    
    # Generate the leaderboard text
    leaderboard_text = "🇪🇺 Turnir bo'yicha JADVAL 🇪🇺\n\n"
    #leaderboard_text += "<pre>"
    sn = 0 #space number needed
    for i, (player, data) in enumerate(sorted_players):
        rank = f"{i+1}️."
        goals = str(data['goals'])
        sn = 25 - len(player) - len(str(i+1)) - len(goals)
        # Format leaderboard line
        # player_line = f"{rank}️ {player}{'-'*sn}{goals}⚽️"
        player_line = f"{rank} {player.ljust(20)} {goals.rjust(3)} ⚽️"
        if i < 11:
            leaderboard_text += player_line + "\n"
        
        elif i == 11:
            leaderboard_text += "\n🔄⬇️🔄⬇️🔄⬇️🔄⬇️🔄⬇️\n\n"
            leaderboard_text += f"🔴 {player.ljust(20)} {goals.rjust(3)} ⚽️\n"
        else: 
            leaderboard_text += f"🔴 {player.ljust(20)} {goals.rjust(3)} ⚽️\n"
    leaderboard_text += "\n⬆️🔄⬆️🔄⬆️🔄⬆️🔄⬆️🔄⬆️🔄\n"
    wish_list = list(tournament_data["wish_list"].items())
    for i in range(5):
        if i < len(wish_list):  
            player, ovr = wish_list[i]
        else:  
            player, ovr = "Bo'sh o'rin", "***"
        leaderboard_text += f"\n🟢 {player}   {ovr} OVR"
    #leaderboard_text += "</pre>"
    leaderboard_text += "⏳ 11 gacha o'yinchilar kengi turnirga 🇪🇺 avtomatik qo'shiladi.\n"
    leaderboard_text += "Qizildigilar 🔴 kengi turnirdan qolishadi.\n"
    leaderboard_text += "Yashildigilar 🟢 ularni o'rnilariga o'tishadi 🔄.\n"
    leaderboard_text += "Jadval doimiy yangilanib boradi ❗️\n"
    leaderboard_text += "Kengi turnirga 20 soat ⏳ vaqt bor.\n"
    leaderboard_text += "Yashilga 🟢 yozilishni hohlasez, qo'shilaman *** ovr deb yozing. 107+ ovr olinadi."

    return leaderboard_text

# Start the bot
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
