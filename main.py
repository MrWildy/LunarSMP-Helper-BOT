import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import datetime
import asyncio

# =====================
# LOAD TOKEN
# =====================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# =====================
# CONFIG
# =====================
ALLOWED_GUILD_NAME = "Lunar_SMP"
WELCOME_CHANNEL_NAME = "🚪┃welcome"
GUILD_ID = 1456318479396507651  # YOUR SERVER ID
MY_GUILD = discord.Object(id=GUILD_ID)


OWNER_ROLE_ID = 1456320973761548308
MANAGER_ROLE_ID = 1457419886753091828
MOD_LOG_CHANNEL_ID = 1457456683713302609

# =====================
# FILTER / FUN
# =====================
BAD_WORDS = [
    "nigger", "nigga", "faggot", "retard",
    "no father", "kill yourself", "mf",
    "motherfucker", "mother fucker",
    "no mother", "fatherless",
]

HELLO_TRIGGERS = ["hello", "hi", "hey", "yo"]
HELLO_RESPONSES = [
    "Hey 👋",
    "Yo, what’s up?",
    "Hello 😄",
    "Sup 👀",
    "Hey there!"
]

ROASTS = [
    "You bring everyone together, just to talk about you.",
    "Your brain has left the chat.",
    "You have the personality of unseasoned chicken.",
    "You’re like Wi-Fi with one bar, disappointing.",
    "Somewhere out there is a tree producing oxygen for you. You owe it an apology.",
    "You're not stupid, you just have bad luck thinking.",
    "Your brain is on airplane mode.",
    "I'd explain it to you but I left my patience at home.",
    "You're proof that confidence doesn't require intelligence.",
    "You have the personality of a loading screen.",
    "Your thoughts run on dial-up.",
    "You make silence uncomfortable.",
    "You're like a broken calculator, always wrong.",
    "I've seen smarter conversations with a wall.",
    "You have main character energy in a background role.",
    "Your opinions are like pop-up ads, nobody asked.",
    "You're not useless, but you could be replaced by a rock.",
    "Your brain skipped the tutorial.",
    "You bring nothing to the table except crumbs.",
    "You have the confidence of someone who never checks facts.",
]

# =====================
# INTENTS
# =====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# PERMISSIONS
# =====================
def is_admin(member: discord.Member) -> bool:
    return any(r.id in (OWNER_ROLE_ID, MANAGER_ROLE_ID) for r in member.roles)

# =====================
# EMBEDS
# =====================
def dm_action_embed(action, guild, user, reason=None, duration=None, color=discord.Color.red()):
    embed = discord.Embed(
        title=f"🚨 Moderation Notice: {action}",
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else user.display_avatar.url)
    embed.add_field(name="Server", value=guild.name, inline=False)
    embed.add_field(name="Action", value=action, inline=False)

    if duration:
        embed.add_field(name="Duration", value=duration, inline=False)

    embed.add_field(
        name="Reason",
        value=reason if reason else "No reason provided",
        inline=False
    )
    embed.set_footer(text="This action was taken by the server staff.")
    return embed


def mod_log_embed(action, member, moderator, reason=None, duration=None, color=discord.Color.orange()):
    embed = discord.Embed(
        title=f"📋 Moderation Log: {action}",
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=f"{moderator} ({moderator.id})", inline=False)

    if duration:
        embed.add_field(name="Duration", value=duration, inline=False)

    embed.add_field(
        name="Reason",
        value=reason if reason else "No reason provided",
        inline=False
    )
    return embed

