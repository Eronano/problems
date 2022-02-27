import argparse
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import IO

import requests
from bs4 import BeautifulSoup
from more_itertools import first_true

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

EDITOR = "code"
PATH_GENTP_CPP = Path("template/gen_tp.cpp")
PATH_GENTP_PY = Path("template/gen_tp.py")
PATH_PROTP = Path("template/pro_tp.md")
PATH_SACFG_TP = Path("template/cfg_sa_tp.yaml")
PATH_SAPROTP = Path("template/pro_sa_tp.md")
PATH_STDTP = Path("template/std_tp.cpp")
PATH_TMP_FOLDER = Path("tmp")

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43",
    "Connection": "keep-alive"
}

RE_TABLE_ALIGN = r"-(?=\040\|)"
RE_EXAMPLE_CASE_NOTICE = r"【.*(?P<a>\d).*样例.*】|【.*样例.*(?P<b>\d).*】|#+.*样例.*(?P<c>\d).*|#+.*(?P<d>\d).*样例.*"
RE_CASES_RANGE = r"【数据.*】|#+\s数据.*"
RE_EXAMPLE_INPUT_CASE = r"输入样例 #\d"


def write_normal(f: IO, article: BeautifulSoup, title: str):
    h = article.find(lambda t: t.string == title)
    if h:
        f.write(f"# {title}\n\n" + h.find_next("div").string.strip('\n') + "\n\n")


def write_example(f: IO, article: BeautifulSoup):
    f.write("# 输入输出样例\n\n")
    cnt = 0
    cursor = article.find(lambda tag: tag.string == "输入输出样例").find_next("h3")
    while cursor and re.match(RE_EXAMPLE_INPUT_CASE, cursor.string):
        cnt += 1
        f.write(f"```input{cnt}\n")
        f.write(cursor.find_next("code").string.strip('\n'))
        f.write("\n```\n\n")
        cursor = cursor.find_next("code")

        f.write(f"```output{cnt}\n")
        f.write(cursor.find_next("code").string.strip('\n'))
        f.write("\n```\n\n")
        cursor = cursor.find_next("h3").find_next("h3")


def write_notice(f: IO, article: BeautifulSoup):
    notice: BeautifulSoup = article.find(lambda tag: str(tag.string).find("说明") != -1)
    f.write("# 说明/提示\n\n")
    s = notice.find_next("div").string.strip('\n')
    s = re.sub(RE_TABLE_ALIGN, ":", s)
    s = re.sub(RE_EXAMPLE_CASE_NOTICE, lambda m: f"【样例解释 #{first_true(m.groups())}】", s)
    s = re.sub(RE_CASES_RANGE, "【数据规模】", s)
    f.write(s + '\n')


def get_problem(_id: str, name: str):
    with open(get_pro_path(name) / f"{name}.md", "w", encoding="UTF-8") as f:
        article: BeautifulSoup = BeautifulSoup(
            requests.get(f"https://www.luogu.com.cn/problem/{_id}", headers=HEADERS).content, "lxml"
        ).article

        write_normal(f, article, "题目背景")
        write_normal(f, article, "题目描述")
        write_normal(f, article, "输入格式")
        write_normal(f, article, "输出格式")
        write_example(f, article)
        write_notice(f, article)


def compile_cpp(path: Path):
    if os.system(f"g++ {path} -o {PATH_TMP_FOLDER / path.stem} -O2 -std=c++17"):
        raise Exception(f"{path.name} 编译失败")


def get_pro_path(problem: str):
    return Path(f"{re.match(r'[A-Z]+', problem).group()}/{problem}")


def process_problems(raw: list[str]):
    problems = []
    for it in raw:
        t = it.split('-')
        if len(t) == 1:
            problems.extend(t)
        elif len(t) == 2:
            lb = int(re.search(r"\d+$", t[0]).group())
            rb = int(re.search(r"\d+$", t[1]).group())
            if rb < lb:
                raise Exception("题目区间错误")
            lpre = t[0][:-len(str(lb))]
            if lpre != t[1][:-len(str(rb))]:
                raise Exception("题目 ID 前缀不相同")
            for i in range(lb, rb + 1):
                problems.append(lpre + str(i))
        else:
            raise Exception("题目区间格式错误")
    return problems


