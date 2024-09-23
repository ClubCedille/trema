from discord import\
	ButtonStyle,\
	ui,\
	Interaction

class confirmation_button(ui.View):
	def __init__(self):
		super().__init__()

	async def disable_buttons(self):
		for item in self.children:
			item.disabled = True
		await self.message.edit(view=self)

	@ui.button(label="Oui", custom_id="yes_button", style=ButtonStyle.success)
	async def yes_button_callback(self, button: ui.Button, interaction: Interaction):
		button.style = ButtonStyle.grey
		button.label = "Confirmé"
		await self.disable_buttons()
		self.stop()

	@ui.button(label="Non", custom_id="no_button", style=ButtonStyle.danger)
	async def no_button_callback(self, button: ui.Button, interaction: Interaction):
		button.style = ButtonStyle.grey
		button.label = "Refusé"
		await self.disable_buttons()
		self.stop()

class skip_button(ui.View):
	def __init__(self):
		super().__init__()
	
	@ui.button(label="Skip", custom_id="skip_button", style=ButtonStyle.blurple)
	async def skip_button_callback(self, button: ui.Button, interaction: Interaction):
		button.style = ButtonStyle.grey
		button.label = "Ignoré"
		button.disabled = True
		self.stop()  

		# Update the original message's embed
		embed = interaction.message.embeds[0]
		embed.color = 0x808080  
		embed.title = "Ignoré"
		await interaction.message.edit(embed=embed, view=self)

class now_button(ui.View):
	def __init__(self):
		super().__init__()
	
	@ui.button(label="Maintenant", custom_id="now_button", style=ButtonStyle.blurple)
	async def now_button_callback(self, button: ui.Button, interaction: Interaction):
		button.style = ButtonStyle.grey
		button.disabled = True
		self.stop()  

		# Update the original message's embed
		embed = interaction.message.embeds[0]
		embed.color = 0x808080  
		embed.description = "Annonce programmée pour maintenant."
		await interaction.message.edit(embed=embed, view=self)