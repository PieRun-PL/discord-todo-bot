import discord
from discord import app_commands
import json
import os

# ----------------- SETUP -----------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

FILE = "data.json"


# ----------------- DATA -----------------
def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"name": "Moja lista", "tasks": []}


def save_data():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()


# ----------------- UI -----------------
class TaskButton(discord.ui.Button):
    def __init__(self, index: int):
        self.index = index

        label = "✔" if data["tasks"][index]["done"] else "❌"

        super().__init__(
            label=label,
            style=discord.ButtonStyle.green
        )

    async def callback(self, interaction: discord.Interaction):
        data["tasks"][self.index]["done"] = not data["tasks"][self.index]["done"]
        save_data()

        await refresh(interaction)


class ResetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🧹 Reset listy",
            style=discord.ButtonStyle.red
        )

    async def callback(self, interaction: discord.Interaction):
        data["tasks"] = []
        save_data()

        await refresh(interaction)


class TaskView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        for i in range(len(data["tasks"])):
            self.add_item(TaskButton(i))

        self.add_item(ResetButton())


# ----------------- REFRESH -----------------
async def refresh(interaction: discord.Interaction):

    msg = f"📋 **{data['name']}**\n\n"

    if not data["tasks"]:
        msg += "Pusta lista"
    else:
        for i, t in enumerate(data["tasks"]):
            status = "✔" if t["done"] else "❌"
            msg += f"{i+1}. {status} {t['task']}\n"

    await interaction.response.edit_message(
        content=msg,
        view=TaskView()
    )


# ----------------- BOT -----------------
@client.event
async def on_ready():
    await tree.sync()
    print(f"Zalogowano jako {client.user}")


# ----------------- COMMANDS -----------------
@tree.command(name="add", description="Dodaj zadanie")
async def add(interaction: discord.Interaction, task: str):
    data["tasks"].append({"task": task, "done": False})
    save_data()

    await interaction.response.send_message(f"Dodano: {task}")


@tree.command(name="list", description="Pokaż listę")
async def list_tasks(interaction: discord.Interaction):

    msg = f"📋 **{data['name']}**\n\n"

    if not data["tasks"]:
        msg += "Pusta lista"
    else:
        for i, t in enumerate(data["tasks"]):
            status = "✔" if t["done"] else "❌"
            msg += f"{i+1}. {status} {t['task']}\n"

    await interaction.response.send_message(msg, view=TaskView())


@tree.command(name="setname", description="Ustaw nazwę listy")
async def setname(interaction: discord.Interaction, name: str):
    data["name"] = name
    save_data()

    await interaction.response.send_message(f"Nazwa listy: {name}")


@tree.command(name="reset", description="Wyczyść listę")
async def reset(interaction: discord.Interaction):
    data["tasks"] = []
    save_data()

    await interaction.response.send_message("Lista wyczyszczona 🧹")


# ----------------- RUN -----------------
import os
client.run(os.environ["TOKEN"])
