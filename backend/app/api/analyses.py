from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.api import (
    Analysis,
    AnalysisDetail,
    AnalysisStatus,
    CreateAnalysisRequest,
)

router = APIRouter(
    prefix="/api/analyses",
    tags=["analyses"],
)


@router.post(
    "",
    response_model=Analysis,
    status_code=status.HTTP_201_CREATED,
    summary="Nuevo analisis",
)
async def create_analysis(payload: CreateAnalysisRequest) -> Analysis:
    now = datetime.now(timezone.utc)

    return Analysis(
        id=uuid4(),
        targetUrl=payload.targetUrl,
        status=AnalysisStatus.pending,
        createdAt=now,
        finishedAt=None,
    )

@router.get(
    "/{analysisId}",
    response_model=AnalysisDetail,
    status_code=status.HTTP_200_OK,
    summary="Consultar  un análisis",
)
async def get_analysis(analysisId: UUID) -> AnalysisDetail:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "type": "about:blank",
            "title": "Análisis no encontrado",
            "status": 404,
            "detail": f"No existe un análisis con id {analysisId}",
        },
    )