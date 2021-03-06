import importlib.util
from pathlib import Path

mem = []
line = 0
extensions = {}

def import_ext(path):
    nametxt = open(str((path / "name.txt").resolve()), "r")
    name = "kq_" + nametxt.read()
    nametxt.close()
    main = str((path / "main.py").resolve())
    
    spec = importlib.util.spec_from_file_location(name, main)
    extension = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extension)
    return extension

def split_level(line, split_char):
    parentheses = 0
    line_split = []
    parentheses_visibility = []
    element = ""
    for i in line:
        if i == "(":
            in_list = element.startswith(("&#", "#", "$#"))
            if parentheses > 0 or in_list:
                element = element + i
                parentheses_visibility.append(True)
            else:
                parentheses_visibility.append(False)
            parentheses += 1
        elif i == ")":
            parentheses -= 1
            if parentheses_visibility.pop():
                element = element + i
        elif i == split_char and parentheses == 0:
            line_split.append(element)
            element = ""
        else:
            element = element + i
    if element != "":
        line_split.append(element)
    return line_split

def process_operation(line):
    if not line.startswith(".."):
        line_split = split_level(line, " ")
        line_processed = []
        for i in range(1, len(line_split)):
            line_processed.append(process_value(line_split[i]))
        OPERATIONS[line_split[0]](line_processed)

def process_value(value):
    if not value.split(" ")[0] in INOPS:
        value_type = value[0]
        value_val = value[1:]
        STATIC_CHARACTERS = [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "&", "#"
        ]
        if value_type in STATIC_CHARACTERS:
            if value_type != "&":
                value_val = value_type + value_val
            if value_val[0] == "#":
                value_val = split_level(value_val[1:], ",")
                value_processed = []
                for i in value_val:
                    value_processed.append(process_value(i))
                return value_processed
            else:
                if "." in value_val:
                    return float(value_val)
                else:
                    return int(value_val)
        elif value_type == "$":
            if value_val[0] == "#":
                value_val = split_level(value_val[1:], ",")
                value_processed = []
                for i in range(0, 2):
                    value_processed.append(int(process_value(value_val[i])))
                return mem[value_processed[0]: value_processed[1]]
            else:
                return mem[int(process_value(value_val))]
        elif value_type == ":":
            return value_val
        elif value_type + value_val == "null":
            return None
        else:
            raise ValueError(f"Invalid inop / identifier")
    else:
        value_split = split_level(value, " ")
        value_processed = []
        for i in range(1, len(value_split)):
            value_processed.append(process_value(value_split[i]))
        return INOPS[value_split[0]](value_processed)


# The most useful function.
def expect_type(value, val_type):
    if not ((bool in val_type) and (value == 0 or value == 1)):
        if not ((None in val_type) and (value is None)):
            if not type(value) in val_type:
                raise ValueError(f"Expected {val_type}")
            else:
                return type(value)
        else:
            return None
    else:
        return bool

# Because I was too lazy to just do a bit of subtraction, lol
def set_line(set):
    global line

    line = set - 1

def str_to_list(string):
    ord_list = []
    for i in string:
        ord_list.append(ord(i))
    return ord_list
    
def list_to_str(string_list):
    chr_string = ""
    for i in string_list:
        chr_string += chr(i)
    return chr_string
    
# I don't actually know what classes do but I'm just using them to
# organize stuff


class Operation:
    def prt(params):
        param_type = expect_type(params[0], [int, float, None, list])
        if param_type is list:
            print(list_to_str(params[0])) 
        elif param_type is None:
            print("null")
        else:
            print(params[0])

    def alloc(params):
        expect_type(params[0], [int])
        expect_type(params[1], [int])
        for i in range(0, params[0]):
            mem.insert(params[1], None)

    def set(params):
        param_type = expect_type(params[0], [int, None])
        expect_type(params[1], [int, float, None])
        if param_type is not None:
            mem[params[0]] = params[1]

    def free(params):
        param_type = expect_type(params[0], [int])
        param_type = expect_type(params[1], [int])
        del mem[params[0]: params[1] + params[0]]

    def goto(params):
        expect_type(params[0], [int])
        set_line(params[0])

    def conditional(params):
        expect_type(params[0], [bool])
        expect_type(params[1], [int])
        expect_type(params[2], [int])
        if params[0] == 1:
            set_line(params[1])
        else:
            set_line(params[2])

    def import_extension(params):
        global extensions
        
        expect_type(params[0], [str])
        expect_type(params[1], [str])
        extensions[params[1]] = import_ext(Path(params[0]))
        
    def extension_op(params):
        global extensions
        global mem
        global line
        
        expect_type(params[0], [str])
        expect_type(params[1], [str])
        expect_type(params[2], [list])
        extensions[params[0]].OPERATIONS[params[1]](params[2], [mem, line])

