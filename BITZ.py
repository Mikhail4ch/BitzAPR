import discord
import asyncio
import requests
from fake_useragent import FakeUserAgent
from discord import app_commands

TOKEN = 'MTM4NzQyMjA3MTkzMTUzNTM4MA.GP_AeL.BlKwn2-D4-I97y-lBfFE-UtGOwSPtIlVFqnGXM'
GUILD_ID = 1387438507559223308  # make sure this is your test server ID, as an int

headers = {
    'user-agent': FakeUserAgent().random
}

class BITZ:
    def __init__(self):
        self._rewardPool = 720
        self._api = 'https://api.eclipsescan.xyz/v1/account/tokens?address=5FgZ9W81khmNXG8i96HSsG7oJiwwpKnVzmHgn9ZnqQja'
        self._totalStaked = None
        self._fetch_total_staked()

    def _fetch_total_staked(self):
        try:
            response = requests.get(self._api, headers=headers, timeout=8)
            data = response.json()
            tokens = data['data']['tokens']
            for token in tokens:
                if token.get('symbol', '').upper() == 'BITZ':
                    self._totalStaked = float(token['balance'])
                    return
            self._totalStaked = float(tokens[0]['balance'])
        except Exception:
            self._totalStaked = 0

    def _get_apr(self):
        if not self._totalStaked or self._totalStaked == 0:
            return 0
        return round(self._rewardPool / self._totalStaked * 100, 3)

    def findOutApr(self):
        apr = self._get_apr()
        return f'24H APR = {apr}％'

    def annualAPR(self):
        if not self._totalStaked or self._totalStaked == 0:
            return "Annual APR = N/A"
        apr = self._rewardPool / self._totalStaked * 365 * 100
        return f'Annual APR = {round(apr)}％'

    def bitz_summary(self, initial_amount):
        apr = self._get_apr()  # This should return the annual APR as a percent (not fraction)
        apr_fraction = apr * 365 / 100  # Convert to decimal

        period_days = {
            "Daily": 1,
            "Weekly": 7,
            "Monthly": 30.436875,
            "Yearly": 365
        }

        results = []
        results.append(f"⬇️ Fam, by staking {initial_amount} $BITZ ⬇️")
        for label, days in period_days.items():
            earn = initial_amount * apr_fraction * (days / 365)
            results.append(f"👉 {label} you will earn: {earn:.3f} $BITZ")

        return "\n".join(results)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
bitz = BITZ()

async def update_status():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            bitz._fetch_total_staked()
            apr24 = bitz.findOutApr().replace('％', '%').split('=')[1].strip()
            aprAnnual = bitz.annualAPR().replace('％', '%').split('=')[1].strip()
            status_text = f"24H: {apr24} | Annual: {aprAnnual}"
            activity = discord.Activity(type=discord.ActivityType.custom, state=status_text,name='123')
            await client.change_presence(activity=activity)
            print(f"Set custom activity: {status_text}")
        except Exception as e:
            print(f"Failed to update status: {e}")
        await asyncio.sleep(300)

@tree.command(name="purestakingyield", description="Calculate daily earnings from staked BITZ", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(amount='Amount of BITZ staked')
async def dailyprofit(interaction: discord.Interaction, amount: float):
    await interaction.response.defer(thinking=True)
    bitz._fetch_total_staked()
    response = bitz.bitz_summary(amount)
    await interaction.followup.send(response)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    client.loop.create_task(update_status())

client.run(TOKEN)



