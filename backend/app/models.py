from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class LLMConfig(BaseModel):
    api_key: str
    api_url: str
    model: str
    temperature: Optional[float] = 0.3
    abbr_max_len: int = Field(default=4, ge=1, le=12)


class TextInput(BaseModel):
    type: Literal["text", "file_base64"]
    content: str


class GenerateDDLRequest(BaseModel):
    llm_config: LLMConfig
    word_roots_input: TextInput
    standards_input: TextInput
    description: str
    db_type: Literal["mysql", "postgresql", "oracle"]
    custom_prompt: str = ""
    root_match_priority: Literal["full", "abbr"] = "abbr"
    history_roots: Optional[List[str]] = []
    enable_validation: bool = True


class GenerateDDLResponse(BaseModel):
    code: int
    data: str
    message: str = ""
    extracted_roots: Optional[List[dict]] = []
    violations: Optional[List[dict]] = []


class TestConnectionRequest(BaseModel):
    api_key: str
    api_url: str
    model: str


class TestConnectionResponse(BaseModel):
    code: int
    message: str


class DbConnectionRequest(BaseModel):
    name: str
    db_type: Literal["mysql", "postgresql", "oracle"]
    host: str
    port: int
    database: str
    username: str = ""
    password: Optional[str] = None


class ExecuteDDLRequest(BaseModel):
    connection_id: str


class WordRootItem(BaseModel):
    business_domain: str
    chinese_name: str
    full_root: str
    abbr_root: str
    recommended_type: str


class WordRootsResponse(BaseModel):
    code: int
    data: List[WordRootItem]
    message: str = ""
