from treelib import Node, Tree
from Utils import Lexem, Constants


class TreePresenter(object):
    def __init__(self, param):
        self.param = param

class Token(object):
    lexem_class = ""
    lexem = ""
    line_number = 0
    position_number = 0

    def __init__(self, lexem_class, lexem, line_number, position_number):
        self.lexem_class = lexem_class
        self.lexem = lexem
        self.line_number = line_number
        self.position_number = position_number


class SyntaxAnalyzer(object):

    __tokens = []
    __node_identifier = 0

    def __init__(self, tokens):
        self.__tokens = tokens

    def parse_tokens(self):
        tree, _ = self.__handle_common_block(self.__tokens[:], False, False, False)
        tree.show()

    def __handle_common_block(self, tokens_list, expect_end_token, expect_elseif_token, expect_else_token):
        common_tree = Tree()
        common_tree.create_node(tag=Constants.common_block)


        receive_end_token = False
        receive_else_token = False
        receive_elseif_token = False

        while len(tokens_list) != 0:
            start_tokens_length = len(tokens_list)

            tree, new_tokens = self.__handle_arithmetic_expression(tokens_list[:])
            if tree is not None:
                common_tree.paste(common_tree.root, tree)
                tokens_list = new_tokens
                continue

            tree, new_tokens = self.__handle_comparasion_expression(tokens_list[:])
            if tree is not None:
                common_tree.paste(common_tree.root, tree)
                tokens_list = new_tokens
                continue

            tree, new_tokens = self.__handle_logical_expression(tokens_list[:])
            if tree is not None:
                common_tree.paste(common_tree.root, tree)
                tokens_list = new_tokens
                continue

            tree, new_tokens = self.__handle_identifier(tokens_list[:])
            if tree is not None:
                common_tree.paste(common_tree.root, tree)
                tokens_list = new_tokens
                continue

            tree, new_tokens = self.__handle_while_block(tokens_list[:])
            if tree is not None:
                common_tree.paste(common_tree.root, tree)
                tokens_list = new_tokens
                continue

            tree, new_tokens = self.__handle_for_block(tokens_list[:])
            if tree is not None:
                common_tree.paste(common_tree.root, tree)
                tokens_list = new_tokens
                continue

            tree, new_tokens = self.__handle_if_else_block(tokens_list[:])
            if tree is not None:
                common_tree.paste(common_tree.root, tree)
                tokens_list = new_tokens
                continue


            tree, new_tokens =  self.__handle_end_token(tokens_list[:])
            if tree is not None:
                if expect_end_token:
                    receive_end_token = True
                    tokens_list = new_tokens
                    break
                else:
                    return None, tokens_list

            tree, new_tokens = self.__handle_else_token(tokens_list[:])
            if tree is not None:
                if expect_else_token:
                    receive_else_token = True
                    tokens_list = new_tokens
                    break
                else:
                    return None, tokens_list

            tree, new_tokens = self.__handle_elseif_token(tokens_list[:])
            if tree is not None:
                if expect_elseif_token:
                    receive_elseif_token = True
                    tokens_list = new_tokens
                    break
                else:
                    return None, tokens_list

            if start_tokens_length == len(tokens_list):
                raise "NO GRAMMAR PRODUCTION"


        if not (expect_end_token or receive_end_token) and \
            not (expect_else_token or receive_else_token) and \
            not (expect_elseif_token or receive_elseif_token) and \
            len(tokens_list) == 0:
                return common_tree, tokens_list

        if expect_end_token and receive_end_token and not receive_else_token and not receive_elseif_token:
            return common_tree, tokens_list

        if expect_else_token and receive_else_token and not receive_end_token and not receive_elseif_token:
            return common_tree, tokens_list

        if expect_elseif_token and receive_elseif_token and not receive_end_token and not receive_else_token:
            return common_tree, tokens_list

        raise "DID RECEIVE SYNTAX ERROR"

    def __handle_arithmetic_expression(self, tokens_list):
        if len(tokens_list) > 0:
            first_token = tokens_list[0]

            current_tokens = self.__get_tokens_for_line(tokens_list[:], first_token.line_number)

            if first_token.lexem_class == Lexem.identifier or \
                first_token.lexem_class == Lexem.number:
                tree, new_tokens = self.__handle_arithmetic_expression_helper(current_tokens[:], False)
                if tree is not None and len(new_tokens):

                    return tree, new_tokens

            if first_token.lexem_class == Lexem.l_par:
                tree, new_tokens = self.__handle_arithmetic_expression_helper(current_tokens[1:], True)
                if tree is not None and len(new_tokens) == 0:

                    arithmetic_tree = Tree()
                    arithmetic_tree.create_node(tag=Constants.arithmetic_expression)
                    arithmetic_tree.create_node(tag="(", parent=arithmetic_tree.root)
                    arithmetic_tree.paste(arithmetic_tree.root, tree)
                    arithmetic_tree.create_node(tag=")", parent=arithmetic_tree.root)

                    return arithmetic_tree, tokens_list[len(current_tokens):]

        return None, tokens_list



    def __handle_arithmetic_expression_helper(self, tokens_list, expecting_close_par):
        if len(tokens_list) > 0:

            first_token = tokens_list[0]

            if first_token.lexem_class == Lexem.l_par:
                expr_tree, new_tokens = self.__handle_arithmetic_expression_helper(tokens_list[1:], True)
                if expr_tree is not None:
                    if len(new_tokens) == 0:
                        raise "Expected close PAR"

                    tree = Tree()
                    tree.create_node(tag=Constants.arithmetic_expression)
                    tree.create_node(tag="(", parent=tree.root)
                    tree.paste(tree.root, expr_tree)
                    tree.create_node(tag=")", parent=tree.root)
                    return tree, new_tokens[1:]

            if first_token.lexem_class == Lexem.identifier or \
                first_token.lexem_class == Lexem.number:

                tree = Tree()
                tree.create_node(tag=Constants.arithmetic_expression)

                lexem_class_node = tree.create_node(tag=first_token.lexem_class, parent=tree.root)

                tree.create_node(tag=first_token.lexem, parent=lexem_class_node.identifier)

                if len(tokens_list) == 1 and not expecting_close_par:
                    return tree, tokens_list[1:]

                if len(tokens_list) > 1:

                    if tokens_list[1].lexem_class == Lexem.r_par:
                        if expecting_close_par:
                            return tree, tokens_list[2:]
                        else:
                            raise "Unexpected close brace"

                    arithmetic_token = tokens_list[1]

                    if arithmetic_token.lexem_class == Lexem.arithmetic_operation:
                        arithmetic_class_node = tree.create_node(tag=Lexem.arithmetic_operation,
                                                                parent=tree.root)

                        tree.create_node(tag=arithmetic_token.lexem, parent=arithmetic_class_node.identifier)

                        subtree, new_tokens = self.__handle_arithmetic_expression_helper(tokens_list[2:], expecting_close_par)

                        if subtree is not None:
                            tree.paste(tree.root, subtree)
                            return tree, new_tokens

        return None, tokens_list



    def __handle_comparasion_expression(self, tokens_list):
        if len(tokens_list) >= 3:

            current_line_number = tokens_list[0].line_number

            current_tokens = self.__get_tokens_for_line(tokens_list, current_line_number)

            logical_tokens = list(filter(lambda token: token.lexem_class == Lexem.comparison_operation, current_tokens))

            if len(logical_tokens) == 1 and len(current_tokens) >= 3:

                tree = Tree()
                tree.create_node(tag=Lexem.comparison_expression)


                logical_index = current_tokens.index(logical_tokens[0])

                expr1 = current_tokens[:logical_index]
                expr2 = current_tokens[logical_index + 1:]

                tree1, _ = self.__handle_arithmetic_expression(expr1)
                tree2, _ = self.__handle_arithmetic_expression(expr2)

                if tree1 is None or tree2 is None:
                    return None, tokens_list

                tree.paste(tree.root, tree1)

                op_node = tree.create_node(tag=Lexem.comparison_operation, parent=tree.root)

                tree.create_node(tag=logical_tokens[0].lexem, parent=op_node.identifier)


                tree.paste(tree.root, tree2)

                return tree, tokens_list[len(current_tokens):]

        return None, tokens_list

    def __handle_identifier(self, tokens_list):
        if len(tokens_list) > 0:
            first_token = tokens_list[0]
            if first_token.lexem_class == Lexem.identifier:

                tree = Tree()
                tree.create_node(tag=Lexem.identifier_expression)


                id_node = tree.create_node(tag=Lexem.identifier, parent=tree.root)


                tree.create_node(tag=first_token.lexem, parent=id_node.identifier)


                current_tokens = self.__get_tokens_for_line(tokens_list, first_token.line_number)

                if len(current_tokens) == 1:
                    return tree, tokens_list[1:]

                if len(current_tokens) >= 3:

                    second_token = current_tokens[1]
                    if second_token.lexem_class == Lexem.assign:

                        sub_tokens = current_tokens[2:]

                        expr_tree, _ = self.__handle_arithmetic_expression(sub_tokens)
                        if expr_tree is not None:
                            tree.create_node(tag="=", parent=tree.root)

                            tree.paste(tree.root, expr_tree)

                            return tree, tokens_list[len(current_tokens):]

                        expr_tree, _ = self.__handle_comparasion_expression(sub_tokens)
                        if expr_tree is not None:
                            tree.create_node(tag="=", parent=tree.root)

                            tree.paste(tree.root, expr_tree)

                            return tree, tokens_list[len(current_tokens):]

        return None, tokens_list

    def __handle_while_block(self, tokens_list):

        if len(tokens_list) >= 3:

            first_token = tokens_list[0]

            current_tokens = self.__get_tokens_for_line(tokens_list, first_token.line_number)

            last_token = current_tokens[-1]

            if len(current_tokens) >= 3 and \
                            first_token.lexem_class == Lexem.while_keyword and \
                            last_token.lexem_class == Lexem.do_keyword:

                comp_tokens = current_tokens[1:-1]
                comp_tree, _ = self.__handle_comparasion_expression(comp_tokens)
                if comp_tree is not None:
                    del tokens_list[:len(current_tokens)]
                    common_tree, new_tokens = self.__handle_common_block(tokens_list, True, False, False)
                    if common_tree is not None:

                        tree = Tree()
                        tree.create_node(tag=Constants.while_block)


                        tree.create_node(tag="WHILE", parent=tree.root)


                        tree.paste(tree.root, comp_tree)

                        tree.create_node(tag="DO", parent=tree.root)


                        tree.paste(tree.root, common_tree)

                        tree.create_node(tag="END", parent=tree.root)


                        return tree, new_tokens
        return None, tokens_list


    def __handle_for_block(self, tokens_list):

        if len(tokens_list) > 0:
            first_token = tokens_list[0]
            current_tokens = self.__get_tokens_for_line(tokens_list, first_token.line_number)
            if len(current_tokens) == 7:
                if first_token.lexem_class == Lexem.for_keyword and \
                    current_tokens[1].lexem_class == Lexem.identifier and \
                    current_tokens[2].lexem_class == Lexem.in_keyword:
                    iter_tokens = current_tokens[3:]
                    iter_tree, _ = self.__handle_iterator_block(iter_tokens)
                    if iter_tree is not None:
                        common_tokens = tokens_list[7:]
                        common_tree, new_tokens = self.__handle_common_block(common_tokens, True, False, False)
                        if common_tree is not None:
                            tree = Tree()
                            tree.create_node(tag=Constants.for_block)

                            tree.create_node(tag="FOR", parent=tree.root)

                            id_tree, _ = self.__handle_identifier([current_tokens[1]])

                            if id_tree is None:
                                raise "Identifier in FOR expression is missing"

                            tree.paste(tree.root, id_tree)

                            tree.create_node(tag="IN", parent=tree.root)

                            tree.paste(tree.root, iter_tree)

                            tree.paste(tree.root, common_tree)

                            tree.create_node(tag="END", parent=tree.root)

                            return tree, new_tokens
        return None, tokens_list

    def __handle_iterator_block(self, tokens_list):
        if len(tokens_list) > 0:
            first_token = tokens_list[0]
            current_tokens = self.__get_tokens_for_line(tokens_list, first_token.line_number)
            if len(current_tokens) == 4:
                if (first_token.lexem_class == Lexem.identifier or
                    first_token.lexem_class == Lexem.number) and \
                    current_tokens[1].lexem_class == Lexem.dot and \
                    current_tokens[2].lexem_class == Lexem.dot and \
                    (current_tokens[3].lexem_class == Lexem.identifier or
                    current_tokens[3].lexem_class == Lexem.number):

                    tree = Tree()
                    tree.create_node(tag=Constants.iterator_block)

                    start_node = tree.create_node(tag=Constants.iterator_start, parent=tree.root)
                    start_lexem_class_node = tree.create_node(tag=first_token.lexem_class, parent=start_node.identifier)
                    tree.create_node(tag=first_token.lexem, parent=start_lexem_class_node.identifier)

                    tree.create_node(tag=Lexem.dot, parent=tree.root)
                    tree.create_node(tag=Lexem.dot, parent=tree.root)

                    end_node = tree.create_node(tag=Constants.iterator_end, parent=tree.root)
                    end_l_c_node = tree.create_node(tag=current_tokens[3].lexem_class, parent=end_node.identifier)
                    tree.create_node(tag=current_tokens[3].lexem, parent=end_l_c_node.identifier)

                    return tree, tokens_list[4:]
        return None, tokens_list

    def __handle_if_else_block(self, tokens_list):
        if len(tokens_list) > 0:
            if_token = tokens_list[0]
            current_tokens = self.__get_tokens_for_line(tokens_list[:], if_token.line_number)

            expression_tree, _ = self.__handle_arithmetic_expression(current_tokens[1:])
            comp_tree, _ = self.__handle_comparasion_expression(current_tokens[1:])

            if if_token.lexem_class == Lexem.if_keyword and (expression_tree is not None or comp_tree is not None):
                common_tokens = tokens_list[len(current_tokens):]

                tree = Tree()
                tree.create_node(tag=Constants.if_block)
                tree.create_node(tag="IF", parent=tree.root)
                if expression_tree is not None:
                    tree.paste(tree.root, expression_tree)
                else:
                    tree.paste(tree.root, comp_tree)

                common_tree_elseif_token, new_tokens = self.__handle_common_block(tokens_list=common_tokens[:],
                                                                                  expect_else_token=False,
                                                                                  expect_end_token=False,
                                                                                  expect_elseif_token=True)
                while common_tree_elseif_token is not None:
                    if len(new_tokens) > 0:
                        sub_tokens = self.__get_tokens_for_line(new_tokens[0].line_number)

                        expr_tree, after_expr_tokens = self.__handle_arithmetic_expression(sub_tokens[:])
                        if expr_tree is not None:
                            tree.create_node(tag="ELSEIF", parent=tree.root)
                            tree.paste(tree.root, expr_tree)
                            common_tree_elseif_token, new_tokens = self.__handle_common_block(
                                tokens_list=after_expr_tokens[:],
                                expect_else_token=False,
                                expect_end_token=False,
                                expect_elseif_token=True)

                            continue

                        comp_tree, after_comp_tokens = self.__handle_comparasion_expression(sub_tokens[:])
                        if comp_tree is not None:
                            tree.create_node(tag="ELSEIF", parent=tree.root)
                            tree.paste(tree.root, comp_tree)
                            common_tree_elseif_token, new_tokens = self.__handle_common_block(
                                tokens_list=new_tokens[after_comp_tokens[:]],
                                expect_else_token=False,
                                expect_end_token=False,
                                expect_elseif_token=True)

                            continue

                common_tree_else_token, new_tokens = self.__handle_common_block(common_tokens[:], False, False, True)
                if common_tree_else_token is not None:
                    common_tokens = new_tokens
                    tree.paste(tree.root, common_tree_else_token)
                    tree.create_node(tag="ELSE", parent=tree.root)

                common_tree_end_token, new_tokens = self.__handle_common_block(common_tokens[:], True, False, False)
                if common_tree_end_token is not None:
                    tree.paste(tree.root, common_tree_end_token)
                    tree.create_node(tag="END", parent=tree.root)

                    return tree, new_tokens

        return None, tokens

    def __handle_elseif_token(self, tokens_list):
        if len(tokens_list) > 0:
            elseif_token = tokens_list[0]
            current_tokens = self.__get_tokens_for_line(tokens_list[:], elseif_token.line_number)
            if len(current_tokens) > 1 and elseif_token.lexem_class == Lexem.elseif_keyword:
                tree = Tree()
                tree.create_node(tag="ELSEIF")
                return tree, tokens_list[1:]
        return None, tokens_list


    def __handle_else_token(self, tokens_list):
        if len(tokens_list) > 0:
            first_token = tokens_list[0]
            current_tokens = self.__get_tokens_for_line(tokens_list, first_token.line_number)
            if len(current_tokens) == 1 and first_token.lexem_class == Lexem.else_keyword:
                tree = Tree()
                tree.create_node(tag="ELSE")
                return tree, tokens_list[1:]
        return None, tokens_list


    def __handle_end_token(self, tokens_list):
        if len(tokens_list) > 0:
            first_token = tokens_list[0]
            current_tokens = self.__get_tokens_for_line(tokens_list, first_token.line_number)
            if len(current_tokens) == 1 and first_token.lexem_class == Lexem.end_keyword:
                tree = Tree()
                tree.create_node(tag="END")
                return tree, tokens_list[1:]
        return None, tokens_list

    def __get_tokens_for_line(self, tokens, line):
        return list(filter(lambda token: token.line_number == line, tokens))

