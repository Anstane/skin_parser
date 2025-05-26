from aiogram.fsm.state import StatesGroup, State


class AuthStates(StatesGroup):
    waiting_for_token = State()
    confirm_overwrite = State()
    confirm_trade_url_add = State()
    waiting_for_trade_url = State()


class SearchForSkinStates(StatesGroup):
    lis_token = State()
    waiting_for_skin_name = State()
    waiting_for_optional_search_params = State()


class ParseStates(StatesGroup):
    active_parse_action = State()
    confirm_start_parse = State()
    ask_to_start_first_parse = State()

    add_item_name = State()
    add_item_price = State()
    add_item_float = State()
    add_item_patterns = State()
    confirm_add_another = State()

    delete_item_id = State()


class ShowParsedStates(StatesGroup):
    amount_of_records = State()


class BuyItemStates(StatesGroup):
    id_of_item = State()


class CheckAvailabilityStates(StatesGroup):
    id_of_item = State()
