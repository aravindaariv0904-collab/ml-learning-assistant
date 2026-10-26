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

logger = logging.getLogger("SlackNotifier")


class SlackNotifier:
    """
    Builds and posts Slack Block Kit payloads to an incoming webhook or channel.
    """

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

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
        Dispatches Block Kit message to Slack webhook endpoint.
        """
        payload = self.build_block_kit_payload(
            day_info=day_info,
            validation_result=validation_result,
            drive_links=drive_links,
            html_preview_url=html_preview_url,
            calendar_link=calendar_link
        )

        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL not configured. Simulating Slack dispatch.")
            return {
                "status": "simulated",
                "payload": payload
            }

        try:
            res = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            if res.status_code == 200:
                logger.info(f"Successfully posted Slack notification for Day {day_info.get('day')}")
                return {"status": "sent", "code": 200}
            else:
                logger.error(f"Slack webhook returned status {res.status_code}: {res.text}")
                return {"status": "error", "code": res.status_code, "text": res.text}
        except Exception as e:
            logger.error(f"Failed to send Slack webhook notification: {e}")
            return {"status": "error", "error": str(e)}
