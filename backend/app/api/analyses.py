import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.analysis import Analysis as AnalysisModel
from app.db.models.job import Job
from app.db.session import get_db
from app.schemas.api import (
    Analysis as AnalysisResponse,
    AnalysisDetail,
    AnalysisStatus,
    CreateAnalysisRequest,
)
from app.services.analysis_orchestrator import run_analysis_job


router = APIRouter(
    prefix="/api/analyses",
    tags=["analyses"],
)


ACTIVE_ANALYSIS_STATUSES = ["queued", "running"]


@router.post(
    "",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Nuevo análisis",
)
async def create_analysis(
    payload: CreateAnalysisRequest,
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    target_url = str(payload.targetUrl)

    existing_result = await db.execute(
        select(AnalysisModel).where(
            AnalysisModel.target_url == target_url,
            AnalysisModel.status.in_(ACTIVE_ANALYSIS_STATUSES),
        )
    )
    active_analysis = existing_result.scalar_one_or_none()

    if active_analysis is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ya existe un análisis activo para esta URL. "
                "Espere a que finalice antes de iniciar otro."
            ),
        )

    analysis = AnalysisModel(
        target_url=target_url,
        status="queued",
        current_stage="queued",
        scan_mode="passive",
        created_at=datetime.now(timezone.utc),
    )

    db.add(analysis)

    # Envía el INSERT a PostgreSQL para que analysis.id esté disponible.
    await db.flush()

    job = Job(
        analysis_id=analysis.id,
        status="pending",
        attempts=0,
        available_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    db.add(job)
    await db.commit()

    asyncio.create_task(
        run_analysis_job(
            analysis_id=analysis.id,
            job_id=job.id,
        )
    )

    return AnalysisResponse(
        id=analysis.id,
        targetUrl=analysis.target_url,
        status=AnalysisStatus(analysis.status),
        createdAt=analysis.created_at,
        finishedAt=analysis.finished_at,
    )


@router.get(
    "/{analysisId}",
    response_model=AnalysisDetail,
    status_code=status.HTTP_200_OK,
    summary="Consultar un análisis",
)
async def get_analysis(
    analysisId: UUID,
    db: AsyncSession = Depends(get_db),
) -> AnalysisDetail:
    result = await db.execute(
        select(AnalysisModel).where(
            AnalysisModel.id == analysisId
        )
    )
    analysis = result.scalar_one_or_none()

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "about:blank",
                "title": "Análisis no encontrado",
                "status": 404,
                "detail": f"No existe un análisis con id {analysisId}",
            },
        )

    return AnalysisDetail(
        id=analysis.id,
        targetUrl=analysis.target_url,
        status=AnalysisStatus(analysis.status),
        createdAt=analysis.created_at,
        finishedAt=analysis.finished_at,
        protections=[],
        vulnerabilities=[],
        errorMessage=analysis.error_message,
    )