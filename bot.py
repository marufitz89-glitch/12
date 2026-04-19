‎import asyncio
‎import logging
‎from aiogram import Bot, Dispatcher, types, F
‎from aiogram.filters import CommandStart, Command
‎from aiogram.fsm.context import FSMContext
‎from aiogram.fsm.state import State, StatesGroup
‎from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
‎
‎# --- Configuration ---
‎BOT_TOKEN = "8655726261:AAFxaB4-kJIml8Kk-GmzF6BeujIYkwG7vyg"
‎ADMIN_ID = 8370472280 # Replace with your Telegram ID
‎
‎# Initialize Bot and Dispatcher
‎bot = Bot(token=BOT_TOKEN)
‎dp = Dispatcher()
‎
‎# Logging setup for professional debugging
‎logging.basicConfig(level=logging.INFO)
‎
‎# --- FSM States for Poll Creation ---
‎class PollCreation(StatesGroup):
‎    waiting_for_question = State()
‎    waiting_for_options = State()
‎    waiting_for_settings = State()
‎
‎# --- Keyboards (UI/UX) ---
‎def get_main_menu():
‎    keyboard = [
‎        [InlineKeyboardButton(text="📊 পোল তৈরি করুন", callback_data="create_poll")],
‎        [
‎            InlineKeyboardButton(text="⚙️ সেটিংস", callback_data="settings"),
‎            InlineKeyboardButton(text="📖 সাহায্য", callback_data="help")
‎        ],
‎        [InlineKeyboardButton(text="🚀 প্রিমিয়াম ফিচার", callback_data="premium")]
‎    ]
‎    return InlineKeyboardMarkup(inline_keyboard=keyboard)
‎
‎def get_poll_type_menu():
‎    keyboard = [
‎        [InlineKeyboardButton(text="সাধারণ পোল", callback_data="type_regular")],
‎        [InlineKeyboardButton(text="বেনামী (Anonymous) পোল", callback_data="type_anonymous")],
‎        [InlineKeyboardButton(text="কুইজ মোড", callback_data="type_quiz")],
‎        [InlineKeyboardButton(text="❌ বাতিল করুন", callback_data="cancel_creation")]
‎    ]
‎    return InlineKeyboardMarkup(inline_keyboard=keyboard)
‎
‎# --- Handlers ---
‎
‎@dp.message(CommandStart())
‎async def cmd_start(message: types.Message):
‎    """Welcome Message with Pro UI"""
‎    welcome_text = (
‎        f"আসসালামু আলাইকুম **{message.from_user.first_name}**! 🌟\n\n"
‎        "প্রফেশনাল পোল মেকার বটে আপনাকে স্বাগতম। আমি আপনার গ্রুপ বা চ্যানেলের জন্য "
‎        "আকর্ষণীয় পোল এবং কুইজ তৈরি করতে সাহায্য করব।\n\n"
‎        "শুরু করতে নিচের মেনু থেকে একটি অপশন বেছে নিন:"
‎    )
‎    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
‎
‎@dp.callback_query(F.data == "create_poll")
‎async def start_poll_creation(callback: types.CallbackQuery, state: FSMContext):
‎    """Step 1: Ask for Poll Question"""
‎    await callback.message.edit_text(
‎        "📝 **ধাপ ১/৩:**\n\nঅনুগ্রহ করে আপনার পোলের প্রশ্নটি লিখুন:", 
‎        parse_mode="Markdown"
‎    )
‎    await state.set_state(PollCreation.waiting_for_question)
‎    await callback.answer()
‎
‎@dp.message(PollCreation.waiting_for_question)
‎async def process_question(message: types.Message, state: FSMContext):
‎    """Step 2: Save question and ask for options"""
‎    if len(message.text) < 5:
‎        await message.answer("দুঃখিত, আপনার প্রশ্নটি খুব ছোট। অনুগ্রহ করে একটি পরিষ্কার প্রশ্ন লিখুন।")
‎        return
‎
‎    await state.update_data(question=message.text)
‎    instruction = (
‎        "✅ প্রশ্ন সেভ করা হয়েছে!\n\n"
‎        "📋 **ধাপ ২/৩:**\n"
‎        "এবার পোলের বিকল্পগুলো কমা (,) দিয়ে লিখে পাঠান।\n"
‎        "*(যেমন: হ্যাঁ, না, বলা যাচ্ছে না)*\n\n"
‎        "সর্বোচ্চ ১০টি বিকল্প দিতে পারবেন।"
‎    )
‎    await message.answer(instruction, parse_mode="Markdown")
‎    await state.set_state(PollCreation.waiting_for_options)
‎
‎@dp.message(PollCreation.waiting_for_options)
‎async def process_options(message: types.Message, state: FSMContext):
‎    """Step 3: Save options and ask for poll type/settings"""
‎    options = [opt.strip() for opt in message.text.split(",") if opt.strip()]
‎    
‎    if len(options) < 2 or len(options) > 10:
‎        await message.answer("দুঃখিত, আপনার ইনপুটটি সঠিক নয়। অনুগ্রহ করে কমপক্ষে ২টি এবং সর্বোচ্চ ১০টি বিকল্প কমা (,) দিয়ে লিখুন।")
‎        return
‎
‎    await state.update_data(options=options)
‎    await message.answer(
‎        "✅ বিকল্পগুলো সেভ করা হয়েছে!\n\n"
‎        "⚙️ **ধাপ ৩/৩:**\n"
‎        "আপনি কোন ধরনের পোল তৈরি করতে চান তা নির্বাচন করুন:",
‎        reply_markup=get_poll_type_menu(),
‎        parse_mode="Markdown"
‎    )
‎    await state.set_state(PollCreation.waiting_for_settings)
‎
‎@dp.callback_query(PollCreation.waiting_for_settings, F.data.startswith("type_"))
‎async def finalize_and_send_poll(callback: types.CallbackQuery, state: FSMContext):
‎    """Final Step: Generate the Poll using Telegram's Native API"""
‎    data = await state.get_data()
‎    question = data.get("question")
‎    options = data.get("options")
‎    
‎    poll_type = "regular"
‎    is_anonymous = False
‎    
‎    if callback.data == "type_anonymous":
‎        is_anonymous = True
‎    elif callback.data == "type_quiz":
‎        poll_type = "quiz"
‎        # For a full quiz, you would add another step asking for the correct option ID.
‎        # This is kept simple for the structural blueprint.
‎
‎    try:
‎        # Sending the poll
‎        await bot.send_poll(
‎            chat_id=callback.message.chat.id,
‎            question=question,
‎            options=options,
‎            is_anonymous=is_anonymous,
‎            type=poll_type,
‎            # correct_option_id=0  # Required if type is 'quiz'
‎        )
‎        await callback.message.delete()
‎        await callback.message.answer("🎉 আপনার পোল সফলভাবে তৈরি হয়েছে!", reply_markup=get_main_menu())
‎        
‎        # Here you would typically save the poll metadata to your Firebase/MongoDB database
‎        
‎    except Exception as e:
‎        logging.error(f"Error sending poll: {e}")
‎        await callback.message.answer("⚠️ দুঃখিত, পোলটি তৈরি করতে কোনো প্রযুক্তিগত সমস্যা হয়েছে। আবার চেষ্টা করুন।")
‎    finally:
‎        await state.clear()
‎        await callback.answer()
‎
‎@dp.callback_query(F.data == "cancel_creation")
‎async def cancel_creation(callback: types.CallbackQuery, state: FSMContext):
‎    """Cancel FSM State"""
‎    await state.clear()
‎    await callback.message.edit_text("❌ পোল তৈরি বাতিল করা হয়েছে।", reply_markup=get_main_menu())
‎    await callback.answer()
‎
‎# --- Admin Dashboard ---
‎@dp.message(Command("admin"))
‎async def admin_dashboard(message: types.Message):
‎    if message.from_user.id != ADMIN_ID:
‎        return # Ignore silently or say unauthorized
‎    
‎    # Mock data - in reality, fetch from Database
‎    total_users = 1250
‎    total_polls = 4320
‎    
‎    dashboard_text = (
‎        "👨‍💻 **Admin Dashboard**\n"
‎        "━━━━━━━━━━━━━━━━━━\n"
‎        f"👥 মোট ব্যবহারকারী: `{total_users}`\n"
‎        f"📊 মোট পোল তৈরি: `{total_polls}`\n"
‎        "⚡ বট স্ট্যাটাস: **Active**\n"
‎        "━━━━━━━━━━━━━━━━━━"
‎    )
‎    await message.answer(dashboard_text, parse_mode="Markdown")
‎
‎# --- Main Polling ---
‎async def main():
‎    print("Bot is starting...")
‎    await dp.start_polling(bot)
‎
‎if __name__ == "__main__":
‎    asyncio.run(main())