# =====================
# EVENTS
# =====================
@bot.event
async def on_ready():
    bot.tree.clear_commands(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print("✅ Commands force-resynced to guild")

@bot.event
async def on_guild_join(guild):
    if guild.name != ALLOWED_GUILD_NAME:
        await guild.leave()

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        embed = discord.Embed(
            title="🎉 Welcome!",
            description=f"Welcome to **{member.guild.name}**, {member.mention}!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    lower = message.content.lower()

    for word in BAD_WORDS:
        if word in lower:
            await message.delete()
            try:
                await message.author.send(
                    embed=dm_action_embed(
                        "Message Removed",
                        message.guild,
                        message.author,
                        reason="Use of prohibited language",
                        color=discord.Color.orange()
                    )
                )
            except:
                pass
            return

    if lower in HELLO_TRIGGERS:
        await message.channel.send(random.choice(HELLO_RESPONSES))

    await bot.process_commands(message)

# =====================
# FUN
# =====================
@bot.tree.command(name="roast")
async def roast(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(
        title="🔥 Roast",
        description=f"{member.mention}\n\n**{random.choice(ROASTS)}**",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed)

# =====================
# MOD COMMANDS
# =====================
async def send_mod_log(guild, embed):
    channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

@bot.tree.command(name="warn")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    try:
        await member.send(
            embed=dm_action_embed("Warning", interaction.guild, member, reason, color=discord.Color.orange())
        )
    except:
        pass

    await send_mod_log(
        interaction.guild,
        mod_log_embed("Warn", member, interaction.user, reason)
    )

    await interaction.response.send_message("✅ Warning issued.", ephemeral=True)

@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    try:
        await member.send(
            embed=dm_action_embed("Kick", interaction.guild, member, reason)
        )
    except:
        pass

    await member.kick(reason=reason)

    await send_mod_log(
        interaction.guild,
        mod_log_embed("Kick", member, interaction.user, reason, color=discord.Color.red())
    )

    await interaction.response.send_message("✅ User kicked.", ephemeral=True)

@bot.tree.command(name="mute")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = None):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    duration = f"{minutes} minutes"
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)

    try:
        await member.send(
            embed=dm_action_embed("Mute", interaction.guild, member, reason, duration)
        )
    except:
        pass

    await send_mod_log(
        interaction.guild,
        mod_log_embed("Mute", member, interaction.user, reason, duration)
    )

    await interaction.response.send_message("✅ User muted.", ephemeral=True)

@bot.tree.command(name="unmute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await member.timeout(None)

    try:
        await member.send(
            embed=dm_action_embed("Unmute", interaction.guild, member, "Mute removed", color=discord.Color.green())
        )
    except:
        pass

    await send_mod_log(
        interaction.guild,
        mod_log_embed("Unmute", member, interaction.user, "Mute removed", color=discord.Color.green())
    )

    await interaction.response.send_message("✅ User unmuted.", ephemeral=True)

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member, minutes: int = None, reason: str = None):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    duration = f"{minutes} minutes" if minutes else "Permanent"

    try:
        await member.send(
            embed=dm_action_embed("Ban", interaction.guild, member, reason, duration)
        )
    except:
        pass

    await interaction.guild.ban(member, reason=reason)

    await send_mod_log(
        interaction.guild,
        mod_log_embed("Ban", member, interaction.user, reason, duration, discord.Color.dark_red())
    )

    await interaction.response.send_message("✅ User banned.", ephemeral=True)

    if minutes:
        await asyncio.sleep(minutes * 60)
        await interaction.guild.unban(member)

@bot.tree.command(name="unban")
async def unban(interaction: discord.Interaction, user_id: str):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)

    try:
        await user.send(
            embed=dm_action_embed("Unban", interaction.guild, user, "Ban removed", color=discord.Color.green())
        )
    except:
        pass

    await send_mod_log(
        interaction.guild,
        mod_log_embed("Unban", user, interaction.user, "Ban removed", color=discord.Color.green())
    )

    await interaction.response.send_message("✅ User unbanned.", ephemeral=True)

@bot.tree.command(name="message")
async def message(interaction: discord.Interaction, member: discord.Member, title: str, message: str):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    try:
        embed = discord.Embed(
            title=title,
            description=message,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Message from {interaction.guild.name} staff")
        await member.send(embed=embed)
        await interaction.response.send_message("✅ Message sent.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Could not DM user.", ephemeral=True)

# =====================
# RUN
# =====================
bot.run(TOKEN)
