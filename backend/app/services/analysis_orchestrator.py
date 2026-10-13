import asyncio
from datetime import datetime,timezone
from uuid import UUID


from sqlalchemy import select

from app.db.models.analysis import Analysis
from app.db.models.job import Job
from app.db.session import AsyncSessionLocal

#Lista de etapas simladas
STAGES=[
    "scraping",
    "protections",
    "nuclei",
    "vectorizing",
]

async def run_analysis_job(
    analysis_id:UUID,
    job_id:UUID,

)->None:
    async with AsyncSessionLocal() as db:
        analysis_result= await db.execute(
            select(Analysis).where(Analysis.id==analysis_id)
        )
        analysis=analysis_result.scalar_one_or_none() #Se busca analisis por su ID
        job_result=await db.execute(
            select(Job).where(Job.id==job_id)
        )
        job=job_result.scalar_one_or_none()  #Busca el trabajo asociado al analisis

        if analysis is None or job is None:
            return

        try:
            analysis.status="running"
            analysis.current_stage="scraping"

            job.status="running"
            job.started_at=datetime.now(timezone.utc)
            job.attempts +=1

            await db.commit()

            for stage in STAGES:
                analysis.current_stage=stage
                await db.commit()
                await asyncio.sleep(2) #Se espera reemplazar por llamadas reales
            analysis.status="completed"
            analysis.current_stage="completed"
            analysis.finished_at=datetime.now(timezone.utc)
            job.status="completed"
            job.finished_at=datetime.now(timezone.utc)

            await db.commit()

        except Exception as error:
            analysis.status="failed"
            analysis.current_stage="failed"
            analysis.error_message=str(error)
            analysis.finished_at=datetime.now(timezone.utc)

            job.status = "failed"
            job.last_error = str(error)
            job.finished_at = datetime.now(timezone.utc)

            await db.commit()