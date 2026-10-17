from fastapi import APIRouter, Depends
from app.infrastructure.web.dependencies import (
    get_advance_order,
    get_approve_order,
    get_kds_orders,
    get_reject_order,
    get_restaurant_id,
    require_api_key,
)
from app.infrastructure.web.schemas import RejectBody, order_to_dict
from app.use_cases.advance_order import AdvanceOrder
from app.use_cases.approve_order import ApproveOrder
from app.use_cases.get_kds_order import GetKdsOrders
from app.use_cases.reject_order import RejectOrder

router = APIRouter(prefix="/api", dependencies=[Depends(require_api_key)])




@router.get("/orders")
def list_orders(
    restaurant_id: str = Depends(get_restaurant_id),
    use_case: GetKdsOrders = Depends(get_kds_orders),
):
    orders = use_case.execute(restaurant_id)
    return [order_to_dict(order) for order in orders]


# approve, reject, advance: اكتبهم بنفسك
@router.post("/orders/{order_id}/approve")
def approve(order_id: str,
            restaurant_id: str = Depends(get_restaurant_id),
            use_case: ApproveOrder = Depends(get_approve_order)
):
    order = use_case.execute(restaurant_id, order_id)
    return order

@router.post("/orders/{order_id}/reject")
def reject(
    order_id: str,
    body: RejectBody,
    restaurant_id: str = Depends(get_restaurant_id),
    use_case: RejectOrder = Depends(get_reject_order),
):
    order = use_case.execute(restaurant_id, order_id, body.reason)
    return order_to_dict(order)


@router.post("/orders/{order_id}/advance")
def advance(
    order_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    use_case: AdvanceOrder = Depends(get_advance_order),
):
    order = use_case.execute(restaurant_id, order_id)
    return order_to_dict(order)