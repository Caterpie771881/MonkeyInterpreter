# Monkey Interpreter by python

本项目是《用 Go 语言自制解释器》中构建的 Monkey 解释器的 python 实现

支持 python3.10+

## 使用方法

```
cd MonkeyInterpreter; touch main.py
python main.py
```

启动词法分析器的 REPL:

```python
# main.py
from lexer.repl import REPL

repl = REPL()
repl.run()
```

启动语法分析器的 REPL:

```python
# main.py
from parser.repl import REPL, Mode

# tostring 模式
repl = REPL(Mode.tostring)
repl.run()

# json 模式
# repl = RELP(Mode.json)
# repl.run()
```
