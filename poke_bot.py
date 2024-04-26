# /bin/python #

"""
特定のメッセージで応答状態にし、ポケモン名、速度（最速、準速など）を受け取ると、
-6~+6までのポケモンの素早さ実数値が出てくるDiscord bot
"""
__author__ = "uzi"
__version__ = "0.0"
__date__ = "2024/4/12 (created by 2024/4/12)"

import math
import discord
import jaconv
#import pokebase
import requests
import split_text
import bot_token as token

BASE_URL = "https://pokeapi.co/api/v2/"

class PokeClient(discord.Client):
	"""
	Discordの返答とメッセージの受け取りを担うクラス
	"""
	def __init__(self, *args, **options) -> None:
		"""
		PokeClientを初期化するメソッド
		"""
		super().__init__(*args, **options)
		self.poke_dict = get_en_name_of_pokemon()

	async def on_ready(self):
		"""
		botを起動した際に表示させるメッセージ
		"""
		print(f"Logged in as {self.user} ID {self.user.id}")
		print("------")

	async def on_message(self, message):
		"""
		メッセージを受け取り、返答するメソッド
		"""
		if message.content.startswith("!p"):
			await message.channel.send("起動完了！\nポケモンの名前と速度(最速、準速、無振り、下降、最遅)を入力してください！")
			while True:
				receive_message = await self.wait_for("message")
				message_content = receive_message.content
				target_list = split_text.split_text(message_content)
				ja_pokemon_name = jaconv.hira2kata(target_list[0])
				pokemon_condition = target_list[1]
				print(ja_pokemon_name+":"+target_list[1])
				en_pokemon_name = self.poke_dict[ja_pokemon_name]
				speed = get_num_of_speed(en_pokemon_name)
				result = calc_speed(speed, pokemon_condition)
				await message.channel.send(ja_pokemon_name+":"+pokemon_condition+":"+str(result))

def calc_speed(speed, condition):
	"""
	ポケモンの実数値を返す関数
	"""
	result = 0
	#condition_dict = {"最速":1.1, "準速":1.0, "無補正":1.0, "下降":0.9, "最遅":0.9}
	if condition == "最速":
		result = ((speed*2+31+252/4)*0.5+5)*1.1
	elif condition == "準速":
		result = (speed*2+31+252/4)*0.5+5
	elif condition == "無振り":
		result = (speed*2+31)*0.5+5
	elif condition == "下降":
		result = ((speed*2+31)*0.5+5)*0.9
	elif condition == "最遅":
		result = ((speed*2)*0.5+5)*0.9
	else:
		return 0
	return math.floor(result)

def main():
	"""
	Discord上で「!p」のコマンドを入力すると入力待ち状態となり、入力を受け取るとそのポケモンの各ランクの
	素早さ実数値を返すbotのプログラム
	"""
	my_intents = discord.Intents.default()
	my_intents.message_content = True

	#scrape()

	client = PokeClient(intents=my_intents)
	client.run(token.token)

def get_num_of_speed(name):
	"""
	pokeapiに問い合わせて、任意のポケモンの素早さ種族値をもらう関数
	"""
	response = requests.get(BASE_URL + f"pokemon/{name.lower()}", timeout=10)
	if response.ok:
		data = response.json()
		stats_list =data["stats"]
		speed = stats_list[5]["base_stat"]
	else:
		speed = None
		print("http response error")
	return speed

def get_en_name_of_pokemon():
	"""
	ポケモンの日本語名と英語名を対応させている辞書を作成する関数
	"""
	with open("jp_en.txt","r", encoding="utf-8") as file:
		l_strip = [s.rstrip() for s in file.readlines()]
	result_dict = {}
	for i in l_strip:
		both_name = i.split("\t")
		ja_name = both_name[0]
		en_name = both_name[1]
		#print(ja_name+":"+en_name)
		result_dict[ja_name] = en_name
	return result_dict

# def get_pokemon_japanese_name(english_name):
# 	response = requests.get(BASE_URL + f'pokemon-species/{english_name.lower()}')
# 	if response.ok:
# 		data = response.json()
# 		for name_info in data['names']:
# 			if name_info['language']['name'] == 'ja-Hrkt':
# 				return name_info['name']
# 		return "日本語名が見つかりません。"
# 	else:
# 		return "ポケモンの情報を取得できませんでした。"

if __name__ == "__main__":
	main()