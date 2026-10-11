from uuid import UUID

DEMO_USER=UUID("11111111-1111-1111-1111-111111111111")

async def get_current_user()-> UUID:
    return DEMO_USER

