from typing import List, Optional, Any
from .lexical_analyzer import Token, TokenType

class ASTNode:
    def __init__(self, node_type: str, value: Any = None, children: List['ASTNode'] = None):
        self.node_type = node_type
        self.value = value
        self.children = children or []
    
    def __repr__(self):
        return f"ASTNode({self.node_type}, {self.value}, {len(self.children)} children)"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
    
    def parse(self) -> ASTNode:
        """Parse the tokens into an AST"""
        try:
            return self.parse_program()
        except Exception as e:
            self.errors.append(f"Parser Error: {str(e)}")
            return ASTNode("ERROR", str(e))
    
    def parse_program(self) -> ASTNode:
        """Parse the entire C program"""
        program = ASTNode("PROGRAM")
        
        while self.current < len(self.tokens) and self.tokens[self.current].type != TokenType.EOF:
            if self.tokens[self.current].type == TokenType.INCLUDE:
                program.children.append(self.parse_include())
            elif self.tokens[self.current].type == TokenType.DEFINE:
                program.children.append(self.parse_define())
            elif self.tokens[self.current].type in [TokenType.INT, TokenType.CHAR, TokenType.FLOAT, 
                                                   TokenType.DOUBLE, TokenType.VOID, TokenType.STRUCT]:
                # Could be a function declaration/definition or variable declaration
                program.children.append(self.parse_declaration())
            else:
                # Skip unknown tokens
                self.current += 1
        
        return program
    
    def parse_include(self) -> ASTNode:
        """Parse #include directive"""
        self.expect(TokenType.INCLUDE)
        
        # Handle both <header.h> and "header.h" formats
        if self.tokens[self.current].type == TokenType.STRING:
            header = self.expect(TokenType.STRING)
            return ASTNode("INCLUDE", header.value)
        elif self.tokens[self.current].type == TokenType.LESS_THAN:
            self.expect(TokenType.LESS_THAN)
            header = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.GREATER_THAN)
            return ASTNode("INCLUDE", f"<{header.value}>")
        else:
            raise Exception(f"Expected string or <header> at line {self.tokens[self.current].line}")
    
    def parse_define(self) -> ASTNode:
        """Parse #define directive"""
        self.expect(TokenType.DEFINE)
        macro = self.expect(TokenType.IDENTIFIER)
        
        value = None
        if self.current < len(self.tokens) and self.tokens[self.current].type != TokenType.NEWLINE:
            value = self.parse_expression()
        
        return ASTNode("DEFINE", macro.value, [value] if value else [])
    
    def parse_declaration(self) -> ASTNode:
        """Parse variable or function declaration"""
        # Parse type specifier
        type_spec = self.parse_type_specifier()
        
        # Parse declarator
        declarator = self.parse_declarator()
        
        if self.tokens[self.current].type == TokenType.SEMICOLON:
            # Variable declaration
            self.expect(TokenType.SEMICOLON)
            return ASTNode("VARIABLE_DECLARATION", type_spec, [declarator])
        elif self.tokens[self.current].type == TokenType.LBRACE:
            # Function definition
            body = self.parse_compound_statement()
            return ASTNode("FUNCTION_DEFINITION", type_spec, [declarator, body])
        else:
            # Function declaration
            self.expect(TokenType.SEMICOLON)
            return ASTNode("FUNCTION_DECLARATION", type_spec, [declarator])
    
    def parse_type_specifier(self) -> ASTNode:
        """Parse type specifier"""
        token = self.tokens[self.current]
        
        if token.type in [TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.DOUBLE, TokenType.VOID]:
            self.current += 1
            return ASTNode("TYPE_SPECIFIER", token.value)
        elif token.type == TokenType.STRUCT:
            return self.parse_struct_declaration()
        else:
            raise Exception(f"Expected type specifier at line {token.line}")
    
    def parse_struct_declaration(self) -> ASTNode:
        """Parse struct declaration"""
        self.expect(TokenType.STRUCT)
        
        if self.tokens[self.current].type == TokenType.IDENTIFIER:
            tag = self.expect(TokenType.IDENTIFIER)
            
            if self.tokens[self.current].type == TokenType.LBRACE:
                # Struct definition
                self.expect(TokenType.LBRACE)
                members = []
                
                while self.current < len(self.tokens) and self.tokens[self.current].type != TokenType.RBRACE:
                    if self.tokens[self.current].type in [TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.DOUBLE]:
                        members.append(self.parse_struct_member())
                    else:
                        self.current += 1
                
                self.expect(TokenType.RBRACE)
                return ASTNode("STRUCT_DEFINITION", tag.value, members)
            else:
                # Struct declaration
                return ASTNode("STRUCT_DECLARATION", tag.value)
        else:
            raise Exception(f"Expected struct tag at line {self.tokens[self.current].line}")
    
    def parse_struct_member(self) -> ASTNode:
        """Parse struct member"""
        type_spec = self.parse_type_specifier()
        declarator = self.parse_declarator()
        self.expect(TokenType.SEMICOLON)
        return ASTNode("STRUCT_MEMBER", type_spec, [declarator])
    
    def parse_declarator(self) -> ASTNode:
        """Parse declarator (variable name, function name, etc.)"""
        if self.tokens[self.current].type == TokenType.IDENTIFIER:
            name = self.expect(TokenType.IDENTIFIER)
            
            if self.tokens[self.current].type == TokenType.LPAREN:
                # Function declarator
                self.expect(TokenType.LPAREN)
                params = []
                
                if self.tokens[self.current].type != TokenType.RPAREN:
                    while True:
                        if self.tokens[self.current].type in [TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.DOUBLE, TokenType.VOID]:
                            param_type = self.parse_type_specifier()
                            param_name = None
                            if self.tokens[self.current].type == TokenType.IDENTIFIER:
                                param_name = self.expect(TokenType.IDENTIFIER)
                            params.append(ASTNode("PARAMETER", param_type, [param_name] if param_name else []))
                        else:
                            self.current += 1
                        
                        if self.tokens[self.current].type == TokenType.RPAREN:
                            break
                        self.expect(TokenType.COMMA)
                
                self.expect(TokenType.RPAREN)
                return ASTNode("FUNCTION_DECLARATOR", name.value, params)
            else:
                # Variable declarator
                return ASTNode("VARIABLE_DECLARATOR", name.value)
        else:
            raise Exception(f"Expected identifier at line {self.tokens[self.current].line}")
    
    def parse_compound_statement(self) -> ASTNode:
        """Parse compound statement (block)"""
        self.expect(TokenType.LBRACE)
        
        statements = []
        while self.current < len(self.tokens) and self.tokens[self.current].type != TokenType.RBRACE:
            if self.tokens[self.current].type == TokenType.NEWLINE:
                self.current += 1
                continue
            
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
        
        self.expect(TokenType.RBRACE)
        return ASTNode("COMPOUND_STATEMENT", statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        if self.current >= len(self.tokens):
            return None
        
        token = self.tokens[self.current]
        
        if token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.DO:
            return self.parse_do_while_statement()
        elif token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif token.type == TokenType.BREAK:
            return self.parse_break_statement()
        elif token.type == TokenType.CONTINUE:
            return self.parse_continue_statement()
        elif token.type == TokenType.LBRACE:
            return self.parse_compound_statement()
        elif token.type in [TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.DOUBLE]:
            return self.parse_variable_declaration()
        elif token.type == TokenType.IDENTIFIER:
            return self.parse_expression_statement()
        else:
            # Skip unknown tokens
            self.current += 1
            return None
    
    def parse_if_statement(self) -> ASTNode:
        """Parse if statement"""
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        then_statement = self.parse_statement()
        
        else_statement = None
        if self.current < len(self.tokens) and self.tokens[self.current].type == TokenType.ELSE:
            self.expect(TokenType.ELSE)
            else_statement = self.parse_statement()
        
        return ASTNode("IF_STATEMENT", "if", [condition, then_statement, else_statement])
    
    def parse_for_statement(self) -> ASTNode:
        """Parse for statement"""
        self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)
        
        init = None
        if self.tokens[self.current].type != TokenType.SEMICOLON:
            init = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        condition = None
        if self.tokens[self.current].type != TokenType.SEMICOLON:
            condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        update = None
        if self.tokens[self.current].type != TokenType.RPAREN:
            update = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        body = self.parse_statement()
        
        return ASTNode("FOR_STATEMENT", "for", [init, condition, update, body])
    
    def parse_while_statement(self) -> ASTNode:
        """Parse while statement"""
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        
        return ASTNode("WHILE_STATEMENT", "while", [condition, body])
    
    def parse_do_while_statement(self) -> ASTNode:
        """Parse do-while statement"""
        self.expect(TokenType.DO)
        body = self.parse_statement()
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        
        return ASTNode("DO_WHILE_STATEMENT", "do-while", [body, condition])
    
    def parse_return_statement(self) -> ASTNode:
        """Parse return statement"""
        self.expect(TokenType.RETURN)
        value = None
        if self.tokens[self.current].type != TokenType.SEMICOLON:
            value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        return ASTNode("RETURN_STATEMENT", "return", [value] if value else [])
    
    def parse_break_statement(self) -> ASTNode:
        """Parse break statement"""
        self.expect(TokenType.BREAK)
        self.expect(TokenType.SEMICOLON)
        return ASTNode("BREAK_STATEMENT", "break")
    
    def parse_continue_statement(self) -> ASTNode:
        """Parse continue statement"""
        self.expect(TokenType.CONTINUE)
        self.expect(TokenType.SEMICOLON)
        return ASTNode("CONTINUE_STATEMENT", "continue")
    
    def parse_variable_declaration(self) -> ASTNode:
        """Parse variable declaration"""
        type_spec = self.parse_type_specifier()
        declarator = self.parse_declarator()
        self.expect(TokenType.SEMICOLON)
        return ASTNode("VARIABLE_DECLARATION", type_spec, [declarator])
    
    def parse_expression_statement(self) -> ASTNode:
        """Parse expression statement"""
        expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ASTNode("EXPRESSION_STATEMENT", expr)
    
    def parse_expression(self) -> ASTNode:
        """Parse an expression"""
        return self.parse_assignment_expression()
    
    def parse_assignment_expression(self) -> ASTNode:
        """Parse assignment expression"""
        left = self.parse_logical_or_expression()
        
        if self.current < len(self.tokens) and self.tokens[self.current].type in [
            TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
            TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN, TokenType.MODULO_ASSIGN,
            TokenType.AND_ASSIGN, TokenType.OR_ASSIGN, TokenType.XOR_ASSIGN,
            TokenType.LEFT_SHIFT_ASSIGN, TokenType.RIGHT_SHIFT_ASSIGN
        ]:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_assignment_expression()
            return ASTNode("ASSIGNMENT_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_logical_or_expression(self) -> ASTNode:
        """Parse logical OR expression"""
        left = self.parse_logical_and_expression()
        
        while self.current < len(self.tokens) and self.tokens[self.current].type == TokenType.OR:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_logical_and_expression()
            left = ASTNode("LOGICAL_OR_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_logical_and_expression(self) -> ASTNode:
        """Parse logical AND expression"""
        left = self.parse_equality_expression()
        
        while self.current < len(self.tokens) and self.tokens[self.current].type == TokenType.AND:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_equality_expression()
            left = ASTNode("LOGICAL_AND_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_equality_expression(self) -> ASTNode:
        """Parse equality expression"""
        left = self.parse_relational_expression()
        
        while self.current < len(self.tokens) and self.tokens[self.current].type in [TokenType.EQUAL, TokenType.NOT_EQUAL]:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_relational_expression()
            left = ASTNode("EQUALITY_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_relational_expression(self) -> ASTNode:
        """Parse relational expression"""
        left = self.parse_shift_expression()
        
        while self.current < len(self.tokens) and self.tokens[self.current].type in [
            TokenType.LESS_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_THAN, TokenType.GREATER_EQUAL
        ]:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_shift_expression()
            left = ASTNode("RELATIONAL_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_shift_expression(self) -> ASTNode:
        """Parse shift expression"""
        left = self.parse_additive_expression()
        
        while self.current < len(self.tokens) and self.tokens[self.current].type in [TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT]:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_additive_expression()
            left = ASTNode("SHIFT_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_additive_expression(self) -> ASTNode:
        """Parse additive expression"""
        left = self.parse_multiplicative_expression()
        
        while self.current < len(self.tokens) and self.tokens[self.current].type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_multiplicative_expression()
            left = ASTNode("ADDITIVE_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_multiplicative_expression(self) -> ASTNode:
        """Parse multiplicative expression"""
        left = self.parse_unary_expression()
        
        while self.current < len(self.tokens) and self.tokens[self.current].type in [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO]:
            operator = self.tokens[self.current].value
            self.current += 1
            right = self.parse_unary_expression()
            left = ASTNode("MULTIPLICATIVE_EXPRESSION", operator, [left, right])
        
        return left
    
    def parse_unary_expression(self) -> ASTNode:
        """Parse unary expression"""
        token = self.tokens[self.current]
        
        if token.type in [TokenType.PLUS, TokenType.MINUS, TokenType.NOT, TokenType.BITWISE_NOT]:
            operator = token.value
            self.current += 1
            operand = self.parse_unary_expression()
            return ASTNode("UNARY_EXPRESSION", operator, [operand])
        elif token.type in [TokenType.INCREMENT, TokenType.DECREMENT]:
            operator = token.value
            self.current += 1
            operand = self.parse_postfix_expression()
            return ASTNode("UNARY_EXPRESSION", operator, [operand])
        else:
            return self.parse_postfix_expression()
    
    def parse_postfix_expression(self) -> ASTNode:
        """Parse postfix expression"""
        left = self.parse_primary_expression()
        
        while self.current < len(self.tokens):
            token = self.tokens[self.current]
            
            if token.type == TokenType.LBRACKET:
                # Array access
                self.expect(TokenType.LBRACKET)
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                left = ASTNode("ARRAY_ACCESS", "[]", [left, index])
            elif token.type == TokenType.LPAREN:
                # Function call
                self.expect(TokenType.LPAREN)
                args = []
                
                if self.tokens[self.current].type != TokenType.RPAREN:
                    while True:
                        args.append(self.parse_expression())
                        if self.tokens[self.current].type == TokenType.RPAREN:
                            break
                        self.expect(TokenType.COMMA)
                
                self.expect(TokenType.RPAREN)
                left = ASTNode("FUNCTION_CALL", "()", [left] + args)
            elif token.type in [TokenType.INCREMENT, TokenType.DECREMENT]:
                # Postfix increment/decrement
                operator = token.value
                self.current += 1
                left = ASTNode("POSTFIX_EXPRESSION", operator, [left])
            elif token.type == TokenType.DOT:
                # Member access
                self.expect(TokenType.DOT)
                member = self.expect(TokenType.IDENTIFIER)
                left = ASTNode("MEMBER_ACCESS", ".", [left, member])
            elif token.type == TokenType.ARROW:
                # Pointer member access
                self.expect(TokenType.ARROW)
                member = self.expect(TokenType.IDENTIFIER)
                left = ASTNode("POINTER_MEMBER_ACCESS", "->", [left, member])
            else:
                break
        
        return left
    
    def parse_primary_expression(self) -> ASTNode:
        """Parse primary expression"""
        token = self.tokens[self.current]
        
        if token.type == TokenType.NUMBER:
            self.current += 1
            return ASTNode("NUMBER", float(token.value))
        elif token.type == TokenType.STRING:
            self.current += 1
            return ASTNode("STRING", token.value)
        elif token.type == TokenType.CHARACTER:
            self.current += 1
            return ASTNode("CHARACTER", token.value)
        elif token.type == TokenType.IDENTIFIER:
            self.current += 1
            return ASTNode("IDENTIFIER", token.value)
        elif token.type == TokenType.LPAREN:
            self.expect(TokenType.LPAREN)
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        else:
            raise Exception(f"Unexpected token {token.type} at line {token.line}, column {token.column}")
    
    def expect(self, expected_type: TokenType) -> Token:
        """Expect a specific token type and advance"""
        if self.current >= len(self.tokens):
            raise Exception(f"Expected {expected_type}, but reached end of input")
        
        token = self.tokens[self.current]
        if token.type != expected_type:
            raise Exception(f"Expected {expected_type}, but got {token.type} at line {token.line}, column {token.column}")
        
        self.current += 1
        return token 