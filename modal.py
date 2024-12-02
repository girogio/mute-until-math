import discord
from discord import ui


class QuestionModal(ui.Modal, title="Anti Matthias Problem"):
    message = "Solve this problem to get more time!"
    name = ui.TextInput(label="What is your name?", placeholder="Your name here")
    answer = ui.TextInput(label="What is the answer?", placeholder="Your answer here")
    custom_id = "question_modal"
    children = [name, answer]
    _children = [name]

    def __init__(self, question: str, answer: int):
        self.question = question
        self.answer = answer

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks for your response, {self.name}!", ephemeral=True
        )

    async def on_cancel(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "You cancelled the modal!", ephemeral=True
        )
