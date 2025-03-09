import discord
from discord.ext import commands
from discord.ui import View, Button, Modal
from discord import app_commands
import datetime
import json
import os

# Configuration des permissions du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents)

CHANNEL_ID = 1347731990752788510  # Remplace par l'ID du salon de log


class VenteVehiculeModal1(discord.ui.Modal, title="Formulaire (1/2)"):
    def __init__(self):
        super().__init__(title="Formulaire de Vente (1/2)")
        self.add_item(discord.ui.TextInput(label="Vendeur", placeholder="Nom du vendeur"))
        self.add_item(discord.ui.TextInput(label="Acheteur", placeholder="Prénom-Nom"))
        self.add_item(discord.ui.TextInput(label="Nom du véhicule", placeholder="Ex: Audi RS6"))

    async def on_submit(self, interaction: discord.Interaction):
        vendeur = self.children[0].value
        acheteur = self.children[1].value
        vehicule = self.children[2].value

        view = OpenVenteVehiculeModal2(vendeur, acheteur, vehicule)

        await interaction.response.send_message(
            "✅ Première partie complétée ! Cliquez sur le bouton ci-dessous pour continuer.",
            view=view,
            ephemeral=True
        )


class VenteVehiculeModal2(discord.ui.Modal, title="Formulaire (2/2)"):
    def __init__(self, vendeur, acheteur, vehicule):
        super().__init__(title="Formulaire de Vente (2/2)")
        self.vendeur = vendeur
        self.acheteur = acheteur
        self.vehicule = vehicule
        self.add_item(discord.ui.TextInput(label="Type de véhicule", placeholder="Ex: Berline, SUV..."))
        self.add_item(discord.ui.TextInput(label="Plaque d'immatriculation", placeholder="Ex: AB-123-CD"))
        self.add_item(discord.ui.TextInput(label="Date et Heure", placeholder="JJ/MM/AAAA HH:MM"))

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="💰 Vente de Véhicule", color=discord.Color.gold())
        embed.add_field(name="Vendeur", value=self.vendeur, inline=True)
        embed.add_field(name="Acheteur", value=self.acheteur, inline=True)
        embed.add_field(name="Véhicule", value=self.vehicule, inline=False)
        embed.add_field(name="Type", value=self.children[0].value, inline=True)
        embed.add_field(name="Plaque", value=self.children[1].value, inline=True)
        embed.add_field(name="Date & Heure", value=self.children[2].value, inline=False)

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Formulaire soumis avec succès !", ephemeral=True)


class OpenVenteVehiculeModal2(discord.ui.View):
    def __init__(self, vendeur, acheteur, vehicule):
        super().__init__(timeout=180)  # Le bouton reste actif pendant 3 minutes
        self.vendeur = vendeur
        self.acheteur = acheteur
        self.vehicule = vehicule

    @discord.ui.button(label="Continuer la vente", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VenteVehiculeModal2(self.vendeur, self.acheteur, self.vehicule))


class VenteVehiculeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Remplir le formulaire", style=discord.ButtonStyle.primary)
    async def bouton_formulaire(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VenteVehiculeModal1())


@bot.tree.command(name="say", description="Répète un message")
@app_commands.describe(message="Le message à répéter")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="vente", description="Affiche le formulaire de vente de véhicule")
async def vente(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💰 Vente de Véhicule",
        description="En cas de vente de véhicule, le vendeur doit remplir ce formulaire",
        color=discord.Color.gold()
    )
    view = VenteVehiculeView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"Commandes synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur de synchronisation : {e}")

bot.run("DISCORD_TOKEN")
