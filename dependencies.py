from fastapi import Header, HTTPException
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.account import Account
from typing import Annotated
from config import PROJECT_ID


async def authenticate(authorization: Annotated[str, Header()]) -> tuple[Client, Users]:
    client = Client()
    client.set_endpoint("https://cloud.appwrite.io/v1").set_project(PROJECT_ID).set_jwt(
        authorization.removeprefix("Bearer ")
    )
    account = Account(client)
    try:
        user = account.get()
        return client, user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Unauthorized")
