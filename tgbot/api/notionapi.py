import httpx
import asyncio


integration_token = "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"

database_id = "141996c06b93805f88e3c6944374bcca"

headers = {
    "Authorization": f"Bearer {integration_token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
},

data = {
    "parent": {"type": "database_id", "database_id": database_id},
    "properties": {
        "title" : {
            "type" : "title",
            "title" : 


        }


    }

}
