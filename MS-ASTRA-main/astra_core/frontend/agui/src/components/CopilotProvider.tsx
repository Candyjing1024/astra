/*
TEMPLATE FILE: Generic CopilotKit Integration for ASTRA Core

CUSTOMIZATION:
1. Update the runtime URL for your deployment environment
2. Configure agent name to match your backend agent configuration
3. Add domain-specific properties and context
4. Customize chat interface labels and instructions
5. Configure session management based on your authentication system

This template provides:
- CopilotKit provider setup with backend integration
- Generic agent configuration
- Session management template
- Chat interface integration
- Customizable properties for your domain
*/

import React, { useState, useEffect, ReactNode } from 'react';
import { CopilotKit } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';

interface CopilotProviderProps {
  children: ReactNode;
  // CUSTOMIZE: Add your domain-specific props
  userId?: string;
  sessionId?: string;
  domainContext?: Record<string, any>;
}

// CUSTOMIZE: Update these URLs for your deployment
const COPILOT_RUNTIME_URL = process.env.REACT_APP_COPILOT_URL || 'http://localhost:8000/copilotkit';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export function CopilotProvider({ 
  children, 
  userId = 'default-user',
  sessionId,
  domainContext = {}
}: CopilotProviderProps) {
  const [threadId, setThreadId] = useState<string | undefined>(sessionId);
  const [sessionCheckComplete, setSessionCheckComplete] = useState(false);

  useEffect(() => {
    // CUSTOMIZE: Implement your session management logic
    const checkForRecentSession = async () => {
      try {
        console.log('🔍 Checking for recent session for user:', userId);
        
        // Optional: Check for existing session on the backend
        if (userId && userId !== 'default-user') {
          const response = await fetch(`${BACKEND_URL}/session/${userId}`);
          const sessionInfo = await response.json();

          if (sessionInfo.has_recent_session && sessionInfo.thread_id) {
            console.log('🔄 Found recent session, using thread_id:', sessionInfo.thread_id);
            setThreadId(sessionInfo.thread_id);
          }
        }
      } catch (error) {
        // Continue without threadId, let CopilotKit create a new one
        console.error('❌ Error checking for recent session:', error);
      } finally {
        setSessionCheckComplete(true);
      }
    };

    checkForRecentSession();
  }, [userId]);

  // Show loading state while session is being checked
  if (!sessionCheckComplete) {
    return (
      <div className="copilot-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Initializing AI Assistant...</p>
        </div>
      </div>
    );
  }

  console.log('🚀 Initializing CopilotKit with:', {
    user_id: userId,
    threadId: threadId || 'new',
    domainContext
  });

  return (
    <CopilotKit
      runtimeUrl={COPILOT_RUNTIME_URL}
      // CUSTOMIZE: Update agent name to match your backend configuration
      agent="domain_supervisor"
      properties={{
        // CUSTOMIZE: Add your domain-specific properties
        user_id: userId,
        domain_context: domainContext,
        // Add any additional context your agents need
        session_context: {
          timestamp: new Date().toISOString(),
          version: '1.0.0'
        }
      }}
      // Only pass threadId if we found a recent session
      {...(threadId ? { threadId } : {})}
    >
      {children}
    </CopilotKit>
  );
}

// CUSTOMIZE: Create domain-specific wrapper components
export function DomainCopilotProvider({ children }: { children: ReactNode }) {
  // CUSTOMIZE: Add your authentication and session logic here
  const userId = 'example-user-123'; // Replace with actual user ID from auth
  const domainContext = {
    // CUSTOMIZE: Add your domain-specific context
    domain: 'generic-domain',
    capabilities: ['analysis', 'research', 'recommendations'],
    preferences: {}
  };

  return (
    <CopilotProvider 
      userId={userId}
      domainContext={domainContext}
    >
      {children}
    </CopilotProvider>
  );
}

// CSS for loading spinner (add to your styles.css or here)
const loadingStyles = `
.copilot-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 2s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;

// Inject styles if not already present
if (typeof document !== 'undefined') {
  const styleId = 'copilot-loading-styles';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = loadingStyles;
    document.head.appendChild(style);
  }
}