def create(args):
    problems = process_problems(args.problem)
    for problem in problems:
        path_pro = get_pro_path(problem)
        if path_pro.exists():
            opt = input(f"题目 {problem} 已经存在了，继续还是跳过(Y/Not Y)")
            if opt != 'Y':
                continue
        os.makedirs(path_pro)
        if args.submitans:
            continue
        if not args.nogen:
            if args.python:
                shutil.copy(PATH_GENTP_PY, path_pro / "gen.py")
            else:
                shutil.copy(PATH_GENTP_CPP, path_pro / "gen.cpp")
        if not args.nostd:
            shutil.copy(PATH_STDTP, path_pro / "std.cpp")

    if args.get:
        sources = process_problems(args.get)
        if len(problems) != len(sources):
            raise Exception("题目数量不匹配")
        for (problem, source) in zip(problems, sources):
            get_problem(source, problem)
    elif args.submitans:
        for problem in problems:
            shutil.copy(PATH_SAPROTP, get_pro_path(problem) / f"{problem}.md")
            shutil.copy(PATH_SACFG_TP, get_pro_path(problem) / "config.yaml")
    else:
        for problem in problems:
            shutil.copy(PATH_PROTP, get_pro_path(problem) / f"{problem}.md")
    if len(problems) == 1:
        os.system(f"{EDITOR} {get_pro_path(problems[0]) / f'{problems[0]}.md'}")


def generate(args):
    logger = logging.getLogger("generate")
    problems = process_problems(args.problem)
    for problem in problems:
        for file in PATH_TMP_FOLDER.iterdir():
            os.remove(file)
        path_pro = get_pro_path(problem)
        path_std = path_pro / "std.cpp"
        if path_std.exists():
            logger.info(f"编译 {path_std.name}")
            compile_cpp(path_std)
        else:
            raise Exception("标程不存在")

        logger.info("开始生成输入样例")
        path_gen_cpp = path_pro / "gen.cpp"
        path_gen_py = path_pro / "gen.py"
        if path_gen_cpp.exists():
            logger.info(f"编译 {path_gen_cpp.name}")
            compile_cpp(path_gen_cpp)
            os.system(f"cd {PATH_TMP_FOLDER} && gen")
        elif path_gen_py.exists():
            shutil.copy(path_gen_py, PATH_TMP_FOLDER)
            os.system(f"cd {PATH_TMP_FOLDER} && python gen.py")
        else:
            raise Exception("生成器不存在")
        logger.info("所有输入样例已生成")

        logger.info("开始生成输出样例")
        files_input = PATH_TMP_FOLDER.glob("*.in")
        for file in files_input:
            os.system(f"{PATH_TMP_FOLDER / 'std'} < {file} > {PATH_TMP_FOLDER / (file.stem + '.out')}")
            logger.info(f"输出样例 #{file.stem} 已生成")

        logger.info("开始打包测试数据")
        os.system(f"7z a -tzip {path_pro / 'testcase.zip'} {PATH_TMP_FOLDER / '*.in'} {PATH_TMP_FOLDER / '*.out'}")
        logger.info("测试数据打包完成")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title="command")

    parser_create = subparser.add_parser("c", help="创建题目")
    parser_create.add_argument("problem", nargs="+", help="要创建的题目，支持区间")
    group = parser_create.add_mutually_exclusive_group()
    group.add_argument("--get", "-g", nargs="*", metavar="SOURCE", help="从洛谷获取题面，支持区间，题目数量及且顺序要与要创建的题目相同")
    group.add_argument("--submitans", "-s", action="store_true", help="提交答案题")
    parser_create.add_argument("--python", "-p", action="store_true", help="使用 python 生成器")
    parser_create.add_argument("--nogen", "-ng", action="store_true", help="不生成生成器模板")
    parser_create.add_argument("--nostd", "-ns", action="store_true", help="不生成标程模板")
    parser_create.set_defaults(func=create)

    parser_generate = subparser.add_parser("g", help="生成测试数据")
    parser_generate.add_argument("problem", nargs="+", help="要生成数据的题目，支持区间")
    parser_generate.set_defaults(func=generate)

    if len(sys.argv) < 2:
        parser.print_help()
    else:
        arguments = parser.parse_args()
        arguments.func(arguments)
