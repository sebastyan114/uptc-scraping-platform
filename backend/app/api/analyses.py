import asyncio
from datetime import datetime, timezone
from uuid import UUID



from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.db.session import get_db
from app.db.models.analysis import Analysis as AnalysisORM
from app.db.models.finding import Finding
from app.db.models.protection import Protection
from app.db.models.scan_log import ScanLog


from sqlalchemy import select


from app.db.models.analysis import Analysis as AnalysisModel
from app.db.models.job import Job


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

async def create_analysis(payload: CreateAnalysisRequest,db: AsyncSession = Depends(get_db),) -> AnalysisResponse:
    target_url = str(payload.targetUrl)

    existing_result = await db.execute(
            select(AnalysisModel).where(
                AnalysisModel.target_url == target_url,
                AnalysisModel.status.in_(ACTIVE_ANALYSIS_STATUSES),
            )
    )
    now = datetime.now(timezone.utc)

#Construit una fila del postgres convertir la url al texto que valida
    analysis = AnalysisORM(
    
    target_url=str(payload.targetUrl),
    status=AnalysisStatus.pending.value, #Guardar la columna de texto en pending
    created_at=now,
    finished_at=None,
    scan_mode="passive",
)

    db.add(analysis)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(analysis)

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


     "",
    status_code=status.HTTP_200_OK,
    summary="Consultar historial de analisis",
)

async def list_analyses(
    page:int = Query(default=1,ge=1),
    page_size: int = Query(default=20,ge=1,le=100),
    db: AsyncSession=Depends(get_db),
    
):
    
    total = await db.scalar(
        select(func.count())
        .select_from(AnalysisORM)
    )

    result = await db.execute(
    select(AnalysisORM)
    .order_by(AnalysisORM.created_at.desc())
    .offset((page - 1) * page_size)
    .limit(page_size)
    ) 

    analyses=result.scalars().all()

    return{
        "items":[
            {
                "id":item.id,
                "targetUrl": item.target_url,
                "status":item.status,
                "createdAt":item.created_at,
                "finishedAt": item.finished_at,
            }
            for item in analyses
        ],
        "page":page,
        "pageSize":page_size,
        "total":total or 0,
    }
@router.get(
    "/{analysisId}/results",
    response_model=AnalysisDetail,
    status_code=status.HTTP_200_OK,
    summary="Consultar resultados de un análisis",
)
@router.get(
    "/{analysisId}",
    response_model=AnalysisDetail,
    status_code=status.HTTP_200_OK,

    summary="Consultar un analisis",
)

async def get_analysis(analysisId: UUID,
    db: AsyncSession = Depends(get_db),) -> AnalysisDetail:
    result=await db.execute(
        select(AnalysisORM).options(
            selectinload(AnalysisORM.findings),
            selectinload(AnalysisORM.protections),
            selectinload(AnalysisORM.scan_logs),
        )
        .where(AnalysisORM.id==analysisId)
    )
    analysis=result.scalar_one_or_none()
    
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
        status=analysis.status,  #garantizar que se cumpla el contrato
        createdAt=analysis.created_at,
        finishedAt=analysis.finished_at,
        
        protections=[
        {
            "type": protection.protection_type,
            "details": protection.details,
        }
        for protection in analysis.protections
        ],
        vulnerabilities=[
        {
            "type": finding.finding_type,
            "severity": finding.severity,
            "description": finding.description,
        }
        for finding in analysis.findings
    ],
    errorMessage=analysis.error_message,
    )

    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "type": "about:blank",
            "title": "Análisis no encontrado",
            "status": 404,
            "detail": f"No existe un análisis con id {analysisId}",
        },
)