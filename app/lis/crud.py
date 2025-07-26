from sqlalchemy import select, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.lis.schemas import ItemConditionsSchema, ConditionSchema

from app.db import db_helper, AuthLis, ActiveParse, SkinToParse, ParsedItems


async def check_exist_user_or_not(tg_id: int) -> AuthLis | None:
    async for session in db_helper.get_async_session():
        stmt = select(AuthLis).where(AuthLis.tg_id == tg_id)

        return await session.scalar(statement=stmt)


async def add_lis_auth(
    user_id: int,
    token: str,
    steam_partner: str | None = None,
    steam_token: str | None = None,
) -> AuthLis:
    async for session in db_helper.get_async_session():
        stmt = (
            pg_insert(AuthLis)
            .values(
                tg_id=user_id,
                lis_token=token,
                steam_partner=steam_partner,
                steam_token=steam_token,
            )
            .on_conflict_do_update(
                index_elements=[AuthLis.tg_id],
                set_={
                    "lis_token": token,
                    "steam_partner": steam_partner,
                    "steam_token": steam_token,
                },
            )
            .returning(AuthLis)
        )

        result = await session.execute(statement=stmt)
        await session.commit()

        return result.scalar_one()


async def get_user_parse_model(tg_id: int) -> ActiveParse | None:
    async for session in db_helper.get_async_session():
        stmt = select(ActiveParse).where(ActiveParse.tg_id == tg_id)

        return await session.scalar(statement=stmt)


async def get_items_by_tg_id(tg_id: int) -> list[SkinToParse]:
    async for session in db_helper.get_async_session():
        stmt = select(SkinToParse).where(SkinToParse.tg_id == tg_id)

        result = await session.execute(statement=stmt)
        return result.scalars().all()


async def set_parse_status(tg_id: int, active: bool):
    async for session in db_helper.get_async_session():
        result = await session.execute(
            select(ActiveParse).where(ActiveParse.tg_id == tg_id)
        )
        row = result.scalar_one_or_none()

        if row:
            await session.execute(
                update(ActiveParse)
                .where(ActiveParse.tg_id == tg_id)
                .values(is_active=active)
            )

        else:
            await session.execute(
                insert(ActiveParse).values(tg_id=tg_id, is_active=active)
            )

        await session.commit()


async def get_conditions_for_user(tg_id: int) -> ItemConditionsSchema:
    async for session in db_helper.get_async_session():
        result = await session.execute(
            select(SkinToParse).where(SkinToParse.tg_id == tg_id)
        )
        rows = result.scalars().all()

        conditions = [
            ConditionSchema(
                skin_name=row.skin_name,
                patterns=row.patterns.split(",") if row.patterns else [],
                float_condition=row.float,
                price_condition=row.price,
                ready_to_buy=row.ready_to_buy,
            )
            for row in rows
        ]

        return ItemConditionsSchema(items=conditions)


async def add_item_to_parse(
    tg_id: int,
    skin_name: str,
    autobuy: bool,
    patterns: list[str],
    price: str | None = None,
    float: str | None = None,
) -> tuple[bool, str]:
    patterns_str = (
        ",".join([p.strip() for p in patterns if p.strip()]) if patterns else None
    )

    async for session in db_helper.get_async_session():
        item = SkinToParse(
            tg_id=tg_id,
            skin_name=skin_name,
            ready_to_buy=autobuy,
            patterns=patterns_str,
            float=float,
            price=price,
        )

        session.add(item)
        await session.commit()

        return True, "✅ Предмет успешно добавлен. Хотите добавить ещё один?"


async def delete_items_by_ids(tg_id: int, item_ids: list[int]) -> list[int]:
    async for session in db_helper.get_async_session():
        result = await session.execute(
            select(SkinToParse).where(
                SkinToParse.id.in_(item_ids), SkinToParse.tg_id == tg_id
            )
        )
        items = result.scalars().all()

        deleted_ids = [item.id for item in items]

        for item in items:
            await session.delete(item)

        await session.commit()
        return deleted_ids


async def get_all_active_parse_models() -> list[ActiveParse]:
    async for session in db_helper.get_async_session():
        stmt = select(ActiveParse).where(ActiveParse.is_active == True)

        result = await session.scalars(statement=stmt)
        return result.all()


async def create_record_about_parsed_skin(
    tg_id: int,
    item_data: dict,
    event: str,
    bought_result: dict | None = None,
) -> ParsedItems:
    if bought_result:
        if "error" in bought_result:
            bought_result = False

        elif "data" in bought_result:
            bought_result = True

    async for session in db_helper.get_async_session():
        new_item = ParsedItems(
            tg_id=tg_id,
            skin_name=item_data["name"],
            pattern=item_data["item_paint_seed"],
            item_float=item_data["item_float"],
            price=item_data["price"],
            lis_item_id=item_data["id"],
            unlock_at_lis=item_data["unlock_at"],
            created_at_lis=item_data["created_at"],
            event=event,
            bought_result=bought_result,
        )

        session.add(new_item)
        await session.commit()

        return new_item


async def get_last_parsed_items(tg_id: int, limit: int) -> list[ParsedItems]:
    async for session in db_helper.get_async_session():
        stmt = (
            select(ParsedItems)
            .where(ParsedItems.tg_id == tg_id)
            .order_by(ParsedItems.created_at_lis.desc())
            .limit(limit)
        )

        result = await session.execute(statement=stmt)
        return result.scalars().all()
