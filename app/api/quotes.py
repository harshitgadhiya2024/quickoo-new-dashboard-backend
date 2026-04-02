from fastapi import APIRouter, status

from app.schemas.quote import QuoteRequest, QuoteResponse
from app.services.quote_service import generate_quotes

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post(
    "/get-quotes",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get price quotes for a route (London / UK coordinates)",
)
async def get_quotes(payload: QuoteRequest) -> QuoteResponse:
    return await generate_quotes(payload)
