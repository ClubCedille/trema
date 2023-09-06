from discord import\
	Embed
import re 
from quart import request, jsonify

def create_routes(app, database, trema):
	create_routes_webhooks(app, database, trema)

def create_routes_webhooks(app, database, trema):
	@app.route('/webhooks/<uuid>', methods=['POST'])
	async def handle_webhook(uuid):
		channelID = database.get_channel_by_webhook(uuid)
		if channelID is None:
			return jsonify({'error': 'Invalid webhook UUID'}), 400

		incoming_data = await request.json
		embed_data = incoming_data.get('embeds', [])[0]

		embed = Embed(
			title=embed_data.get('title', 'N/A'),
			color=int(embed_data.get('color', '0'))
		)

		description = embed_data.get('description', 'N/A')

		fields = re.findall(r"\*\*(.+?):\*\* (.+?)(?=\n|$)", description)
		for name, value in fields:
			embed.add_field(name=name, value=value, inline=False if "Details" in name else True)

		footer_data = embed_data.get('footer', {})
		footer_text = footer_data.get('text', '')
		if footer_text:
			embed.set_footer(text=footer_text)

		channel = trema.get_channel(int(channelID))
		await channel.send(embed=embed)
			
		return jsonify({'status': 'success'}), 200