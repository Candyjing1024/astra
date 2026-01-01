/*
TEMPLATE FILE: Generic CopilotKit Runtime Service for ASTRA Core

CUSTOMIZATION:
1. Update the backend endpoint URL for your deployment
2. Configure service adapter based on your requirements
3. Add domain-specific middleware or routing
4. Update port configuration for your environment
5. Add authentication/authorization if needed

This template provides:
- CopilotKit runtime service setup
- Integration with ASTRA Core backend
- Configurable endpoint and port
- Ready for deployment customization
*/

import { createServer } from 'node:http';
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNodeHttpEndpoint,
} from '@copilotkit/runtime';

// CUSTOMIZE: Update these configurations for your deployment
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const COPILOT_ENDPOINT = process.env.COPILOT_ENDPOINT || '/copilotkit';
const PORT = process.env.PORT || 4000;

// CUSTOMIZE: Configure service adapter based on your needs
const serviceAdapter = new ExperimentalEmptyAdapter();

const server = createServer((req, res) => {
  // CUSTOMIZE: Add CORS headers for your domain
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Create runtime with backend endpoint
  const runtime = new CopilotRuntime({
    remoteEndpoints: [
      { 
        url: `${BACKEND_URL}${COPILOT_ENDPOINT}`,
        // CUSTOMIZE: Add authentication headers if needed
        // headers: {
        //   'Authorization': 'Bearer your-token',
        //   'X-API-Key': 'your-api-key'
        // }
      },
    ],
    // CUSTOMIZE: Add runtime configuration
    // maxTokens: 4000,
    // temperature: 0.7,
  });

  const handler = copilotRuntimeNodeHttpEndpoint({
    endpoint: COPILOT_ENDPOINT,
    runtime,
    serviceAdapter,
  });

  return handler(req, res);
});

server.listen(PORT, () => {
  console.log(`🚀 ASTRA Core CopilotKit Runtime Service listening at http://localhost:${PORT}${COPILOT_ENDPOINT}`);
  console.log(`📡 Connected to backend: ${BACKEND_URL}${COPILOT_ENDPOINT}`);
  console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 Received SIGTERM, shutting down gracefully');
  server.close(() => {
    console.log('✅ Process terminated');
  });
});

process.on('SIGINT', () => {
  console.log('🛑 Received SIGINT, shutting down gracefully');
  server.close(() => {
    console.log('✅ Process terminated');
  });
});