from buttons import\
	confirmation_button,\
	skip_button,\
	now_button

from discord import\
	Color,\
	Embed,\
	Interaction,\
	Attachment,\
	Message

from text_format import\
    _make_config_error_embed

import asyncio
from datetime import datetime
import pytz
import os

mtl_tz = pytz.timezone('America/Toronto') 

async def prompt_user(ctx, description, title=None):
    embed = Embed(
        title=title or "Prompt",
        description=description,
        color=Color.blue()
    )
    message = await ctx.author.send(embed=embed)
    dm_channel_id = message.channel.id
    
    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == dm_channel_id

    try:
        response = await ctx.bot.wait_for('message', check=check, timeout=120)
        if not response:
            ctx.author.send('Entrée invalide. Veuillez réessayer.')
            return None
    except asyncio.TimeoutError:
        await ctx.author.send('Temps écoulé. Opération annulée.')
        return None

    return response.content

async def prompt_user_with_confirmation(ctx, description, title=None):    
    embed = Embed(
        title=title or "Confirmation",
        description=description,
        color=Color.blue()
    )
    message = await ctx.author.send(embed=embed, view=confirmation_button())

    def check(interaction: Interaction):
        return interaction.user.id == ctx.author.id and interaction.message.id == message.id
    
    try:
        interaction = await ctx.bot.wait_for("interaction", check=check, timeout=60)
        await interaction.response.defer()
        
        if interaction.data["custom_id"] == "yes_button":
            return True
        else:
            return False
    except asyncio.TimeoutError:
        await ctx.author.send('Temps écoulé. Opération annulée.')
        return None
    
async def prompt_for_image(ctx):

    if not os.path.exists("./temp"):
        os.makedirs("./temp")

    embed = Embed(
        title="Image",
        description="Veuillez envoyer l'image que vous voulez ajouter au message.",
        color=Color.blue()
    )
    await ctx.author.send(embed=embed, view=skip_button())

    def image_check(message):
        return message.author.id == ctx.author.id and message.attachments

    def interaction_check(interaction: Interaction):
        return interaction.user.id == ctx.author.id and interaction.data["custom_id"] == "skip_button"

    try:
        done, pending = await asyncio.wait([
			asyncio.create_task(ctx.bot.wait_for("message", check=image_check, timeout=60)),
			asyncio.create_task(ctx.bot.wait_for("interaction", check=interaction_check, timeout=60))
		], return_when=asyncio.FIRST_COMPLETED)

        for future in pending:
            future.cancel()

        result = done.pop().result()

        if isinstance(result, Interaction):
            await result.response.defer()
            return None  # No image selected
        elif isinstance(result, Message):
            attachment: Attachment = result.attachments[0]
            image_path = f"./temp/{attachment.filename}"
            await attachment.save(image_path)
            return image_path

    except asyncio.TimeoutError:
        await ctx.author.send("Temps écoulé. Opération annulée.")
        return None

async def prompt_user_with_date(ctx, description, title=None):
	embed = Embed(
		title=title or "Date et heure",
		description=description,
		color=Color.blue()
	)
	def message_check(m):
		return m.author.id == ctx.author.id and m.channel.id == dm_channel_id

	def interaction_check(interaction: Interaction):
		return interaction.user.id == ctx.author.id and interaction.message.id == message.id

	while True:
		try:
			message = await ctx.author.send(embed=embed, view=now_button())
			dm_channel_id = message.channel.id

			done, pending = await asyncio.wait([
				asyncio.create_task(ctx.bot.wait_for("message", check=message_check, timeout=60)),
				asyncio.create_task(ctx.bot.wait_for("interaction", check=interaction_check, timeout=60))
			], return_when=asyncio.FIRST_COMPLETED)

			for future in pending:
				future.cancel()

			result = done.pop().result()

			if isinstance(result, Interaction) and result.data["custom_id"] == "now_button":
				await result.response.defer()
				return datetime.now(mtl_tz), 0

			elif isinstance(result, Message):
				try:
					time_and_date = datetime.strptime(result.content, '%Y-%m-%d %H:%M:%S')
					aware_time_and_date = mtl_tz.localize(time_and_date)
					delay = (aware_time_and_date - datetime.now(mtl_tz)).total_seconds()

					if delay <= 0:
						proceed = await prompt_user_with_confirmation(ctx, "La date spécifiée est dans le passé. Voulez vous envoyer le message maintenant ?", 'Date et heure')
						if proceed:
							return time_and_date, delay
					else:
						return time_and_date, delay
				except ValueError:
					await ctx.author.send(embed=_make_config_error_embed("Date et heure", result.content, "Format de date invalide. Veuillez réessayer."))

		except asyncio.TimeoutError:
			await ctx.author.send('Temps écoulé. Opération annulée.')
			return None, None