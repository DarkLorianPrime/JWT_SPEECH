from uuid import UUID

import backoff
import httpx


@backoff.on_exception(
    backoff.expo,
    (httpx.RequestError, httpx.HTTPStatusError),
    max_tries=5,
    jitter=backoff.full_jitter,
)
async def get_roles(user_id: UUID, headers):
    print(headers)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://auth-service:8000/api/v1/roles/{user_id}",
            headers={"Authorization": headers["authorization"]},
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise httpx.HTTPStatusError(f"Error: {response.status_code}")
