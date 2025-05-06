from aiogram.fsm.state import StatesGroup, State


class AuthStates(StatesGroup):
    waiting_for_token = State()


class SearchForSkinStates(StatesGroup):
    lis_token = State()
    waiting_for_skin_name = State()
    waiting_for_optional_search_params = State()


class ParseStates(StatesGroup):
    active_parse_action = State()
    confirm_start_parse = State()
    ask_to_start_first_parse = State()

    add_item_name = State()
    add_item_float = State()
    add_item_patterns = State()
    confirm_add_another = State()
