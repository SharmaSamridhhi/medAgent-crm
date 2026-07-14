from unittest.mock import patch

from app.agent.tools.flag_compliance_risks import (
    FlagComplianceRisksInput,
    FlagComplianceRisksOutput,
    flag_compliance_risks,
)
from app.schemas.interaction import ComplianceFlag

_PATCH_TARGET = "app.agent.tools.flag_compliance_risks.extract_structured"

# Realistic pharma rep note fixtures — reusable for the demo video per this
# spec's acceptance criteria.
CLEAN_NOTE = (
    "Met with Dr. Patel, discussed CardioX's approved dosing schedule and "
    "answered her questions about administration timing. She seemed "
    "engaged and receptive."
)
OFF_LABEL_NOTE = (
    "Mentioned that CardioX could also help with weight loss even though "
    "it isn't approved for that, and suggested she consider it for "
    "patients looking to shed pounds."
)
ADVERSE_EVENT_NOTE = (
    "She mentioned one of her patients on CardioX developed a rash and "
    "had to stop taking it after a few days."
)


def test_flag_compliance_risks_clean_text_returns_no_flags() -> None:
    with patch(_PATCH_TARGET, return_value=FlagComplianceRisksOutput(flags=[])):
        result = flag_compliance_risks(FlagComplianceRisksInput(text=CLEAN_NOTE))

    assert result.flags == []


def test_flag_compliance_risks_off_label_mention() -> None:
    canned = FlagComplianceRisksOutput(
        flags=[
            ComplianceFlag(
                category="off_label_claim",
                excerpt="could also help with weight loss",
                rationale="Suggests an unapproved indication.",
            )
        ]
    )

    with patch(_PATCH_TARGET, return_value=canned):
        result = flag_compliance_risks(FlagComplianceRisksInput(text=OFF_LABEL_NOTE))

    assert len(result.flags) == 1
    assert result.flags[0].category == "off_label_claim"


def test_flag_compliance_risks_adverse_event_mention() -> None:
    canned = FlagComplianceRisksOutput(
        flags=[
            ComplianceFlag(
                category="adverse_event_mention",
                excerpt="developed a rash and had to stop taking it",
                rationale="Possible adverse event requiring AE reporting review.",
            )
        ]
    )

    with patch(_PATCH_TARGET, return_value=canned):
        result = flag_compliance_risks(
            FlagComplianceRisksInput(text=ADVERSE_EVENT_NOTE)
        )

    assert len(result.flags) == 1
    assert result.flags[0].category == "adverse_event_mention"


def test_flag_compliance_risks_empty_text_skips_llm_call() -> None:
    with patch(_PATCH_TARGET) as mock_extract:
        result = flag_compliance_risks(FlagComplianceRisksInput(text="   "))

    assert result.flags == []
    mock_extract.assert_not_called()
