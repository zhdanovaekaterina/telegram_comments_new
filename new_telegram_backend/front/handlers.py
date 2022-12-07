from aiogram import Router
from magic_filter import F

router = Router()
router.message.filter(F.chat.type == "private")


def your_user_id(id):
    return f'Ваш ID пользователя Телеграмм: {id}'


@router.message(commands=['my_id'])
async def info_from_base(message):
    await message.answer(your_user_id(message.from_user.id))
