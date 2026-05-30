import discord
from discord import app_commands
from discord.ext import commands
import os
from datetime import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

warn_db = {}

def success_embed(title, description, author=None):
    embed = discord.Embed(title=title, description=description, color=0x2ecc71, timestamp=datetime.utcnow())
    if author:
        embed.set_footer(text=f"Action by {author}")
    return embed

def error_embed(title, description):
    embed = discord.Embed(title=title, description=description, color=0xe74c3c, timestamp=datetime.utcnow())
    return embed

def warn_embed(title, description, author=None):
    embed = discord.Embed(title=title, description=description, color=0xf39c12, timestamp=datetime.utcnow())
    if author:
        embed.set_footer(text=f"Action by {author}")
    return embed

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the server | /help"))

# ── /ping ──────────────────────────────────────────────────────────────
@bot.tree.command(name="ping", description="Check if the bot is alive")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot is alive! Latency: `{round(bot.latency * 1000)}ms`",
        color=0x3498db,
        timestamp=datetime.utcnow()
    )
    await interaction.response.send_message(embed=embed)

# ── /ban ───────────────────────────────────────────────────────────────
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for the ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member == interaction.user:
        await interaction.response.send_message(embed=error_embed("❌ Error", "You cannot ban yourself."), ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message(embed=error_embed("❌ Error", "You cannot ban someone with an equal or higher role."), ephemeral=True)
        return
    try:
        await member.send(embed=warn_embed(f"🔨 You were banned from {interaction.guild.name}", f"**Reason:** {reason}\n**Banned by:** {interaction.user}"))
    except:
        pass
    await member.ban(reason=reason)
    await interaction.response.send_message(embed=success_embed(
        "🔨 Member Banned",
        f"**User:** {member.mention} (`{member}`)\n**Reason:** {reason}",
        author=interaction.user
    ))

@ban.error
async def ban_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=error_embed("❌ Permission Denied", "You need the **Ban Members** permission."), ephemeral=True)

# ── /kick ──────────────────────────────────────────────────────────────
@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for the kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member == interaction.user:
        await interaction.response.send_message(embed=error_embed("❌ Error", "You cannot kick yourself."), ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message(embed=error_embed("❌ Error", "You cannot kick someone with an equal or higher role."), ephemeral=True)
        return
    try:
        await member.send(embed=warn_embed(f"👢 You were kicked from {interaction.guild.name}", f"**Reason:** {reason}\n**Kicked by:** {interaction.user}"))
    except:
        pass
    await member.kick(reason=reason)
    await interaction.response.send_message(embed=success_embed(
        "👢 Member Kicked",
        f"**User:** {member.mention} (`{member}`)\n**Reason:** {reason}",
        author=interaction.user
    ))

@kick.error
async def kick_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=error_embed("❌ Permission Denied", "You need the **Kick Members** permission."), ephemeral=True)

# ── /mute ──────────────────────────────────────────────────────────────
@bot.tree.command(name="mute", description="Timeout (mute) a member")
@app_commands.describe(member="The member to mute", duration="Duration in minutes (default: 10)", reason="Reason for the mute")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "No reason provided"):
    if member == interaction.user:
        await interaction.response.send_message(embed=error_embed("❌ Error", "You cannot mute yourself."), ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message(embed=error_embed("❌ Error", "You cannot mute someone with an equal or higher role."), ephemeral=True)
        return
    import datetime as dt
    until = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=duration)
    await member.timeout(until, reason=reason)
    await interaction.response.send_message(embed=success_embed(
        "🔇 Member Muted",
        f"**User:** {member.mention} (`{member}`)\n**Duration:** {duration} minute(s)\n**Reason:** {reason}",
        author=interaction.user
    ))
    try:
        await member.send(embed=warn_embed(
            f"🔇 You were muted in {interaction.guild.name}",
            f"**Duration:** {duration} minute(s)\n**Reason:** {reason}\n**Muted by:** {interaction.user}"
        ))
    except:
        pass

@mute.error
async def mute_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=error_embed("❌ Permission Denied", "You need the **Moderate Members** permission."), ephemeral=True)

# ── /warn ──────────────────────────────────────────────────────────────
@bot.tree.command(name="warn", description="Warn a member")
@app_commands.describe(member="The member to warn", reason="Reason for the warning")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member == interaction.user:
        await interaction.response.send_message(embed=error_embed("❌ Error", "You cannot warn yourself."), ephemeral=True)
        return
    user_id = str(member.id)
    guild_id = str(interaction.guild.id)
    if guild_id not in warn_db:
        warn_db[guild_id] = {}
    if user_id not in warn_db[guild_id]:
        warn_db[guild_id][user_id] = []
    warn_db[guild_id][user_id].append({"reason": reason, "by": str(interaction.user), "time": str(datetime.utcnow())})
    count = len(warn_db[guild_id][user_id])
    await interaction.response.send_message(embed=warn_embed(
        "⚠️ Member Warned",
        f"**User:** {member.mention} (`{member}`)\n**Reason:** {reason}\n**Total Warnings:** {count}",
        author=interaction.user
    ))
    try:
        await member.send(embed=warn_embed(
            f"⚠️ You were warned in {interaction.guild.name}",
            f"**Reason:** {reason}\n**Total Warnings:** {count}\n**Warned by:** {interaction.user}"
        ))
    except:
        pass

