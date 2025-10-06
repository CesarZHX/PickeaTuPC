from asyncio import run

from aiohttp import ClientSession

from .models.sercoplus import Sercoplus


async def main() -> None:
    async with ClientSession() as session:
        sercoplus: Sercoplus = Sercoplus(session)
        endpoint: str = "731-arma-tu-pc"
        items = await sercoplus.search(endpoint)
    return print(*items, sep="\n")


if __name__ == "__main__":
    run(main())
