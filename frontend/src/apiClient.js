const actionPaths = Object.freeze({
  RUN_REVIEW: '/api/review',
  APPROVE_ONCE: '/api/approve',
  REJECT: '/api/reject',
  TRY_BYPASS: '/api/bypass',
  RESET: '/api/reset',
});

async function request(path, options, fetchImpl) {
  const response = await fetchImpl(path, options);
  if (!response.ok) throw new Error('LOCAL_API_REQUEST_FAILED');
  return response.json();
}

export function getState(fetchImpl = globalThis.fetch) {
  return request('/api/state', { headers: { Accept: 'application/json' } }, fetchImpl);
}

export function runAction(action, fetchImpl = globalThis.fetch) {
  const path = actionPaths[action];
  if (!path) return Promise.reject(new Error('UNKNOWN_LOCAL_ACTION'));
  return request(
    path,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-AgentGuard-Intent': 'human-ui-v1',
      },
      body: '{}',
    },
    fetchImpl,
  );
}
