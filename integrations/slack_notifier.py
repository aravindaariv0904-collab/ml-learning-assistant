"""
Slack Block Kit Notification Dispatcher
Constructs rich, interactive Slack cards with status badges, code sandbox results,
and direct access buttons for #ml-learning channel.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("SlackNotifier")


class SlackNotifier:
    """
    Builds and posts Slack Block Kit payloads to an incoming webhook or channel.
    """

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.channel = os.getenv("SLACK_CHANNEL", "#ml-learning")

    def build_block_kit_payload(
        self,
        day_info: Dict[str, Any],
        validation_result: Dict[str, Any],
        drive_links: Dict[str, str],
        html_preview_url: str = "",
        calendar_link: str = ""
    ) -> Dict[str, Any]:
        """
        Assembles Slack Block Kit blocks according to system specifications.
        Badges:
          - READY (Code verified 0 errors)
          - NEEDS REVIEW (Runtime or syntax warning)
          - FAILED (Critical failure)
        """
        day_num = day_info.get("day", 1)
        title = day_info.get("title", "")
        module = day_info.get("module", "")

        is_valid = validation_result.get("is_valid", False)
        badge_text = validation_result.get("status_badge", "VERIFIED (0 errors)")

        if is_valid and "VERIFIED" in badge_text:
            status_emoji = "🟢"
            status_label = f"`READY` &bull; {badge_text}"
        elif not is_valid and "SYNTAX" in badge_text:
            status_emoji = "🔴"
            status_label = f"`FAILED` &bull; {badge_text}"
        else:
            status_emoji = "🟡"
            status_label = f"`NEEDS REVIEW` &bull; {badge_text}"

        exec_time = validation_result.get("execution_time", 0.0)
        blocks_count = validation_result.get("blocks_count", 0)

        # Truncate stdout preview for Slack message
        stdout_preview = validation_result.get("stdout", "No output captured.")
        if len(stdout_preview) > 280:
            stdout_preview = stdout_preview[:280] + "\n...[truncated]"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📘 Day {day_num:02d}: {title}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Module:*\n{module}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Validation Status:*\n{status_emoji} {status_label}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Sandbox Telemetry:*\n{blocks_count} block(s) tested in {exec_time}s"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Study Session:*\n📅 7:00 PM – 9:00 PM IST"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🎯 Key Learning Objectives:*\n" + "\n".join([f"• {obj}" for obj in day_info.get("learning_objectives", [])[:3]])
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⚡ Code Sandbox Execution Output:*\n```{stdout_preview}```"
                }
            }
        ]

        # Action Buttons
        elements = []
        if html_preview_url:
            elements.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📖 Read HTML Lesson",
                    "emoji": True
                },
                "url": html_preview_url,
                "style": "primary"
            })

        pptx_url = drive_links.get("pptx_view_url")
        if pptx_url:
            elements.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Slides (.pptx)",
                    "emoji": True
                },
                "url": pptx_url
            })

        md_url = drive_links.get("md_view_url")
        if md_url:
            elements.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📁 Drive Notes (.md)",
                    "emoji": True
                },
                "url": md_url
            })

        if calendar_link:
            elements.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📅 Calendar Event",
                    "emoji": True
                },
                "url": calendar_link
            })

        if elements:
            blocks.append({
                "type": "actions",
                "elements": elements
            })

        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🤖 *Autonomous Cloud Orchestrator* &bull; GitHub Actions &bull; Zero-Cost Serverless Pipeline"
                }
            ]
        })

        return {"blocks": blocks}

    def send_notification(
        self,
        day_info: Dict[str, Any],
        validation_result: Dict[str, Any],
        drive_links: Dict[str, str],
        html_preview_url: str = "",
        calendar_link: str = ""
    ) -> Dict[str, Any]:
        """
        Dispatches Block Kit message to Slack.
        Prefers SLACK_WEBHOOK_URL for zero-friction channel posting, with SLACK_BOT_TOKEN fallback.
        Provides actionable recovery telemetry when channel_not_found or not_in_channel is encountered.
        """
        payload = self.build_block_kit_payload(
            day_info=day_info,
            validation_result=validation_result,
            drive_links=drive_links,
            html_preview_url=html_preview_url,
            calendar_link=calendar_link
        )

        # 1. Preferred Route: Incoming Webhook (Zero-friction channel posting)
        if self.webhook_url:
            try:
                logger.info("Dispatching Slack notification via preferred Incoming Webhook...")
                res = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                if res.status_code == 200:
                    logger.info(f"Successfully posted Slack notification for Day {day_info.get('day')} via webhook.")
                    return {"status": "sent", "provider": "slack_webhook", "code": 200}
                else:
                    logger.warning(f"Slack webhook returned status {res.status_code}: {res.text}. Attempting bot token if configured...")
            except Exception as e:
                logger.warning(f"Slack webhook request failed: {e}. Attempting bot token fallback...")

        # 2. Secondary Route: Slack Bot Token API (chat.postMessage)
        if self.bot_token:
            try:
                logger.info(f"Posting Slack message via Bot Token to channel: {self.channel}")
                res = requests.post(
                    "https://slack.com/api/chat.postMessage",
                    json={
                        "channel": self.channel,
                        "blocks": payload["blocks"],
                        "text": f"📘 Day {day_info.get('day', 1):02d}: {day_info.get('title', '')} notes ready"
                    },
                    headers={
                        "Authorization": f"Bearer {self.bot_token}",
                        "Content-Type": "application/json; charset=utf-8"
                    },
                    timeout=15
                )
                data = res.json()
                if data.get("ok"):
                    logger.info(f"Successfully posted Slack notification via Bot Token to {self.channel}")
                    return {"status": "sent", "provider": "slack_bot_api", "ts": data.get("ts")}
                else:
                    error_code = data.get("error", "unknown_error")
                    if error_code in ["channel_not_found", "not_in_channel", "channel_not_in_group"]:
                        logger.error(
                            "\n"
                            "================================================================================\n"
                            "⚠️  SLACK DELIVERY FAILURE RECOVERY TELEMETRY:\n"
                            f"Slack API returned error '{error_code}' for target channel '{self.channel}'.\n\n"
                            "To resolve this, choose one of two zero-friction paths:\n"
                            f"  Option 1: Invite the bot directly into the channel. In Slack channel '{self.channel}', run:\n"
                            "            /invite @ML Assitent\n"
                            "            (or the exact name assigned to your Slack Bot User)\n"
                            "  Option 2: Supply an Incoming Webhook URL in your .env or GitHub Secrets:\n"
                            "            SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...\n"
                            "            Webhooks bypass OAuth channel membership constraints completely.\n"
                            "================================================================================\n"
                        )
                    else:
                        logger.error(f"Slack Bot API returned error: {error_code} ({data.get('response_metadata')})")
                    return {"status": "error", "error": error_code, "data": data}
            except Exception as e:
                logger.error(f"Slack Bot API request exception: {e}")
                return {"status": "error", "error": str(e)}

        # 3. Neither configured or available
        logger.warning("Neither valid SLACK_WEBHOOK_URL nor SLACK_BOT_TOKEN available. Simulating Slack dispatch.")
        return {
            "status": "simulated",
            "payload": payload
        }
