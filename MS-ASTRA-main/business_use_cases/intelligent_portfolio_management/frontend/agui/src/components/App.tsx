import React from 'react';
import { PortfolioDashboard } from '../pages/PortfolioDashboard';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Intelligent Portfolio Management</h1>
        <p>AI-powered investment advisory platform</p>
      </header>
      <main className="app-main">
        <PortfolioDashboard />
      </main>
    </div>
  );
}

export default App;