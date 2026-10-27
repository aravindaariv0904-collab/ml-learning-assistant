"""
Integrations package for Google Workspace (Drive, Calendar, Gmail) and Slack.
"""

from .google_workspace import GoogleWorkspaceManager
from .slack_notifier import SlackNotifier
from .email_notifier import EmailNotifier

__all__ = ["GoogleWorkspaceManager", "SlackNotifier", "EmailNotifier"]
