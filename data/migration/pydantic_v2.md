# Pydantic V1 to V2 Migration Guide

## Validators Migration

### Field Validators
In Pydantic v1, field-level validation was performed using the `@validator` decorator.
In Pydantic v2, `@validator` is deprecated and replaced by `@field_validator`.

Key differences:
- `@field_validator` is a class method by default and requires the `@classmethod` decorator.
- The `pre=True` parameter is replaced by `mode='before'`.
- The `always=True` parameter is replaced by `mode='after'`.
- The first argument of the validated method is `cls`, followed by the value `v`.

```python
# Pydantic v1
from pydantic import BaseModel, validator

class UserModel(BaseModel):
    name: str

    @validator("name")
    def validate_name(cls, v):
        return v.title()

# Pydantic v2
from pydantic import BaseModel, field_validator

class UserModel(BaseModel):
    name: str

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.title()
```

### Root Validators
In Pydantic v1, whole-model validation was performed using `@root_validator`.
In Pydantic v2, `@root_validator` is deprecated and replaced by `@model_validator`.

Key differences:
- `@root_validator(pre=True)` is replaced by `@model_validator(mode='before')`. In this mode, the method receives raw input data (usually a `dict`).
- `@root_validator(pre=False)` is replaced by `@model_validator(mode='after')`. In this mode, the method receives `self` (the model instance).

```python
# Pydantic v1
from pydantic import BaseModel, root_validator

class Item(BaseModel):
    price: float
    tax: float

    @root_validator
    def check_totals(cls, values):
        if values.get("tax", 0) > values.get("price", 0):
            raise ValueError("tax cannot exceed price")
        return values

# Pydantic v2
from pydantic import BaseModel, model_validator

class Item(BaseModel):
    price: float
    tax: float

    @model_validator(mode="after")
    def check_totals(self) -> "Item":
        if self.tax > self.price:
            raise ValueError("tax cannot exceed price")
        return self
```

---

## Model Serialization Methods

### dict and json Export
In Pydantic v1, model instances were dumped using `.dict()` and `.json()`.
In Pydantic v2, these methods are deprecated:
- Replace `model.dict()` with `model.model_dump()`.
- Replace `model.json()` with `model.model_dump_json()`.

Supported arguments like `include`, `exclude`, and `by_alias` are retained in `model_dump()`.

### parse_obj and parse_raw Methods
In Pydantic v1, creating a model instance from a raw dictionary or JSON string used `.parse_obj()` and `.parse_raw()`.
In Pydantic v2, these methods are deprecated:
- Replace `Model.parse_obj(data)` with `Model.model_validate(data)`.
- Replace `Model.parse_raw(json_str)` with `Model.model_validate_json(json_str)`.

---

## Configuration and Settings

### Model Config
In Pydantic v1, configuration was defined via an inner `class Config`.
In Pydantic v2, the inner `Config` class is deprecated in favor of the `model_config` attribute using `ConfigDict`.

```python
# Pydantic v1
from pydantic import BaseModel

class Profile(BaseModel):
    username: str

    class Config:
        frozen = True
        extra = "forbid"

# Pydantic v2
from pydantic import BaseModel, ConfigDict

class Profile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    username: str
```

### BaseSettings Package Split
The `BaseSettings` class was completely removed from the core `pydantic` package in v2.
To manage application settings:
1. Install `pydantic-settings` via your package manager.
2. Import `BaseSettings` from `pydantic_settings` instead of `pydantic`.
