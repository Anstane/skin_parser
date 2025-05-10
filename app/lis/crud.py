from sqlalchemy import select, insert, update

from app.lis.schemas import ItemConditionsSchema, ConditionSchema

from app.db import db_helper, AuthLis, ActiveParse, SkinToParse


async def check_exist_user_or_not(tg_id: int) -> AuthLis | None:
    async for session in db_helper.get_async_session():
        stmt = select(AuthLis).where(AuthLis.tg_id == tg_id)

        return await session.scalar(statement=stmt)


async def add_lis_auth(user_id: int, token: str) -> AuthLis:
    async for session in db_helper.get_async_session():
        new_auth = AuthLis(tg_id=user_id, lis_token=token)

        session.add(new_auth)
        await session.commit()

        return new_auth


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
            )
            for row in rows
        ]

        return ItemConditionsSchema(items=conditions)


async def add_item_to_parse(
    tg_id: int,
    skin_name: str,
    patterns: list[str],
    float: str | None = None,
) -> tuple[bool, str]:
    patterns_str = (
        ",".join([p.strip() for p in patterns if p.strip()]) if patterns else None
    )

    async for session in db_helper.get_async_session():
        # stmt = select(SkinToParse).where(
        #     SkinToParse.tg_id == tg_id,
        #     SkinToParse.skin_name == skin_name,
        # )
        # existed_item = await session.scalar(statement=stmt)

        # if existed_item:
        #     return (
        #         False,
        #         "❗ Такой предмет уже есть в списке для парсинга. Укажите название повторно.",
        #     )

        item = SkinToParse(
            tg_id=tg_id,
            skin_name=skin_name,
            patterns=patterns_str,
            float=float,
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
