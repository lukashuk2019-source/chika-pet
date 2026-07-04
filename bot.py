import asyncio
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


TOKEN = "8744326055:AAEVJS7uxq-cebQZTwr3Gpx2hupvriqA79Y"

# Для реального Telegram Mini App нужна HTTPS-ссылка.
# Потом сюда вставишь ссылку с хостинга/ngrok.
WEB_APP_URL = "https://chika-pet.vercel.app"

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chika Streak</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
body{
  margin:0;
  font-family:Arial,sans-serif;
  background:linear-gradient(180deg,#fff3bd,#ffb347);
  color:#2b1800;
  text-align:center;
  padding:18px;
}
.card{
  background:rgba(255,255,255,.65);
  border-radius:28px;
  padding:22px;
  box-shadow:0 15px 35px rgba(0,0,0,.2);
}
.pet{
  font-size:110px;
  animation:float 2s infinite ease-in-out;
}
@keyframes float{
  0%{transform:translateY(0) rotate(-3deg)}
  50%{transform:translateY(-12px) rotate(3deg)}
  100%{transform:translateY(0) rotate(-3deg)}
}
input,button{
  width:92%;
  padding:15px;
  margin:8px 0;
  border-radius:18px;
  border:0;
  font-size:16px;
}
button{
  background:#ff8500;
  color:white;
  font-weight:bold;
  box-shadow:0 7px 0 #b95c00;
}
button:active{
  transform:translateY(4px);
  box-shadow:0 3px 0 #b95c00;
}
.bar{
  width:92%;
  height:18px;
  background:#0002;
  border-radius:20px;
  margin:12px auto;
  overflow:hidden;
}
.fill{
  height:100%;
  width:0%;
  background:linear-gradient(90deg,#ff6a00,#ffe600);
  transition:.5s;
}
.small{opacity:.75;font-size:14px}
</style>
</head>
<body>

<div class="card">
  <h1>🐣 Chika Streak</h1>
  <p>Создай общего Чику с другом. Кормите его каждый день и держите стрик.</p>

  <div id="setup">
    <input id="friend" placeholder="@username друга">
    <input id="petName" placeholder="Имя питомца, например Боба">
    <button onclick="createPet()">➕ Создать питомца</button>
    <button onclick="inviteFriend()">📨 Пригласить друга</button>
    <p class="small">Официально персонаж — Чика, но имя можно поставить любое.</p>
  </div>

  <div id="game" style="display:none;">
    <div class="pet" id="petEmoji">🥚</div>
    <h2 id="name">Чика</h2>
    <p id="friendText"></p>
    <h3 id="stage">Стадия: Яйцо</h3>

    <p>🔥 Стрик: <b id="streak">0</b> дней</p>
    <p>🍗 Кормлений: <b id="feeds">0</b></p>

    <div class="bar"><div class="fill" id="progress"></div></div>

    <button onclick="feedPet()">🍗 Покормить</button>
    <button onclick="trainPet()">💪 Тренировка</button>
    <button onclick="petPet()">❤️ Погладить</button>
    <button onclick="inviteFriend()">📨 Позвать друга</button>
    <button onclick="resetPet()">🗑 Сбросить тест</button>
  </div>
</div>

<script>
const tg = window.Telegram.WebApp;
tg.expand();

let pet = JSON.parse(localStorage.getItem("chika_pet")) || null;

function save(){
  localStorage.setItem("chika_pet", JSON.stringify(pet));
}

function createPet(){
  const friend = document.getElementById("friend").value || "@friend";
  const name = document.getElementById("petName").value || "Чика";

  pet = {
    name:name,
    friend:friend,
    streak:0,
    feeds:0,
    strength:0,
    joy:50,
    lastFeed:""
  };

  save();
  render();
}

function getStage(feeds){
  if(feeds < 5) return ["🥚","Яйцо",20];
  if(feeds < 15) return ["🐣","Птенец",45];
  if(feeds < 30) return ["🐥","Молодой Чика",70];
  if(feeds < 60) return ["🐔","Взрослый Чика",90];
  return ["👑","Легендарный Чика",100];
}

function feedPet(){
  const today = new Date().toDateString();

  if(pet.lastFeed === today){
    alert("Сегодня уже покормили 🍗");
    return;
  }

  pet.lastFeed = today;
  pet.feeds += 1;
  pet.streak += 1;
  pet.joy = Math.min(100, pet.joy + 10);

  save();
  render();

  tg.HapticFeedback.impactOccurred("medium");
}

function trainPet(){
  pet.strength += 1;
  pet.joy = Math.min(100, pet.joy + 5);
  save();
  render();
  alert("💪 Чика стал сильнее!");
}

function petPet(){
  pet.joy = Math.min(100, pet.joy + 15);
  save();
  render();
  alert("❤️ Чика доволен!");
}

function inviteFriend(){
  const text = encodeURIComponent("🐣 Давай растить общего Чику и держать стрик вместе!");
  const url = encodeURIComponent("https://t.me/ChikaStreakBot");
  window.open(`https://t.me/share/url?url=${url}&text=${text}`, "_blank");
}

function resetPet(){
  localStorage.removeItem("chika_pet");
  pet = null;
  render();
}

function render(){
  if(!pet){
    document.getElementById("setup").style.display = "block";
    document.getElementById("game").style.display = "none";
    return;
  }

  const [emoji, stage, progress] = getStage(pet.feeds);

  document.getElementById("setup").style.display = "none";
  document.getElementById("game").style.display = "block";

  document.getElementById("petEmoji").innerText = emoji;
  document.getElementById("name").innerText = pet.name;
  document.getElementById("friendText").innerText = "Питомец с другом: " + pet.friend;
  document.getElementById("stage").innerText = "Стадия: " + stage;
  document.getElementById("streak").innerText = pet.streak;
  document.getElementById("feeds").innerText = pet.feeds;
  document.getElementById("progress").style.width = progress + "%";
}

render();
</script>
</body>
</html>
"""


@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🐣 Открыть Chika App",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ])

    await message.answer(
        "🐣 <b>Добро пожаловать в Chika Streak!</b>\n\n"
        "Хочешь завести своего Чику и растить его вместе с другом?\n\n"
        "Создайте общего питомца, кормите его каждый день, держите стрик "
        "и открывайте новые стадии роста.\n\n"
        "Нажми кнопку ниже, чтобы открыть мини-приложение 👇",
        reply_markup=kb
    )


async def web_index(request):
    return web.Response(text=HTML, content_type="text/html")


async def start_web():
    app = web.Application()
    app.router.add_get("/", web_index)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    logging.info("Mini App server started on http://localhost:8080")


async def main():
    await start_web()
    logging.info("Chika bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())