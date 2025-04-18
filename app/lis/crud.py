from sqlalchemy import select

from app.db import db_helper, AuthLis


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
