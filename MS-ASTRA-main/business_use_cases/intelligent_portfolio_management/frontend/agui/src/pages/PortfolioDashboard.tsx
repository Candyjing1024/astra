import React from 'react';

export function PortfolioDashboard() {
  return (
    <div className="portfolio-dashboard">
      <h2>Portfolio Overview</h2>
      <div className="dashboard-grid">
        <div className="card">
          <h3>Total Portfolio Value</h3>
          <p className="value">$0.00</p>
          <p className="change">+0.00% today</p>
        </div>
        <div className="card">
          <h3>Asset Allocation</h3>
          <p>Stocks: 0%</p>
          <p>Bonds: 0%</p>
          <p>Cash: 100%</p>
        </div>
        <div className="card">
          <h3>Performance</h3>
          <p>1 Month: 0%</p>
          <p>3 Months: 0%</p>
          <p>1 Year: 0%</p>
        </div>
        <div className="card">
          <h3>AI Recommendations</h3>
          <p>No recommendations available</p>
          <button>Get AI Analysis</button>
        </div>
      </div>
    </div>
  );
}