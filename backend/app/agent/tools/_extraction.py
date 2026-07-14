from typing import TypeVar

from pydantic import BaseModel

from app.agent.llm import get_heavy_llm

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def extract_structured(prompt: str, schema: type[SchemaT]) -> SchemaT:
    """Run one structured-output extraction call against GROQ_MODEL_HEAVY."""
    llm = get_heavy_llm().with_structured_output(schema)
    result = llm.invoke(prompt)
    assert isinstance(result, schema)
    return result
