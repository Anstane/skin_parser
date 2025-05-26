SKIN_NAME_INPUT_PROMPT = (
    "🎯 <b>Введите точное название скина</b>, включая качество в <b>круглых скобках</b> в конце.\n\n"
    "📌 <b>Формат:</b>\n"
    "— Указывайте <b>качество</b> скина (Factory New, Minimal Wear, Field-Tested, Well-Worn, Battle-Scarred).\n"
    "— Для <b>StatTrak™</b> оружия — добавьте <code>StatTrak™</code> в начале.\n"
    "— Для <b>ножей</b> и <b>перчаток</b> — добавьте <code>★</code> в начале.\n"
    "— Для <b>Souvenir</b> скинов — добавьте <code>Souvenir</code> в начале.\n"
    "— Для <b>обычных предметов</b> — просто укажите полное название, без дополнительных параметров (float и т.п.).\n\n"
    "🧪 <b>Примеры корректных названий:</b>\n"
    "- <code>AK-47 | Aquamarine Revenge (Battle-Scarred)</code>\n"
    "- <code>StatTrak™ USP-S | Blood Tiger (Factory New)</code>\n"
    "- <code>★ StatTrak™ Karambit | Crimson Web (Battle-Scarred)</code>\n"
    "- <code>Souvenir M4A1-S | Knight (Minimal Wear)</code>\n"
    "- <code>Fever Case</code>\n\n"
    "⏭ Если хотите пропустить указание названия, нажмите кнопку <b>Skip</b>."
)


JSON_SEARCH_PROMPT = (
    "📦 <b>Дополнительные параметры поиска</b>\n\n"
    "<b>Пример:</b>\n"
    "<pre>{\n"
    '  "float_from": 0.0,\n'
    '  "float_to": 1.0,\n'
    '  "only_unlocked": 1,\n'
    '  "price_from": 10,\n'
    '  "price_to": 200,\n'
    '  "sort_by": "oldest"\n'
    "}</pre>\n\n"
    "<i>Поля можно указывать частично.</i>\n\n"
    "Допустимые значения для <b>sort_by</b>:\n"
    "<code>oldest</code>, <code>newest</code>, <code>lowest_price</code>, <code>highest_price</code>"
)


USD_TO_RUB = 80.0

MAX_MESSAGE_LENGTH = 4096
