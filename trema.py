"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""


from argparse import ArgumentParser
import asyncio
import discord


_DELAY_SECS_15_MIN = 15 * 60
_ROLE_EVERYONE = "@everyone"


def _make_arg_parser():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("-s", "--serveur", type=str,
		help="L'identifiant du serveur où ce robot fonctionnera")
	parser.add_argument("-j", "--jeton", type=str,
		help="Le jeton d'authentification de ce robot logiciel")
	return parser


arg_parser = _make_arg_parser()
args = arg_parser.parse_args()

server_ids = (args.serveur,)
bot_token = args.jeton

intents = discord.Intents.default()
intents.members = True

trema = discord.Bot(intents=intents)


def get_channel_by_name(channel_name):
	return discord.utils.get(trema.get_all_channels(), name=channel_name)


def member_roles_are_default(member):
	"""
	Determines whether a server member does not have roles besides the default
	ones: @everyone and the member's name.

	Args:
		member (discord.member.Member): a server member

	Returns:
		bool: True if all of member's roles are default one, False otherwise
	"""
	member_name = member.name

	for role in member.roles:
		role_name = role.name

		if role_name != _ROLE_EVERYONE and role_name != member_name:
			return False

	return True


async def send_delayed_dm(user, message, delay, condition=None):
	"""
	Sends a direct message (DM) to the specified Discord user after a delay.
	This function should be called asynchronously. The condition is evaluated
	after the delay.

	Args:
		user (discord.abc.User): a Discord user
		message (str): the direct message to send to user
		delay (int): the time to wait, in seconds, before sending the message
		condition (function): a Boolean function that takes no argument. The
			message is sent if it is None or it returns True. Defaults to None.
	"""
	await asyncio.sleep(delay)

	if condition is None or condition():
		await user.send(message)


@trema.event
async def on_member_join(member):
	guild = member.guild
	sys_chan = guild.system_channel
	# A channel that contains integration instructions
	instruct_chan = get_channel_by_name("accueil")
	welcome_msg =\
		f"Heille {member.mention}!"\
		+ f"\nBienvenue au Club CEDILLE. "\
		+ f"Suis les instructions dans {instruct_chan.mention} "\
		+ "pour avoir accès au reste du serveur!"
	await sys_chan.send(welcome_msg)

	# A reminder if the new member does not select a role
	if not member.bot:
		reminder_msg =\
			f"Viens dans {instruct_chan.mention} pour t'attribuer un rôle!"
		msg_condition = lambda: member_roles_are_default(member)
		reminder_task = asyncio.create_task(send_delayed_dm(
			member, reminder_msg, 10, msg_condition))
		await asyncio.wait([reminder_task])


@trema.event
async def on_member_remove(member):
	guild = member.guild
	sys_chan = guild.system_channel
	message = f"{member.name} a quitté le serveur."
	await sys_chan.send(message)


@trema.event
async def on_ready():
    print(f"{trema.user} fonctionne.")


trema.run(bot_token)
