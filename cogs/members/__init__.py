from datetime import datetime
from discord import\
	Color,\
	Embed,\
	Option,\
	SlashCommandGroup,\
	utils,\
	File,\
	SelectOption
from discord.ui import Select, View
from cogs.admin import is_authorized
from cogs.prompts import prompt_user_with_select, prompt_user_with_confirmation, prompt_user
from logger import logger
from cogs.utils.dispatch import dispatch_add_member_to_gh_org_gw

def _create_member_cmds(trema_db, github_token):
	member = SlashCommandGroup(name="member", description="Gérer les membres du serveur.")

	@member.command(name="list", description="Lister les membres du serveur.")
	@is_authorized(trema_db)
	async def list_members(ctx, status: Option(str, "Statut des membres à afficher", choices=["pending", "approved", "rejected"], required=False) = None):
		server_id = ctx.guild.id
		members = trema_db.get_members(server_id, status=status)

		if not members:
			await ctx.respond("Aucun membre trouvé pour ce serveur.", ephemeral=True)
		else:
			embed = Embed(title="Liste des membres", description="Voici la liste des membres du serveur:", color=Color.blue())
			for idx, member in enumerate(members, start=1):
				embed.add_field(
					name=f"#{idx}: {member['username']}",
					value=f"ID: {member['_id']}\nStatut: {member['status']}\nRequête: {member.get('request_time', 'N/A')}\nGitHub: {member.get('github_username', 'N/A')}\nEmail: {member.get('github_email', 'N/A')}",
					inline=False
				)
			await ctx.respond(embed=embed, ephemeral=True)

	@member.command(name="update", description="Mettre à jour le statut d'un membre.")
	@is_authorized(trema_db)
	async def update_member(ctx):
		await ctx.defer(ephemeral=True)
		server_id = ctx.guild.id
		members = trema_db.get_members(server_id)

		if not members:
			await ctx.respond("Aucun membre trouvé pour ce serveur.", ephemeral=True)
			return

		member_options = [
			SelectOption(label=member['username'], description=f"ID: {member['_id']}, Statut: {member['status']}", value=str(member['_id']))
			for member in members
		]
		
		member_select = Select(
			placeholder="Sélectionnez un membre à mettre à jour",
			options=member_options,
			min_values=1,
			max_values=1
		)

		async def member_select_callback(interaction):
			member_id = int(member_select.values[0])
			selected_member = next(member for member in members if member["_id"] == member_id)

			status_select = Select(
				placeholder="Sélectionnez le nouveau statut",
				options=[
					SelectOption(label="Pending", value="pending"),
					SelectOption(label="Approved", value="approved"),
					SelectOption(label="Rejected", value="rejected")
				],
				min_values=1,
				max_values=1
			)

			async def status_select_callback(interaction):
				new_status = status_select.values[0]
				trema_db.update_member(member_id, {"status": new_status})

				embed = Embed(title="Statut du membre mis à jour", description=f"Le statut du membre avec ID {member_id} est maintenant '{new_status}'.", color=Color.green())
				await interaction.response.send_message(embed=embed, ephemeral=True)

				if new_status == "approved":
					member_user = ctx.guild.get_member(int(selected_member["user_id"]))
					if member_user:
						try:
							await member_user.send(f"Félicitations! Vous avez été approuvé en tant que membre du serveur et vous pouvez maintenant accéder aux canaux réservés aux membres.")
						except:
							await ctx.respond("Impossible d'envoyer un message privé au membre approuvé.", ephemeral=True)

						try:
							member_role_id = trema_db.get_server_member_role(server_id)
							if isinstance(member_role_id, str):
								member_role_id = int(member_role_id)
							member_role = ctx.guild.get_role(member_role_id)
							if member_role:
								await member_user.add_roles(member_role)
							else:
								await interaction.response.send_message("Impossible de trouver le rôle des membres configuré.", ephemeral=True)
						except Exception as e:
							logger.error(f"Exception: {e}")
							await interaction.response.send_message("Impossible d'ajouter le rôle des membres.", ephemeral=True)

						try:
							await add_member_to_gh_org_gw(ctx, selected_member, github_token)
						except Exception as e:
							logger.error(f"Exception: {e}")
							await interaction.response.send_message("Impossible d'ajouter le membre à l'organisation GitHub.", ephemeral=True)

			status_select.callback = status_select_callback
			status_view = View()
			status_view.add_item(status_select)

			await interaction.response.send_message(f"Vous avez sélectionné {selected_member['username']}. Entrez le nouveau statut:", view=status_view, ephemeral=True)

		member_select.callback = member_select_callback
		member_view = View()
		member_view.add_item(member_select)

		await ctx.respond("Sélectionnez le membre à mettre à jour:", view=member_view, ephemeral=True)

	@member.command(name="delete", description="Supprimer un membre.")
	@is_authorized(trema_db)
	async def delete_member(ctx):
		await ctx.defer(ephemeral=True)

		server_id = ctx.guild.id
		members = trema_db.get_members(server_id)

		if not members:
			await ctx.respond("Aucun membre trouvé pour ce serveur.", ephemeral=True)
			return

		member_options = [
			SelectOption(label=member['username'], description=f"ID: {member['_id']}, Statut: {member['status']}", value=str(member['_id']))
			for member in members
		]
		
		member_select = Select(
			placeholder="Sélectionnez un membre à supprimer",
			options=member_options,
			min_values=1,
			max_values=1
		)

		async def member_select_callback(interaction):
			member_id = int(member_select.values[0])
			selected_member = next(member for member in members if member["_id"] == member_id)

			trema_db.delete_member(member_id)

			embed = Embed(title="Membre supprimé", description=f"Le membre avec l'ID {member_id} ({selected_member['username']}) a été supprimé.", color=Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)

		member_select.callback = member_select_callback
		member_view = View()
		member_view.add_item(member_select)

		await ctx.respond("Sélectionnez le membre à supprimer:", view=member_view, ephemeral=True)

	@member.command(name="add", description="Ajouter un membre manuellement.")
	@is_authorized(trema_db)
	async def add_member(ctx, user_id: Option(str, "ID de l'utilisateur à ajouter"), status: Option(str, "Statut du membre", choices=["pending", "approved", "rejected"])):
		await ctx.defer(ephemeral=True)

		server_id = ctx.guild.id
		user_id_int = int(user_id)
		member_user = ctx.guild.get_member(user_id_int)
		username = member_user.name if member_user else "Unknown"

		member_data = {
			"user_id": user_id_int,
			"username": username,
			"status": status,
			"request_time": str(datetime.now())
		}
		
		trema_db.add_member(server_id, member_data)

		embed = Embed(title="Membre ajouté", description=f"Le membre {username} a été ajouté avec le statut '{status}'.", color=Color.green())
		await ctx.respond(embed=embed, ephemeral=True)

		if status == "approved" and member_user:
			try:
				member_role_id = trema_db.get_server_member_role(server_id)
				if isinstance(member_role_id, str):
					member_role_id = int(member_role_id)

				member_role = ctx.guild.get_role(member_role_id)
				
				if member_role:
					await member_user.add_roles(member_role)
					await ctx.respond(f"Le rôle '{member_role.name}' a été attribué à {username}.", ephemeral=True)
				else:
					await ctx.respond("Impossible de trouver le rôle des membres configuré.", ephemeral=True)
			except Exception as e:
				logger.error(f"Exception: {e}")
				await ctx.respond("Impossible d'ajouter le rôle des membres.", ephemeral=True)

			try:
				selected_member = trema_db.get_member(server_id, user_id_int)
				await add_member_to_gh_org_gw(ctx, selected_member, github_token)
			except Exception as e:
				logger.error(f"Exception: {e}")
				await ctx.respond("Impossible d'ajouter le membre à l'organisation GitHub.", ephemeral=True)

	return member