"""
token_1 = Token(lexem_class=Lexem.number, lexem="1", line_number=0, position_number=0)
token_2 = Token(lexem_class=Lexem.arithmetic_operation, lexem="+", line_number=0, position_number=0)
token_3 = Token(lexem_class=Lexem.number, lexem="3", line_number=0, position_number=0)
token_4 = Token(lexem_class=Lexem.number, lexem="3", line_number=1, position_number=0)
token_5 = Token(lexem_class=Lexem.arithmetic_operation, lexem="-", line_number=1, position_number=0)
token_6 = Token(lexem_class=Lexem.number, lexem="4", line_number=1, position_number=0)


token_4 = Token(lexem_class=Lexem.comparison_operation, lexem="<", line_number=0, position_number=0)

token_5 = Token(lexem_class=Lexem.number, lexem="3", line_number=0, position_number=0)
token_6 = Token(lexem_class=Lexem.arithmetic_operation, lexem="-", line_number=0, position_number=0)
token_7 = Token(lexem_class=Lexem.number, lexem="4", line_number=0, position_number=0)

tokens = [token_1, token_2, token_3, token_4, token_5, token_6]
"""
"""
token_1 = Token(lexem_class=Lexem.for_keyword, lexem="for", line_number=0, position_number=0)

token_2 = Token(lexem_class=Lexem.identifier, lexem="i", line_number=0, position_number=0)
token_3 = Token(lexem_class=Lexem.in_keyword, lexem="in", line_number=0, position_number=0)

token_4 = Token(lexem_class=Lexem.number, lexem="3", line_number=0, position_number=0)
token_5 = Token(lexem_class=Lexem.dot, lexem=".", line_number=0, position_number=0)
token_6 = Token(lexem_class=Lexem.dot, lexem=".", line_number=0, position_number=0)
token_7 = Token(lexem_class=Lexem.identifier, lexem="max", line_number=0, position_number=0)


token_8 = Token(lexem_class=Lexem.number, lexem="1", line_number=1, position_number=0)
token_9 = Token(lexem_class=Lexem.arithmetic_operation, lexem="+", line_number=1, position_number=0)
token_10 = Token(lexem_class=Lexem.number, lexem="3", line_number=1, position_number=0)

token_11 = Token(lexem_class=Lexem.number, lexem="1", line_number=2, position_number=0)
token_12 = Token(lexem_class=Lexem.arithmetic_operation, lexem="+", line_number=2, position_number=0)
token_13 = Token(lexem_class=Lexem.number, lexem="3", line_number=2, position_number=0)

token_14 = Token(lexem_class=Lexem.end_keyword, lexem="end", line_number=3, position_number=0)

tokens = [token_1, token_2, token_3,token_4,token_5, token_6, token_7, token_8, token_9, token_10, token_11, token_12, token_13, token_14]
"""
"""
token_1 = Token(lexem_class=Lexem.if_keyword, lexem="IF", line_number=0, position_number=0)

token_2 = Token(lexem_class=Lexem.number, lexem="4", line_number=0, position_number=0)
token_3 = Token(lexem_class=Lexem.comparison_operation, lexem="<", line_number=0, position_number=0)
token_4 = Token(lexem_class=Lexem.number, lexem="3", line_number=0, position_number=0)

token_5 = Token(lexem_class=Lexem.number, lexem="1", line_number=2, position_number=0)
token_6 = Token(lexem_class=Lexem.arithmetic_operation, lexem="+", line_number=2, position_number=0)
token_7 = Token(lexem_class=Lexem.number, lexem="3", line_number=2, position_number=0)

token_8 = Token(lexem_class=Lexem.else_keyword, lexem="else", line_number=3, position_number=0)


token_9 = Token(lexem_class=Lexem.identifier, lexem="i", line_number=4, position_number=0)
token_10 = Token(lexem_class=Lexem.assign, lexem="=", line_number=4, position_number=0)


token_11 = Token(lexem_class=Lexem.number, lexem="5", line_number=4, position_number=0)
token_12 = Token(lexem_class=Lexem.arithmetic_operation, lexem="*", line_number=4, position_number=0)
token_13 = Token(lexem_class=Lexem.number, lexem="2", line_number=4, position_number=0)

token_14 = Token(lexem_class=Lexem.identifier, lexem="index", line_number=5, position_number=0)

token_15 = Token(lexem_class=Lexem.end_keyword, lexem="END", line_number=6, position_number=0)


tokens = [token_1, token_2, token_3,token_4,token_5, token_6, token_7, token_8, token_9, token_10, token_11, token_12, token_13, token_14, token_15]
"""
par_1 = Token(lexem_class=Lexem.l_par, lexem="(", line_number=0, position_number=0)

