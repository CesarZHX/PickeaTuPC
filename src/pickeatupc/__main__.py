from asyncio import run

from aiohttp import ClientSession

from .models.sercoplus import Sercoplus


async def main() -> None:
    async with ClientSession() as session:
        sercoplus: Sercoplus = Sercoplus(session)
        items: tuple[str, ...] = await sercoplus.search("RAM")
    return print(*items, sep="\n")


if __name__ == "__main__":
    run(main())
