// Shell derived from the AWS WAF Analyst React frontend.
// SPDX-License-Identifier: MIT-0
import React, { useEffect, useState } from 'react';

import { getState, runAction } from './apiClient.js';

const timelineLabels = {
  request: 'User request',
  proposal: 'Agent proposal',
  typed: 'Typed action',
  policy: 'Policy decision',
  approval: 'Human approval',
  action: 'WAF action',
  verification: 'Verification',
  audit: 'Audit',
};

function display(value) {
  return value.replaceAll('_', ' ');
}

function DecisionPanel({ state, onAction, busy }) {
  const decisionClass = state.decision.toLowerCase().replaceAll('_', '-');
  return (
    <aside className="decision-panel" aria-label="AgentGuard decision">
      <div className="panel-kicker">AgentGuard decision</div>
      <div className={`decision-badge ${decisionClass}`}>{display(state.decision)}</div>
      <div className="reason-code">{state.reason}</div>

      <div className="fact-grid">
        <div><span>Risk</span><strong className={`risk ${state.risk.toLowerCase()}`}>{state.risk}</strong></div>
        <div><span>Target</span><strong>{state.target}</strong></div>
        <div><span>Rule</span><strong>{state.rule}</strong></div>
        <div><span>Proposal</span><strong>{state.proposal}</strong></div>
      </div>

      <div className="change-card">
        <div><span>Before</span><strong>{state.beforeAction}</strong></div>
        <div className="change-arrow" aria-hidden="true">-&gt;</div>
        <div><span>Requested</span><strong>{state.requestedAction}</strong></div>
        <div className="change-arrow" aria-hidden="true">-&gt;</div>
        <div><span>Actual</span><strong>{state.actualAction}</strong></div>
      </div>

      <ol className="timeline">
        {Object.entries(state.steps).map(([key, status]) => (
          <li key={key} className={status}>
            <span className="step-marker" aria-hidden="true" />
            <span>{timelineLabels[key]}</span>
            <small>{status}</small>
          </li>
        ))}
      </ol>

      {state.mode === 'proposal' && (
        <div className="approval-actions">
          <button disabled={busy} className="approve" onClick={() => onAction('APPROVE_ONCE')}>
            Approve Once
          </button>
          <button disabled={busy} className="reject" onClick={() => onAction('REJECT')}>
            Reject
          </button>
        </div>
      )}

      <div className="audit-strip">
        <span>Mutation: <strong>{state.mutationPerformed ? 'YES' : 'NO'}</strong></span>
        <span>Verified: <strong>{state.verified ? 'YES' : 'NO'}</strong></span>
        <span>Audit: <strong>{state.audit}</strong></span>
      </div>
    </aside>
  );
}

function ToolActivity({ tools }) {
  if (tools.length === 0) return null;
  return (
    <section className="tool-activity" aria-label="Visible tool activity">
      <div className="section-label">Tool activity</div>
      {tools.map((tool) => (
        <div className="tool-row" key={`${tool.name}-${tool.detail}`}>
          <span className="tool-status" aria-hidden="true" />
          <code>{tool.name}</code>
          <span>{tool.detail}</span>
        </div>
      ))}
    </section>
  );
}

export default function App() {
  const [state, setState] = useState(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getState()
      .then(setState)
      .catch(() => setError('LOCAL API UNAVAILABLE'))
      .finally(() => setBusy(false));
  }, []);

  async function onAction(action) {
    setBusy(true);
    setError('');
    try {
      setState(await runAction(action));
    } catch {
      setError('LOCAL API REQUEST FAILED');
    } finally {
      setBusy(false);
    }
  }

  if (!state) {
    return (
      <main className="loading-shell">
        <div className="brand-mark">AG</div>
        <h1>AgentGuard</h1>
        <p>{error || 'Connecting to the local policy API...'}</p>
      </main>
    );
  }

  return (
    <main className="app-layout">
      <section className="chat-shell">
        <header className="app-header">
          <div className="brand-mark">AG</div>
          <div>
            <h1>AgentGuard</h1>
            <p>Trust boundary for sensitive agent actions</p>
          </div>
          <div className="environment-pill">LOCAL SYNTHETIC DEMO</div>
        </header>

        <div className="demo-banner">
          Python policy authority connected. No model or AWS connection; all results are synthetic.
        </div>

        {error && <div className="error-banner" role="alert">{error}</div>}

        <div className="messages">
          {state.messages.map((message, index) => (
            <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <div className="message-role">{message.role === 'agent' ? 'AgentGuard' : 'Manager'}</div>
              <p>{message.text}</p>
            </article>
          ))}
          <ToolActivity tools={state.tools} />
        </div>

        <footer className="control-bar">
          <button disabled={busy} className="primary" onClick={() => onAction('RUN_REVIEW')}>
            Review Firewall
          </button>
          <button disabled={busy} className="danger" onClick={() => onAction('TRY_BYPASS')}>
            Try Approval Bypass
          </button>
          <button disabled={busy} className="secondary" onClick={() => onAction('RESET')}>
            Reset
          </button>
          <p>Demo target: LAB_WAF_01 / LAB_AdminPathProtection</p>
        </footer>
      </section>

      <DecisionPanel state={state} onAction={onAction} busy={busy} />
    </main>
  );
}
