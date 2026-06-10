from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.infrastructure.database.models.product_model import ProductModel
from app.presentation.schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    # Получаем все доступные товары из БД
    result = await db.execute(select(ProductModel).where(ProductModel.is_available == True))
    products = result.scalars().all()
    return products