@warn.error
async def warn_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=error_embed("❌ Permission Denied", "You need the **Kick Members** permission."), ephemeral=True)

# ── /warnings ──────────────────────────────────────────────────────────
@bot.tree.command(name="warnings", description="View all warnings for a member")
@app_commands.describe(member="The member to check warnings for")
@app_commands.checks.has_permissions(kick_members=True)
async def warnings(interaction: discord.Interaction, member: discord.Member):
    user_id = str(member.id)
    guild_id = str(interaction.guild.id)
    warns = warn_db.get(guild_id, {}).get(user_id, [])
    if not warns:
        await interaction.response.send_message(embed=success_embed("✅ No Warnings", f"{member.mention} has no warnings."))
        return
    desc = "\n".join([f"**{i+1}.** {w['reason']} — by {w['by']}" for i, w in enumerate(warns)])
    await interaction.response.send_message(embed=warn_embed("⚠️ Warnings", f"**User:** {member.mention}\n\n{desc}"))

# ── /giverole ──────────────────────────────────────────────────────────
@bot.tree.command(name="giverole", description="Give a role to one member")
@app_commands.describe(member="The member to give the role to", role="The role to give")
@app_commands.checks.has_permissions(manage_roles=True)
async def giverole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message(embed=error_embed("❌ Error", "I cannot assign a role higher than or equal to my own top role."), ephemeral=True)
        return
    if role in member.roles:
        await interaction.response.send_message(embed=error_embed("❌ Error", f"{member.mention} already has the **{role.name}** role."), ephemeral=True)
        return
    await member.add_roles(role)
    await interaction.response.send_message(embed=success_embed(
        "✅ Role Given",
        f"**User:** {member.mention}\n**Role:** {role.mention}",
        author=interaction.user
    ))

@giverole.error
async def giverole_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=error_embed("❌ Permission Denied", "You need the **Manage Roles** permission."), ephemeral=True)

# ── /giveroleall ───────────────────────────────────────────────────────
@bot.tree.command(name="giveroleall", description="Give a role to ALL members in the server")
@app_commands.describe(role="The role to give to everyone")
@app_commands.checks.has_permissions(manage_roles=True)
async def giveroleall(interaction: discord.Interaction, role: discord.Role):
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message(embed=error_embed("❌ Error", "I cannot assign a role higher than or equal to my own top role."), ephemeral=True)
        return
    await interaction.response.send_message(embed=warn_embed("⏳ Processing...", f"Giving **{role.name}** to all members. Please wait..."))
    count = 0
    failed = 0
    for member in interaction.guild.members:
        if role not in member.roles and not member.bot:
            try:
                await member.add_roles(role)
                count += 1
            except:
                failed += 1
    await interaction.edit_original_response(embed=success_embed(
        "✅ Role Given to All",
        f"**Role:** {role.mention}\n**Success:** {count} member(s)\n**Failed:** {failed} member(s)",
        author=interaction.user
    ))

@giveroleall.error
async def giveroleall_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=error_embed("❌ Permission Denied", "You need the **Manage Roles** permission."), ephemeral=True)

# ── /removerole ────────────────────────────────────────────────────────
@bot.tree.command(name="removerole", description="Remove a role from a member")
@app_commands.describe(member="The member to remove the role from", role="The role to remove")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role not in member.roles:
        await interaction.response.send_message(embed=error_embed("❌ Error", f"{member.mention} does not have the **{role.name}** role."), ephemeral=True)
        return
    await member.remove_roles(role)
    await interaction.response.send_message(embed=success_embed(
        "✅ Role Removed",
        f"**User:** {member.mention}\n**Role:** {role.mention}",
        author=interaction.user
    ))

@removerole.error
async def removerole_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(embed=error_embed("❌ Permission Denied", "You need the **Manage Roles** permission."), ephemeral=True)

# ── /help ──────────────────────────────────────────────────────────────
@bot.tree.command(name="help", description="Show all bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 Bot Commands",
        description="Here are all available slash commands:",
        color=0x3498db,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🔨 `/ban @user [reason]`", value="Ban a member from the server", inline=False)
    embed.add_field(name="👢 `/kick @user [reason]`", value="Kick a member from the server", inline=False)
    embed.add_field(name="🔇 `/mute @user [minutes] [reason]`", value="Timeout a member (default: 10 min)", inline=False)
    embed.add_field(name="⚠️ `/warn @user [reason]`", value="Warn a member", inline=False)
    embed.add_field(name="📋 `/warnings @user`", value="View all warnings for a member", inline=False)
    embed.add_field(name="✅ `/giverole @user @role`", value="Give a role to one member", inline=False)
    embed.add_field(name="🌐 `/giveroleall @role`", value="Give a role to ALL members", inline=False)
    embed.add_field(name="❌ `/removerole @user @role`", value="Remove a role from a member", inline=False)
    embed.set_footer(text=f"Requested by {interaction.user}")
    await interaction.response.send_message(embed=embed)

token = os.environ.get("DISCORD_TOKEN")
if not token:
    print("ERROR: DISCORD_TOKEN environment variable not set.")
else:
    bot.run(token)
