const parseResponse = async (response) => {
  const contentType = response.headers.get('content-type') ?? '';

  if (contentType.includes('application/json')) {
    return response.json();
  }

  return null;
};

const request = async (path, init = {}) => {
  const response = await fetch(path, init);
  const data = await parseResponse(response);

  if (!response.ok) {
    const message = data?.detail ?? 'The local moderation backend could not process your request.';
    throw new Error(message);
  }

  return data;
};

export const fetchBackendStatus = () => request('/api/health');

export const analyzeComment = (comment) =>
  request('/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ comment }),
  });
