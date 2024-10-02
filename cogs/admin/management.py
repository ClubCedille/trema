
from discord import Embed, Color, utils, File
from cogs.prompts import\
    prompt_user,\
    prompt_user_with_confirmation,\
    prompt_user_with_date,\
    prompt_for_image
from cogs.utils.text_format import\
    make_mention,\
    generate_mention_dict
from cogs.utils.discord import\
    send_delayed_dm
from cogs.admin import is_authorized
import asyncio

def _create_server_management_cmds(trema_bot, trema_db):

	@trema_bot.command(name="show_server_config", description="Affiche toutes les configurations du serveur")
	@is_authorized(trema_db)
	async def show_server_config(ctx):
		guild_id = ctx.guild_id
		config_values = trema_db.get_all_server_configs(guild_id)

		response_embed = Embed(
			title="Configurations du Serveur",
			description=config_values,
			color=Color.green()
		)

		await ctx.respond(embed=response_embed, ephemeral=True)

	@trema_bot.command(name="annonce", description="Informations sur Trëma")
	@is_authorized(trema_db)
	async def annonce(ctx):

		await ctx.respond("Veuillez vérifier vos messages privés pour des instructions supplémentaires.", ephemeral=True)

		mention_dict = generate_mention_dict(ctx.guild)
		
		time_and_date, delay = await prompt_user_with_date(ctx, "Quelle est la date et l'heure de l'annonce ? (AAAA-MM-JJ HH:MM:SS)", 'Date et heure')
		if not time_and_date:
			return

		title = await prompt_user(ctx, "Quel est le titre de l\'annonce ?", 'Titre')
		if not title:
			return

		body = await prompt_user(ctx, "Entrez le corps de l\'annonce:" 
			   						"\nPour personnaliser ce message, vous pouvez utiliser les mentions suivantes:\n"
									"- `{username}` pour mentionner un username\n"
									"- `{server}` pour le nom du serveur\n"
									"- `{&role}` pour mentionner un rôle par son nom\n"
									"- `{#channel}` pour un lien vers un canal\n"
									"- `{everyone}` pour `@everyone`\n"
									"- `{here}` pour `@here`\n\n", 'Contenu de l\'annonce')
		if not body:
			return

		try_again_msg = True
		while True:
			try:
				channel_name = await prompt_user(ctx, 'Entrer le canal pour afficher l\'annonce : ', 'Choisir canal')
				if not channel_name:
					return
				channel = utils.get(ctx.guild.text_channels, name=channel_name)
				
				if channel is not None:
					confirm_msg = await prompt_user_with_confirmation(ctx, f"Canal :`{channel}`. Confirmez-vous le canal trouvé ?", 'Choisir canal')
					
					if confirm_msg :
						break
				else:
					try_again_msg = await prompt_user_with_confirmation(ctx, "Canal non trouvé. Voulez-vous essayer à nouveau ?", 'Choisir canal')
					
					if not try_again_msg:
						await ctx.author.send("Operation annulé.")
						break

			except asyncio.TimeoutError:
				await ctx.author.send("Temps écoulé. Opération annulée.")
				break
		
		# User canceled the operation
		if not try_again_msg:
			return

		is_embed = await prompt_user_with_confirmation(ctx, "Voulez-vous que l'annonce soit intégrée (embedded)?")
		image_path = None
		if is_embed == True:
			image_url = await prompt_user(ctx, 'Entrez l\'URL de l\'image à intégrer (ou tapez \'aucun\'):',  'Image à intégrer')
			if not image_url:
				return
		elif is_embed == False:
			image_path = await prompt_for_image(ctx)
		else :
			return

		body_with_mentions = make_mention(body, mention_dict)

		confirmation = Embed(title="Détails de l'annonce", description=f"Date de l'annonce : {time_and_date}\nCanal pour l'annonce : {channel}\n\nAperçu de l'annonce dans le prochain message :", color=Color.blurple())
		await ctx.author.send(embed=confirmation)	

		if is_embed: 
			annonce = Embed(title=title, description=body_with_mentions, color=Color.blurple())
			if image_url.lower() != 'aucun':
				annonce.set_thumbnail(url=image_url)
			await ctx.author.send(embed=annonce)
		else:
			formatted_title = make_mention(title, mention_dict)
			formatted_body = f"{body_with_mentions}"
			annonce = f"{formatted_title}\n{formatted_body}"
			await ctx.author.send(annonce)
			if image_path:
				file = File(image_path, filename=image_path.split("/")[-1])
				await ctx.author.send(file=file)

		final_confirmation = await prompt_user_with_confirmation(ctx, "Confirmez-vous ces détails ?")
	
		if final_confirmation:
			condition = lambda: True 
			asyncio.create_task(send_delayed_dm(channel, annonce, delay, condition, 'embed' if is_embed else 'text'))
			if image_path:
				file = File(image_path, filename=image_path.split("/")[-1])
				asyncio.create_task(send_delayed_dm(channel, file, delay, condition, 'file', image_path))
			await ctx.author.send('Annonce programmée.')
		else:
			await ctx.author.send('Annonce annulée.')
