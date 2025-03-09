import discord
from discord.ext import commands
from discord.ui import View, Button
import datetime
import json
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Chargement des variables d'environnement
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

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

        # Now send to second modal, no need for `prix` at this stage
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
        self.add_item(discord.ui.TextInput(label="Prix", placeholder="Prix du véhicule"))

    async def on_submit(self, interaction: discord.Interaction):
        prix = self.children[3].value  # This collects the 'prix' from the second modal
        embed = discord.Embed(title="💰 Vente de Véhicule", color=discord.Color.gold())
        embed.add_field(name="Vendeur", value=self.vendeur, inline=True)
        embed.add_field(name="Acheteur", value=self.acheteur, inline=True)
        embed.add_field(name="Véhicule", value=self.vehicule, inline=False)
        embed.add_field(name="Type", value=self.children[0].value, inline=True)
        embed.add_field(name="Plaque", value=self.children[1].value, inline=True)
        embed.add_field(name="Date & Heure", value=self.children[2].value, inline=False)
        embed.add_field(name="Prix", value=prix, inline=False)

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Formulaire soumis avec succès !", ephemeral=True)


class OpenVenteVehiculeModal2(discord.ui.View):
    def __init__(self, vendeur, acheteur, vehicule, prix):
        super().__init__(timeout=180)  # Le bouton reste actif pendant 3 minutes
        self.vendeur = vendeur
        self.acheteur = acheteur
        self.vehicule = vehicule
        self.prix = prix

    @discord.ui.button(label="Continuer la vente", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VenteVehiculeModal2(self.vendeur, self.acheteur, self.vehicule, self.prix))


class VenteVehiculeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Remplir le formulaire", style=discord.ButtonStyle.primary)
    async def bouton_formulaire(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VenteVehiculeModal1())


@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, message: str):
    """Envoie un message avec le bot"""
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def vente(ctx):
    embed = discord.Embed(title="💰 Vente de Véhicule", description="En cas de vente de véhicule, le vendeur doit remplir ce formulaire", color=discord.Color.gold())
    view = VenteVehiculeView()
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

keep_alive()
bot.run(token=token)
