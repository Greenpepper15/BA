from  pygments.lexers import c_cpp
import pygments.token as Tok
import math
from git import Repo
from pathlib import Path
import time
import subprocess
import calendar
import json

map_num_to_month = {index: month for index, month in enumerate(calendar.month_abbr) if month}


def main():
    yearly_commits = ["3b62de3",  # 2012
                      "f044635",  # 2013
                      "c34dd6b",  # 2014
                      "67bd7d4",  # 2015
                      "c23ead2",  # 2016
                      "7ab96cc",  # 2017
                      "b29110c",  # 2018
                      "b8b04e3",  # 2019
                      "bb51a8b",  # 2020
                      "827170f",  # 2021
                      "a6538ac"  # 2022
                      ]
    git_dir = ".../vtr-verilog-to-routing"  # specify path to git reposiory
    dest = "../Data/halstead"  # specify path to output directory
    path = "../vtr-verilog-to-routing/ODIN_II/SRC"  # specify path to source code of which to measure halstead (must be in specified git repository)

    get_git_data(git_dir, dest, path, yearly_commits)


def get_git_data(git_dir: str, output_file_dir: str, odin_code_dir: str, commits: list):
    repo_py = Repo(git_dir)

    for commit in commits:
        subprocess.run(["git", "-C", git_dir, "checkout", commit])
        commit_date = time.gmtime(repo_py.commit().committed_date)
        output_file_name = f"{commit_date.tm_year}_{map_num_to_month[commit_date.tm_mon]}_{repo_py.commit().hexsha[:7]}.json"
        output_file_path = output_file_dir + "/" + output_file_name
        print(output_file_path)
        compute_halstead_per_file(path=odin_code_dir, output_file_path=output_file_path)


def compute_halstead_per_file(path: str, output_file_path: str):
    data = {}
    # First find out if source directory has any subdirectories with c or cpp source code
    dir_to_search = [Path(path).glob('*.c*')]
    for object_in_dir in Path(path).iterdir():
        if object_in_dir.is_dir():
            dir_to_search.append(object_in_dir.glob("*.c*"))
    # iterate over all the directories with source code
    for directory in dir_to_search:
        for file in directory:
            print(file.name)
            hal = Halstead(file.read_text(encoding="utf8"))
            data[file.name] = {"h_volume": hal.h_volume(),
                               "h_length": hal.h_length(),
                               "h_voc": hal.h_vocabulary(),
                               "distinct_operators": hal.distinct_operators(),
                               "distinct_operands": hal.distinct_operands()
                               }
            if hal.h_volume() == -1:
                print(file.name)
                print(hal.__distinct_operands__)

    with open(output_file_path, "w") as outfile:
        json.dump(data, outfile)


