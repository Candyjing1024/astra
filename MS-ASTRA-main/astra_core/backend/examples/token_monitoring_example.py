"""
Token Monitoring System - Practical Examples

This script demonstrates how to use the token monitoring system in real-world scenarios.
Run this script to see token tracking in action.

Prerequisites:
- Cosmos DB configured and running
- Azure OpenAI credentials in config.py
- Token monitoring service initialized

Usage:
    python -m backend.examples.token_monitoring_example
"""

import asyncio
from datetime import datetime, timedelta
from backend.services.token_monitoring import token_monitor
from backend.callbacks import attach_token_tracking, TokenTrackingCallbackHandler
from backend.utils import chat_completion_model
from langchain_core.messages import HumanMessage


async def example_1_basic_tracking():
    """Example 1: Basic token tracking with manual tracking."""
    print("\n" + "="*60)
    print("Example 1: Manual Token Tracking")
    print("="*60)
    
    # Make a simple OpenAI call
    messages = [HumanMessage(content="Explain quantum computing in one sentence.")]
    response = await chat_completion_model.ainvoke(messages)
    
    # Extract token usage (if available)
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage = response.usage_metadata
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        print(f"\n📊 Response: {response.content[:100]}...")
        print(f"\n📈 Token Usage:")
        print(f"   Input:  {input_tokens} tokens")
        print(f"   Output: {output_tokens} tokens")
        print(f"   Total:  {input_tokens + output_tokens} tokens")
        
        # Track the usage
        record_id = await token_monitor.track_usage(
            user_id="example_user@demo.com",
            thread_id="example-thread-1",
            model="gpt-4o",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            agent_name="example_agent",
            operation_type="chat"
        )
        
        print(f"\n✓ Usage tracked! Record ID: {record_id}")
    else:
        print("⚠️  No usage metadata available in response")


async def example_2_callback_tracking():
    """Example 2: Automatic tracking using callback handler."""
    print("\n" + "="*60)
    print("Example 2: Automatic Tracking with Callback")
    print("="*60)
    
    # Create callback
    callback = TokenTrackingCallbackHandler(
        user_id="example_user@demo.com",
        thread_id="example-thread-2",
        agent_name="callback_agent"
    )
    
    # Make call with callback - tracking happens automatically
    messages = [HumanMessage(content="What is the capital of France?")]
    response = await chat_completion_model.ainvoke(
        messages,
        config={"callbacks": [callback]}
    )
    
    print(f"\n📊 Response: {response.content}")
    print("\n✓ Tokens automatically tracked via callback!")


async def example_3_query_user_stats():
    """Example 3: Query user token usage statistics."""
    print("\n" + "="*60)
    print("Example 3: Query User Statistics")
    print("="*60)
    
    # Get usage for the last 7 days
    start_date = datetime.utcnow() - timedelta(days=7)
    stats = await token_monitor.get_user_usage(
        user_id="example_user@demo.com",
        start_date=start_date
    )
    
    print(f"\n📊 User Usage Statistics (Last 7 Days)")
    print(f"   Total Requests: {stats.total_requests}")
    print(f"   Total Tokens: {stats.total_tokens:,}")
    print(f"   Input Tokens: {stats.total_input_tokens:,}")
    print(f"   Output Tokens: {stats.total_output_tokens:,}")
    print(f"   Total Cost: ${stats.total_cost:.6f}")
    
    if stats.cost_by_model:
        print(f"\n💰 Cost by Model:")
        for model, cost in stats.cost_by_model.items():
            print(f"   {model}: ${cost:.6f}")
    
    if stats.requests_by_agent:
        print(f"\n🤖 Requests by Agent:")
        for agent, count in stats.requests_by_agent.items():
            print(f"   {agent}: {count} requests")


async def example_4_budget_monitoring():
    """Example 4: Implement budget monitoring."""
    print("\n" + "="*60)
    print("Example 4: Budget Monitoring")
    print("="*60)
    
    user_id = "example_user@demo.com"
    monthly_budget = 10.00  # $10 budget
    
    # Get usage for current month
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    stats = await token_monitor.get_user_usage(user_id, start_date=start_of_month)
    
    print(f"\n💵 Budget Status for {user_id}")
    print(f"   Monthly Budget: ${monthly_budget:.2f}")
    print(f"   Current Usage: ${stats.total_cost:.2f}")
    print(f"   Remaining: ${monthly_budget - stats.total_cost:.2f}")
    
    # Calculate percentage used
    percentage_used = (stats.total_cost / monthly_budget) * 100
    print(f"   Percentage Used: {percentage_used:.1f}%")
    
    # Alert if over budget
    if stats.total_cost > monthly_budget:
        print(f"\n⚠️  ALERT: Budget exceeded by ${stats.total_cost - monthly_budget:.2f}!")
    elif percentage_used > 80:
        print(f"\n⚠️  WARNING: Over 80% of budget used!")
    else:
        print(f"\n✓ Budget OK")


