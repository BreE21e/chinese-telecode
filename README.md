# 中文电码转换工具

一个适合 CTF 初学者使用的 Python 小工具，支持 **四位数字转文字** 和 **文字转四位数字**。附带离线码表，运行时不用联网，也不用安装第三方库。

## 中文电码是什么？

中文电码用四位数字表示一个字符，例如：

| 电码 | 文字 |
| --- | --- |
| 0361 | 公 |
| 2973 | 正 |
| 6134 | 诚 |
| 0207 | 信 |

所以 `0361 2973 6134 0207` 转换后是 `公正诚信`。

**四位数字开头的 0 不能省略。** 中文电码是查表编码，不是直接把数字当成 ASCII 或 Unicode。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| `telecode.py` | 转换程序，带中文注释和交互菜单 |
| `telecodes.json` | 离线码表，必须和程序放在同一文件夹 |
| `README.md` | 使用说明 |
| `DATA_SOURCE.md` | 码表来源、快照信息和范围说明 |
| `requirements.txt` | 说明无需第三方依赖 |
| `tests/test_telecode.py` | 转换、输入检查和命令行测试 |

## 新手快速开始（Windows）

1. 安装 Python 3.9 或更新版本。已有 Python 就不用重新安装。
2. 下载项目 ZIP 并解压；不要直接在压缩包里运行。
3. 打开解压后的项目文件夹，确保能看到 `telecode.py` 和 `telecodes.json`。
4. 在资源管理器地址栏输入 `powershell`，按回车。
5. 运行：

```powershell
python .\telecode.py
```

程序会显示菜单：

```text
1. 数字转中文
2. 中文转数字
0. 退出
```

输入 `1` 并回车，再输入：

```text
0361 2973 6134 0207 0735 6168
```

结果是：

```text
公正诚信和谐
```

如果系统使用 `py` 命令，可以把下面各示例里的 `python` 换成 `py`。

## 直接用命令转换

数字转中文：

```powershell
python .\telecode.py decode "0361 2973 6134 0207"
```

输出：`公正诚信`。

连续数字也可以，每四位自动分成一组：

```powershell
python .\telecode.py decode "0361297361340207"
```

中文转数字：

```powershell
python .\telecode.py encode "公正诚信"
```

输出：`0361 2973 6134 0207`。

数字之间支持空格、换行、英文或中文逗号、英文或中文分号。使用分隔符时，每组必须恰好四位，不能混用八位长组和四位短组。使用半角数字，不接受全角数字。

编码时忽略普通空格、换行和制表符；**全角空格 `　` 保留并编码为 `9998`**。本工具不自动转换繁简体，也不自动转换标点样式。

## 转换文本文件

把数字保存到 UTF-8 编码的 `codes.txt`，运行：

```powershell
python .\telecode.py decode -i .\codes.txt -o .\result.txt
```

结果会写入 `result.txt`。输入文件支持 UTF-8 BOM；输出统一为 UTF-8。指定已有输出文件时会覆盖它。

把文字文件编码成数字：

```powershell
python .\telecode.py encode -i .\text.txt -o .\encoded.txt
```

也可以通过管道传入内容：

```powershell
"0361 2973" | python .\telecode.py decode
```

## 在其他 Python 程序中使用

```python
from telecode import load_table, decode, encode

table = load_table()
print(decode("0361 2973", table))  # 公正
print(encode("公正", table))       # 0361 2973
```

不要先把电码转成整数，否则 `0361` 会变成 `361`，前导零会丢失。

## 错误与限制

- 未知代码、未收录的字符、数字长度不正确时，会显示具体错误，不会默默丢弃内容。
- 附带的是大陆 1983 年版本来源的码表快照，不覆盖所有地区、历史版本或全部 Unicode 字符。
- 快照包含 **7287 个单字符映射**；来源中以图片表示的 `5831`、`7016` 和以描述表示的 `9992`～`9995` 未收录，详见 `DATA_SOURCE.md`。
- 本工具处理文字和数字，不负责从 WAV 识别摩斯电码，也不负责继续解核心价值观编码。
- 若出现找不到文件的错误，请检查是否进入了项目文件夹，以及是否保留了 `telecodes.json`。

## 原理

解码：按四位分组 → 在码表中查找 → 把查到的字符拼接起来。

编码：逐个读取字符 → 在反向码表中查找 → 输出四位代码，用空格分隔。

实现中的核心操作是字典查询。比如字典记录 `"0361": "公"`，查询 `table["0361"]` 就得到 `公`。

## 运行测试

在项目目录运行：

```powershell
python -m unittest discover -s tests -v
```

测试覆盖已知转换、整张码表往返、无效输入、UTF-8 BOM 文件、管道输入、交互菜单和错误退出码。

## 上传到 GitHub

建议仓库名：`chinese-telecode`。

建议仓库描述：`离线中文电码双向转换工具，支持命令行、交互菜单和文本文件，适合 CTF 初学者。`

在 GitHub 新建仓库，选择 **Add file → Upload files**，上传解压后的项目文件和 `tests` 文件夹，再点击 **Commit changes**。上传项目内容，方便 GitHub 直接展示 README 和源代码。

## 数据来源

码表参考 [千千秀字：1983 年《标准电码本（修订本）》](https://www.qqxiuzi.cn/bianma/dianbao.html)。详细来源和未收录项目见 `DATA_SOURCE.md`。
