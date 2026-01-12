import discord
import logging
import requests
from .base import BaseCommandGroup
from utils.config import config


# Grouping of slash commands into a command list
class AnalyticsCommandGroup(BaseCommandGroup):
    def __init__(self, params={}):
        super().__init__(params)

        self.command_list = [
            get_message_stats,
            get_voice_stats,
            get_member_activity,
            export_analytics,
        ]


"""
Get message statistics for the current session
"""


@discord.app_commands.command(
    name="get_message_stats", description="Get message statistics for current session"
)
async def get_message_stats(interaction) -> None:
    try:
        response = requests.get(
            config.jaison_api_endpoint + "/api/analytics/messages"
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        stats = response.get("response", {})
        reply = f"""
**Message Statistics**
Total Messages: {stats.get('total_messages', 0)}
Messages Today: {stats.get('messages_today', 0)}
Average Response Time: {stats.get('avg_response_time', 0):.2f}s
Longest Message: {stats.get('longest_message', 0)} chars
Most Active Hour: {stats.get('most_active_hour', 'N/A')}
        """

        logging.info(f"Message stats retrieved: {stats}")
        await interaction.response.send_message(reply)
    except Exception as err:
        logging.error(f"Failed to get message stats: {str(err)}")
        await interaction.response.send_message(
            f"Failed to get message stats: {str(err)}"
        )


"""
Get voice channel statistics
"""


@discord.app_commands.command(
    name="get_voice_stats", description="Get voice channel statistics"
)
async def get_voice_stats(interaction) -> None:
    try:
        response = requests.get(
            config.jaison_api_endpoint + "/api/analytics/voice"
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        stats = response.get("response", {})
        reply = f"""
**Voice Statistics**
Total Voice Sessions: {stats.get('total_sessions', 0)}
Total Voice Time: {stats.get('total_voice_time', 0)} minutes
Average Session Length: {stats.get('avg_session_length', 0)} minutes
Participants: {stats.get('participants', 0)}
Audio Quality (Avg): {stats.get('avg_quality', 'N/A')}
        """

        logging.info(f"Voice stats retrieved: {stats}")
        await interaction.response.send_message(reply)
    except Exception as err:
        logging.error(f"Failed to get voice stats: {str(err)}")
        await interaction.response.send_message(
            f"Failed to get voice stats: {str(err)}"
        )


"""
Get member activity statistics
"""


@discord.app_commands.command(
    name="get_member_activity", description="Get member activity statistics"
)
async def get_member_activity(interaction) -> None:
    try:
        response = requests.get(
            config.jaison_api_endpoint + "/api/analytics/members"
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        members = response.get("response", [])
        reply = "**Top Members by Activity**\n"
        for i, member in enumerate(members[:10], 1):
            reply += f"{i}. {member.get('name', 'Unknown')}: {member.get('messages', 0)} messages\n"

        logging.info(f"Member activity retrieved")
        await interaction.response.send_message(reply)
    except Exception as err:
        logging.error(f"Failed to get member activity: {str(err)}")
        await interaction.response.send_message(
            f"Failed to get member activity: {str(err)}"
        )


"""
Export analytics as attachment
"""


@discord.app_commands.command(
    name="export_analytics", description="Export analytics data as CSV"
)
async def export_analytics(interaction) -> None:
    try:
        response = requests.get(config.jaison_api_endpoint + "/api/analytics/export")

        if response.status_code != 200:
            raise Exception(f"{response.status_code} {response.reason}")

        # Create a file-like object from the response
        file = discord.File(
            fp=__import__("io").BytesIO(response.content),
            filename="analytics_export.csv",
        )

        logging.info(f"Analytics exported successfully")
        await interaction.response.send_message("Analytics data exported:", file=file)
    except Exception as err:
        logging.error(f"Failed to export analytics: {str(err)}")
        await interaction.response.send_message(
            f"Failed to export analytics: {str(err)}"
        )
