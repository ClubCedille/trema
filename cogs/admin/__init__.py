from cogs.utils.text_format import\
	_make_config_error_embed

from discord.ext import commands

def is_authorized(trema_db):
	async def predicate(ctx):
		admin_role_id = trema_db.get_server_admin_role(ctx.guild.id)
		isAllowed = ctx.author.id == ctx.guild.owner_id or any(role.id == admin_role_id for role in ctx.author.roles)

		if not isAllowed:
			admin_role = ctx.guild.get_role(admin_role_id)
			admin_role_name = 'Owner' if admin_role is None else admin_role.name
			embed_error = _make_config_error_embed(
				"Manque de permission",
				ctx.command,
				f"Vous n'êtes pas autorisé à utiliser cette commande. Le rôle {admin_role_name} est requis."
			)
			await ctx.respond(embed=embed_error, ephemeral=True)
		return isAllowed
	return commands.check(predicate)