class Inop:
    # Yandere moment
    def math(params):
        expect_type(params[0], [list])
        stack = []
        expression = params[0]
        for i in expression:
            if i == "+":
                curr = stack.pop(-1)
                curr = stack.pop(-1) + curr
                stack.append(curr)
            elif i == "-":
                curr = stack.pop(-1)
                curr = stack.pop(-1) - curr
                stack.append(curr)
            elif i == "*":
                curr = stack.pop(-1)
                curr = stack.pop(-1) * curr
                stack.append(curr)
            elif i == "/":
                curr = stack.pop(-1)
                curr = stack.pop(-1) / curr
                stack.append(curr)
            elif i == "//":
                curr = stack.pop(-1)
                curr = stack.pop(-1) // curr
                stack.append(curr)
            elif i == "^":
                curr = stack.pop(-1)
                curr = stack.pop(-1) ** curr
                stack.append(curr)
            elif i == "%":
                curr = stack.pop(-1)
                curr = stack.pop(-1) % curr
                stack.append(curr)
            else:
                expect_type(i, [int, float])
                stack.append(i)
        return stack[0]

    def compare(params):
        expect_type(params[0], [int, float, list, None, bool])
        expect_type(params[1], [str])
        expect_type(params[2], [int, float, list, None, bool])
        if params[1] == "<":
            return int(params[0] < params[2])
        elif params[1] == "<=":
            return int(params[0] <= params[2])
        elif params[1] == "==":
            return int(params[0] == params[2])
        elif params[1] == "!=":
            return int(params[0] != params[2])
        elif params[1] == ">":
            return int(params[0] > params[2])
        elif params[1] == ">=":
            return int(params[0] >= params[2])

    # I don't know how I feel about the logic functions being their own
    # seperate inops, especially since the compare function exists...
    class Logic:
        def logic_and(params):
            expect_type(params[0], [bool])
            expect_type(params[1], [bool])
            return int(bool(params[0]) and bool(params[1]))

        def logic_or(params):
            expect_type(params[0], [bool])
            expect_type(params[1], [bool])
            return int(bool(params[0]) or bool(params[1]))

        def logic_not(params):
            expect_type(params[0], [bool])
            return int(not bool(params[0]))

    def text_input(params):
        param_type = expect_type(params[0], [int, list])
        prompt = ""
        if param_type is list:
            for i in params[0]:
                expect_type(i, [int])
                prompt = prompt + chr(i)
        else:
            prompt = chr(params[0])
        input_list = []
        for i in list(input(prompt)):
            input_list.append(ord(i))
        return input_list

    # This inop is useless.
    def get(params):
        expect_type(params[0], [int])
        return mem[params[0]]

    class Conversions:
        def convert_int(params):
            string = ""
            param_type = expect_type(params[0], [list, float, int])
            if param_type is List:
                for i in params[0]:
                    expect_type(i, [int])
                    string = string + chr(i)
            else:
                string = params[0]
            return int(string)

        def convert_str(params):
            def convert(value):
                param_type = expect_type(value, [int, float, bool, None, list])
                if param_type is None:
                    return [110, 117, 108, 108]
                elif param_type is list:
                    string = [35]
                    for i in value:
                        if isinstance(i, list):
                            string += [40] + convert(i) + [41, 44]
                        else:
                            string += convert(i) + [44]
                    if string == [35]:
                        return string
                    else:
                        return string[0:-1]

                else:
                    string = str(value)
                    string_list = []
                    for i in string:
                        string_list.append(ord(i))
                    return string_list
            return convert(params[0])

        def convert_float(params):
            string = ""
            expect_type(params[0], [list, float, int])
            for i in params[0]:
                expect_type(i, [int])
                string = string + chr(i)
            return float(string)

        def convert_special(params):
            string = ""
            expect_type(params[0], [list])
            return str_to_list(params[0])
         
    def allocated(params):
        return len(mem)

    # This function has been revised over countless times, it used to be an op
    def load(params):
        expect_type(params[0], [int])
        expect_type(params[1], [bool])
        expect_type(params[2], [list])
        length = len(params[2])
        for i, v in enumerate(params[2]):
            expect_type(i, [int])
            if params[0] + i > len(mem) or bool(params[1]):
                mem.insert(params[0] + i, v)
            else:
                mem[i] = v
        return length

    # The following two functions didn't exist until much later in the
    # development
    def length(params):
        expect_type(params[0], [list])
        return len(params[0])

    def index(params):
        expect_type(params[0], [list])
        expect_type(params[1], [int])
        return params[0][params[1]]
    
    def cat(params):
        expect_type(params[0], [list])
        expect_type(params[1], [list])
        return params[0] + params[1]
        
    def extension_inop(params):
        global extensions
        global mem
        global line
        
        expect_type(params[0], [str])
        expect_type(params[1], [str])
        expect_type(params[2], [list])
        return extensions[params[0]].INOPS[params[1]](params[2], [mem, line])


