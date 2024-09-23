from datetime import datetime
from discord import Embed, Color
from cogs.utils.dispatch import post_to_calidum
from cogs.prompts import prompt_user_with_select
from cogs.utils.discord import find_role_in_guild
from logger import logger

def _create_member_requests_cmds(trema_db, request):
    @request.command(name="join", description="Obtenir accès au reste du serveur.")
    async def request_server_access(ctx):
        await ctx.defer(ephemeral=True)

        requester_id = ctx.author.id
        server_id = ctx.guild.id
        username = ctx.author.name

        roles = trema_db.get_server_roles(server_id)

        if not roles:
            logger.error(f"Server {server_id} does not have any roles.")

        server_member_join_msg = trema_db.get_server_member_join_msg(server_id)

        role_name = await prompt_user_with_select(ctx, server_member_join_msg, roles)
        
        if not role_name:
            return

        role = find_role_in_guild(ctx.guild, role_name)

        if not role:
            logger.error(f"Role {role_name} not found in guild {ctx.guild.id}.")
            return
        
        member_role = trema_db.get_server_member_role(server_id)

        if role.id == member_role:
            member_data = {
                "user_id": requester_id,
                "username": username,
                "status": "pending",
                "request_time": str(datetime.now())
            }
            trema_db.add_member(server_id, member_data)

            calidum_enabled = trema_db.get_server_calidum_enabled(ctx.guild.id)
            if calidum_enabled:
                post_to_calidum(username, "Membre du serveur", f"Demande d'ajout comme membre pour {username} avec statut 'pending'.")

            # Send confirmation message to the user
            embed = Embed(
                title="Demande de membre envoyée",
                description=f"Votre demande pour devenir membre est en attente d'approbation.",
                color=Color.green()
            )
            await ctx.respond(embed=embed, ephemeral=True)
        elif role:
            await ctx.author.add_roles(role)
            await ctx.author.send(f"Vous avez été assigné au rôle de {role_name.capitalize()}.")