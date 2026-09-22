from pydantic import AnyHttpUrl, BaseModel


class CreateAnalysisRequest(BaseModel): #crea el modelo que representara el json que recibira el json
    targetUrl: AnyHttpUrl