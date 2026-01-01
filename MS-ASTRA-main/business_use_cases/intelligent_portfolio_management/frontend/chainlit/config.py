"""
Chainlit configuration for Intelligent Portfolio Management
"""

[tool.chainlit]
# The name of the Chainlit app
name = "Intelligent Portfolio Management Assistant"

# Enable/disable authentication
enable_telemetry = false

# Session timeout in seconds (1 hour)
session_timeout = 3600

# Theme configuration
[ui]
name = "Portfolio Assistant"
description = "AI-powered portfolio management and investment advisory"
favicon = "/assets/favicon.ico"
default_collapse_content = true

# Chat configuration
[ui.chat]
default_expand_messages = false
show_readme_as_default = true

[project]
# Whether to enable public data collection
public = false

# Database URL (if using persistence)
# database_url = "sqlite:///chainlit.db"