OPERATIONS = {
    "print": Operation.prt,
    "alloc": Operation.alloc,
    "set": Operation.set,
    "goto": Operation.goto,
    "if": Operation.conditional,
    "free": Operation.free,
    "import": Operation.import_extension,
    "eop": Operation.extension_op,
}
INOPS = {
    "math": Inop.math,
    "compare": Inop.compare,
    "and": Inop.Logic.logic_and,
    "or": Inop.Logic.logic_or,
    "not": Inop.Logic.logic_not,
    "input": Inop.text_input,
    "get": Inop.get,
    "load": Inop.load,
    "int": Inop.Conversions.convert_int,
    "float": Inop.Conversions.convert_float,
    "str": Inop.Conversions.convert_str,
    "special": Inop.Conversions.convert_special,
    "allocated": Inop.allocated,
    "length": Inop.length,
    "index": Inop.index,
    "cat": Inop.cat,
    "ein": Inop.extension_inop,
}

def run_file():
    def init():
        global mem
        global line
        global program

        mem = []
        line = 0
        program = []

    init()

    global line
    global program

    text = txt.get(1.0, tk.END).splitlines()

    for l in text:
        program.append(l)

    while line < len(program):
        process_operation(program[line])
        line += 1

import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("Kinquett Files", "*.kt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        txt.insert(tk.END, text)
    window.title(f"Kinquett - {filepath}")

def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension="kt",
        filetypes=[("Kinquett Files", "*.kt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = txt.get(1.0, tk.END)
        output_file.write(text)
    window.title(f"Kinquett - {filepath}")

window = tk.Tk()
window.title("Kinquett")

window.rowconfigure(0, minsize=900, weight=1)
window.columnconfigure(1, minsize=900, weight=1)

txt = tk.Text(window)
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)

scrollbar = tk.Scrollbar(txt)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
btn_save = tk.Button(fr_buttons, text="Save As...", command=save_file)
btn_run = tk.Button(fr_buttons, text="Run", command=run_file)

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)
btn_run.grid(row=2, column=0, sticky="ew", padx=5)

fr_buttons.grid(row=0, column=0, sticky="ns")
txt.grid(row=0, column=1, sticky="nsew")

if __name__ == "__main__":
    window.mainloop()

"""


def main():
    program = []

    def init():
        global mem
        global line
        nonlocal program

        mem = []
        line = 0
        program = []

    def multi_line_input(prompt):
        single_line = None
        multi_line = []
        print(prompt)
        while True:
            single_line = input()
            if single_line != "":
                multi_line.append(single_line)
            else:
                return multi_line

    while True:
        global line

        init()
        program = multi_line_input("Input program")
        while line < len(program):
            process_operation(program[line])
            line += 1


if __name__ == "__main__":
    main()

"""
