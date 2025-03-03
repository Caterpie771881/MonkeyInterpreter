# Monkey Interpreter by python

本项目是《用 Go 语言自制解释器》中构建的 Monkey 解释器的 python 实现

支持 python3.10+

## 使用方法

```sh
cd MonkeyInterpreter
python main.py # 默认启动的是求值器
```

启动词法分析器的 REPL:

```sh
python main.py --run lexer
```

启动语法分析器的 REPL:

```sh
# tostring 模式
python main.py --run parser --mode tostring

# json 模式
python main.py --run parser --mode json
```

启动求值器的 REPL:

```sh
python main.py --run eval
```

## Monkey 语言介绍

> 引用自《用 Go 语言自制解释器》的前言部分

Monkey 具有以下特性:
* 类 C 语法
* 变量绑定
* 整型和布尔型
* 算数表达式
* 内置函数
* 头等函数和高阶函数
* 闭包
* 字符串数据结构
* 数组数据结构
* 哈希数据结构

在 Monkey 中绑定值和名称的方法如下:

```
let age = 1;
let name = "Monkey";
let result = 10 * (20 / 2);
```

除了整型、布尔型和字符串, Monkey 解释器还支持数组和哈希表.

下面展示如何将一个整型数组绑定到一个名称上:

```
let myArray = [1, 2, 3, 4, 5];
```

下面是一个哈希表, 其中的值和键进行了关联:

```
let thorsten = {"name": "Thirsten", "age": 28}
```

下面使用索引表达式访问数组和哈希表中的元素

```
myArray[0]       // => 1
thorsten["name"] // => "Thorsten"
```

let 语句还可以用来绑定函数和名称, 下面是将两个数字相加的一个函数

```
let add = fn(a, b) { a + b; };
```

调用函数很简单

```
add(1, 2);
```

下面是一个复杂一点的函数 `fibonacci`, 它会返回斐波那契数列的第 n 项:

```
let fibonacci = fn(x) {
    if (x == 0) {
        0
    } else {
        if (x == 1) {
            1
        } else {
            fibonacci(x - 1) + fibonacci(x - 2);
        }
    }
};
```

注意, `fibonacci` 函数在递归中调用了自身

Monkey 还支持一类特殊的函数, 即高阶函数. 这类函数以其他函数作为参数, 如下所示:

```
let twice = fn(f, x) {
    return f(f(x));
}

let addTwo = fn(x) {
    return x + 2;
}

twice(addTwo, 2); // => 6
```

这里的 `twice` 接受了两个参数: 函数 `addTwo` 和整数 `2`. 这段代码调用了 `addTwo` 两次, 第一次以 `2` 为参数, 第二次以第一次的返回值为参数. 最后一行代码返回结果 6

是的, 我们可以在函数调用中将函数作为参数. Monkey 中的函数只是值, 与整数或字符串一样. 具有这个特性的函数成为"头等函数" (first-class function)
