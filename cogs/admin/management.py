
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
import re
import datetime
from datetime import timezone, timedelta
import pytz

eastern = pytz.timezone('America/Toronto')

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

	@trema_bot.message_command(name="Set Reminder")
	@is_authorized(trema_db)
	async def remindme(ctx, message: discord.Message):
		"""
		Context menu command to set a reminder for the selected message.
		"""
		await ctx.respond("Veuillez vérifier vos messages privés pour des instructions supplémentaires.", ephemeral=True)

		def parse_delay(input_str):
			try:
				parsed_date = datetime.datetime.strptime(input_str, "%Y-%m-%d %H:%M:%S")
				local_dt = eastern.localize(parsed_date)
				return local_dt.astimezone(timezone.utc)
			except ValueError:
				pass

			units = {
				# EN
				'second': 1, 'seconds': 1, 'sec': 1, 'secs': 1,
				'minute': 60, 'minutes': 60, 'min': 60, 'mins': 60,
				'hour': 3600, 'hours': 3600, 'hr': 3600, 'hrs': 3600,
				'day': 86400, 'days': 86400,
				'week': 604800, 'weeks': 604800,
				# FR
				'seconde': 1, 'secondes': 1, 'sec': 1, 'secs': 1,
				'heure': 3600, 'heures': 3600, 'h': 3600,
				'jour': 86400, 'jours': 86400,
				'semaine': 604800, 'semaines': 604800, 'sem': 604800
			}

			pattern = r'(\d+)\s*(second|seconds|sec|secs|minute|minutes|min|mins|hour|hours|hr|hrs|day|days|week|weeks|seconde|secondes|heure|heures|h|jour|jours|semaine|semaines|sem)'

			match = re.match(pattern, input_str.lower())
			if match:
				amount, unit = match.groups()
				delay_seconds = int(amount) * units[unit]
				return datetime.datetime.now(timezone.utc)+ timedelta(seconds=delay_seconds)

			return None

		reminder_input = await prompt_user(ctx, "Entrez le délai avant le rappel. Ex: '30 minutes', '1 week/semaine', '3 hours/heures'. Vous pouvez aussi entrer une date et heure précises (AAAA-MM-JJ HH:MM:SS).", 'Délai')
		if not reminder_input:
			await ctx.respond("Commande annulée : Aucun délai fourni.", ephemeral=True)
			return

		scheduled_time = parse_delay(reminder_input)
		if scheduled_time is None:
			await ctx.respond("Format de délai invalide. Utilisez par exemple '30 minutes', '1 week', '3 hours' ou une date et heure précises (AAAA-MM-JJ HH:MM:SS).", ephemeral=True)
			return

		public = await prompt_user_with_confirmation(ctx, "Le rappel sera-t-il public ? (True/False)")
		if public is None:
			await ctx.respond("Commande annulée : Choix public/privé non fourni.", ephemeral=True)
			return


		reminder_data = {
			'guild_id': ctx.guild.id,
			'confirmation_channel_id': ctx.channel.id if public else None,
			'confirmation_message_id': None,
			'scheduled_time': scheduled_time.timestamp(),
			'message_link': message.jump_url,
			'creator_id': ctx.author.id,
			'status': 'pending',
			'public': public
		}

		reminder_id = trema_db.add_reminder(reminder_data)

		formatted_time = scheduled_time.astimezone(eastern).strftime('%Y-%m-%d %H:%M:%S %Z')
		if public:
			confirmation_message = await ctx.channel.send(
				f"Rappel public programmé pour [ce message]({message.jump_url}) {formatted_time}. Réagissez avec ✅ pour vous abonner."
			)

			await confirmation_message.add_reaction('✅')
			trema_db.update_reminder_confirmation_message(reminder_id, confirmation_message.id)

		else:
			await ctx.author.send(
				f"Rappel privé programmé pour [ce message]({message.jump_url}) {formatted_time}."
			)

		asyncio.create_task(send_reminder(reminder_id, trema_bot, trema_db))