async def example_5_cost_analysis():
    """Example 5: Detailed cost analysis."""
    print("\n" + "="*60)
    print("Example 5: Cost Analysis by Model")
    print("="*60)
    
    # Get usage broken down by model
    stats_by_model = await token_monitor.get_usage_by_model(days=30)
    
    if not stats_by_model:
        print("\n⚠️  No usage data found")
        return
    
    print(f"\n📊 Token Usage by Model (Last 30 Days)")
    print("-" * 60)
    
    total_cost = 0
    total_tokens = 0
    
    for model, stats in stats_by_model.items():
        print(f"\n{model}:")
        print(f"   Requests: {stats.total_requests:,}")
        print(f"   Tokens: {stats.total_tokens:,}")
        print(f"   Cost: ${stats.total_cost:.2f}")
        print(f"   Avg tokens/request: {stats.total_tokens / stats.total_requests:.0f}")
        print(f"   Avg cost/request: ${stats.total_cost / stats.total_requests:.4f}")
        
        total_cost += stats.total_cost
        total_tokens += stats.total_tokens
    
    print("\n" + "-" * 60)
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Total Tokens: {total_tokens:,}")


async def example_6_cost_trend():
    """Example 6: Visualize cost trends."""
    print("\n" + "="*60)
    print("Example 6: Cost Trend Analysis")
    print("="*60)
    
    # Get usage for the last 7 days
    start_date = datetime.utcnow() - timedelta(days=7)
    stats = await token_monitor.get_user_usage(
        user_id="example_user@demo.com",
        start_date=start_date
    )
    
    if not stats.cost_trend:
        print("\n⚠️  No trend data available")
        return
    
    print(f"\n📈 Daily Cost Trend")
    print("-" * 60)
    
    # Create simple ASCII chart
    max_cost = max(day["cost"] for day in stats.cost_trend) if stats.cost_trend else 0
    
    for day in stats.cost_trend:
        date = day["date"]
        cost = day["cost"]
        # Create bar chart with * characters
        bar_length = int((cost / max_cost) * 40) if max_cost > 0 else 0
        bar = "*" * bar_length
        print(f"{date}: {bar} ${cost:.6f}")


async def example_7_get_all_records():
    """Example 7: Retrieve raw usage records."""
    print("\n" + "="*60)
    print("Example 7: Recent Usage Records")
    print("="*60)
    
    # Get last 5 records
    records = await token_monitor.get_all_usage(days=7, limit=5)
    
    if not records:
        print("\n⚠️  No records found")
        return
    
    print(f"\n📝 Last 5 Token Usage Records:")
    print("-" * 60)
    
    for i, record in enumerate(records, 1):
        print(f"\nRecord {i}:")
        print(f"   User: {record['user_id']}")
        print(f"   Model: {record['model']}")
        print(f"   Agent: {record.get('agent_name', 'N/A')}")
        print(f"   Tokens: {record['total_tokens']:,} ({record['input_tokens']} in + {record['output_tokens']} out)")
        print(f"   Cost: ${record['total_cost']:.6f}")
        print(f"   Time: {record['timestamp']}")


async def example_8_cost_optimization():
    """Example 8: Model cost optimization suggestions."""
    print("\n" + "="*60)
    print("Example 8: Cost Optimization Recommendations")
    print("="*60)
    
    stats_by_model = await token_monitor.get_usage_by_model(days=30)
    
    if not stats_by_model:
        print("\n⚠️  No usage data available")
        return
    
    print(f"\n💡 Optimization Recommendations:")
    print("-" * 60)
    
    # Check if expensive models are being used for simple tasks
    if "gpt-4" in stats_by_model and "gpt-4o-mini" in stats_by_model:
        gpt4_stats = stats_by_model["gpt-4"]
        mini_stats = stats_by_model["gpt-4o-mini"]
        
        if gpt4_stats.total_requests > mini_stats.total_requests:
            potential_savings = gpt4_stats.total_cost * 0.7  # Assuming 70% could use mini
            print(f"\n1. Consider using gpt-4o-mini for simpler tasks")
            print(f"   Potential savings: ~${potential_savings:.2f}/month")
    
    # Check average tokens per request
    for model, stats in stats_by_model.items():
        avg_tokens = stats.total_tokens / stats.total_requests
        if avg_tokens > 5000:
            print(f"\n2. {model} has high average tokens ({avg_tokens:.0f})")
            print(f"   Consider: Shorter prompts, context trimming, or chunking")
    
    # Check for high-cost models
    expensive_threshold = 0.50
    for model, stats in stats_by_model.items():
        avg_cost_per_request = stats.total_cost / stats.total_requests
        if avg_cost_per_request > expensive_threshold:
            print(f"\n3. {model} has high cost per request (${avg_cost_per_request:.4f})")
            print(f"   Consider: Caching responses, batching requests")


async def run_all_examples():
    """Run all examples."""
    print("\n" + "="*70)
    print("TOKEN MONITORING SYSTEM - PRACTICAL EXAMPLES")
    print("="*70)
    
    try:
        # Initialize token monitoring
        print("\n🔧 Initializing token monitoring service...")
        await token_monitor.initialize()
        print("✓ Token monitoring service initialized")
        
        # Run examples
        await example_1_basic_tracking()
        await asyncio.sleep(1)  # Small delay between examples
        
        await example_2_callback_tracking()
        await asyncio.sleep(1)
        
        await example_3_query_user_stats()
        await asyncio.sleep(1)
        
        await example_4_budget_monitoring()
        await asyncio.sleep(1)
        
        await example_5_cost_analysis()
        await asyncio.sleep(1)
        
        await example_6_cost_trend()
        await asyncio.sleep(1)
        
        await example_7_get_all_records()
        await asyncio.sleep(1)
        
        await example_8_cost_optimization()
        
        print("\n" + "="*70)
        print("✓ All examples completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await token_monitor.close()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(run_all_examples())



