import uuid
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agent.tools.edit_interaction import EditInteractionInput, edit_interaction
from app.agent.tools.flag_compliance_risks import (
    FlagComplianceRisksInput,
    flag_compliance_risks,
)
from app.agent.tools.log_interaction import LogInteractionInput, log_interaction
from app.agent.tools.retrieve_hcp_history import (
    RetrieveHCPHistoryInput,
    retrieve_hcp_history,
)
from app.agent.tools.schedule_follow_up import (
    ScheduleFollowUpInput,
    schedule_follow_up,
)

# LLM-facing args schemas — deliberately narrower than each tool's full
# Pydantic input model. `rep_id` and `db` are never something the LLM
# should supply: `rep_id` is fixed per session (this build is single-rep,
# see steering/04-architecture-tech-stack.md) and `db` isn't LLM-visible
# data at all. Both are bound via closure in `build_tools` below instead.


class _LogInteractionArgs(BaseModel):
    rep_utterance: str = Field(
        description="The rep's own free-form description of what happened"
    )
    hcp_id: uuid.UUID | None = Field(
        default=None,
        description="The HCP's id, if already known from earlier in this conversation",
    )


class _EditInteractionArgs(BaseModel):
    rep_utterance: str = Field(
        description=(
            "The rep's correction or addition to a previously logged interaction"
        )
    )
    interaction_id: uuid.UUID | None = Field(
        default=None,
        description=(
            "The interaction's id, if already known from earlier in this "
            "conversation (e.g. just logged it this turn)"
        ),
    )


class _RetrieveHCPHistoryArgs(BaseModel):
    hcp_id: uuid.UUID | None = Field(default=None, description="The HCP's id, if known")
    hcp_name: str | None = Field(
        default=None, description="The HCP's name, if the id isn't known"
    )


class _ScheduleFollowUpArgs(BaseModel):
    rep_utterance: str = Field(
        description="The rep's free-form follow-up request, or an accepted suggestion"
    )
    hcp_id: uuid.UUID | None = Field(default=None, description="The HCP's id, if known")
    interaction_id: uuid.UUID | None = Field(
        default=None,
        description="The interaction this follow-up relates to, if known",
    )


class _FlagComplianceRisksArgs(BaseModel):
    text: str = Field(description="The text to screen for compliance risk")


def build_tools(
    db: Session, rep_id: uuid.UUID, side_effects: list[dict[str, Any]]
) -> list[BaseTool]:
    """LangChain tools bound to this request's db session, rep, and a
    side-effects sink the chat endpoint reads back for its response."""

    def _record(tool_name: str, output: BaseModel) -> dict[str, Any]:
        payload = output.model_dump(mode="json")
        side_effects.append({"tool": tool_name, "output": payload})
        return payload

    def _run_log_interaction(
        rep_utterance: str, hcp_id: uuid.UUID | None = None
    ) -> dict[str, Any]:
        result = log_interaction(
            LogInteractionInput(
                rep_utterance=rep_utterance, rep_id=rep_id, hcp_id=hcp_id
            ),
            db,
        )
        return _record("log_interaction", result)

    def _run_edit_interaction(
        rep_utterance: str, interaction_id: uuid.UUID | None = None
    ) -> dict[str, Any]:
        result = edit_interaction(
            EditInteractionInput(
                rep_utterance=rep_utterance,
                rep_id=rep_id,
                interaction_id=interaction_id,
            ),
            db,
        )
        return _record("edit_interaction", result)

    def _run_retrieve_hcp_history(
        hcp_id: uuid.UUID | None = None, hcp_name: str | None = None
    ) -> dict[str, Any]:
        result = retrieve_hcp_history(
            RetrieveHCPHistoryInput(hcp_id=hcp_id, hcp_name=hcp_name), db
        )
        return _record("retrieve_hcp_history", result)

    def _run_schedule_follow_up(
        rep_utterance: str,
        hcp_id: uuid.UUID | None = None,
        interaction_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        result = schedule_follow_up(
            ScheduleFollowUpInput(
                rep_utterance=rep_utterance,
                rep_id=rep_id,
                hcp_id=hcp_id,
                interaction_id=interaction_id,
            ),
            db,
        )
        return _record("schedule_follow_up", result)

    def _run_flag_compliance_risks(text: str) -> dict[str, Any]:
        result = flag_compliance_risks(FlagComplianceRisksInput(text=text))
        return _record("flag_compliance_risks", result)

    return [
        StructuredTool.from_function(
            func=_run_log_interaction,
            name="log_interaction",
            description=(
                "Log a new HCP interaction from the rep's free-form "
                "description. Returns status='needs_clarification' if the "
                "HCP can't be resolved or there isn't enough detail — "
                "relay that message to the rep rather than guessing."
            ),
            args_schema=_LogInteractionArgs,
        ),
        StructuredTool.from_function(
            func=_run_edit_interaction,
            name="edit_interaction",
            description=(
                "Correct or add to an interaction the rep already logged. "
                "Resolves the target interaction from recency/context if "
                "no interaction_id is given. Returns "
                "status='needs_clarification' if the target can't be "
                "confidently resolved — relay that message rather than "
                "guessing."
            ),
            args_schema=_EditInteractionArgs,
        ),
        StructuredTool.from_function(
            func=_run_retrieve_hcp_history,
            name="retrieve_hcp_history",
            description=(
                "Look up an HCP's profile and recent interaction history. "
                "Call this proactively as soon as you know which HCP the "
                "rep is discussing, even if they didn't explicitly ask for "
                "history — it grounds the rest of the conversation."
            ),
            args_schema=_RetrieveHCPHistoryArgs,
        ),
        StructuredTool.from_function(
            func=_run_schedule_follow_up,
            name="schedule_follow_up",
            description=(
                "Schedule a dated follow-up reminder for an HCP, resolving "
                "relative dates like 'next month' or 'in two weeks'. Also "
                "used when the rep accepts one of log_interaction's "
                "suggested_follow_ups verbatim."
            ),
            args_schema=_ScheduleFollowUpArgs,
        ),
        StructuredTool.from_function(
            func=_run_flag_compliance_risks,
            name="flag_compliance_risks",
            description=(
                "Screen arbitrary text for compliance risk (off-label "
                "claims, unsubstantiated claims, adverse event mentions). "
                "log_interaction already runs this automatically on every "
                "logged interaction — only call this directly if the rep "
                "explicitly asks you to check some other text."
            ),
            args_schema=_FlagComplianceRisksArgs,
        ),
    ]
