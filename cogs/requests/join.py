from datetime import datetime
from discord import Embed, Color
from cogs.utils.dispatch import post_to_calidum
from cogs.prompts import prompt_user_with_select, prompt_user, prompt_user_with_confirmation
from cogs.utils.discord import find_role_in_guild
from logger import logger
from cogs.utils.text_format import make_mention, generate_mention_dict

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

        message = make_mention(server_member_join_msg, generate_mention_dict(ctx.guild, ctx.author))

        role_name = await prompt_user_with_select(ctx, message, roles)

        if not role_name:
            return

        role = find_role_in_guild(ctx.guild, role_name)

        if not role:
            logger.error(f"Role {role_name} not found in guild {ctx.guild.id}.")
            return

        member_role = trema_db.get_server_member_role(server_id)

        if role.id == member_role:

            await ctx.respond("Afin de compléter votre demande d'adhésion, veuillez vérifier vos messages privés.", ephemeral=True)

            user_has_gh_account = await prompt_user_with_confirmation(ctx, "Avez-vous un compte GitHub ?")

            if not user_has_gh_account:
                 # Give user link to our wiki track to learn git and github and then return to the command to try again
                await ctx.author.send("Vous pouvez apprendre à utiliser Git et GitHub en suivant ce lien : https://wiki.omni.cedille.club/onboarding/tracks/git/ \n\nUne fois que vous avez un compte GitHub, veuillez réessayer la commande `/request join`.")
                return

            github_username = await prompt_user(ctx, "Veuillez entrer votre nom d'utilisateur GitHub", "Nom d'utilisateur GitHub pour devenir membre")
            if not github_username:
                return
            github_email = await prompt_user(ctx, "Veillez entrer votre adresse e-mail associée à GitHub", "Adresse e-mail GitHub pour devenir membre")
            if not github_email:
                return
            calidum_enabled = trema_db.get_server_calidum_enabled(ctx.guild.id)

            try:
                onboarding_role_id = trema_db.get_server_onboarding_role(server_id)
                if isinstance(onboarding_role_id, str):
                    onboarding_role_id = int(onboarding_role_id)
                    onboarding_role = ctx.guild.get_role(onboarding_role_id)
                    if onboarding_role:
                        await ctx.author.add_roles(onboarding_role)
                else:
                    if calidum_enabled:
                        await post_to_calidum(username, f"Impossible de trouver le rôle des membres configuré pour {username}")

            except Exception as e:
                logger.error(f"Exception: {e}")
                if calidum_enabled:
                    await post_to_calidum(username, f"Impossible d'ajouter le rôle des membres pour {username}, exception : {e}")

            member_data = {
                "user_id": requester_id,
                "username": username,
                "status": "pending",
                "request_time": str(datetime.now()),
                "github_username": github_username,
                "github_email": github_email
            }
            trema_db.add_member(server_id, member_data)

            if calidum_enabled:
                await post_to_calidum(username, "Membre du serveur", f"Demande d'ajout comme membre pour {username} avec statut 'pending'.")

            embed = Embed(
                title="Demande de membre envoyée",
                description=f"Votre demande pour devenir membre est en attente d'approbation. \nVous pouvez maintenant vous diriger vers notre [wiki][https://wiki.cedille.club] pour faire les pistes d'intégration. Contactez le capitaine lorsque vous avez fini afin de finaliser votre intégration.",
                color=Color.green()
            )
            await ctx.author.send(embed=embed)

        elif role:
            await ctx.author.add_roles(role)
            await ctx.author.send(f"Vous avez été assigné au rôle de {role_name.capitalize()}.")
