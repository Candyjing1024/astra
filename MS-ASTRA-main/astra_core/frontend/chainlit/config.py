"""
Generic Chainlit Configuration Template for ASTRA Core

TEMPLATE FILE: Generic configuration for Chainlit chat interface.

CUSTOMIZATION:
1. Update app name and description for your domain
2. Configure authentication settings if needed
3. Set up database persistence if required
4. Customize UI theme and branding
5. Configure session and timeout settings
"""

[tool.chainlit]
# CUSTOMIZE: Update app name for your domain
name = "ASTRA Domain Assistant"

# Enable/disable telemetry (set to false for privacy)
enable_telemetry = false

# Session timeout in seconds (1 hour default)
session_timeout = 3600

# CUSTOMIZE: Theme and UI configuration
[ui]
name = "Domain Assistant"
description = "AI-powered domain-specific assistant and analysis platform"
# CUSTOMIZE: Add your domain-specific favicon
favicon = "/assets/favicon.ico"
default_collapse_content = true

# Chat interface configuration
[ui.chat]
default_expand_messages = false
show_readme_as_default = true

[project]
# Whether to enable public data collection
public = false

# CUSTOMIZE: Database configuration for chat persistence
# Uncomment and configure if you want to persist conversations
# database_url = "sqlite:///chainlit.db"
# For production, use a proper database:
# database_url = "postgresql://user:password@host:port/database"

# CUSTOMIZE: Add authentication configuration if needed
# [auth]
# secret_key = "your-secret-key"
# oauth_providers = ["github", "google"]