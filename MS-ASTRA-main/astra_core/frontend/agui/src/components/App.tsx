/*
TEMPLATE FILE: Generic ASTRA Core Frontend App Component

CUSTOMIZATION:
1. Update the app title and description for your domain
2. Replace DomainDashboard with your domain-specific dashboard component
3. Add your domain-specific navigation and routing
4. Configure CopilotKit integration for your agents
5. Update styling and branding

This template provides:
- Basic app structure with header and main content
- CopilotKit integration with domain agents
- Placeholder for domain-specific dashboard
- Responsive layout foundation
*/

import React from 'react';
import { DomainDashboard } from '../pages/DomainDashboard';
import { DomainCopilotProvider } from './CopilotProvider';
import { DomainChat } from './DomainChat';
// CUSTOMIZE: Import your domain-specific components
// import { CustomComponent } from '../components/CustomComponent';

function AppContent() {
  const [showChat, setShowChat] = React.useState(false);

  return (
    <div className="app">
      <header className="app-header">
        {/* CUSTOMIZE: Update title and description for your domain */}
        <h1>ASTRA Domain Application</h1>
        <p>AI-powered domain-specific platform</p>
        {/* Add your domain-specific navigation here */}
        <button 
          className="chat-toggle-btn"
          onClick={() => setShowChat(!showChat)}
        >
          {showChat ? 'Hide AI Assistant' : 'Show AI Assistant'}
        </button>
      </header>
      
      <main className="app-main">
        <div className="main-content">
          {/* CUSTOMIZE: Replace with your domain-specific dashboard */}
          <DomainDashboard />
        </div>
        
        {/* CopilotKit Chat Interface */}
        {showChat && (
          <div className="chat-sidebar">
            <DomainChat />
          </div>
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <DomainCopilotProvider>
      <AppContent />
    </DomainCopilotProvider>
  );
}

export default App;

export default App;