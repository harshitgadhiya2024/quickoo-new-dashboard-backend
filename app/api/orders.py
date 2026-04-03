from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.schemas.order import OrderCreateRequest, OrderResponse, OrderUpdateRequest
from app.services.mail_service import (
    send_order_confirmation_to_customer,
    send_order_created_email,
)
from app.services.order_service import create_order, get_all_orders, update_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_api(
    payload: OrderCreateRequest, background_tasks: BackgroundTasks
) -> OrderResponse:
    created = await create_order(payload)
    order_payload = created.model_dump(by_alias=True, mode="python")
    background_tasks.add_task(send_order_created_email, order_payload)
    background_tasks.add_task(send_order_confirmation_to_customer, order_payload)
    return created


@router.get("", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
async def get_all_orders_api() -> list[OrderResponse]:
    return await get_all_orders()


@router.put("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def update_order_api(order_id: str, payload: OrderUpdateRequest) -> OrderResponse:
    try:
        return await update_order(order_id, payload)
    except ValueError as exc:
        message = str(exc)
        code = (
            status.HTTP_400_BAD_REQUEST
            if message == "At least one field is required for update."
            else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=message) from exc