async def add_member_to_gh_org_gw(ctx, member, github_token):
	add_to_gh_org = await prompt_user_with_confirmation(ctx, f"Ajouter {member['username']} à l'organisation GitHub ?")

	if add_to_gh_org:
		github_username = member.get("github_username")
		if not github_username:
			github_username = await prompt_user(ctx, "Entrez le nom d'utilisateur GitHub du membre", "Nom d'utilisateur GitHub")
			if not github_username:
				return
		github_email = member.get("github_email")
		if not github_email:
			github_email = await prompt_user(ctx, "Entrez l'adresse e-mail associée à GitHub du membre", "E-mail GitHub")
			if not github_email:
				return
		team_sre = await prompt_user_with_select(ctx, "Ajouter dans l'équipe SRE ?", ["vrai", "faux"], True)
		cluster_role = await prompt_user_with_select(ctx, "Choisir le rôle pour le cluster", ["None", "Reader", "Operator", "Admin"], True)

		success, message = await dispatch_add_member_to_gh_org_gw(github_username, github_email, github_token, team_sre, cluster_role)

		if success:
			await ctx.author.send(f"Le membre {member['username']} a été ajouté à l'organisation GitHub avec succès.\n{message}")
		else:
			await ctx.author.send(f"Impossible d'ajouter le membre {member['username']} à l'organisation GitHub.\n{message}")
