import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 👇 Ayarlanabilir ayarlar
WELCOME_MESSAGE = "Selam! Burda doğum gününü kutlayabilirsin 🎂 Unutma: sadece 3 mesaj yazabiliyorsun, sonra kanal kilitleniyor 🔒"
MAX_MESSAGES = 3
CATEGORY_NAME = "Doğum Günü Mesajları"

# Kullanıcı mesaj sayacı
user_message_counts = {}

@bot.event
async def on_ready():
    print(f"✅ Bot giriş yaptı: {bot.user}")

@bot.event
async def on_member_join(member):
    print(f"🟢 {member.name} sunucuya katıldı")
    guild = member.guild

    # Kategori kontrol
    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
    if not category:
        category = await guild.create_category(CATEGORY_NAME)

    # Kanal adı
    channel_name = f"dogum-gunu-{member.name}".lower().replace(" ", "-")

    # Kanal oluştur
    channel = await guild.create_text_channel(channel_name, category=category)

    # Kanal izinlerini ayarla
    await channel.set_permissions(guild.default_role, read_messages=False)  # Diğer herkese kapalı
    await channel.set_permissions(member,
                                   read_messages=True,
                                   send_messages=True,
                                   manage_messages=False,
                                   read_message_history=True)

    # Hoş geldin mesajı
    await channel.send(f"{member.mention} {WELCOME_MESSAGE}")

    # Sayaç başlat
    user_message_counts[channel.id] = {
        "user_id": member.id,
        "count": 0
    }

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot or not message.guild:
        return

    channel_id = message.channel.id
    author_id = message.author.id

    # Eğer takip edilen bir kanal
    if channel_id in user_message_counts:
        data = user_message_counts[channel_id]

        if author_id == data["user_id"]:
            data["count"] += 1
            print(f"{message.author.name} kanalına {data['count']}. mesajı yazdı")

            if data["count"] >= MAX_MESSAGES:
                # Kanalı tamamen gizle
                channel = message.channel
                await channel.set_permissions(message.author, read_messages=False, send_messages=False)
                await channel.send("🔒 3 mesaj sınırına ulaşıldı. Kanal kilitlendi.")
                del user_message_counts[channel_id]

bot.run("BOT TOKEN")
