import httpx


async def post(url: str, **kwargs):
    async with httpx.AsyncClient() as client:
        return await client.post(url, **kwargs)
