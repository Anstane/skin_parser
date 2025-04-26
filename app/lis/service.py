import httpx


async def get_user_balance(lis_token: str) -> dict:
    url = "https://api.lis-skins.com/v1/user/balance"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {lis_token}",
    }

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(url=url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("data", {})

        else:
            return {"error": "Ошибка при получении баланса!"}


async def send_request_for_skins(data: dict, lis_token: str) -> dict:
    base_url = "https://api.lis-skins.com/v1/market/search"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {lis_token}",
    }

    data["game"] = "csgo"

    query_parts = []
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                query_parts.append(f"{key}={item}")
        else:
            query_parts.append(f"{key}={value}")

    query_string = "&".join(query_parts)
    full_url = f"{base_url}?{query_string}"

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            url=full_url,
            headers=headers,
        )
        return response.json()
