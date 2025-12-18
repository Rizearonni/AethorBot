import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime

from src.utils.store import (
    add_to_whitelist,
    remove_from_whitelist,
    read_whitelist,
)
from src.utils import rcon
from src.config import AUTO_SYNC_ENABLED, AUTO_SYNC_HOUR, AUTO_SYNC_MINUTE, AUTO_SYNC_REMOVE_EXTRAS, LOG_CHANNEL_ID, SYNC_COOLDOWN_SECONDS


class Management(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if AUTO_SYNC_ENABLED:
            self.auto_sync_loop.start()
        self._sync_last: dict[int, datetime.datetime] = {}

    def _cooldown_remaining(self, user_id: int) -> int:
        last = self._sync_last.get(user_id)
        if not last:
            return 0
        delta = datetime.datetime.now() - last
        remaining = SYNC_COOLDOWN_SECONDS - int(delta.total_seconds())
        return remaining if remaining > 0 else 0

    # Role management (prefix)
    @commands.command(name="rolegrant")
    @commands.has_permissions(administrator=True)
    async def role_grant_prefix(self, ctx: commands.Context, role: discord.Role, member: discord.Member | None = None):
        target = member or ctx.author
        try:
            await target.add_roles(role, reason=f"Granted by {ctx.author}")
            await ctx.reply(f"Granted role {role.mention} to {target.mention}.")
        except Exception as e:
            await ctx.reply(f"Failed to grant role: {e}")

    @commands.command(name="rolerevoke")
    @commands.has_permissions(administrator=True)
    async def role_revoke_prefix(self, ctx: commands.Context, role: discord.Role, member: discord.Member | None = None):
        target = member or ctx.author
        try:
            await target.remove_roles(role, reason=f"Revoked by {ctx.author}")
            await ctx.reply(f"Revoked role {role.mention} from {target.mention}.")
        except Exception as e:
            await ctx.reply(f"Failed to revoke role: {e}")

    # Role management (slash)
    @app_commands.command(name="role_grant", description="Grant a role to a member")
    @app_commands.default_permissions(administrator=True)
    async def role_grant_slash(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member | None = None):
        target = member or interaction.user
        try:
            await target.add_roles(role, reason=f"Granted by {interaction.user}")
            await interaction.response.send_message(f"Granted role {role.mention} to {target.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to grant role: {e}", ephemeral=True)

    @app_commands.command(name="role_revoke", description="Revoke a role from a member")
    @app_commands.default_permissions(administrator=True)
    async def role_revoke_slash(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member | None = None):
        target = member or interaction.user
        try:
            await target.remove_roles(role, reason=f"Revoked by {interaction.user}")
            await interaction.response.send_message(f"Revoked role {role.mention} from {target.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to revoke role: {e}", ephemeral=True)

    # Whitelist management (prefix)
    @commands.command(name="wladd")
    @commands.has_permissions(administrator=True)
    async def wl_add_prefix(self, ctx: commands.Context, name: str):
        ok = add_to_whitelist(name)
        msg = f"Added `{name}` to whitelist." if ok else f"`{name}` already in whitelist or invalid."
        if ok and rcon.is_enabled():
            try:
                r = rcon.whitelist_add(name)
                msg += f"\nRCON: {r}"
            except Exception as e:
                msg += f"\nRCON failed: {e}"
        await ctx.reply(msg)

    @commands.command(name="wlremove")
    @commands.has_permissions(administrator=True)
    async def wl_remove_prefix(self, ctx: commands.Context, name: str):
        ok = remove_from_whitelist(name)
        msg = f"Removed `{name}` from whitelist." if ok else f"`{name}` not found in whitelist."
        if ok and rcon.is_enabled():
            try:
                r = rcon.whitelist_remove(name)
                msg += f"\nRCON: {r}"
            except Exception as e:
                msg += f"\nRCON failed: {e}"
        await ctx.reply(msg)

    @commands.command(name="wllist")
    @commands.has_permissions(administrator=True)
    async def wl_list_prefix(self, ctx: commands.Context):
        wl = read_whitelist()
        if not wl:
            await ctx.reply("Whitelist is empty.")
            return
        content = "\n".join(wl[:100])
        await ctx.reply(f"Whitelist ({len(wl)}):\n{content}")

    # Whitelist management (slash)
    @app_commands.command(name="whitelist_add", description="Add a Minecraft name to whitelist")
    @app_commands.default_permissions(administrator=True)
    async def wl_add_slash(self, interaction: discord.Interaction, name: str):
        ok = add_to_whitelist(name)
        msg = f"Added `{name}` to whitelist." if ok else f"`{name}` already in whitelist or invalid."
        if ok and rcon.is_enabled():
            try:
                r = rcon.whitelist_add(name)
                msg += f"\nRCON: {r}"
            except Exception as e:
                msg += f"\nRCON failed: {e}"
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="whitelist_remove", description="Remove a Minecraft name from whitelist")
    @app_commands.default_permissions(administrator=True)
    async def wl_remove_slash(self, interaction: discord.Interaction, name: str):
        ok = remove_from_whitelist(name)
        msg = f"Removed `{name}` from whitelist." if ok else f"`{name}` not found in whitelist."
        if ok and rcon.is_enabled():
            try:
                r = rcon.whitelist_remove(name)
                msg += f"\nRCON: {r}"
            except Exception as e:
                msg += f"\nRCON failed: {e}"
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="whitelist_list_server", description="List whitelisted names via RCON")
    @app_commands.default_permissions(administrator=True)
    async def wl_list_server_slash(self, interaction: discord.Interaction):
        if not rcon.is_enabled():
            await interaction.response.send_message("RCON not enabled.", ephemeral=True)
            return
        try:
            names = rcon.whitelist_list()
            if not names:
                await interaction.response.send_message("Server whitelist is empty.", ephemeral=True)
                return
            content = "\n".join(names[:100])
            await interaction.response.send_message(f"Server whitelist ({len(names)}):\n{content}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"RCON failed: {e}", ephemeral=True)

    # Scheduled auto-sync via tasks.loop
    @tasks.loop(time=datetime.time(hour=AUTO_SYNC_HOUR, minute=AUTO_SYNC_MINUTE))
    async def auto_sync_loop(self):
        if not rcon.is_enabled():
            # Optionally announce skipped run
            if LOG_CHANNEL_ID:
                chan = self.bot.get_channel(LOG_CHANNEL_ID)
                if isinstance(chan, discord.TextChannel):
                    try:
                        await chan.send("[Aethor] Nightly whitelist sync skipped: RCON disabled.")
                    except Exception:
                        pass
            return

        local = set(read_whitelist())
        try:
            server = set(rcon.whitelist_list())
        except Exception:
            # Optionally announce error
            if LOG_CHANNEL_ID:
                chan = self.bot.get_channel(LOG_CHANNEL_ID)
                if isinstance(chan, discord.TextChannel):
                    try:
                        await chan.send("[Aethor] Nightly whitelist sync failed: unable to fetch server list via RCON.")
                    except Exception:
                        pass
            return

        to_add = sorted(local - server)
        to_remove = sorted(server - local) if AUTO_SYNC_REMOVE_EXTRAS else []

        added = 0
        removed = 0
        for name in to_add:
            try:
                rcon.whitelist_add(name)
                added += 1
            except Exception:
                pass
        for name in to_remove:
            try:
                rcon.whitelist_remove(name)
                removed += 1
            except Exception:
                pass

        if LOG_CHANNEL_ID:
            chan = self.bot.get_channel(LOG_CHANNEL_ID)
            if isinstance(chan, discord.TextChannel):
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                msg = (
                    f"[Aethor] Nightly whitelist sync ({ts})\n"
                    f"Added: {added} (local→server)\n"
                    f"Removed: {removed}{' (extras pruned)' if AUTO_SYNC_REMOVE_EXTRAS else ''}"
                )
                try:
                    await chan.send(msg)
                except Exception:
                    pass

    @auto_sync_loop.before_loop
    async def before_auto_sync(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="whitelist_list", description="List whitelisted Minecraft names")
    @app_commands.default_permissions(administrator=True)
    async def wl_list_slash(self, interaction: discord.Interaction):
        wl = read_whitelist()
        if not wl:
            await interaction.response.send_message("Whitelist is empty.", ephemeral=True)
            return
        content = "\n".join(wl[:100])
        await interaction.response.send_message(f"Whitelist ({len(wl)}):\n{content}", ephemeral=True)

    # Sync local whitelist with server via RCON
    @commands.command(name="wlsync")
    @commands.has_permissions(administrator=True)
    async def wl_sync_prefix(self, ctx: commands.Context, remove_extras: bool = False):
        rem = self._cooldown_remaining(ctx.author.id)
        if rem > 0:
            await ctx.reply(f"Sync is rate-limited. Try again in {rem}s.")
            return
        if not rcon.is_enabled():
            await ctx.reply("RCON not enabled.")
            return
        local = set(read_whitelist())
        try:
            server = set(rcon.whitelist_list())
        except Exception as e:
            await ctx.reply(f"RCON failed: {e}")
            return

        to_add = sorted(local - server)
        to_remove = sorted(server - local) if remove_extras else []

        added, removed, add_errs, remove_errs = 0, 0, [], []
        for name in to_add:
            try:
                rcon.whitelist_add(name)
                added += 1
            except Exception as e:
                add_errs.append(f"{name}: {e}")

        for name in to_remove:
            try:
                rcon.whitelist_remove(name)
                removed += 1
            except Exception as e:
                remove_errs.append(f"{name}: {e}")

        summary = [
            f"Added: {added} (pending: {len(to_add)})",
            f"Removed: {removed}{' (extras only)' if remove_extras else ''}",
        ]
        if add_errs:
            summary.append("Add errors: " + "; ".join(add_errs[:5]))
        if remove_errs:
            summary.append("Remove errors: " + "; ".join(remove_errs[:5]))

        await ctx.reply("Sync complete.\n" + "\n".join(summary))
        self._sync_last[ctx.author.id] = datetime.datetime.now()

        if LOG_CHANNEL_ID:
            chan = self.bot.get_channel(LOG_CHANNEL_ID)
            if isinstance(chan, discord.TextChannel):
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                msg = (
                    f"[Aethor] Manual whitelist sync by {ctx.author.mention} ({ts})\n"
                    + "\n".join(summary)
                )
                try:
                    await chan.send(msg)
                except Exception:
                    pass

    @app_commands.command(name="whitelist_sync", description="Sync local whitelist to server via RCON")
    @app_commands.default_permissions(administrator=True)
    async def wl_sync_slash(self, interaction: discord.Interaction, remove_extras: bool = False):
        rem = self._cooldown_remaining(interaction.user.id)
        if rem > 0:
            await interaction.response.send_message(f"Sync is rate-limited. Try again in {rem}s.", ephemeral=True)
            return
        if not rcon.is_enabled():
            await interaction.response.send_message("RCON not enabled.", ephemeral=True)
            return
        local = set(read_whitelist())
        try:
            server = set(rcon.whitelist_list())
        except Exception as e:
            await interaction.response.send_message(f"RCON failed: {e}", ephemeral=True)
            return

        to_add = sorted(local - server)
        to_remove = sorted(server - local) if remove_extras else []

        added, removed, add_errs, remove_errs = 0, 0, [], []
        for name in to_add:
            try:
                rcon.whitelist_add(name)
                added += 1
            except Exception as e:
                add_errs.append(f"{name}: {e}")

        for name in to_remove:
            try:
                rcon.whitelist_remove(name)
                removed += 1
            except Exception as e:
                remove_errs.append(f"{name}: {e}")

        summary = [
            f"Added: {added} (pending: {len(to_add)})",
            f"Removed: {removed}{' (extras only)' if remove_extras else ''}",
        ]
        if add_errs:
            summary.append("Add errors: " + "; ".join(add_errs[:5]))
        if remove_errs:
            summary.append("Remove errors: " + "; ".join(remove_errs[:5]))

        await interaction.response.send_message("Sync complete.\n" + "\n".join(summary), ephemeral=True)
        self._sync_last[interaction.user.id] = datetime.datetime.now()

        if LOG_CHANNEL_ID:
            chan = self.bot.get_channel(LOG_CHANNEL_ID)
            if isinstance(chan, discord.TextChannel):
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                msg = (
                    f"[Aethor] Manual whitelist sync by {interaction.user.mention} ({ts})\n"
                    + "\n".join(summary)
                )
                try:
                    await chan.send(msg)
                except Exception:
                    pass

    # Diff-only commands (no changes applied)
    @commands.command(name="wldiff")
    @commands.has_permissions(administrator=True)
    async def wl_diff_prefix(self, ctx: commands.Context):
        if not rcon.is_enabled():
            await ctx.reply("RCON not enabled.")
            return
        local = set(read_whitelist())
        try:
            server = set(rcon.whitelist_list())
        except Exception as e:
            await ctx.reply(f"RCON failed: {e}")
            return
        to_add = sorted(local - server)
        to_remove = sorted(server - local)
        lines = [
            f"Would add ({len(to_add)}): " + ", ".join(to_add[:20]),
            f"Would remove ({len(to_remove)}): " + ", ".join(to_remove[:20]),
        ]
        await ctx.reply("Diff preview:\n" + "\n".join(lines))

    @app_commands.command(name="whitelist_diff", description="Preview local vs server whitelist changes")
    @app_commands.default_permissions(administrator=True)
    async def wl_diff_slash(self, interaction: discord.Interaction):
        if not rcon.is_enabled():
            await interaction.response.send_message("RCON not enabled.", ephemeral=True)
            return
        local = set(read_whitelist())
        try:
            server = set(rcon.whitelist_list())
        except Exception as e:
            await interaction.response.send_message(f"RCON failed: {e}", ephemeral=True)
            return
        to_add = sorted(local - server)
        to_remove = sorted(server - local)
        lines = [
            f"Would add ({len(to_add)}): " + ", ".join(to_add[:20]),
            f"Would remove ({len(to_remove)}): " + ", ".join(to_remove[:20]),
        ]
        await interaction.response.send_message("Diff preview:\n" + "\n".join(lines), ephemeral=True)

    # Status commands
    def _next_sync_text(self) -> str:
        if not AUTO_SYNC_ENABLED:
            return "disabled"
        now = datetime.datetime.now()
        target = now.replace(hour=AUTO_SYNC_HOUR, minute=AUTO_SYNC_MINUTE, second=0, microsecond=0)
        if target <= now:
            target = target + datetime.timedelta(days=1)
        return target.strftime("%Y-%m-%d %H:%M")

    @commands.command(name="status")
    async def status_prefix(self, ctx: commands.Context):
        local_count = len(read_whitelist())
        server_count = "N/A"
        if rcon.is_enabled():
            try:
                server_count = str(len(rcon.whitelist_list()))
            except Exception:
                server_count = "error"
        lines = [
            f"RCON: {'enabled' if rcon.is_enabled() else 'disabled'}",
            f"Next auto-sync: {self._next_sync_text()}",
            f"Local whitelist: {local_count}",
            f"Server whitelist: {server_count}",
        ]
        await ctx.reply("Status:\n" + "\n".join(lines))

    @app_commands.command(name="status", description="Show bot status (RCON, sync time, whitelist counts)")
    async def status_slash(self, interaction: discord.Interaction):
        local_count = len(read_whitelist())
        server_count = "N/A"
        if rcon.is_enabled():
            try:
                server_count = str(len(rcon.whitelist_list()))
            except Exception:
                server_count = "error"
        lines = [
            f"RCON: {'enabled' if rcon.is_enabled() else 'disabled'}",
            f"Next auto-sync: {self._next_sync_text()}",
            f"Local whitelist: {local_count}",
            f"Server whitelist: {server_count}",
        ]
        await interaction.response.send_message("Status:\n" + "\n".join(lines), ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Management(bot))
