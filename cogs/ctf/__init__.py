from discord import Embed, Color
from prometheus_client import Counter

ODYSSEE_CMD_COUNT = Counter('trema_odyssee_cmd_total', 'Total uses of the /odyssee command')
SECRET_CMD_COUNT = Counter('trema_secret_cmd_total', 'Total uses of the /secret command')

def _create_odyssee_cmds(trema_bot):    
    @trema_bot.command(name="odyssee", description="Groupe de commandes pour l'événement Odyssée des clubs.")
    async def odyssee(ctx):
        ODYSSEE_CMD_COUNT.inc()
        embed = Embed(
            title="🎉 Félicitation 🎉",
            description="Vous avez réussi à invoquer l'événement Odyssée des clubs. La récompense est un /secret bien gardé.",
            color=Color.green()
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @trema_bot.command(name="secret", description="Révéler le secret de l'Odyssée des clubs.")
    async def secret(ctx):
        SECRET_CMD_COUNT.inc()
        embed = Embed(
            title="🎉 Secret de l'Odyssée des clubs 🎉",
            description="Le secret est : **Le club CEDILLE est le meilleur club de l'ÉTS!**",
            color=Color.green()
        )
        await ctx.respond(embed=embed, ephemeral=True)
