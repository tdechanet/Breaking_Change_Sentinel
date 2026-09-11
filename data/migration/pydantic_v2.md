# Pydantic V1 to V2 Migration Guide

## Validators Migration

### Field Validators
In Pydantic v1, field validation was performed using the `@validator` decorator.
In Pydantic v2, `@validator` is deprecated and replaced by `@field_validator`.

Key differences:
- `@field_validator` is a class method by default and requires the `@classmethod` decorator.
- The `pre=True` parameter is replaced by `mode='before'`.
- The `always=True` parameter is replaced by `mode='after'`.

Example Migration:
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