class Halstead:
    """
    Class computes Halstead metrics for a complete file.
    To do that we aggregate the Halstead metrics for each method found
    within a file.
    """

    def __init__(self, code: str):
        """
        Compute Halstead metric for cpp programs
        :param code: Needs to be valid cpp code
        """
        code = c_cpp.CppLexer().get_tokens(code)
        self.__tokens__ = self.filter_whitespace(code)
        function_blocks = self.split_tokens_into_function_block(self.__tokens__)
        self.__distinct_operators__ = []
        self.__distinct_operands__ = []
        for i in function_blocks:
            self.__distinct_operators__.append(self.count_dist_operators(i))
            self.__distinct_operands__.append(self.count_dist_operands(i))

    def distinct_operands(self):
        result = 0
        for function_block in self.__distinct_operands__:
            result += len(function_block)
        return result

    def distinct_operators(self):
        result = 0
        for function_block in self.__distinct_operators__:
            for unique_operator_type in function_block:
                for unique_operator in function_block[unique_operator_type]:
                    if function_block[unique_operator_type][unique_operator] > 0:
                        result += 1
        return result

    def total_operators(self):
        total_operators = 0
        for operators_in_function in self.__distinct_operators__:
            for unique_operator_type in operators_in_function:
                for unique_operator in operators_in_function[unique_operator_type]:
                    total_operators += operators_in_function[unique_operator_type][unique_operator]
        return total_operators

    def total_operands(self):
        total_operants = 0
        for operands_in_function in self.__distinct_operands__:
            for unique_operant in operands_in_function:
                total_operants += operands_in_function[unique_operant]
        return total_operants

    def h_length(self):
        return self.total_operators() + self.total_operands()

    def h_vocabulary(self):
        return self.distinct_operators() + self.distinct_operands()

    def h_volume(self):
        if self.h_vocabulary() == 0:
            return -1
        return self.h_length() * math.log2(self.h_vocabulary())

    @classmethod
    def filter_whitespace(cls, tokens):
        res = []
        white = Tok.string_to_tokentype("Token.Text.Whitespace")
        for i in tokens:
            if i[0] != white:
                res.append(i)
        return res

    @classmethod
    def split_tokens_into_function_block(cls, tokens):
        """Splits cpp tokens into function blocks"""
        function = Tok.string_to_tokentype("Token.Name.Function")
        punctuation = Tok.string_to_tokentype("Token.Punctuation")
        name = Tok.string_to_tokentype("Token.Name")
        function_blocks = []
        token_consumed = []
        klammer_auf_stack = []
        klammer_zu_stack = []
        function_block = []
        state = 0
        states = {0: "searching_for_function",
                  1: "searching_for_function_begin_block",
                  2: "searching_for_function_end_block"}
        declaration_length = 0
        for i in tokens:
            if state == 0:
                if i[0] == function:
                    state = 1
                    declaration_length = 1
                elif i[0] == name: # extra case to detect cpp class method implementation
                    state = 1
                    declaration_length = 1
            elif state == 1:
                declaration_length += 1
                if i[0] == punctuation and i[1] == "{":
                    klammer_auf_stack.append("{")
                    function_block = []
                    declaration_length = 0
                    state = 2
                    continue
            elif state == 2:
                if i[0] == punctuation:
                    if i[1] == "}":
                        klammer_zu_stack.append("}")
                    if i[1] == "{":
                        klammer_auf_stack.append("{")
                    # function block ends if the number of '{' is equal to the number of '}'
                    if len(klammer_auf_stack) == len(klammer_zu_stack):
                        state = 0
                        continue
                if function_blocks:
                    function_block = function_blocks.pop()
                function_block.append(i)
                function_blocks.append(function_block)
            token_consumed.append(i)
        return function_blocks

    @classmethod
    def count_dist_operands(cls, token_function_block: list):
        def initialize_or_increment(dictionary: dict, key1):
            if key1 in dictionary:
                dictionary[key1] += 1
            else:
                dictionary[key1] = 1
        name_token = Tok.string_to_tokentype("Token.Name")
        num_token = Tok.string_to_tokentype("Token.Literal.Number")
        keyword = Tok.string_to_tokentype("Token.Keyword")
        operands = {}
        for i, token in enumerate(token_function_block):
            token_type, token_string = token
            if token_type == name_token:
                if len(token_function_block) > i + 1:
                    next_token = token_function_block[i + 1]
                    # function calls like '<name>(' are not operands
                    if next_token[1] != '(':
                        initialize_or_increment(operands, token_string)
            if Tok.is_token_subtype(token_type, num_token):
                initialize_or_increment(operands, token_string)
            if token_type == keyword and token_string == 'this':
                initialize_or_increment(operands, token_string)
        return operands

    @classmethod
    def count_dist_operators(cls, token_function_block: list):
        def initialize_or_increment(dictionary: dict, key1, key2):
            if key2 in dictionary[key1]:
                dictionary[key1][key2] += 1
            else:
                dictionary[key1][key2] = 1
        types = Tok.string_to_tokentype("Token.Keyword.Type")
        operators = Tok.string_to_tokentype("Token.Operator")
        punctuation = Tok.string_to_tokentype("Token.Punctuation")
        name_token = Tok.string_to_tokentype("Token.Name")
        keywords = Tok.string_to_tokentype("Token.Keyword")
        destinct = {types: {}, operators: {}, "function_calls": {}, punctuation: {}, keywords: {}}
        token_stack = []
        type_stack = []
        for token_type, token_string in token_function_block:
            if token_type == types:
                initialize_or_increment(destinct, types, token_string)
            elif token_type == operators:
                if token_string == '=':
                    compound_statement = ['=','!','<','>', '+', '-','*','/','%','&','|','^'] # checks for '>=', '==', '!=' etc.
                    if token_stack[-1] in compound_statement:
                        token_string = token_stack[-1] + '='
                        if token_stack[-1] in destinct[operators]:
                            destinct[operators][token_stack[-1]] -= 1 # decretement if operants on its own already has been counted
                if token_string == '>':
                    # case for '->'
                    if token_stack[-1] == '-':
                        token_string = "->"
                        destinct[operators]['-'] -= 1
                    # case for '>>'
                    if token_stack[-1] == '>':
                        token_string = '>>'
                        destinct[operators]['>'] -= 1
                if token_string == '<':
                    if token_stack[-1] == '<':
                        token_string = '<<'
                        destinct[operators]['<'] -= 1
                if token_string == '&':
                    if token_stack[-1] == '&':
                        token_string = '&&'
                        destinct[operators]['&'] -= 1
                if token_string == '|':
                    if token_stack[-1] == '|':
                        token_string = '||'
                        destinct[operators]['|'] -= 1
                if token_string == '+':
                    if token_stack[-1] == '+':
                        # ++op and op++ are the same
                        token_string = '++'
                        destinct[operators]['+'] -= 1
                if token_string == ':':
                    if token_stack[-1] == ':':
                        token_string = '::'
                        destinct[operators][':'] -= 1
                if token_string == '*':
                    if token_stack[-1] == '*':
                        token_string = '**'
                        destinct[operators]['*'] -= 1
                initialize_or_increment(destinct, operators, token_string)
            elif token_type == punctuation:
                if token_string == '.':
                    if type_stack[-1] == name_token:
                        initialize_or_increment(destinct, punctuation, token_string)
                if token_string == '[' or token_string == ']':
                    initialize_or_increment(destinct, punctuation, token_string)
                if token_string == '(':
                    # Count function calls
                    if type_stack[-1] == name_token:
                        initialize_or_increment(destinct, 'function_calls', token_stack[-1])
                    initialize_or_increment(destinct, punctuation, token_string)
                if token_string == ')':
                    initialize_or_increment(destinct, punctuation, token_string)
                if token_string == ',':
                    initialize_or_increment(destinct, punctuation, token_string)
                if token_string == ';':
                    initialize_or_increment(destinct, punctuation, token_string)
                if token_string == '{' or token_string == '}':
                    initialize_or_increment(destinct, punctuation, token_string)
            elif token_type == keywords and token_string != 'this':
                initialize_or_increment(destinct, keywords, token_string)
            token_stack.append(token_string)
            type_stack.append(token_type)
        return destinct


if __name__ == "__main__":
    main()
