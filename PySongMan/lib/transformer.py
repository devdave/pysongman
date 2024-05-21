"""
A python class to typescript adapter/bridge transformer.

The transformed product is a helper class for use with PyWebview and the js_api bridge.

"""

import ast
import pathlib
import typing as T
import warnings
from itertools import zip_longest
import dataclasses

import jinja2
import tap

TEMPLATE_BODY = """
interface Boundary {
    remote: (method_name:string, ...args:unknown[])=> Promise<unknown>
}

{% for child_name, child_methods in child_classes|items() %}
class {{child_name}} {
    private boundary: Boundary

    constructor(boundary:Boundary) {
        this.boundary = boundary
    }

{% for func_name, func_def in child_methods|items() -%}
{%if func_def.doc %}

/*
{{func_def.doc}}
*/
{% endif %}
    {{ func_name }}({{func_def.compiled|join(', ')}}){%if func_def.return_type %}:Promise<{{func_def.return_type}}>{% else %}: Promise<void>{% endif %} {
        {% if func_def.arg_names|length >= 2 -%}
        return this.boundary.remote('{{child_name|lower()}}.{{ func_name }}', {{func_def.arg_names|join(', ')}}) as {%if func_def.return_type %}Promise<{{func_def.return_type}}>{%else%}Promise<void>{% endif %}
        {%- elif func_def.arg_names|length == 1 -%}
        return this.boundary.remote('{{child_name|lower()}}.{{ func_name }}', {{func_def.arg_names[0]}}) as {%if func_def.return_type %}Promise<{{func_def.return_type}}>{%else%}Promise<void>{% endif %}
        {%- else -%}
        return this.boundary.remote('{{child_name|lower()}}.{{ func_name }}') as {%if func_def.return_type %}Promise<{{func_def.return_type}}>{%else%}Promise<void>{% endif %}
        {%- endif %}
    }
{%- endfor %}
}
{% endfor %}

class APIBridge {
    private boundary:Boundary
{% for child_name, _ in child_classes|items() %}
    public {{child_name|lower}}:{{child_name}}
{% endfor %}

    constructor(boundary:Boundary) {
        this.boundary = boundary
{% for child_name, _ in child_classes|items() %}
        this.{{child_name|lower}} = new {{child_name}}(boundary)
{% endfor %}
    }
{% for func_name, func_def in functions|items() -%}
{%if func_def.doc %}

/*
{{func_def.doc}}
*/
{% endif %}
    {{ func_name }}({{func_def.compiled|join(', ')}}){%if func_def.return_type %}:Promise<{{func_def.return_type}}>{% else %}: Promise<void>{% endif %} {
        {% if func_def.arg_names|length >= 2 -%}
        return this.boundary.remote('{{ func_name }}', {{func_def.arg_names|join(', ')}}) as {%if func_def.return_type %}Promise<{{func_def.return_type}}>{%else%}Promise<void>{% endif %}
        {%- elif func_def.arg_names|length == 1 -%}
        return this.boundary.remote('{{ func_name }}', {{func_def.arg_names[0]}}) as {%if func_def.return_type %}Promise<{{func_def.return_type}}>{%else%}Promise<void>{% endif %}
        {%- else -%}
        return this.boundary.remote('{{ func_name }}') as {%if func_def.return_type %}Promise<{{func_def.return_type}}>{%else%}Promise<void>{% endif %}
        {%- endif %}
    }
{%- endfor %}
}

export default APIBridge

"""

INTERFACE_TEMPLATE = """
{%- for name, def in bodies|items() %}export interface {{name}}{% if def.parent %} extends {{def.parent}}{% endif %} {
{% for field_name, field_type in def.elements|items() %}
    {{field_name}}: {{field_type}}
{%- endfor %}
}
{% endfor %}
""".strip()


class FuncArg(T.NamedTuple):
    """
    A simple function name and its annotated type tuple
    """

    name: T.Optional[ast.expr]
    annotype: T.Optional[str] = None


class FuncDef(T.NamedTuple):
    """
    A transformed function definition
    """

    args: T.List[FuncArg]
    doc: T.Optional[str]
    compiled: T.List[str]
    arg_names: T.List[str]
    return_type: T.Optional[str]


ClassDigest = T.NewType("ClassDigest", tuple[str, dict[str, FuncDef]])


