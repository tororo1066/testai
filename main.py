import asyncio
import threading
import time
from asyncio import Future

import discord
import torch
from discord import Client
from transformers import AutoModelForCausalLM, AutoTokenizer

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = "あなたはAIアシスタントです。"

model_name = "elyza/ELYZA-japanese-Llama-2-7b-fast-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

# if torch.cuda.is_available():
#     model = model.to("cuda")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = Client(intents=intents)


@bot.event
async def on_message(message: discord.Message):
    global DEFAULT_SYSTEM_PROMPT
    if message.author.bot:
        return
    if not message.content.startswith("!"):
        return
    print(message.content)

    command = message.content.split("!")[1].split(" ")[0]
    if command is None:
        await message.channel.send("!system <prompt>")
        await message.channel.send("!msg <prompt>")
        return
    args = message.content.split(" ")[1:]
    if command == "system":
        if len(args) == 0:
            await message.channel.send("現在のシステムプロンプト: " + DEFAULT_SYSTEM_PROMPT)
        else:
            DEFAULT_SYSTEM_PROMPT = " ".join(args)
            await message.channel.send("システムプロンプトを変更しました。")
    elif command == "msg":
        generating_msg = await message.reply("生成中...")
        cor = asyncio.to_thread(generate, " ".join(args))
        output = await cor
        await generating_msg.edit(content=output)


def generate(prompt: str):
    prompt = "{bos_token}{b_inst} {system}{prompt} {e_inst} ".format(
        bos_token=tokenizer.bos_token,
        b_inst=B_INST,
        system=f"{B_SYS}{DEFAULT_SYSTEM_PROMPT}{E_SYS}",
        prompt=prompt,
        e_inst=E_INST,
    )

    with torch.no_grad():
        now = time.perf_counter()
        print("Generating...")
        token_ids = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")

        output_ids = model.generate(
            token_ids.to(model.device),
            max_new_tokens=256,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    print("End of generation. Time: ", time.perf_counter() - now)
    output = tokenizer.decode(output_ids.tolist()[0][token_ids.size(1):], skip_special_tokens=True)
    print("Output: ", output)
    return output


bot.run("MTE1NzE3NTE0MDU4NTU4MjYwMw.GEcU-s.R38hcO5HDKJxkBT_-th1-kiK3Zg2aj6l4yOg0E")
