"""
Integrations package for Google Workspace (Drive, Calendar, Gmail) and Slack.
"""

from .google_workspace import GoogleWorkspaceManager
from .slack_notifier import SlackNotifier

__all__ = ["GoogleWorkspaceManager", "SlackNotifier"]