@dataclasses.dataclass
class ChildClass:
    """
    Helper utility that may be deprecated
    """

    name: str
    methods: T.Dict[str, FuncDef] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class TypedDictionary:
    name: str
    elements: T.Dict[str, str]
    parent: str | None = None


def python2ts_types(typename: str | None) -> str:
    """
    Given a python type name, return its typescript equivalent.

    :param typename:
    :return:
    """
    target = typename
    match typename:
        case "str":
            target = "string"
        case "int":
            target = "number"
        case "float":
            target = "number"
        case "bool":
            target = "boolean"
        case None:
            target = "undefined"
        case "datetime":
            target = "string"
        case "date":
            target = "string"
        case _:
            target = typename

    return target


def is_typed_dict(element: ast.ClassDef, bodies=None):
    if isinstance(element, ast.ClassDef):
        if len(element.bases) >= 1:
            for basecls in element.bases:
                if bodies is not None and isinstance(basecls, ast.Name):
                    if basecls.id in bodies:
                        return True

                if isinstance(basecls, ast.Attribute):
                    if basecls.attr == "TypedDict":
                        return True
                    if bodies is not None and basecls.attr in bodies:
                        return True

    return False


def process_types_source(
    src_file: pathlib.Path,
    dest_file: pathlib.Path = None,
):
    if isinstance(src_file, pathlib.Path):
        mod = ast.parse(src_file.read_text(), filename=src_file.name, mode="exec")
    else:
        mod = ast.parse(src_file, filename="app_types.py", mode="exec")

    interface_bodies = {}
    typedefs = []
    for element in mod.body:
        if isinstance(element, ast.ClassDef) and is_typed_dict(
            element, interface_bodies
        ):
            interface_bodies[element.name] = process_typeddict(
                element, interface_bodies
            )

        elif isinstance(element, ast.Assign):
            typedefs.append(process_type_assignment(element))

    typedef_body = "\n".join(typedefs)

    interfaces = transform_types(interface_bodies)

    body = f"{typedef_body}\n{interfaces}\n".strip() + "\n"

    body.replace("\r\n", "\n")

    if dest_file is not None:
        dest_file.write_text(body)

    return body


def process_source(
    src_file: pathlib.Path | str,
    dest: pathlib.Path | None = None,
    header: pathlib.Path | str | None = None,
    product_template: str = TEMPLATE_BODY,
) -> str:
    """

    :param src_file: misnomer as this can be a pathlike object or a string
    :param dest: where to write the transformed product file
    :param header: a header file to append to the transformed product file
    :param product_template: the template for generating the transformed product file
    :return:
    """
    if isinstance(src_file, pathlib.Path):
        module = ast.parse(src_file.read_text(), src_file.name, mode="exec")
    else:
        module = ast.parse(src_file, "raw_source.py", mode="exec")

    body = []

    api_body = None
    child_classes = {}

    for element in module.body:
        if isinstance(element, ast.ClassDef):
            if element.name == "API":
                api_body = process_class(element)
            else:
                child_name, child_methods = process_class(element)
                child_classes[child_name] = child_methods

    clsbody = transform(api_body, child_classes, product_template)
    body.append(clsbody)

    product = "\n\n\n\n".join(body)

    if header is not None:
        if isinstance(header, pathlib.Path) and header.is_file():
            product = header.read_text() + product
        else:
            product = header + "\n" + product

    if dest is not None:
        dest.write_text(product, newline="\n")

    return product


def process_class(class_elm: ast.ClassDef) -> ClassDigest:
    """
    Given a class definition, return a manifect of parsed method definitions.

    :param class_elm:
    :return:
    """
    cls_name = class_elm.name
    functions = {}
    for element in class_elm.body:
        if isinstance(element, ast.FunctionDef):
            if element.name.startswith("__"):
                continue

            functions[element.name] = process_function(element)

    return ClassDigest(
        (
            cls_name,
            functions,
        )
    )


def py2ts_value(something):
    """
    Convert a python value to a transformed value.
    :param something:
    :return:
    """
    if isinstance(something, str):
        return f"'{something}'"
    if isinstance(something, bool):
        return "true" if something is True else "false"

    return repr(something)


def sanitize_defaults(def_type):
    """
    Check for falsey def type and convert it to be TS undefined

    :param def_type:
    :return:
    """
    if def_type in [None, "None", "'None'"]:
        return "undefined"

    return def_type


