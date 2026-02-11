from pydantic import BaseModel, ValidationError, Field, root_validator
from typing import List, Optional, Tuple, Dict, Any


class FeatureSpec(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    api: Optional[Dict[str, Any]] = None


class ProductSpec(BaseModel):
    name: str
    description: Optional[str] = ""
    features: List[FeatureSpec] = Field(default_factory=list)
    integrations: Optional[List[str]] = Field(default_factory=list)


class PageSpec(BaseModel):
    id: str
    route: str
    title: str
    components: List[str] = Field(default_factory=list)


class DesignSpec(BaseModel):
    name: str
    description: Optional[str] = ""
    pages: List[PageSpec] = Field(default_factory=list)
    tokens: Optional[Dict[str, Any]] = Field(default_factory=dict)


def validate_product_spec(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate product spec dict against ProductSpec model.

    Returns (is_valid, errors)
    """
    try:
        ProductSpec(**spec)
        return True, []
    except ValidationError as e:
        return False, [err['msg'] for err in e.errors()]


def validate_design_spec(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate design spec dict against DesignSpec model.

    Returns (is_valid, errors)
    """
    try:
        DesignSpec(**spec)
        return True, []
    except ValidationError as e:
        return False, [err['msg'] for err in e.errors()]
