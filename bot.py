import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp

TOKEN = "PUT_TOKEN_HERE"

WELCOME_CHANNEL_ID = 1482181191841874021
ADMIN_ID = 1374891505675665420
TOURNAMENT_CHANNEL_ID = 1481072797206712481

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

players = {}

# تشغيل البوت
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot is online as {bot.user}")

# -----------------------------
# شارة المطور
# -----------------------------

@bot.tree.command(name="ping", description="Ping command")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# -----------------------------
# الترحيب
# -----------------------------

@bot.event
async def on_member_join(member):

    role = discord.utils.get(member.guild.roles, name="Member")

    if role:
        await member.add_roles(role)

    try:
        await member.edit(nick=f"BLZ {member.name}")
    except:
        pass

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    embed = discord.Embed(
        title="🎉 عضو جديد!",
        description=f"اهلا {member.mention} في سيرفر **{member.guild.name}**",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📢 الشكاوي",
        value=f"يمكنك الشكايه خلال الادمن <@{ADMIN_ID}>",
        inline=False
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await channel.send(embed=embed)

# -----------------------------
# جدول البطولة
# -----------------------------

def leaderboard():

    sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)

    text = ""

    rank = 1

    for name, points in sorted_players:

        medal = "🏅"

        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"

        text += f"{medal} {rank}. {name} — {points} نقطة\n"

        rank += 1

    if text == "":
        text = "لا يوجد لاعبين"

    return text

# -----------------------------
# مودال إضافة لاعب
# -----------------------------

class AddPlayerModal(discord.ui.Modal, title="اضافة لاعب"):

    player = discord.ui.TextInput(label="اسم اللاعب")

    async def on_submit(self, interaction: discord.Interaction):

        players[self.player.value] = 0

        await interaction.response.send_message(
            f"تم اضافة {self.player.value}",
            ephemeral=True
        )

# -----------------------------
# مودال إضافة نقاط
# -----------------------------

class AddPointsModal(discord.ui.Modal, title="اضافة نقاط"):

    player = discord.ui.TextInput(label="اسم اللاعب")
    points = discord.ui.TextInput(label="النقاط")

    async def on_submit(self, interaction: discord.Interaction):

        name = self.player.value
        pts = int(self.points.value)

        if name not in players:
            await interaction.response.send_message(
                "اللاعب غير موجود",
                ephemeral=True
            )
            return

        players[name] += pts

        embed = discord.Embed(
            title="🏆 جدول البطولة",
            description=leaderboard(),
            color=discord.Color.gold()
        )

        channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)

        await channel.send(embed=embed)

        await interaction.response.send_message(
            "تم تحديث النقاط",
            ephemeral=True
        )

# -----------------------------
# لوحة البطولة
# -----------------------------

class TournamentPanel(discord.ui.View):

    @discord.ui.button(label="اضافة لاعب", style=discord.ButtonStyle.green)
    async def add_player(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(AddPlayerModal())

    @discord.ui.button(label="اضافة نقاط", style=discord.ButtonStyle.blurple)
    async def add_points(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(AddPointsModal())

# -----------------------------
# امر لوحة البطولة
# -----------------------------

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):

    await ctx.message.delete()

    embed = discord.Embed(
        title="🎮 لوحة البطولة",
        description="اختر العملية",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed, view=TournamentPanel())

# -----------------------------
# الموسيقى
# -----------------------------

@bot.command()
async def play(ctx, *, search):

    if ctx.author.voice is None:
        await ctx.send("ادخل كول الاول")
        return

    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()

    ydl_opts = {'format': 'bestaudio'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]

        url = info['url']

        vc.play(discord.FFmpegPCMAudio(url))

        await ctx.send(f"🎵 شغلت: {info['title']}")

@bot.command()
@commands.has_permissions(administrator=True)
async def room(ctx, room_number, password):

    # حذف رسالة الامر
    await ctx.message.delete()

    embed = discord.Embed(
        title="🚨 بدأ الروم الآن!",
        description="لقد بدأ الروم الآن يا شباب",
        color=discord.Color.red()
    )

    embed.add_field(
        name="🎮 رقم الروم",
        value=room_number,
        inline=False
    )

    embed.add_field(
        name="🔑 الباسورد",
        value=password,
        inline=False
    )

    embed.set_footer(text="BLZ ESPORTS")

    await ctx.send("@everyone", embed=embed)


bot.run(TOKEN)
