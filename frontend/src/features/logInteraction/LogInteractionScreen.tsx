import { skipToken } from '@reduxjs/toolkit/query/react'
import { useEffect, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { useGetHcpQuery } from '../../api/hcpsApi'
import type { Interaction } from '../../api/types'
import ChatPanel from './ChatPanel'
import ComplianceFlagsBanner from './ComplianceFlagsBanner'
import { draftFromInteraction } from './draft'
import FormPanel from './FormPanel'
import {
  chatEditInteractionApplied,
  chatLogInteractionApplied,
  draftChanged,
  draftLoaded,
  draftReset,
  draftSavedAsUpdate,
  hcpContextResolved,
  hcpNameResolved,
} from './logInteractionDraftSlice'
import RecentInteractionsList from './RecentInteractionsList'
import { useAgentChat } from './useAgentChat'
import './LogInteractionScreen.css'

function LogInteractionScreen() {
  const dispatch = useAppDispatch()
  const draftState = useAppSelector((state) => state.logInteractionDraft)
  const { draft, interactionId, suggestedFollowUps, complianceFlags } =
    draftState

  const activeHcp = draft.hcp_id
    ? { id: draft.hcp_id, name: draft.hcp_name }
    : null
  const chat = useAgentChat({ hcp: activeHcp, interactionId })

  const appliedSideEffectIds = useRef(new Set<string>())
  useEffect(() => {
    for (const message of chat.messages) {
      if (message.role !== 'agent' || !message.sideEffects) {
        continue
      }
      message.sideEffects.forEach((effect, index) => {
        const key = `${message.id}-${effect.tool}-${index}`
        if (appliedSideEffectIds.current.has(key)) {
          return
        }
        appliedSideEffectIds.current.add(key)

        if (
          effect.tool === 'log_interaction' &&
          effect.output.status === 'created'
        ) {
          dispatch(chatLogInteractionApplied(effect.output))
        }
        if (
          effect.tool === 'edit_interaction' &&
          effect.output.status === 'updated'
        ) {
          dispatch(chatEditInteractionApplied(effect.output))
        }
        if (
          effect.tool === 'retrieve_hcp_history' &&
          effect.output.status === 'found' &&
          effect.output.hcp_id &&
          effect.output.hcp_name
        ) {
          dispatch(
            hcpContextResolved({
              id: effect.output.hcp_id,
              name: effect.output.hcp_name,
            }),
          )
        }
      })
    }
  }, [chat.messages, dispatch])

  // log_interaction's own output only carries hcp_id, not hcp_name — look
  // it up once so the form's HCP field can display a name, not just an id.
  const { data: resolvedHcp } = useGetHcpQuery(
    draft.hcp_id && !draft.hcp_name ? draft.hcp_id : skipToken,
  )
  useEffect(() => {
    if (resolvedHcp) {
      dispatch(hcpNameResolved({ id: resolvedHcp.id, name: resolvedHcp.name }))
    }
  }, [resolvedHcp, dispatch])

  function handleSuggestedFollowUpClick(suggestion: string) {
    void chat.sendMessage(suggestion)
  }

  function handleSaved(saved: Interaction) {
    if (interactionId) {
      dispatch(draftSavedAsUpdate(saved.compliance_flags))
    } else {
      dispatch(draftReset())
    }
  }

  function handleEditInteraction(interaction: Interaction) {
    dispatch(
      draftLoaded({
        draft: draftFromInteraction(interaction),
        interactionId: interaction.id,
        source: interaction.source,
        complianceFlags: interaction.compliance_flags,
      }),
    )
  }

  return (
    <div className="log-interaction-screen">
      <ComplianceFlagsBanner flags={complianceFlags} />
      <div className="log-interaction-screen__panels">
        <div>
          <FormPanel
            value={draft}
            onChange={(next) => dispatch(draftChanged(next))}
            interactionId={interactionId}
            originalSnapshot={draftState.originalDraft}
            suggestedFollowUps={suggestedFollowUps}
            onSuggestedFollowUpClick={handleSuggestedFollowUpClick}
            onSaved={handleSaved}
          />
          <RecentInteractionsList
            hcpId={draft.hcp_id}
            onEdit={handleEditInteraction}
          />
        </div>
        <ChatPanel
          chat={chat}
          onSuggestedFollowUpClick={handleSuggestedFollowUpClick}
        />
      </div>
    </div>
  )
}

export default LogInteractionScreen
