import assert from 'node:assert/strict';
import test from 'node:test';

import { getState, runAction } from './apiClient.js';

function response(payload, ok = true) {
  return { ok, json: async () => payload };
}

test('state is read from the local API', async () => {
  const calls = [];
  const fetchImpl = async (...args) => {
    calls.push(args);
    return response({ decision: 'ALLOW' });
  };

  const state = await getState(fetchImpl);

  assert.deepEqual(state, { decision: 'ALLOW' });
  assert.equal(calls[0][0], '/api/state');
});

test('approved UI actions map only to fixed local endpoints', async () => {
  const calls = [];
  const fetchImpl = async (...args) => {
    calls.push(args);
    return response({ decision: 'APPROVAL_REQUIRED' });
  };

  await runAction('RUN_REVIEW', fetchImpl);

  assert.equal(calls[0][0], '/api/review');
  assert.equal(calls[0][1].method, 'POST');
  assert.equal(calls[0][1].body, '{}');
  assert.equal(calls[0][1].headers['X-AgentGuard-Intent'], 'human-ui-v1');
});

test('unknown actions and failed responses return generic errors', async () => {
  await assert.rejects(runAction('ARBITRARY_MUTATION'), /UNKNOWN_LOCAL_ACTION/);
  await assert.rejects(
    runAction('REJECT', async () => response({ error: 'private detail' }, false)),
    /LOCAL_API_REQUEST_FAILED/,
  );
});
