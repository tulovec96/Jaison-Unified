import discord
import logging
import requests
from .base import BaseCommandGroup
from utils.config import config


# Grouping of slash commands into a command list
class ModerationCommandGroup(BaseCommandGroup):
    def __init__(self, params={}):
        super().__init__(params)

        self.command_list = [
            set_activity_filter,
            set_response_tone,
            add_blocked_user,
            remove_blocked_user,
            list_moderation_rules,
        ]


"""
Set activity filter level
"""


@discord.app_commands.command(
    name="set_activity_filter", description="Set activity filter level"
)
async def set_activity_filter(interaction, level: str) -> None:
    try:
        valid_levels = ["strict", "moderate", "relaxed", "none"]
        if level not in valid_levels:
            raise Exception(f"Invalid level. Must be one of: {', '.join(valid_levels)}")

        response = requests.post(
            config.jaison_api_endpoint + "/api/moderation/filter",
            headers={"Content-type": "application/json"},
            json={"level": level},
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        logging.info(f"Activity filter set to: {level}")
        await interaction.response.send_message(f"✓ Activity filter set to **{level}**")
    except Exception as err:
        logging.error(f"Failed to set activity filter: {str(err)}")
        await interaction.response.send_message(
            f"Failed to set activity filter: {str(err)}"
        )


"""
Set response tone/personality
"""


@discord.app_commands.command(
    name="set_response_tone", description="Set response tone/personality"
)
async def set_response_tone(interaction, tone: str) -> None:
    try:
        valid_tones = ["professional", "casual", "humorous", "formal", "friendly"]
        if tone not in valid_tones:
            raise Exception(f"Invalid tone. Must be one of: {', '.join(valid_tones)}")

        response = requests.post(
            config.jaison_api_endpoint + "/api/moderation/tone",
            headers={"Content-type": "application/json"},
            json={"tone": tone},
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        logging.info(f"Response tone set to: {tone}")
        await interaction.response.send_message(f"✓ Response tone set to **{tone}**")
    except Exception as err:
        logging.error(f"Failed to set response tone: {str(err)}")
        await interaction.response.send_message(
            f"Failed to set response tone: {str(err)}"
        )


"""
Add user to blocklist
"""


@discord.app_commands.command(
    name="add_blocked_user", description="Add user to blocklist"
)
async def add_blocked_user(
    interaction, user: discord.User, reason: str = "No reason provided"
) -> None:
    try:
        response = requests.post(
            config.jaison_api_endpoint + "/api/moderation/blocklist",
            headers={"Content-type": "application/json"},
            json={"user_id": str(user.id), "user_name": user.name, "reason": reason},
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        logging.info(f"User {user.name} added to blocklist: {reason}")
        await interaction.response.send_message(
            f"✓ **{user.name}** added to blocklist\nReason: {reason}"
        )
    except Exception as err:
        logging.error(f"Failed to add blocked user: {str(err)}")
        await interaction.response.send_message(
            f"Failed to add blocked user: {str(err)}"
        )


"""
Remove user from blocklist
"""


@discord.app_commands.command(
    name="remove_blocked_user", description="Remove user from blocklist"
)
async def remove_blocked_user(interaction, user: discord.User) -> None:
    try:
        response = requests.delete(
            config.jaison_api_endpoint + f"/api/moderation/blocklist/{user.id}"
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        logging.info(f"User {user.name} removed from blocklist")
        await interaction.response.send_message(
            f"✓ **{user.name}** removed from blocklist"
        )
    except Exception as err:
        logging.error(f"Failed to remove blocked user: {str(err)}")
        await interaction.response.send_message(
            f"Failed to remove blocked user: {str(err)}"
        )


"""
List current moderation rules
"""


@discord.app_commands.command(
    name="list_moderation_rules", description="List current moderation rules"
)
async def list_moderation_rules(interaction) -> None:
    try:
        response = requests.get(
            config.jaison_api_endpoint + "/api/moderation/rules"
        ).json()

        if response["status"] != 200:
            raise Exception(f"{response['status']} {response['message']}")

        rules = response.get("response", {})
        reply = """
**Moderation Rules**
Activity Filter: {activity_filter}
Response Tone: {response_tone}
Blocklist Size: {blocklist_size}
Content Filter: {content_filter}
Auto-Moderation: {auto_mod}
        """.format(
            activity_filter=rules.get("activity_filter", "N/A"),
            response_tone=rules.get("response_tone", "N/A"),
            blocklist_size=rules.get("blocklist_size", 0),
            content_filter=rules.get("content_filter", "Disabled"),
            auto_mod=rules.get("auto_mod", "Disabled"),
        )

        logging.info(f"Moderation rules retrieved")
        await interaction.response.send_message(reply)
    except Exception as err:
        logging.error(f"Failed to list moderation rules: {str(err)}")
        await interaction.response.send_message(
            f"Failed to list moderation rules: {str(err)}"
        )
