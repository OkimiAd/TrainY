import googletrans
from aiogram import types, Router, F
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils import markdown
from googletrans import Translator
# from translate import Translator
# from transliterate import translit

import app.data.database as db
import app.keyboards as kb

router = Router()


class DocumentMess:
    type_doc: str = "doc"
    caption: str = ""
    file_id: int

    def __init__(self, f, type_doc, caption):
        self.file_id = f
        self.type_doc = type_doc
        self.caption = caption


class SubscribesFlow(StatesGroup):
    add_sub_direction = State()
    add_sub_company = State()
    delete_sub = State()
    delete_all_sub = State()
    translate = State()


@router.message(Command('translate'))
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SubscribesFlow.translate)


@router.message(SubscribesFlow.translate)
async def subscribe_search(message: types.Message, state: FSMContext):
    translator = Translator()
    translation = translator.translate(message.text, dest = "en")
    # translation = translit(message.text, 'ru', reversed=True)
    print(googletrans.LANGUAGES)
    await message.answer(translation.text)


@router.message(F.text == 'FAQ')
async def on_FAQ(message: types.Message, state: FSMContext):
    await state.clear()

    text = markdown.text(
        "С помощью этих инструментов ты можешь записывать свои собеседования:",
        "\n",
        "*Windows*",
        "Xbox Game Bar",
        "OBS Studio",
        "bandicam",
        "NVIDIA ShadowPlay",
        "\n",
        "*MacOS*",
        "OBS Studio",
        "SurFlex Screen Recorder",
        "\n",
        "*Telegram*",
        "1 \- Создать группу в телеграм на себя одного",
        "2 \- Включить видеовстречу с демонстрацией экрана и там включить запись",
        "Пишет сразу в хорошем разрешение с захватом звука и сохраняет в избранное в самом телеграме",
        sep="\n"
    )

    await message.answer(text, protect_content=True, parse_mode=ParseMode.MARKDOWN_V2)


class CatalogFlow(StatesGroup):
    choose_id_buy = State()
    filter_direction = State()
    filter_company = State()
    choose_id_open = State()


@router.message(F.text == 'Подписка на поиск')
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Это раздел настройки подписки на поиск. Вы можете выбрать компанию и направление которое вас интересует и вы будете получать уведомление о появлении новых записей сразу же как они появятся.",
        protect_content=True, reply_markup=kb.subscribes)


@router.message(F.text == 'Добавить подписку')
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SubscribesFlow.add_sub_direction)
    await message.answer(
        "Какое направление программирования вас интересует",
        protect_content=True, reply_markup=kb.directions)


@router.message(F.text == 'Мои подписки')
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    list_subs = db.get_subscribes_for_user(chat_id=message.chat.id)
    if len(list_subs) == 0:
        await message.answer(
            "Подписок пока нет. Нажмите кнопку \"Добавить подписку\"",
            protect_content=True)
        return

    await message.answer(
        "Если хотите удалить подписку, напишите \n/delete_sub или /delete_sub_all",
        protect_content=True)

    for sub in list_subs:
        await message.answer(
            f'id *{sub[0]}* \- *{sub[3]}* \- *{sub[2]}*',
            protect_content=True)


@router.message(Command('delete_sub'))
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SubscribesFlow.delete_sub)
    await message.answer("Напишите id подписки которую вы хотите удалить")


@router.message(Command('delete_sub_all'))
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SubscribesFlow.delete_all_sub)
    await message.answer("Вы уверены что хотите удалить все подписки? Y/N")


@router.message(SubscribesFlow.delete_sub)
async def filter_direction(message: types.Message, state: FSMContext):
    try:
        db.delete_subscribe(chat_id=message.chat.id, sub_id=int(message.text))
        await message.answer(f'Подписка id {int(message.text)} удалена')
    except:
        await message.answer(f'Введите id(только число)')


@router.message(SubscribesFlow.delete_all_sub)
async def filter_direction(message: types.Message, state: FSMContext):
    if message.text == 'Y':
        db.delete_all_subscribes(chat_id=message.chat.id)
        await message.answer(f'Все подписки удалены')
        await state.clear()
    elif message.text == 'N':
        await message.answer("Возвращение в начало чата", reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer("Y/N?")


@router.message(SubscribesFlow.add_sub_direction)
async def filter_direction(message: types.Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await state.set_state(SubscribesFlow.add_sub_company)
    await message.answer("Какая компания вас интересует?(Англ)", protect_content=True)


@router.message(SubscribesFlow.add_sub_company)
async def filter_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    state_data = await state.get_data()
    db.add_subscribe_search(direction=state_data["direction"],
                            company=state_data["company"], chat_id=message.chat.id)
    await message.answer("Подписка успешно добавлена", protect_content=True, reply_markup=kb.main)
    await state.clear()


@router.message()
async def other(message: types.Message):
    await message.answer("Не понимаю тебя😅", protect_content=True)
