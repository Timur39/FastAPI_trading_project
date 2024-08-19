from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from operations.models import operation
from operations.schemas import OperationCreate
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/operations",
    tags=["Operation"]
)


@router.get('/all_operations')
@cache(expire=30)
async def get_all_operations(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(operation)
        result = await session.execute(query)
        data = result.all()
        return {
            "status": "success",
            "data": [i._asdict() for i in data],
            "details": None
        }
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": str(e)
        })


@router.get("")
async def get_specific_operations(operation_type: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(operation).where(operation.c.type == operation_type)
        result = await session.execute(query)
        data = result.all()
        return {
            "status": "success",
            "data": list(map(lambda x: x._asdict(), data)),
            "details": None
        }
    except Exception as e:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": str(e)
        })


@router.post("")
async def add_specific_operations(new_operation: OperationCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(operation).values(**new_operation.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}
