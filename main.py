import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.client.default import DefaultBotProperties

# Token Railway'dagi Environment Variables'dan olinadi
API_TOKEN = os.getenv("API_TOKEN")

# Token mavjudligini tekshirish
if not API_TOKEN:
    raise ValueError("API_TOKEN topilmadi. Railway'dagi Environment Variables'ga qo‘shing.")

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Xizmatlar ro'yxati
services = [
    "Uy tozalash", "Supurish", "Bolalarni qarovchi", "Yuk tashish",
    "Quruvchi", "G'isht terish", "Santexnik", "Oboy yopishtirish",
    "Bo'yovchi (malyar)", "Gipskartonchi"
]

# Menyular
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨‍🔧 Ishchi topish"), KeyboardButton(text="🔧 Ishchi sifatida qo‘shilish")]
    ],
    resize_keyboard=True
)

back_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Bosh menyu")]],
    resize_keyboard=True
)

def service_menu():
    builder = ReplyKeyboardBuilder()
    for s in services:
        builder.add(KeyboardButton(text=s))
    builder.add(KeyboardButton(text="🔙 Bosh menyu"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Holatlar
class RegisterWorker(StatesGroup):
    waiting_for_service = State()
    waiting_for_name = State()
    waiting_for_phone = State()

class FindWorker(StatesGroup):
    choosing_service = State()

# START
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Assalomu alaykum! Quyidagilardan birini tanlang:", reply_markup=main_menu)

# Bosh menyuga qaytish
@dp.message(StateFilter("*"), F.text == "🔙 Bosh menyu")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyuga qaytdingiz:", reply_markup=main_menu)

# Ishchi sifatida qo‘shilish
@dp.message(F.text == "🔧 Ishchi sifatida qo‘shilish")
async def start_register_worker(message: types.Message, state: FSMContext):
    await state.set_state(RegisterWorker.waiting_for_service)
    await message.answer("Qaysi xizmatni ko‘rsatasiz?", reply_markup=service_menu())

@dp.message(RegisterWorker.waiting_for_service)
async def get_service(message: types.Message, state: FSMContext):
    if message.text not in services:
        await message.answer("Iltimos, xizmat turini menyudan tanlang.", reply_markup=service_menu())
        return
    await state.update_data(service=message.text)
    await state.set_state(RegisterWorker.waiting_for_name)
    await message.answer("Ismingizni kiriting:", reply_markup=back_menu)

@dp.message(RegisterWorker.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegisterWorker.waiting_for_phone)
    await message.answer("Telefon raqamingizni kiriting:", reply_markup=back_menu)

@dp.message(RegisterWorker.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    service = data.get("service")
    name = data.get("name")
    phone = message.text.strip()

    with open("ishchilar.txt", "a", encoding="utf-8") as f:
        f.write(f"{service} | {name} | {phone}\n")

    await message.answer("✅ Ma'lumotlaringiz saqlandi. Rahmat!", reply_markup=main_menu)
    await state.clear()

# Ishchi topish
@dp.message(F.text == "👨‍🔧 Ishchi topish")
async def find_worker(message: types.Message, state: FSMContext):
    await state.set_state(FindWorker.choosing_service)
    await message.answer("Qanday xizmatga ishchi kerak?", reply_markup=service_menu())

@dp.message(FindWorker.choosing_service)
async def show_workers(message: types.Message, state: FSMContext):
    if message.text not in services:
        await message.answer("Iltimos, xizmat turini tanlang.", reply_markup=service_menu())
        return
    service = message.text
    result = []

    try:
        with open("ishchilar.txt", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(service):
                    result.append(line.strip())
    except FileNotFoundError:
        pass

    if result:
        await message.answer(f"<b>{service}</b> bo‘yicha ishchilar:\n\n" + "\n\n".join(result), reply_markup=main_menu)
    else:
        await message.answer("❌ Bu xizmat bo‘yicha ishchilar topilmadi.", reply_markup=main_menu)

    await state.clear()

# Notanish xabarlar
@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("Iltimos, menyudan birini tanlang.", reply_markup=main_menu)

# MAIN — Railway uchun muhim
async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Pollingda xatolik: {e}")

if __name__ == "__main__":
    asyncio.run(main())
