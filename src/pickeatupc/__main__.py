from asyncio import run

from aiohttp import ClientSession

from .sercoplus import get_sercoplus_items


async def main() -> None:
    async with ClientSession() as session:
        items = await get_sercoplus_items(session, endpoint="731-arma-tu-pc")
    return print(*items, sep="\n")


if __name__ == "__main__":
    run(main())
