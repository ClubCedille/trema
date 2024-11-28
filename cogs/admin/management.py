
from discord import Embed, Color, Option, utils, File
import discord
from cogs.prompts import\
    prompt_user,\
    prompt_user_with_confirmation,\
    prompt_user_with_date,\
    prompt_for_image
from cogs.utils.text_format import\
    make_mention,\
    generate_mention_dict
from cogs.utils.discord import\
    send_delayed_dm,\
	send_reminder
from cogs.admin import is_authorized
import asyncio
import random

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

	@trema_bot.command(name="tombola", description="Organiser un tirage au sort")
	@is_authorized(trema_db)
	async def tombola(ctx):
		await ctx.respond("Veuillez vérifier vos messages privés pour des instructions supplémentaires.", ephemeral=True)

		mention_dict = generate_mention_dict(ctx.guild)

		time_and_date, delay = await prompt_user_with_date(ctx, "Quelle est la date et l'heure du tirage au sort ? (AAAA-MM-JJ HH:MM:SS)", 'Date et heure du tirage')
		if not time_and_date:
			return

		message_content = await prompt_user(ctx, "Entrez le message à inclure dans l'annonce du tirage au sort:"
										"\nPour personnaliser ce message, vous pouvez utiliser les mentions suivantes:\n"
										"- `{username}` pour mentionner un username\n"
										"- `{server}` pour le nom du serveur\n"
										"- `{&role}` pour mentionner un rôle par son nom\n"
										"- `{#channel}` pour un lien vers un canal\n"
										"- `{!emojiname}` pour un emoji personnalisé\n"
										"- `{everyone}` pour `@everyone`\n"
										"- `{here}` pour `@here`\n\n", 'Message du tirage au sort')
		if not message_content:
			return

		emoji_input = await prompt_user(ctx, "Veuillez entrer l'emoji personnalisé à utiliser pour le tirage au sort. Vous pouvez envoyer l'emoji directement ou taper son nom (par exemple :cedille:).", 'Emoji personnalisé')
		if not emoji_input:
			return

		try:
			# Try to find the emoji in the guild if it's a custom emoji name
			emoji = None
			if emoji_input.startswith(":") and emoji_input.endswith(":"):
				emoji_name = emoji_input.strip(':')
				emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
				if not emoji:
					raise ValueError(f"L'emoji nommé `{emoji_name}` n'a pas été trouvé dans le serveur.")
			else:
				emoji = emoji_input

			if isinstance(emoji, discord.Emoji):
				emoji_display = f"<:{emoji.name}:{emoji.id}>"
			else:
				emoji_display = emoji
		except Exception as e:
			await ctx.author.send(f"Emoji invalide ou non trouvé dans le serveur. Veuillez réessayer. Erreur : {e}")
			return

		body_with_mentions = make_mention(message_content, mention_dict, ctx.guild)
		formatted_time = time_and_date.strftime('%Y-%m-%d %H:%M:%S')
		announcement_message = f"{body_with_mentions}\n\nLe tirage au sort aura lieu le {formatted_time}.\nRéagissez avec {emoji_display} pour participer."

		confirmation_embed = Embed(title="Détails du tirage au sort", description=f"Date du tirage : {formatted_time}\nEmoji du tirage : {emoji_display}\n\nAperçu du message d'annonce :", color=Color.blurple())
		await ctx.author.send(embed=confirmation_embed)
		await ctx.author.send(announcement_message)

		final_confirmation = await prompt_user_with_confirmation(ctx, "Confirmez-vous ces détails ?")
		if not final_confirmation:
			await ctx.author.send('Opération annulée.')
			return

		try:
			message = await ctx.channel.send(announcement_message)
		except Exception as e:
			await ctx.author.send(f"Erreur lors de l'envoi de l'annonce : {e}")
			return

		try:
			if isinstance(emoji, discord.Emoji):
				await message.add_reaction(emoji)
			else:
				await message.add_reaction(emoji_display)
		except Exception as e:
			await ctx.author.send(f"Erreur lors de l'ajout de la réaction : {e}")
			return

		async def pick_winner():
			await asyncio.sleep(delay)
			try:
				cached_message = await ctx.channel.fetch_message(message.id)
				for reaction in cached_message.reactions:
					if str(reaction.emoji) == str(emoji) or str(reaction.emoji) == emoji_display:
						users = await reaction.users().flatten()
						# Remove the bot itself from the list
						users = [user for user in users if user.id != ctx.bot.user.id]
						break
				else:
					users = []

				if users:
					winner = random.choice(users)
					await ctx.channel.send(f"🎉 Le gagnant du tirage au sort est : {winner.mention} ! Félicitations !")
				else:
					await ctx.channel.send("Personne n'a participé au tirage au sort.")
			except Exception as e:
				await ctx.channel.send(f"Erreur lors du tirage au sort : {e}")

		asyncio.create_task(pick_winner())
		await ctx.author.send('Tirage au sort organisé avec succès.')

	@trema_bot.command(name="remindme", description="Set a reminder for a message")
	@is_authorized(trema_db)
	async def remindme(ctx, message_link: Option(str, "Lien du message à rappeler"), delay: Option(str, "Délai avant le rappel. Ex: '1 week', '3 hours', '4 days'")):
		import re
		from datetime import datetime, timezone, timedelta

		def parse_delay(delay_str):
			units = {
				'second': 1, 'seconds': 1,
				'minute': 60, 'minutes': 60,
				'hour': 3600, 'hours': 3600,
				'day': 86400, 'days': 86400,
				'week': 604800, 'weeks': 604800
			}
			pattern = r'(\d+)\s*(second|seconds|minute|minutes|hour|hours|day|days|week|weeks)'
			match = re.match(pattern, delay_str.lower())
			if not match:
				return None
			amount, unit = match.groups()
			return int(amount) * units[unit]

		message_link_regex = r"https?://discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)"
		match = re.match(message_link_regex, message_link)
		if not match:
			await ctx.respond("Lien du message invalide.", ephemeral=True)
			return

		guild_id, channel_id, message_id = match.groups()

		guild = ctx.guild
		if str(guild.id) != guild_id:
			await ctx.respond("Le lien du message doit être dans ce serveur.", ephemeral=True)
			return

		channel = guild.get_channel(int(channel_id))
		if not channel:
			await ctx.respond("Le canal du message n'a pas été trouvé.", ephemeral=True)
			return

		try:
			message = await channel.fetch_message(int(message_id))
		except discord.NotFound:
			await ctx.respond("Message introuvable.", ephemeral=True)
			return

		delay_seconds = parse_delay(delay)
		if delay_seconds is None:
			await ctx.respond("Format de délai invalide. Utilisez par exemple '1 week', '3 hours', '4 days'.", ephemeral=True)
			return

		scheduled_time = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)

		confirmation_message = await ctx.channel.send(
			f"Rappel programmé pour [ce message]({message_link}) dans {delay}. Réagissez avec ✅ pour vous abonner."
		)

		await confirmation_message.add_reaction('✅')

		await ctx.respond(f"Rappel programmé pour le message: {message.jump_url} dans {delay}.", ephemeral=True)

		reminder_data = {
			'guild_id': guild.id,
			'confirmation_channel_id': ctx.channel.id,
			'confirmation_message_id': confirmation_message.id,
			'scheduled_time': scheduled_time.timestamp(),
			'message_link': message_link,
			'creator_id': ctx.author.id,
		}
		trema_db.add_reminder(reminder_data)

		asyncio.create_task(send_reminder(reminder_data, trema_bot, trema_db))
