// OAuth Configuration
const BACKEND_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const OAUTH_CONFIG = {
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    scope: 'openid email profile',
    responseType: 'code',
    accessType: 'offline',
    prompt: 'consent',
  },
  microsoft: {
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    scope: 'openid email profile',
    responseType: 'code',
    prompt: 'select_account',
  },
  apple: {
    authUrl: 'https://appleid.apple.com/auth/authorize',
    scope: 'name email',
    responseType: 'code id_token',
    responseMode: 'form_post',
  },
  callbackUrl: `${window.location.origin}/oauth-callback`,
  backendUrl: BACKEND_URL,
};

// Helper function to generate OAuth URL
export const getOAuthUrl = (provider, state, clientId) => {
  const config = OAUTH_CONFIG[provider];
  if (!config) {
    throw new Error(`Unknown OAuth provider: ${provider}`);
  }

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: OAUTH_CONFIG.callbackUrl,
    scope: config.scope,
    response_type: config.responseType,
    state: `${provider}:${state}`,
    ...(config.accessType && { access_type: config.accessType }),
    ...(config.prompt && { prompt: config.prompt }),
    ...(config.responseMode && { response_mode: config.responseMode }),
  });

  return `${config.authUrl}?${params.toString()}`;
};