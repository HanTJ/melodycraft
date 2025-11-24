from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="사용자 프롬프트")
    measures: int = Field(16, ge=2, le=64, description="생성할 마디 수")
    seed: Optional[int] = Field(None, description="재현 가능한 결과를 위한 시드값")
    instruments: Optional[List[str]] = Field(None, description="생성할 악기 파트 목록")


class GenerateResponse(BaseModel):
    abc: str
    tempo: int
    meter: str
    key: str
    mood: str
    highlights: List[str]
    parts: List[dict]
