# -*- coding: utf-8 -*-
import os, json, random, asyncio
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = "scores.json"
POINTS_PER_QUESTION = 10
QUIZ_TIMEOUT = 20

QUESTIONS = {
    "أنمي": [
        {"نص": "من هو بطل أنمي ناروتو؟", "خيارات": ["ساسكي", "ناروتو", "ايتاتشي", "كاكاشي"], "صح": 1},
        {"نص": "كم عدد كرات التنين في Dragon Ball؟", "خيارات": ["5","6","7","8"], "صح": 2},
        {"نص": "هل لوفي في ون بيس قرصان؟", "خيارات": ["صح","خطأ"], "صح": 0}
    ],
    "Free Fire": [
        {"نص": "اسم العملة داخل Free Fire؟", "خيارات": ["Diamonds","Gold","Credits","Coins"], "صح": 0},
        {"نص": "طور اللعبة الأشهر في Free Fire؟", "خيارات": ["Deathmatch","Battle Royale","Zombie","Arena"], "صح": 1},
        {"نص": "هل Garena هي ناشر Free Fire؟", "خيارات": ["صح","خطأ"], "صح": 0}
    ],
    "World of Warcraft": [
        {"نص": "ما اسم كوكب الـ Orcs الأصلي؟", "خيارات": ["Azeroth","Draenor","Outland","Northrend"], "صح": 1},
        {"نص": "أي فصيل يضم الـ Humans؟", "خيارات": ["Horde","Alliance"], "صح": 1},
        {"نص": "هل WoW لعبة MMORPG؟", "خيارات": ["صح","خطأ"], "صح": 0}
    ],
    "محترفين": [
        {"نص": "من هو لاعب فورتنايت الفائز بكأس العالم 2019؟", "خيارات": ["Bugha","Ninja","Tfue","Mongraal"], "صح": 0},
        {"نص": "من هو s1mple؟", "خيارات": ["لاعب CS:GO","لاعب LoL","ستريمر فري فاير","يوتيوبر أنمي"], "صح": 0},
        {"نص": "هل Faker لاعب في League of Legends؟", "خيارات": ["صح","خطأ"], "صح": 0}
    ],
    "عامة": [
        {"نص": "ما عاصمة فرنسا؟", "خيارات": ["باريس","مدريد","روما","برلين"], "صح": 0},
        {"نص": "عدد قارات العالم؟", "خيارات": ["5","6","7","8"], "صح": 2},
    ]
}

CATEGORIES = list(QUESTIONS.keys())

def load_scores():
    if not os.path.exists(DATA_FILE): return {}
    try:
        return json.load(open(DATA_FILE,"r",encoding="utf-8"))
    except: return {}

def save_scores(scores): json.dump(scores, open(DATA_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def add_points(uid, pts): 
    scores=load_scores(); scores[str(uid)] = scores.get(str(uid),0)+pts; save_scores(scores)
def top_scores(n=10): 
    items=[(int(uid),pts) for uid,pts in load_scores().items()]; items.sort(key=lambda x:x[1],reverse=True); return items[:n]

class ChoiceView(discord.ui.View):
    def __init__(self, choices, correct): super().__init__(timeout=QUIZ_TIMEOUT); self.correct=correct; self.answered=False; [self.add_item(ChoiceButton(label=c,i=i)) for i,c in enumerate(choices)]
class ChoiceButton(discord.ui.Button):
    def __init__(self,label,i): super().__init__(label=label,style=discord.ButtonStyle.secondary); self.i=i
    async def callback(self, interaction): 
        view:ChoiceView=self.view
        if view.answered: await interaction.response.send_message("❌ تمّت الإجابة!",ephemeral=True); return
        view.answered=True
        for item in view.children: item.disabled=True
        if self.i==view.correct: add_points(interaction.user.id,POINTS_PER_QUESTION); txt=f"✅ إجابة صحيحة {interaction.user.mention}!"
        else: txt="❌ إجابة خاطئة!"
        await interaction.response.edit_message(content=txt,view=view)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} جاهز ويشتغل!")

@bot.tree.command(name="مسابقة",description="ابدأ مسابقة")
@app_commands.choices(فئة=[app_commands.Choice(name=c,value=c) for c in CATEGORIES]+[app_commands.Choice(name="عشوائي",value="عشوائي")])
async def quiz(inter:discord.Interaction, فئة:app_commands.Choice[str], عدد:int=3):
    for n in range(1,عدد+1):
        cat=random.choice(CATEGORIES) if فئة.value=="عشوائي" else فئة.value
        q=random.choice(QUESTIONS[cat])
        view=ChoiceView(q["خيارات"],q["صح"])
        await inter.response.send_message(f"❓ {q['نص']}", view=view)
        await asyncio.sleep(QUIZ_TIMEOUT+1)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
