import dataclasses
import json
from typing import List, Dict


@dataclasses.dataclass
class UserSnippet:
    prefix: str
    body: List[str]
    description: str


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def create_snippets(max_args: int, is_function: bool, is_return: bool) -> Dict[str, UserSnippet]:
    return {
        create_snippet_name(number, is_function, is_return):
            UserSnippet(
                prefix=create_prefix(number, is_function, is_return),
                body=create_body(number, is_function, is_return),
                description=create_description_comment(number, is_function, is_return))
        for number in range(max_args + 1)
    }


def create_body(number: int, is_function: bool, is_return: bool) -> List[str]:
    body: List[str] = [
        create_function_definition(number, is_function),
        create_comment(number, is_return),
    ]
    if number > 0 or is_return:
        body.extend(create_definition_comment(number, is_return))
    return body


def create_definition_comment(number: int, is_return: bool) -> List[str]:
    comments: List[str] = []
    if number > 0:
        comments.extend(create_augment_comments(number))
    if is_return:
        comments.extend(create_return_comments())
    comments.append(create_docstring_comment())
    return comments


def create_augment_comments(number: int) -> List[str]:
    args_comments = [
        f"\t${{arg{i}}} (${{arg{i}type}}): ${{args{i}comment}}" for i in range(1, number + 1)]
    return ["", "Args:"] + args_comments


def create_return_comments() -> List[str]:
    return [
        "",
        "Returns:",
        "\t${returntype}: ${returncomment}"
    ]


def create_snippet_name(number: int, is_function: bool, is_return: bool) -> str:
    func = "Function" if is_function else "Method"
    returns = " Returns " if is_return else " "
    return f"Args {number}{returns}{func}"


def create_prefix(number: int, is_function: bool, is_return: bool) -> str:
    prefix = "f" if is_function else "m"
    ret = "r" if is_return else ""
    return f"{prefix}a{number}{ret}"


def create_function_definition(number: int, is_function: bool) -> str:
    var_name = "functionname" if is_function else "methodname"
    return f"def ${{{var_name}}}({create_augment(number, is_function)}) -> ${{returntype}}:"


def create_augment(number: int, is_function: bool) -> str:
    args_str = ", ".join(
        [f"${{arg{i}}}: ${{arg{i}type}}" for i in range(1, number + 1)])
    return f"{create_self(number, is_function)}{args_str}"


def create_self(number: int, is_function: bool) -> str:
    slf = "" if is_function else "self"
    self_comma = ", " if not is_function and number > 0 else ""
    return f"{slf}{self_comma}"


def create_comment(number: int, is_return: bool) -> str:
    end_comment = create_docstring_comment() if number == 0 and not is_return else ""
    return f"\t\"\"\"${{comment}}${end_comment}"


def create_docstring_comment() -> str:
    return "\"\"\""


def create_description_comment(number: int, is_function: bool, is_return: bool) -> str:
    return_str = "で戻り値が" if is_return else ""
    type_string = "関数" if is_function else "メソッド"
    return f"引数が{number}個{return_str}ある時の{type_string}"


max_args = int(input("最大引数:"))

dic: Dict[str, UserSnippet] = {}
dic.update(create_snippets(max_args=max_args,
                           is_function=True, is_return=False))
dic.update(create_snippets(max_args=max_args,
                           is_function=True, is_return=True))
dic.update(create_snippets(max_args=max_args,
                           is_function=False, is_return=False))
dic.update(create_snippets(max_args=max_args,
                           is_function=False, is_return=True))


with open("snippet.json", mode="w", encoding="utf-8") as f:
    f.write(json.dumps(dic, cls=EnhancedJSONEncoder, ensure_ascii=False,
                       indent=4, sort_keys=True, separators=(',', ': ')))