token_1 = Token(lexem_class=Lexem.number, lexem="1", line_number=0, position_number=0)
token_2 = Token(lexem_class=Lexem.arithmetic_operation, lexem="+", line_number=0, position_number=0)
token_3 = Token(lexem_class=Lexem.identifier, lexem="var", line_number=0, position_number=0)
token_5 = Token(lexem_class=Lexem.r_par, lexem=")", line_number=0, position_number=0)
par_2 = Token(lexem_class=Lexem.r_par, lexem=")", line_number=0, position_number=0)


tokens = [par_1, par_1, token_1, token_2, token_3, par_2, par_2]

syntaxAnalyzer = SyntaxAnalyzer(tokens)
syntaxAnalyzer.parse_tokens()



"""

    def __handle_logical_expression(self, tokens_list):
        if len(tokens_list) > 0:
            first_token = tokens_list[0]

            current_tokens = self.__get_tokens_for_line(tokens_list[:], first_token.line_number)

            if first_token.lexem_class == Lexem.identifier or \
                first_token.lexem_class == Lexem.number:
                tree, new_tokens = self.__handle_arithmetic_expression_helper(current_tokens[:], False)
                if tree is not None and len(new_tokens):

                    return tree, new_tokens

            if first_token.lexem_class == Lexem.l_par:
                tree, new_tokens = self.__handle_arithmetic_expression_helper(current_tokens[1:], True)
                if tree is not None and len(new_tokens) == 0:

                    arithmetic_tree = Tree()
                    arithmetic_tree.create_node(tag=Constants.arithmetic_expression)
                    arithmetic_tree.create_node(tag="(", parent=arithmetic_tree.root)
                    arithmetic_tree.paste(arithmetic_tree.root, tree)
                    arithmetic_tree.create_node(tag=")", parent=arithmetic_tree.root)

                    return arithmetic_tree, tokens_list[len(current_tokens):]

        return None, tokens_list



    def __handle_logical_expression_helper(self, tokens_list, expecting_close_par):
        if len(tokens_list) > 0:

            first_token = tokens_list[0]

            if first_token.lexem_class == Lexem.l_par:
                expr_tree, new_tokens = self.__handle_arithmetic_expression_helper(tokens_list[1:], True)
                if expr_tree is not None:
                    if len(new_tokens) == 0:
                        raise "Expected close PAR"

                    tree = Tree()
                    tree.create_node(tag=Constants.arithmetic_expression)
                    tree.create_node(tag="(", parent=tree.root)
                    tree.paste(tree.root, expr_tree)
                    tree.create_node(tag=")", parent=tree.root)
                    return tree, new_tokens[1:]

            if first_token.lexem_class == Lexem.identifier or \
                first_token.lexem_class == Lexem.number:

                tree = Tree()
                tree.create_node(tag=Constants.arithmetic_expression)

                lexem_class_node = tree.create_node(tag=first_token.lexem_class, parent=tree.root)

                tree.create_node(tag=first_token.lexem, parent=lexem_class_node.identifier)

                if len(tokens_list) == 1 and not expecting_close_par:
                    return tree, tokens_list[1:]

                if len(tokens_list) > 1:

                    if tokens_list[1].lexem_class == Lexem.r_par:
                        if expecting_close_par:
                            return tree, tokens_list[2:]
                        else:
                            raise "Unexpected close brace"

                    arithmetic_token = tokens_list[1]

                    if arithmetic_token.lexem_class == Lexem.arithmetic_operation:
                        arithmetic_class_node = tree.create_node(tag=Lexem.arithmetic_operation,
                                                                parent=tree.root)

                        tree.create_node(tag=arithmetic_token.lexem, parent=arithmetic_class_node.identifier)

                        subtree, new_tokens = self.__handle_arithmetic_expression_helper(tokens_list[2:], expecting_close_par)

                        if subtree is not None:
                            tree.paste(tree.root, subtree)
                            return tree, new_tokens

        return None, tokens_list










    def __handle_logical_expression(self, tokens_list):
        if len(tokens_list) > 0:

            current_token = tokens_list[0]

            if current_token.lexem_class == Lexem.identifier or \
                            current_token.lexem_class == Lexem.bool:

                current_tokens = self.__get_tokens_for_line(tokens_list, current_token.line_number)

                tree = Tree()
                tree.create_node(tag=Lexem.logical_expression)


                lexem_class_node = tree.create_node(tag=current_token.lexem_class, parent=tree.root)


                tree.create_node(tag=current_token.lexem, parent=lexem_class_node.identifier)



                if len(current_tokens) > 1:
                    next_token = current_tokens[1]

                    if next_token.lexem_class == Lexem.logical_operation:

                        logic_class_node = tree.create_node(tag=Lexem.logical_operation,
                                                            parent=tree.root)

                        tree.create_node(tag=next_token.lexem, parent=logic_class_node.identifier)


                        subtree, new_tokens = self.__handle_logical_expression(tokens_list[2:])

                        if subtree is not None:
                            tree.paste(tree.root, subtree)
                            return tree, new_tokens

                    return None, tokens_list

                return tree, tokens_list[1:]
        return None, tokens_list

    """