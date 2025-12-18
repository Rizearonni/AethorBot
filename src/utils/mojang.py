import aiohttp

API_URL = "https://api.mojang.com/users/profiles/minecraft/"


async def fetch_uuid(name: str) -> tuple[str | None, str | None]:
    name = name.strip()
    if not name:
        return None, None
    url = API_URL + name
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as resp:
            if resp.status == 204 or resp.status == 404:
                return None, None
            resp.raise_for_status()
            data = await resp.json()
            # data: {"id": "uuid_no_dashes", "name": "ExactName"}
            uuid = data.get("id")
            exact = data.get("name")
            return (uuid, exact)
