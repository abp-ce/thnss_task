import asyncio
from io import BytesIO

from aiogram import (
    F,
    Router,
    types,
)
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    ContentType,
    Message,
)

import pandas as pd

from technesis.keyboards import to_start_button, upload_button
from technesis.tasks import process_file_data
from technesis.utils import (
    average_price_text,
    save_file,
)

router = Router()


class UploadFileStates(StatesGroup):
    waiting_for_file = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("Ожидание файла прекращено.")
    await message.answer("Нажмите кнопку для загрузки файла:", reply_markup=upload_button)


@router.callback_query(F.data == "upload_file")
async def ask_for_file_upload(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, отправьте файл в этом чате!", reply_markup=to_start_button)
    await state.set_state(UploadFileStates.waiting_for_file)


@router.callback_query(F.data == "to_start")
async def handle_to_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Вы вернулись к началу.\nИспользуйте команду /start.",
    )


@router.message(UploadFileStates.waiting_for_file, F.content_type == ContentType.DOCUMENT)
async def handle_document(message: Message, state: FSMContext):
    from technesis.config import bot

    document = message.document
    file_name = document.file_name

    # Скачиваем файл в память
    file = await bot.download(document)
    file_content = file.getvalue()

    # Читаем содержимое файла
    try:
        data = pd.read_excel(BytesIO(file_content))
        await message.answer(f"Файл '{file_name}' успешно загружен. Содержимое (начало):\n{data.head().to_string()}")
    except Exception as e:
        await message.answer(f"Ошибка при загрузке файла '{file_name}': {e}")
    await state.clear()

    # Сохраняем файл на диск
    await message.answer(save_file(message.from_user.id, file_name, file_content))

    task = asyncio.create_task(process_file_data(data, message.from_user.id))

    try:
        await task
        result = task.result()  # Попытаемся получить результат
        await message.answer(f"Файл '{file_name}': {result}.")
        await message.answer(average_price_text(message.from_user.id))
        await message.answer("Используйте команду /start.")

    except Exception as e:
        await message.answer(
            f"Файл '{file_name}': Ошибка при обработке и сохранении данных в базе данных: {e}."
            "\nИспользуйте команду /start."
        )
