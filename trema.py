"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""


from argparse import ArgumentParser
import asyncio
import discord

from discord_util import\
	get_channel_by_name,\
	member_roles_are_default,\
	send_delayed_dm

#from slash_commands import\
#	create_slash_cmds

from trema_database import\
	get_trema_database


_DELAY_SECS_15_MIN = 15 * 60


def _make_arg_parser():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("-s", "--serveur", type=str, default=None,
		help="L'identifiant du serveur où ce robot fonctionnera")
	parser.add_argument("-j", "--jeton", type=str,
		help="Le jeton d'authentification de ce robot logiciel")
	return parser


arg_parser = _make_arg_parser()
args = arg_parser.parse_args()

bot_token = args.jeton
server_id = args.serveur

intents = discord.Intents.default()
intents.members = True

trema = discord.Bot(intents=intents)

database = get_trema_database()

#if server_id is not None:
#	create_slash_cmds(trema, database, server_id)


@trema.event
async def on_guild_join(guild):
	database.register_server(guild)
#	create_slash_cmds(trema, database, guild.id)


@trema.event
async def on_member_join(member):
	guild = member.guild
	guild_id = guild.id
	sys_chan = guild.system_channel
	# A channel that contains integration instructions
	#instruct_chan = get_channel_by_name(trema, "accueil")

	welcome_msg = database.get_server_welcome_msg(guild_id)
	#welcome_msg =\
	#	f"Heille {member.mention}!"\
	#	+ f"\nBienvenue au Club CEDILLE. "\
	#	+ f"Suis les instructions dans {instruct_chan.mention} "\
	#	+ "pour avoir accès au reste du serveur!"
	await sys_chan.send(welcome_msg)

	# A reminder if the new member does not select a role
	reminder_msg = database.get_server_reminder_msg(guild_id)
	if not member.bot and reminder_msg is not None:
		#reminder_msg =\
		#	f"Viens dans {instruct_chan.mention} pour t'attribuer un rôle!"
		msg_condition = lambda: member_roles_are_default(member)
		reminder_task = asyncio.create_task(send_delayed_dm(
			member, reminder_msg, _DELAY_SECS_15_MIN, msg_condition))
		await asyncio.wait([reminder_task])


@trema.event
async def on_member_remove(member):
	guild = member.guild
	guild_id = guild.id
	sys_chan = guild.system_channel
	leave_msg = database.get_server_leave_msg(guild_id)
	#leave_msg = f"{member.name} a quitté le serveur."
	if leave_msg is not None:
		await sys_chan.send(leave_msg)


@trema.event
async def on_ready():
    print(f"{trema.user} fonctionne.")


@trema.slash_command(guild_ids=(server_id,),
	name="config", describe="")
async def config(ctx,
		param: discord.Option(str, "Paramètre à régler"),
		value: discord.Option(str, "Valeur du paramètre")):
	embed_title = "Paramètre mis à jour: "

	if param == "canalaccueil":
		embed_title += "canal d'accueil"
		prev_value = database.get_server_welcome_chan_id(ctx.guild_id)
		database.set_server_welcome_chan_id(ctx.guild_id, int(value))

	elif param == "msgaccueil":
		embed_title += "message d'accueil"
		prev_value = database.get_server_welcome_msg(ctx.guild_id)
		database.set_server_welcome_msg(ctx.guild_id, value)

	confirm_embed = discord.Embed(
		title=embed_title,
		description=f"Valeur précédente: {prev_value}\nNouvelle valeur: {value}",
		color=discord.Color.green())

	await ctx.send(embed=confirm_embed)


trema.run(bot_token)
