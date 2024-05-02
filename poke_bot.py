# !/usr/bin/env python #
# -*- coding: utf-8 -*-

"""
特定のメッセージで応答状態にし、ポケモン名、速度（最速、準速など）を受け取ると、
-6~+6までのポケモンの素早さ実数値が出てくるDiscord bot
"""
__author__ = "uzi"
__version__ = "0.0"
__date__ = "2024/4/12 (created by 2024/4/12)"

from math import floor
import discord
from jaconv import hira2kata
import requests
from .split_text import split_text
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
		self.poke_dict = get_dict_id_of_pokemon()
		self.except_list =["ランドロス","ボルトロス", "トルネロス", "ヒヒダルマ", "シェイミ", "ジガルデ",
							"メテノ", "コオリッポ", "ヨワシ", "ザシアン", "ザマゼンタ", "フーパ", "ネクロズマ",
							"バドレックス", "ロトム", "デオキシス", "ロトム"]

	async def on_ready(self):
		"""
		botを起動した際に表示させるメッセージ
		"""
		print(f"Logged in as {self.user} ID {self.user.id}")
		print("------")
		#test()

	async def on_message(self, message):
		"""
		メッセージを受け取り、返答するメソッド

		Prameters:
		message(discord.Message):受け取ったメッセージオブジェクト
		"""
		if message.author == self.user:
			return
		if message.content.startswith("!p"):
			await message.channel.send("起動完了！\nポケモンの名前と速度(最速、準速、無振り、下降、最遅)を入力してください！")

			def check(m):
				return m.channel == message.channel

			while True:
				#メッセージを受け取ってポケモン名と速さを取り出す
				receive_message = await self.wait_for("message", check=check)
				message_content = receive_message.content
				target_list = split_text(message_content)

				#ポケモン名をカタカナに変換する
				try:
					ja_pokemon_name = hira2kata(target_list[0])
					await self.check_except_pokemon(ja_pokemon_name, message)
					pokemon_condition = target_list[1]
					print(ja_pokemon_name+":"+target_list[1])
				except IndexError:
					await message.channel.send("正しい文字を入力してください。")
					continue

				try:
					#ポケモン名からidを辞書で取得する
					pokemon_id = self.poke_dict[ja_pokemon_name]
					print("pokemon_id:"+pokemon_id)
					speed = get_num_of_speed(pokemon_id)
					print("speed:"+str(speed))
					result = calc_speed(speed, pokemon_condition)
					await message.channel.send(ja_pokemon_name+":"+pokemon_condition+":"+str(result))
					await self.say_real_num_of_each_rank(result, message)
				except KeyError:
					await message.channel.send("入力失敗、正しい文字列を入力してください")
		return

	async def say_real_num_of_each_rank(self, result, message):
		"""
		各ランクの実数値を計算して送信するメソッド
		"""
		result_string = ""
		dict_of_rank = {-6:1/4, -5:2/7, -4:1/3, -3:2/5, -2:1/2, -1:2/3, 0:1, 1:3/2, 2:2, 3:5/2, 4:3, 5:7/2, 6:4}
		for key, value in dict_of_rank.items():
			if key == 0:
				continue
			num = floor(result*value)
			result_string = f"{result_string}" + "{:+d}".format(key) + f" : {num}\n" # noqa
		print(f"{result_string}")
		await message.channel.send(f"{result_string}")
		return

	async def check_except_pokemon(self, poke_name, message):
		"""
		素早さが複数あるポケモンには通常フォルムしか対応していない旨を警告するメソッド
		"""
		if poke_name in self.except_list:
			await message.channel.send("このポケモンは通常フォルムの素早さで応答します。")
		return

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
	return floor(result)

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

def get_dict_id_of_pokemon():
	"""
	ポケモンの日本語名と英語名を対応させている辞書を作成する関数
	"""
	with open("ja_2_id.txt","r", encoding="utf-8") as file:
		l_strip = [s.rstrip() for s in file.readlines()]
	result_dict = {}
	for i in l_strip:
		both_name = i.split("\t")
		ja_name = both_name[0]
		en_name = both_name[1]
		#print(ja_name+":"+en_name)
		result_dict[ja_name] = en_name
	return result_dict

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

if __name__ == "__main__":
	main()
