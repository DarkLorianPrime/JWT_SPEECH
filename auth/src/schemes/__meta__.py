import json

from pydantic import BaseModel
from starlette.requests import Request


class BodyModel(BaseModel):
    @classmethod
    async def as_form(cls, request: Request) -> 'BodyModel':
        body = await request.body()

        content_type = request.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {}
        else:
            form_data = await request.form()
            data = dict(form_data)

        return cls(**data)
