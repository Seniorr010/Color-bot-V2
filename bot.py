import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# .env faylından tokeni yüklə
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

COLORS = {
    # Standart vs Tünd versiyalar
    "Red":          ("🔴", (255, 0,   0)),
    "Dark Red":     ("🩸", (139, 0,   0)),
    "Green":        ("🟢", (0,   255, 0)),
    "Dark Green":   ("🌲", (0,   100, 0)),
    "Blue":         ("🔵", (0,   0,   255)),
    "Dark Blue":    ("🎆", (0,   0,   139)),
    "Orange":       ("🟠", (255, 165, 0)),
    "Brown":        ("🟤", (139, 69, 19)),
    "Purple":       ("🟣", (128, 0,   128)),
    "Indigo":       ("🌌", (75,  0,   130)),
    "Pink":         ("🩷", (255, 192, 203)),
    "Hot Pink":     ("💖", (255, 20,  147)),
    "Yellow":       ("🟡", (255, 255, 0)),
    "Gold":         ("🏆", (255, 215, 0)),
    "Cyan":         ("🌐", (0,   255, 255)),
    "Dark Cyan":    ("🧪", (0,   139, 139)),
    "Gray":         ("🩶", (128, 128, 128)),
    "Dark Gray":    ("🔘", (169, 169, 169)),
    "White":        ("⚪", (255, 255, 255)),
    "Black":        ("⚫", (1,   1,   1)),
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def get_or_create_role(guild, name, color):
    role = discord.utils.get(guild.roles, name=name)
    if role is None:
        role = await guild.create_role(name=name, color=color, reason="Color Bot")
    
    # Rolun mövqeyini botun rolunun tam altına qoyuruq ki hər kəsə verə bilsin
    try:
        bot_role = guild.me.top_role
        if role.position != bot_role.position - 1:
            await role.edit(position=bot_role.position - 1)
    except Exception as e:
        print(f"⚠️ Rol mövqeyi dəyişdirilə bilmədi: {e}")
        
    return role


async def remove_color_roles(member):
    """Bütün mövcud rəng rollarını silir."""
    names = set(COLORS.keys())
    to_remove = [r for r in member.roles if r.name in names]
    if to_remove:
        await member.remove_roles(*to_remove, reason="Rəng dəyişdirildi və ya silindi")


class ColorButton(discord.ui.Button):
    def __init__(self, label, emoji, rgb):
        # Bütün düymələr eyni (Primary/Göy) rəngdə olacaq
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.primary, custom_id=f"color_btn_{label}")
        self.rgb = rgb

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        role_name = self.label
        had_this_role = any(r.name == role_name for r in interaction.user.roles)
        
        await remove_color_roles(interaction.user)
        
        if had_this_role:
            await interaction.followup.send(f"❌ **{role_name}** removed.", ephemeral=True)
        else:
            # Rəng məlumatını tapırıq
            _, rgb_color = COLORS[role_name]
            dc = discord.Color.from_rgb(*rgb_color)
            role = await get_or_create_role(interaction.guild, role_name, dc)
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"✅ **{role_name}** set!", ephemeral=True)


class ColorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for label, (emoji, rgb) in COLORS.items():
            self.add_item(ColorButton(label=label, emoji=emoji, rgb=rgb))


@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Slash əmrlərini serverdə anında qeydiyyata alır."""
    await ctx.send("⏳ Syncing commands, please wait...")
    try:
        fmt = await bot.tree.sync()
        await ctx.send(f"✅ {len(fmt)} commands synced successfully.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


@bot.command(name="reng")
@commands.has_permissions(manage_roles=True)
async def prefix_reng(ctx):
    """Klassik !reng əmri panelini göndər."""
    embed = discord.Embed(
        title="✨ Pick Your Color",
        description=(
            "Click a button below to change your name color.\n\n"
            "• You can only have one color at a time.\n"
            "• Click the same color again to remove it.\n"
            "• Clicking another color will automatically replace the old one."
        ),
        color=discord.Color.from_rgb(255, 215, 0) # Gold Color
    )
    await ctx.send(embed=embed, view=ColorView())


@bot.tree.command(name="reng", description="Send the color selection panel")
@app_commands.checks.has_permissions(manage_roles=True)
async def reng(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ Pick Your Color",
        description=(
            "Click a button below to change your name color.\n\n"
            "• You can only have one color at a time.\n"
            "• Click the same color again to remove it.\n"
            "• Clicking another color will automatically replace the old one."
        ),
        color=discord.Color.from_rgb(255, 215, 0) # Gold Color
    )
    await interaction.response.send_message(embed=embed, view=ColorView())


@bot.event
async def on_ready():
    bot.add_view(ColorView())
    print(f"✅ Bot is online: {bot.user}")
    print("ℹ️ Type !sync in a channel to register slash commands.")


if __name__ == "__main__":
    if not TOKEN:
        print("❌ SƏHV: .env faylında DISCORD_TOKEN tapılmadı!")
    else:
        bot.run(TOKEN)
