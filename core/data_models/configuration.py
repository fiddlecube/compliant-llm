from typing import List, Optional, Dict, Any
from pydantic import BaseModel, model_validator


class OutputPath(BaseModel):
    path: str
    filename: str


class ProviderSettings(BaseModel):
    provider_name: str
    api_key: str
    temperature: float
    timeout: int


class OrchestratorConfig(BaseModel):
    prompt: str
    strategies: List[str]
    provider_name: str
    output_path: OutputPath
    provider_config: ProviderSettings


class PromptConfiguration(BaseModel):
    content: Optional[str]
    # [WIP] future support if needed
    # variables: Optional[Dict[str, Any]]
    # file: Optional[str]
    # source: Optional[str]
    # source_id: Optional[str]
    # source_config: Optional[PromptSource]
    # template: Optional[str]


class StrategyConfiguration(BaseModel):
    name: str
    enabled: bool
    description: Optional[str]


class ProviderConfiguration(BaseModel):
    name: str
    model: str
    fallbacks: List[str]
    timeout: int
    max_retries: int
    temperature: float


class OutputConfiguration(BaseModel):
    format: str
    path: str
    filename: str
    include_prompts: bool
    include_responses: bool


class FeaturesConfiguration(BaseModel):
    parallel_testing: bool
    max_threads: int
    eval_metrics: List[str]


class BlackboxConfiguration(BaseModel):
    enabled: bool
    api_url: str
    api_key: str
    headers: Dict[str, Any]
    payload: List[Dict[str, Any]]


class AppConfiguration(BaseModel):
    name: str
    description: str
    version: str
    prompt: PromptConfiguration
    strategies: List[StrategyConfiguration]
    provider: ProviderConfiguration
    output: OutputConfiguration
    features: FeaturesConfiguration
    blackbox: BlackboxConfiguration

    @model_validator(mode="before")
    def check_prompt_source(cls, values):
        prompt = values.get('prompt')
        if not any([prompt.content, prompt.file, prompt.source, prompt.template]):
            raise ValueError('Prompt must include content, file, source, or template')
        return values

# Usage example:
# import yaml
# from pathlib import Path
# raw = yaml.safe_load(Path('config.yaml').read_text())
# cfg = AppConfig(**raw)
# print(cfg.json(indent=2))