def process_function_subscript_annotation(arg: ast.Subscript):
    """
    Handle functions with list arguments

    :param arg:
    :return:
    """

    func_type = "any"

    if hasattr(arg.annotation.value, "id") and arg.annotation.value.id == "list":
        func_type = f"{python2ts_types(arg.annotation.slice.id)}[]"

    elif (
        isinstance(arg.annotation.value, ast.Attribute)
        and arg.annotation.value.attr == "Optional"
    ):
        func_type = f"{python2ts_types(arg.annotation.slice.id)} | undefined"

    elif (
        isinstance(arg.annotation.value, ast.Name) and arg.annotation.value.id == "list"
    ):
        func_type = f"{python2ts_types(arg.annotation.slice.id)}[]"

    elif (
        isinstance(arg.annotation.value, ast.Name) and arg.annotation.value.id == "dict"
    ):
        if len(arg.annotation.slice.dims) == 2:
            key_type = python2ts_types(arg.annotation.slice.dims[0].id)
            value_type = python2ts_types(arg.annotation.slice.dims[1].id)
            func_type = f"{{[key:{key_type}]: {value_type}}}"
        else:
            raise ValueError(
                f"Unexpected element count for dict subscript - {arg.annotation} - {len(arg.annotation.slice.dims)}"
            )

    return func_type


def process_function(func_elm: ast.FunctionDef) -> FuncDef:
    """
    Given a function definition, return a transformed function definition.

    :param func_elm:
    :return:
    """
    # unit tests... we don't need no stinking unit tests!
    # beeline for the args

    arg_map = {}

    definition = FuncDef(
        process_args(func_elm.args.args),
        ast.get_docstring(func_elm),
        [],
        [],
        process_returntype(func_elm),
    )

    mapped_defaults = {}

    # does the function have default arguments?
    if len(func_elm.args.defaults) > 0:
        names = [arg.arg for arg in func_elm.args.args]
        names.reverse()
        try:
            defaults = []
            for _, elm in enumerate(func_elm.args.defaults):
                val = py2ts_value(process_default_argument(elm))
                defaults.append(val)

            # defaults = [py2ts_value(elm.value) for elm in func_elm.args.defaults]
        except AttributeError:
            print(f"Unable to process {func_elm} with {func_elm.args}")
            raise

        defaults.reverse()
        married = list(zip_longest(names, defaults))
        married.reverse()
        mapped_defaults = dict(married)

    for arg in func_elm.args.args:  # type: ast.arg
        if arg.arg == "self":
            continue

        definition.arg_names.append(arg.arg)

        func_type = "any"

        match arg.annotation:
            case ast.Name():
                func_type = python2ts_types(arg.annotation.id)
            case ast.Subscript():
                func_type = process_function_subscript_annotation(arg)
            case ast.BinOp():
                func_type = process_binop(arg.annotation)
            case element if element is not None and hasattr(element, "id"):
                func_type = python2ts_types(element.id)
            case element if isinstance(
                element, ast.Attribute
            ) and element.annotation.attr in ["date", "datetime"]:
                func_type = python2ts_types(arg.annotation.attr)
            # case element if element is None:
            #     func_type = "any"
            case None:
                warnings.warn(
                    f"{func_elm.name=} has an argument `{arg.arg}` missing an annotation",
                    SyntaxWarning,
                )
            case _:
                raise TypeError(
                    f"Unable to process {func_elm=} with {arg.annotation=} {vars(arg)}"
                )

        arg_map[arg.arg] = f"{arg.arg}:{func_type}"
        if arg.arg in mapped_defaults and mapped_defaults[arg.arg] in (None, "None"):
            del mapped_defaults[arg.arg]

        if arg.arg not in mapped_defaults:
            arg_body = f"{arg.arg}:{func_type}"
        else:
            arg_body = f"{arg.arg}:{func_type} = {sanitize_defaults(mapped_defaults[arg.arg])}".replace(
                "'", ""
            )

        definition.compiled.append(arg_body)

    return definition


