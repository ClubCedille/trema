from discord import Embed, Color
from datetime import datetime
from cogs.utils.text_format import _make_cmd_full_name

def _create_information_cmds(trema_bot, start_time, trema_db):	
	@trema_bot.command(name="ping", description="Répond avec pong")
	async def ping(ctx):
		latency = round(trema_bot.latency * 1000) 
		uptime = datetime.now() - start_time
		uptime_str = str(uptime).split('.')[0]  # remove the microseconds part
		server_count = len(trema_bot.guilds)

		response_embed = Embed(
			title="Pong!",
			color=Color.green()
		)
		response_embed.add_field(name="Latency", value=f"{latency}ms")
		response_embed.add_field(name="Uptime", value=uptime_str)
		response_embed.add_field(name=f'{trema_bot.user} server Count', value=str(server_count))

		await ctx.respond(embed=response_embed)


	@trema_bot.command(name="info", description="Informations sur Trëma")
	async def info(ctx):
		embed_title = _make_cmd_full_name(ctx.command)
		instructions =\
			"Trëma est un bot Discord dedié à accueillir et guider les membres du serveur.\n\n"\
			+ "Trëma est développé par le club CEDILLE de l'ÉTS."
		
		help_embed = Embed(
			title=embed_title,
			description=instructions,
			color=Color.blue())
		help_embed.set_thumbnail(url="https://cedille.etsmtl.ca/images/cedille-logo-orange.png")
			
		await ctx.respond(embed=help_embed)
