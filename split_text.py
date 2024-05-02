# !/usr/bin/env python #
# -*- coding: utf-8 -*-

"""
受け取ったテキストを区切り文字で区切ったリストを返す関数を定義するファイル
"""

import re

def split_text(text):
	"""
	受け取ったstringから「,、」などで区切ってリストに束縛して返すプログラム
	"""
	# 正規表現パターンを定義
	pattern = r'[^\w\s]'  # 単語や空白以外の文字で区切る

	# 正規表現による分割
	tokens = re.split(pattern, text)

	# 空白文字のトークンを除去
	tokens = [token.strip() for token in tokens if token.strip()]

	return tokens