def process_default_argument(default_op):
    """
    Looks for complex default arguments like `list[int,bool]` and converts them to be `number|boolean` if possible

    :param default_op:
    :return:
    """
    if (
        isinstance(
            default_op,
            (
                ast.unaryop,
                ast.UnaryOp,
            ),
        )
        is True
    ):
        # Very likely a negative number
        if isinstance(default_op.op, ast.USub):
            return f"-{default_op.operand.value}"
        if isinstance(default_op.op, ast.UAdd):
            return f"+{default_op.operand.value}"
    elif isinstance(default_op, ast.Constant):
        match default_op.value:
            case True:
                return "True"
            case False:
                return "False"
            case _:
                return str(default_op.value)

    elif hasattr(default_op, "val"):
        return default_op.val
    elif isinstance(default_op, ast.BinOp) and isinstance(default_op.op, ast.BitOr):
        left = python2ts_types(default_op.left.id)
        right = python2ts_types(default_op.right.value)
        return f"{left} | {right}"

    raise ValueError(
        f"I don't know how to handle {type(default_op)} {vars(default_op)}"
    )


def process_args(func_args: T.List[ast.arg]):
    """
    Takes a function arguments, excludes 'self', and converts the rest to TS definitions

    :param func_args:
    :return:
    """
    return {
        arg_elm.arg: FuncArg(arg_elm.annotation)
        for arg_elm in func_args
        if arg_elm.arg != "self"
    }


def process_returntype(func_elm: ast.FunctionDef):
    """
    Converts a function return type to be TS safe.


    :param func_elm:
    :return:
    """

    if isinstance(func_elm.returns, ast.Subscript):
        if (
            isinstance(func_elm.returns.value, ast.Name)
            and func_elm.returns.value.id == "list"
        ):
            name_elm = func_elm.returns.value  # type: ast.Name
            return_slice = func_elm.returns.slice  # type: ast.Name
            if name_elm.id == "list" and isinstance(return_slice, ast.Name):
                return f"{return_slice.id}[]"
        elif isinstance(func_elm.returns.value, ast.Attribute):
            if func_elm.returns.value.attr == "Optional":
                if isinstance(func_elm.returns.slice, ast.Attribute):
                    return f"{func_elm.returns.slice.attr} | undefined"
                if isinstance(func_elm.returns.slice, ast.Name):
                    return f"{func_elm.returns.slice.id} | undefined "

        elif getattr(func_elm.returns.value, "id", None) == "dict":
            return process_dict(func_elm.returns)

    if isinstance(func_elm.returns, ast.Name):
        return python2ts_types(func_elm.returns.id)

    return None


def process_dict(return_elm: ast.Subscript) -> str:
    """
    Given a return type like `dict[str, int]`, converts it into a TS object definition like
        {[key:str]:int}

    :param return_elm:
    :return:
    """
    if len(return_elm.slice.dims) == 2:
        left_side = python2ts_types(return_elm.slice.dims[0].id)
        right_side = python2ts_types(return_elm.slice.dims[1].id)
        return f"{{[key:{left_side}]: {right_side}}}"

    raise ValueError("I don't know how to handle dict[] {return_elm.slice.dims}")


def process_child_class(child_cls: ast.ClassDef) -> ClassDigest:
    """
    Given a child class that is not API, break it down for use by the
    transformer

    :param child_cls:
    :return:
    """
    child = ChildClass(child_cls.name)
    for element in child_cls.body:
        if isinstance(element, ast.FunctionDef):
            child.methods[element.name] = process_function(element)

    return ClassDigest(
        (
            child_cls.name,
            child.methods,
        )
    )


def find_name(element: ast.Name) -> str:
    if hasattr(element, "id"):
        return element.id
    if hasattr(element, "attr"):
        return element.attr

    raise ValueError(f"I don't know how to handle {element}")


