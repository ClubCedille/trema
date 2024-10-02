from discord import Embed, Color, Option, SlashCommandGroup
from cogs.admin import is_authorized
from cogs.utils.text_format import _make_cmd_full_name, _SPACE
from uuid import uuid4

def generate_unique_webhook_url():
    return str(uuid4())

def _create_webhooks_cmds(trema_db):
	webhook = SlashCommandGroup(name="webhook",
		description="Groupe de commandes pour gérer les webhooks.")

	@webhook.command(name="create",
		description="Créer un webhook pour le canal spécifié")
	@is_authorized(trema_db)
	async def create_webhook(ctx,
			channel_id: Option(str, "Le canal affilié au webhook qui sera créé"),
			webhook_name: Option(str, "Le nom du webhook qui sera créé")):
		
		guild_id = ctx.guild_id
		unique_url = generate_unique_webhook_url()

		trema_db.create_webhook(webhook_name, channel_id, unique_url, guild_id)

		embed=Embed(title="Webhook créé", description=f"Le webhook '{webhook_name}' a été créé avec succès.\nwebhook uuid : ```{unique_url}```", color=Color.blurple())
		await ctx.respond(embed=embed, ephemeral=True)

	@webhook.command(name="list",
		description="Liste des webhooks existants")
	@is_authorized(trema_db)
	async def list_webhooks(ctx):
		webhooks = trema_db.get_all_webhooks(ctx.guild.id)
		if webhooks == []:
			embed=Embed(title="Liste des webhooks", description=f"Aucun webhook n'existe pour ce serveur.", color=Color.blurple())
			await ctx.respond(embed=embed, ephemeral=True)
			return
		
		webhook_strings = []
		for webhook in webhooks:
			webhook_str = f"Name: {webhook.get('webhookName', 'Unknown')}, Channel ID: {webhook.get('channelID', 'Unknown')}"
			webhook_strings.append(webhook_str)
			
		embed=Embed(title="Liste des webhooks", description=f"Voici la liste des webhooks existants :\n" + f'\n'.join(webhook_strings), color=Color.blurple())
		await ctx.respond(embed=embed, ephemeral=True)

	@webhook.command(name="delete",
		description="Supprime le webhook référencé")
	@is_authorized(trema_db)
	async def delete_webhook(ctx, webhook_name: Option(str, "Le nom du webhook à supprimer")):
		# Your logic here to delete the specified webhook
		webhook = trema_db.get_webhook_by_name(webhook_name, ctx.guild.id)
		if webhook is None:
			embed=Embed(title="Webhook non trouvé", description=f"Le webhook '{webhook_name}' n'existe pas.", color=Color.blurple())
			await ctx.respond(embed=embed, ephemeral=True)
			return
		
		trema_db.delete_webhook(webhook_name, ctx.guild.id)

		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + webhook_name
		embed = Embed(title=embed_title, description=f"Webhook '{webhook_name}' supprimé.", color=Color.blurple())
		await ctx.respond(embed=embed, ephemeral=True)
    
	@webhook.command(name="update",
		description="Met à jour le canal lié au webhook")
	@is_authorized(trema_db)
	async def update_webhook(ctx,
			webhook_name: Option(str, "Le nom du webhook à mettre à jour"),
			new_channel_id: Option(str, "Le nouveau canal à associer au webhook")):

		new_channel = ctx.guild.get_channel(int(new_channel_id))
		if new_channel:
			trema_db.update_webhook_channel(webhook_name, new_channel.id, ctx.guild.id)
			embed=Embed(title="Webhook mis à jour", description=f"Le webhook '{webhook_name}' a été mis à jour pour le canal {new_channel_id} avec succès.", color=Color.blurple())
			await ctx.respond(embed=embed, ephemeral=True)
		else:
			await ctx.respond(f"Le canal '{new_channel_id}' n'existe pas.", ephemeral=True)

	return webhook