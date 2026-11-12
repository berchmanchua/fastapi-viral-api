from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services.item_service import ItemService
from app.api.dependencies import get_item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=Item, status_code=201)
async def create_item(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service),
):
    return await service.create_and_cache_item(item)


@router.get("/", response_model=List[Item])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    platform: Optional[str] = Query(None, max_length=50),
    service: ItemService = Depends(get_item_service),
):
    return await service.list_items(skip=skip, limit=limit, platform=platform)


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
):
    item = await service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    service: ItemService = Depends(get_item_service),
):
    updated = await service.update_and_cache_item(item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
):
    deleted = await service.soft_delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Null or item not found")
    return Response(status_code=204)