def process_binop(bin_st: ast.BinOp) -> str:

    match bin_st:
        case element if hasattr(element, "value"):
            left = python2ts_types(find_name(element.value.left))
            right = python2ts_types(find_name(element.value.right))

        case element if hasattr(element, "left") and hasattr(element, "right"):

            if isinstance(element.left, ast.Subscript):
                left = process_dict(element.left)
            else:
                left = python2ts_types(find_name(element.left))

            match element.right:
                case element if isinstance(
                    element, ast.Constant
                ) and element.value is None:
                    right = "undefined"

                case element if isinstance(element, ast.Name):
                    right = python2ts_types(find_name(element))

                case _:
                    raise ValueError(
                        f"I don't know how to handle this {element.right}, {vars(element.right)}"
                    )
        case _:
            raise ValueError(
                f"I don't know how to handle this {bin_st}, {vars(bin_st)}"
            )

    # if hasattr(bin_st, "value"):
    #     left = python2ts_types(find_name(bin_st.value.left))
    #     right = python2ts_types(find_name(bin_st.value.right))
    #
    # elif hasattr(bin_st, "left") and hasattr(bin_st, "right"):
    #     # assuming `arg: type|None`
    #     left = python2ts_types(find_name(bin_st.left))
    #     if isinstance(bin_st.right, ast.Constant) and bin_st.right.value is None:
    #         right = "undefined"
    #     elif isinstance(bin_st.right, ast.Name):
    #         right = python2ts_types(find_name(bin_st.right))
    #     else:
    #         raise ValueError(
    #             f"I don't know how to handle this {bin_st}, {vars(bin_st)}"
    #         )
    #
    # else:
    #     raise ValueError(f"I don't know how to handle this {bin_st}, {vars(bin_st)}")

    return f"{left} | {right}"


def process_typeddict(target_cls: ast.ClassDef, bases=None) -> TypedDictionary:

    if is_typed_dict(target_cls, bases) is False:
        raise ValueError(f"{target_cls.name} is not a TypedDict")

    # Is something besides TypedDict as base[0]
    parent = (
        target_cls.bases[0].id if isinstance(target_cls.bases[0], ast.Name) else False
    )

    fields = {}
    for element in target_cls.body:
        if isinstance(element, ast.AnnAssign):
            name = element.target.id

            if (
                isinstance(element.annotation, ast.Subscript)
                and element.annotation.value.id == "list"
            ):
                fields[name] = f"{element.annotation.slice.id}[]"
            else:
                element_type = (
                    element.annotation.id
                    if hasattr(element.annotation, "id")
                    else element.annotation.value.id
                )
                field_type = python2ts_types(element_type)
                fields[name] = field_type

    return TypedDictionary(target_cls.name, fields, parent)


def transform_types(bodies: dict[str, TypedDictionary]) -> str:
    """
    Transforms a dictionary of typed dict fields into interfaces

    :param bodies:
    :return:
    """

    template = jinja2.Template(INTERFACE_TEMPLATE, newline_sequence="\n")
    return template.render(
        bodies=bodies,
    ).replace("\r\n", "\n")


def transform(
    payload: ClassDigest, child_classes: dict[str, list[FuncDef]], product_template: str
) -> str:
    """

    Converts a ClassDigest using product_template into a transformed string for use with
        typescript

    :param payload:
    :param product_template:
    :return:
    """

    cls_name, functions = payload

    template = jinja2.Template(product_template, newline_sequence="\n")
    return template.render(
        cls_name=cls_name, functions=functions, child_classes=child_classes
    ).replace("\r\n", "\n")


def process_type_assignment(element: ast.Assign) -> str:
    name = element.targets[0].id

    if isinstance(element.value, ast.BinOp):
        body = process_binop(element.value)

    else:
        raise ValueError(
            f"I don't know how to handle this {element}-{type(element.value)}"
        )

    return f"export type {name} = {body}"


class MainArgs(tap.Tap):
    """
    Dirt simple AST to hopefully parseable Javascript/Typescript
    """

    source: pathlib.Path  # Source Python file to transform into quasi js/ts
    dest: T.Optional[pathlib.Path] = (
        None  # optional file to write to instead of printing to stdout
    )

    dest_header: pathlib.Path = None

    def configure(self) -> None:
        self.add_argument("source", type=pathlib.Path)
        self.add_argument("dest", type=pathlib.Path)
        self.add_argument("dest_header", type=pathlib.Path)


def main():
    """
        see `--help` for more info

    :return:
    """
    args = MainArgs().parse_args()
    assert args.source.exists(), f"Cannot find source {args.source} file to process!"

    if args.dest.name == "-":
        args.dest = None

    if args.dest is not None:
        assert (
            args.dest.parent.exists()
        ), f"Cannot write {args.dest.name} to {args.dest.parent} as it does not exist!"
        assert (
            args.dest.parent.is_dir()
        ), f"Cannot write {args.dest.name} to {args.dest.parent} as it is not a dir!"

    process_source(args.source, dest=args.dest, header=args.dest_header)


if __name__ == "__main__":
    main()
