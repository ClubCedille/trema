from discord import Embed, Color, Option
from cogs.utils.text_format import \
	_make_cmd_full_name, \
    _make_config_confirm_embed, \
	_make_config_error_embed, \
    _make_config_display_embed
from cogs.admin import is_authorized
from cogs.utils.text_format import _SPACE, _REQUEST_VALUE
import asyncio

def _create_config_reminder_cmds(trema_db, config):

	@config.command(name="message_rappel",
		description=f"Changez le message de rappel aux membres sans rôles.")
	@is_authorized(trema_db)
	async def config_reminder_msg(ctx):
		
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE
		prev_value = trema_db.get_server_reminder_msg(guild_id)

		await ctx.respond("Veuillez vérifier vos messages privés pour des instructions supplémentaires.", ephemeral=True)
		
		user = ctx.author
		dm_channel = user.dm_channel
		if dm_channel is None:
			dm_channel = await user.create_dm()
			
		embed = Embed(
			title="Configuration du message de rappel aux membres qui n'ont pas choisi de rôles",
			description=f"Le message de rappel actuel est: `{prev_value}`\n\n"
						"Pour personnaliser ce message, vous pouvez utiliser les mentions suivantes:\n"
						"- `{member}` pour mentionner le nouveau membre\n"
						"- `{username}` pour mentionner un username\n"
						"- `{server}` pour le nom du serveur\n"
						"- `{&role}` pour mentionner un rôle par son nom\n"
						"- `{#channel}` pour un lien vers un canal\n"
						"- `{everyone}` pour `@everyone`\n"
						"- `{here}` pour `@here`\n\n"
						"Veuillez entrer le nouveau message d'accueil.",
			color=Color.blue()
		)
		
		await dm_channel.send(embed=embed)
		
		# Wait for user input in DM
		def check(m):
			return m.author.id == user.id and m.channel.id == dm_channel.id
		
		try:
			user_message = await ctx.bot.wait_for('message', timeout=120.0, check=check)
		except asyncio.TimeoutError:
			await dm_channel.send("Temps écoulé. Opération annulée.")
		else:
			new_value = user_message.content
			trema_db.set_server_reminder_msg(guild_id, new_value)
			response_embed = _make_config_confirm_embed(embed_title, new_value, prev_value)
			await dm_channel.send(embed=response_embed)


	@config.command(name="delai_rappel",
		description="Changer le délai d'envoi du rappel (minutes) aux membres sans rôles.")
	@is_authorized(trema_db)
	async def config_reminder_delay(ctx,
			delai: Option(str, "Délai du rappel (minutes) aux membres sans rôles")):
		
		guild_id = ctx.guild_id
		embed_title = _make_cmd_full_name(ctx.command) + _SPACE + delai
		prev_value = trema_db.get_server_reminder_delay(guild_id) / 60
		prev_value = int(prev_value)

		try:
			delai = int(delai) * 60

		except ValueError:
			pass

		if isinstance(delai, str) and delai == _REQUEST_VALUE:
				response_embed = _make_config_display_embed(embed_title, prev_value)
			
		elif not isinstance(delai, int) or delai < 0:
			response_embed = _make_config_error_embed(embed_title, prev_value,
				"Le délai de rappel (minutes) est un nombre entier positif.")

		else:
			trema_db.set_server_reminder_delay(guild_id, delai)
			confirmed_delay = trema_db.get_server_reminder_delay(guild_id) / 60
			confirmed_delay = int(confirmed_delay)
			response_embed = _make_config_confirm_embed(
				embed_title, confirmed_delay, prev_value)

		await ctx.respond(embed=response_embed, ephemeral=True)