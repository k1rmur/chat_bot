from vkbottle import Keyboard, KeyboardButtonColor, Text


def general_menu():
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("🌊 О боте"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("🤖 ИИ Собеседник"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("💻 Госуслуги"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("📞 Прием граждан"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("Обратная связь"), color=KeyboardButtonColor.PRIMARY)
    return keyboard


def gosuslugi_menu():
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("Водный реестр"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("Право пользования"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("Договоры"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("Допустимые нормы"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("Земельный участок"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("Назад"), color=KeyboardButtonColor.NEGATIVE)
    return keyboard


def inline_rating_keyboard():
    keyboard = Keyboard(one_time=False, inline=True)
    for i in range(1, 11):
        keyboard.add(Text(str(i)), color=KeyboardButtonColor.SECONDARY)
        if i % 2 == 0:
            keyboard.row()
    return keyboard
