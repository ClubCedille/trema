from quart import request, jsonify
from prometheus_client import Counter, Summary
import traceback
from logger import logger
import re
from discord import Embed

REQUEST_COUNT = Counter('trema_http_requests_total', 'Total HTTP Requests')
REQUEST_LATENCY = Summary('trema_http_request_latency_seconds', 'Latency of HTTP requests')
ERROR_COUNT = Counter('trema_http_errors_total', 'Total HTTP Errors')

def create_routes(app, database, trema):
    create_routes_webhooks(app, database, trema)

    @app.before_request
    @REQUEST_LATENCY.time()
    def before_request():
        REQUEST_COUNT.inc()

    @app.after_request
    def after_request(response):
        if response.status_code >= 400:
            ERROR_COUNT.inc()
        return response

def create_routes_webhooks(app, database, trema):
    @app.route('/webhooks/<uuid>', methods=['POST'])
    async def handle_webhook(uuid):
        logger.info(f"Processing webhook called with UUID: {uuid}")

        try:
            channelID = database.get_channel_by_webhook(uuid)
            if channelID is None:
                logger.error(f"Webhook called with UUID: {uuid} - Invalid UUID")
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
            
            logger.info(f"Webhook called with UUID: {uuid} - Success")
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            error_info = {
                'error': 'Internal Server Error',
                'message': str(e),
                'trace': traceback.format_exc()
            }
            logger.error(f"Webhook called with UUID: {uuid} - Error: {error_info}")
            return jsonify(error_info), 500
