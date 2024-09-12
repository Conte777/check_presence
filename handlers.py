from aiogram import Bot, F, Router, types
from aiogram.filters.command import Command

router = Router()
router.message.filter(F.from_user.id.in_([760709790, 378790166]))
routers = [router]

NAMES = {
    "2061148502": "Барбаччи Анастасия",
    "@SOSchlenoSOS": "Батин Платон",
    "@sssaaassshhhkkkooo": "Борисов Александр",
    "855323286": "Быков Денис",
    "@MaxMerzyl": "Голубенко Максим",
    "@Kikaaaaar": "Горбунова Ксения",
    "@zombiksha": "Дерибин Матвей",
    "@Xx_ToRTiK_xX": "Дзикевич Максим",
    "@mentaldevastation": "Ермохин Андрей",
    "810636482": "Занин Никита",
    "@Nek1s": "Иванов Никита",
    "@sqw1zii": "Казанцев Арсений",
    "@sanyakanev": "Канев Александр",
    "378790166": "Колесников Алексей",
    "@nhyseq": "Королёв Олег",
    "@Taroso0": "Кузнецов Александр",
    "@michael_983": "Курохтин Михаил",
    "@Skrea1m": "Лихачёв Алексей",
    "@SonikFerry": "Лучшев Вадим",
    "@twelvy_tg": "Лясин Иван",
    "@Prapor02": "Магомедов Пайзула",
    "@HaroldFromRivia": "Макаров Вячеслав",
    "760709790": "Олейник Данил",
    "@zzbzy": "Пшеничнов Святослав",
    "@Doony_Freeman": "Ребриков Артём",
    "@redlyaguha": "Рыбаченок Вадим",
    "7148607418": "Сафронов Денис",
    "@VovseNeTorch": "Селиверстов Дмитрий",
    "@Tankist_c_Kazahstana": "Сон Владимир",
    "@Yarikash": "Трубников Ярослав",
    "@Nikii963": "Ушакова Ника",
    "@dmitrii_shtrikov": "Штриков Дмитрий",
}
TARGET_CHAT = "-1002183941184_2140"
actual_poll_id = -1


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет, чтобы запустить голосование введи команду /presence")


@router.message(Command("presence"))
async def cmd_presence(message: types.Message, bot: Bot):
    await message.answer("Опрос запущен")
    result = await bot.send_poll(
        "-1002434066039_5",
        question="Присутствие на паре",
        options=["На паре", "Опаздываю", "Отсутствую"],
        is_anonymous=False,
        open_period=600,
    )
    global actual_poll_id
    actual_poll_id = result.poll.id


@router.poll_answer_handler()
async def poll_answer(poll_answer: types.PollAnswer):
    if actual_poll_id != poll_answer.poll_id:
        return
