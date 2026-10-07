#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中文电码双向转换：不带参数进入菜单，带参数可批量处理。"""

import argparse
import json
import re
import sys
from pathlib import Path

TABLE_PATH = Path(__file__).resolve().with_name("telecodes.json")


def load_table(path=TABLE_PATH):
    """加载随项目附带的离线码表。四位代码必须以字符串保存。"""
    with Path(path).open(encoding="utf-8") as file:
        table = json.load(file)["codes"]
    if not isinstance(table, dict) or not table:
        raise ValueError("码表为空或格式不正确。")
    for code, character in table.items():
        if not re.fullmatch(r"[0-9]{4}", code) or not isinstance(character, str) or len(character) != 1:
            raise ValueError(f"码表条目格式不正确：{code!r}")
    return table


def split_codes(text):
    """接受连续数字，或用空白、逗号、分号分隔的四位数字。"""
    text = text.strip()
    if not text:
        raise ValueError("请输入中文电码，内容不能为空。")

    if re.fullmatch(r"[0-9]+", text):
        if len(text) % 4:
            raise ValueError("连续数字的长度必须是4的倍数，不能省略开头的0。")
        return [text[i:i + 4] for i in range(0, len(text), 4)]

    parts = re.split(r"[\s,，;；]+", text)
    for index, part in enumerate(parts, 1):
        if not re.fullmatch(r"[0-9]{4}", part):
            raise ValueError(f"第{index}组 {part!r} 不正确：每组必须是4位半角数字。")
    return parts


def decode(text, table):
    """数字转文字；遇到未知代码时报错，避免悄悄丢掉内容。"""
    characters = []
    for index, code in enumerate(split_codes(text), 1):
        if code not in table:
            raise ValueError(f"第{index}组代码 {code} 不在本项目码表中，请核对数字或码表版本。")
        characters.append(table[code])
    return "".join(characters)


def encode(text, table):
    """文字转数字；忽略排版空白，但保留有码的全角空格。"""
    reverse = {}
    for code, character in sorted(table.items()):
        reverse.setdefault(character, code)

    codes = []
    for index, character in enumerate(text, 1):
        if character.isspace() and character != "\u3000":
            continue
        if character not in reverse:
            raise ValueError(f"第{index}个字符 {character!r} 不在本项目码表中。")
        codes.append(reverse[character])
    if not codes:
        raise ValueError("请输入要转换的文字，内容不能为空。")
    return " ".join(codes)


def interactive(table):
    """适合初学者的交互菜单：运行后按照提示输入即可。"""
    print("中文电码转换工具（离线版）")
    while True:
        print("\n1. 数字转中文\n2. 中文转数字\n0. 退出")
        choice = input("请选择：").strip()
        if choice == "0":
            return 0
        if choice not in ("1", "2"):
            print("请输入 1、2 或 0。")
            continue
        try:
            text = input("请输入四位数字代码：" if choice == "1" else "请输入文字：")
            result = decode(text, table) if choice == "1" else encode(text, table)
            print("转换结果：", result)
        except ValueError as error:
            print("错误：", error)


def build_parser():
    parser = argparse.ArgumentParser(description="中文电码双向转换；不带参数时进入中文菜单。")
    commands = parser.add_subparsers(dest="command")
    for name, description in (("decode", "四位数字转文字"), ("encode", "文字转四位数字")):
        command = commands.add_parser(name, help=description, description=description)
        command.add_argument("text", nargs="?", help="需要转换的内容，建议用双引号包起来")
        command.add_argument("-i", "--input", type=Path, help="读取UTF-8文本文件")
        command.add_argument("-o", "--output", type=Path, help="把结果保存为UTF-8文本文件")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        table = load_table()
        if args.command is None:
            return interactive(table)

        if args.text is not None and args.input is not None:
            parser.error("直接输入内容和 -i 文件输入只能选一种。")
        if args.input is not None:
            text = args.input.read_text(encoding="utf-8-sig")
        elif args.text is not None:
            text = args.text
        elif not sys.stdin.isatty():
            text = sys.stdin.read().lstrip("\ufeff")
        else:
            parser.error("请提供要转换的内容，或用 -i 指定文件。")

        result = decode(text, table) if args.command == "decode" else encode(text, table)
        if args.output is None:
            print(result)
        else:
            args.output.write_text(result + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("\n已退出。", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
