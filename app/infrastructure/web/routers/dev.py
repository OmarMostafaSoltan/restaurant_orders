from fastapi import APIRouter, Depends
from app.infrastructure.web.schemas import DevMessage
from app.domain.entities.customer import CustomerRef
from app.infrastructure.web.dependencies import (
    get_process_customer_message,
    get_restaurant_id,
    require_api_key,
)
from app.use_cases.process_customer_message import ProcessCustomerMessage

router = APIRouter(prefix="/dev", dependencies=[Depends(require_api_key)])




@router.post("/message")
def dev_message(
    body: DevMessage,
    restaurant_id: str = Depends(get_restaurant_id),
    use_case: ProcessCustomerMessage = Depends(get_process_customer_message),
):
    # 1. ابني CustomerRef من body.channel و body.customer_id
    # 2. نادي use_case.execute(restaurant_id, customer, body.text)
    # 3. ارجع {"reply": الرد}
    customer = CustomerRef(channel=body.channel, external_id=body.customer_id)
    reply = use_case.execute(restaurant_id, customer, body.text)
    return {"reply": reply}