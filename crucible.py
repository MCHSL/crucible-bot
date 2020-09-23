from aiohttp_requests import requests
import discord
import os

async def disassemble_code(code):
	resp = await requests.post("http://crucible.lulzsec.co.uk/post", headers={
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
			"Accept": "*/*",
			"Accept-Language": "en-US,en;q=0.5",
			"Content-Type": "multipart/form-data; boundary=---------------------------2922271336469813944540577231"
		},
		data=f'-----------------------------2922271336469813944540577231\r\nContent-Disposition: form-data; name=\"uploaded_file\"; filename=\"direct.dm\"\r\nContent-Type: application/octet-stream\r\n\r\n{code}\r\n-----------------------------2922271336469813944540577231--\r\n')
	return await resp.json()

client = discord.Client()
@client.event
async def on_ready():
	print('Ready')

@client.event
async def on_message(message):
	if message.author == client.user:
		return
		
	if message.content.startswith("<@"+str(client.user.id)+">"):
		code = message.content
		code = code[code.find(">")+1:]
		procname = code[:code.find("```")].strip()

		code = code[code.find("```") + 3 : code.rfind("```")]
		
		disassembly = await disassemble_code(code)
		print(disassembly)
		
		error = disassembly["errorCode"]
		color = 0x00FF00
		if error:
			color = 0xFF0000
		elif not disassembly["analysisSuccess"]: # TODO: changewhen the right field is added
			color = 0xFFFF00
			
		desc = ""
		if not disassembly["analysisSuccess"]:
			desc = "WARNING: Unsupported opcodes detected, results of disassembly may be incorrect."
		
		embed = discord.Embed(title="Crucible", type = "rich", color=color, description=desc)
		embed.add_field(name="Compiler Output", value="```" + disassembly["output"] + "```", inline=False)
		if not error:
			proc = disassembly["procs"][0]
			if procname:
				for candidate in disassembly["procs"]:
					if candidate["path"].startswith(procname):
						proc = candidate
						break
			
			embed.add_field(name="Disassembly", value="```" + proc["disasm"] + "```", inline=False)
		embed.set_footer(text="Powered by http://crucible.lulzsec.co.uk\nPing @Asd#2411 with issues.")
		await message.channel.send(embed=embed)

client.run(os.environ.get("DISCORD_API_KEY"))