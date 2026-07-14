from pydantic import BaseModel

from app.agent.tools._extraction import extract_structured
from app.schemas.interaction import ComplianceFlag

_FLAG_PROMPT = (
    "You are a pharmaceutical compliance reviewer screening a sales rep's "
    "call notes for regulatory risk. Flag ONLY genuine concerns; if the "
    "text is clean, return an empty list — do not flag ordinary sales "
    "conversation, sentiment, or scheduling details.\n\n"
    "Categories:\n"
    "- off_label_claim: discussing a product for a use not in its "
    "approved label/indication.\n"
    "- unsubstantiated_claim: an efficacy or safety claim stated as flat "
    "fact without qualification (e.g. absolute superiority, guaranteed "
    "outcomes) beyond what's normally supportable.\n"
    "- adverse_event_mention: any mention of a patient experiencing a "
    "side effect, complication, or negative health event tied to a "
    "product — these carry separate AE reporting obligations regardless "
    "of severity.\n"
    "- other: a genuine compliance concern that doesn't fit the above; "
    "give your own rationale.\n\n"
    "For each flag, quote the exact excerpt that concerned you and give a "
    "short rationale.\n\n"
    "Text to review:\n{text}"
)


class FlagComplianceRisksInput(BaseModel):
    text: str


class FlagComplianceRisksOutput(BaseModel):
    flags: list[ComplianceFlag] = []


def flag_compliance_risks(
    payload: FlagComplianceRisksInput,
) -> FlagComplianceRisksOutput:
    if not payload.text.strip():
        return FlagComplianceRisksOutput(flags=[])
    return extract_structured(
        _FLAG_PROMPT.format(text=payload.text), FlagComplianceRisksOutput
    )
