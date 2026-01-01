/*
TEMPLATE FILE: Generic Chat Interface Component for ASTRA Core

CUSTOMIZATION:
1. Update chat labels and instructions for your domain
2. Configure chat appearance and styling
3. Add domain-specific welcome messages
4. Customize agent instructions and capabilities
5. Add domain-specific message rendering

This template provides:
- CopilotChat UI component integration
- Generic chat interface with customizable styling
- Domain-agnostic message handling
- Integration with backend agents
*/

import React from 'react';
import { CopilotChat } from '@copilotkit/react-ui';
import { useCopilotChat } from '@copilotkit/react-core';

interface DomainChatProps {
  // CUSTOMIZE: Add domain-specific props
  placeholder?: string;
  title?: string;
  instructions?: string;
  className?: string;
}

export function DomainChat({ 
  placeholder = "Ask me anything about your domain...",
  title = "AI Assistant",
  instructions = "You are a helpful domain expert assistant. Provide accurate and helpful information.",
  className = "domain-chat"
}: DomainChatProps) {
  const { messages, isLoading } = useCopilotChat();

  return (
    <div className={`${className} chat-container`}>
      <CopilotChat
        labels={{
          title: title,
          initial: "Hello! How can I help you with your domain-specific questions today?",
          placeholder: placeholder,
        }}
        instructions={instructions}
        className="chat-interface"
        // CUSTOMIZE: Add domain-specific configurations
        makeSystemMessage={(message) => {
          // Add domain context to system messages
          return `${message}\n\nDomain Context: You are helping with domain-specific analysis and insights.`;
        }}
        // CUSTOMIZE: Add custom message rendering if needed
        // renderMessage={(message) => {
        //   return <CustomMessageRenderer message={message} />;
        // }}
      />
    </div>
  );
}

// CUSTOMIZE: Create specialized chat components for different use cases
export function AnalysisChat() {
  return (
    <DomainChat
      title="Analysis Assistant"
      placeholder="What would you like me to analyze?"
      instructions="You are an expert analyst. Help users understand their data and provide insights based on analysis."
      className="analysis-chat"
    />
  );
}

export function ResearchChat() {
  return (
    <DomainChat
      title="Research Assistant"
      placeholder="What would you like me to research?"
      instructions="You are a research specialist. Help users find information and provide comprehensive research results."
      className="research-chat"
    />
  );
}

// CUSTOMIZE: Chat popup component for overlay integration
export function DomainChatPopup() {
  return (
    <div className="chat-popup-container">
      <DomainChat
        title="Quick Help"
        placeholder="Quick question?"
        className="chat-popup"
      />
    </div>
  );
}

// CUSTOMIZE: Inline chat component for dashboard integration
export function InlineChat({ width = "100%", height = "400px" }) {
  return (
    <div 
      className="inline-chat" 
      style={{ width, height }}
    >
      <DomainChat 
        title="AI Assistant"
        className="inline-chat-component"
      />
    </div>
  );
}