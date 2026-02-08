from discord import Embed, Color, Option, SlashCommandGroup
from cogs.admin import is_authorized
from cogs.utils.dispatch import post_to_calidum, dispatch_grav_gw
def _create_grav_requests_cmds(trema_db, request, github_token):
    @request.command(name="grav",
        description="Créer une requête pour un site web GRAV")
    @is_authorized(trema_db)
    async def request_grav_workflow(ctx,
            domaine: Option(str, "Domaine à utiliser (eg cedille.etsmtl.ca)"),
            nom_club: Option(str, "Nom du club. Pas de caractères spéciaux ou d'espaces outre - et _"),
            contexte: Option(str, "Contexte du site (eg. site web, blog, etc.)"),
            skeleton_url: Option(str, "URL du squelette Grav (optionnel, voir getgrav.org/downloads/skeletons)", required=False, default="")):

        await ctx.defer(ephemeral=True)

        success, message = await dispatch_grav_gw(domaine, nom_club, contexte, github_token, skeleton_url)

        if success:
            request_data = {
                "domaine": domaine,
                "nom_club": nom_club,
                "contexte": contexte,
                "skeleton_url": skeleton_url
            }

            trema_db.create_request(ctx.guild_id, "grav", request_data)

            calidum_enabled = trema_db.get_server_calidum_enabled(ctx.guild_id)
            if calidum_enabled:
                await post_to_calidum(ctx.author.name, "Requête création site web Grav", f"Domaine: {domaine}, Nom du club: {nom_club}, Contexte: {contexte}")

            embed = Embed(title="Requête de service", description=f"La requête pour '{nom_club}' a été initiée avec succès.\n{message}", color=Color.green())
        else:
            embed = Embed(title="Erreur de requête", description=f"Échec de l'initiation de la requête pour '{nom_club}'.\n{message}", color=Color.red())

        await ctx.followup.send(embed=embed, ephemeral=True)

    @request.command(name="list",
                    description="Liste des requêtes pour ce serveur")
    @is_authorized(trema_db)
    async def list_requests(ctx):
        requests = trema_db.list_requests(ctx.guild_id)
        if not requests:
            await ctx.respond("Aucune requête n'a été faite pour ce serveur.", ephemeral=True)
        else:
            embed = Embed(title="Liste des requêtes", description="Voici la liste des requêtes dans ce serveur:", color=Color.blue())
            
            for request in requests:
                data_display = ', '.join([f"{key}: {value}" for key, value in request['request_data'].items()])
                request_description = f"Type: {request['request_type']}, Status: {request['status']}, Data: {data_display}"
                embed.add_field(name=f"Requête avec id:{request['_id']}", value=request_description, inline=False)
            
            await ctx.respond(embed=embed, ephemeral=True)

    @request.command(name="delete",
                    description="Supprimer une requête")
    @is_authorized(trema_db)
    async def delete_request(ctx, request_id: Option(str, "Id de la requête à supprimer")):
        success = trema_db.delete_request(ctx.guild_id, request_id)
        if not success:
            await ctx.respond(f"Requête avec l'id {request_id} non trouvé.", ephemeral=True)
        else:
            await ctx.respond(f"Requête avec l'id {request_id} supprimé.", ephemeral=True)
