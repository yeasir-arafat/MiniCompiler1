from enum import Enum, auto
from typing import List, Tuple, Optional

class TokenType(Enum):
    # Keywords
    AUTO = auto()
    BREAK = auto()
    CASE = auto()
    CHAR = auto()
    CONST = auto()
    CONTINUE = auto()
    DEFAULT = auto()
    DO = auto()
    DOUBLE = auto()
    ELSE = auto()
    ENUM = auto()
    EXTERN = auto()
    FLOAT = auto()
    FOR = auto()
    GOTO = auto()
    IF = auto()
    INT = auto()
    LONG = auto()
    REGISTER = auto()
    RETURN = auto()
    SHORT = auto()
    SIGNED = auto()
    SIZEOF = auto()
    STATIC = auto()
    STRUCT = auto()
    SWITCH = auto()
    TYPEDEF = auto()
    UNION = auto()
    UNSIGNED = auto()
    VOID = auto()
    VOLATILE = auto()
    WHILE = auto()
    
    # Identifiers and literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    CHARACTER = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    BITWISE_AND = auto()
    BITWISE_OR = auto()
    BITWISE_XOR = auto()
    BITWISE_NOT = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    INCREMENT = auto()
    DECREMENT = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    MULTIPLY_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()
    MODULO_ASSIGN = auto()
    AND_ASSIGN = auto()
    OR_ASSIGN = auto()
    XOR_ASSIGN = auto()
    LEFT_SHIFT_ASSIGN = auto()
    RIGHT_SHIFT_ASSIGN = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    ARROW = auto()
    
    # Preprocessor
    HASH = auto()
    INCLUDE = auto()
    DEFINE = auto()
    IFDEF = auto()
    IFNDEF = auto()
    ENDIF = auto()
    ELIF = auto()
    ELSE_PP = auto()
    
    # Special
    NEWLINE = auto()
    COMMENT = auto()
    COMMENT_BLOCK = auto()
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {
            'auto': TokenType.AUTO,
            'break': TokenType.BREAK,
            'case': TokenType.CASE,
            'char': TokenType.CHAR,
            'const': TokenType.CONST,
            'continue': TokenType.CONTINUE,
            'default': TokenType.DEFAULT,
            'do': TokenType.DO,
            'double': TokenType.DOUBLE,
            'else': TokenType.ELSE,
            'enum': TokenType.ENUM,
            'extern': TokenType.EXTERN,
            'float': TokenType.FLOAT,
            'for': TokenType.FOR,
            'goto': TokenType.GOTO,
            'if': TokenType.IF,
            'int': TokenType.INT,
            'long': TokenType.LONG,
            'register': TokenType.REGISTER,
            'return': TokenType.RETURN,
            'short': TokenType.SHORT,
            'signed': TokenType.SIGNED,
            'sizeof': TokenType.SIZEOF,
            'static': TokenType.STATIC,
            'struct': TokenType.STRUCT,
            'switch': TokenType.SWITCH,
            'typedef': TokenType.TYPEDEF,
            'union': TokenType.UNION,
            'unsigned': TokenType.UNSIGNED,
            'void': TokenType.VOID,
            'volatile': TokenType.VOLATILE,
            'while': TokenType.WHILE,
        }
        
        self.operators = {
            '++': TokenType.INCREMENT,
            '--': TokenType.DECREMENT,
            '->': TokenType.ARROW,
            '<<=': TokenType.LEFT_SHIFT_ASSIGN,
            '>>=': TokenType.RIGHT_SHIFT_ASSIGN,
            '<<': TokenType.LEFT_SHIFT,
            '>>': TokenType.RIGHT_SHIFT,
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '+=': TokenType.PLUS_ASSIGN,
            '-=': TokenType.MINUS_ASSIGN,
            '*=': TokenType.MULTIPLY_ASSIGN,
            '/=': TokenType.DIVIDE_ASSIGN,
            '%=': TokenType.MODULO_ASSIGN,
            '&=': TokenType.AND_ASSIGN,
            '|=': TokenType.OR_ASSIGN,
            '^=': TokenType.XOR_ASSIGN,
            '&&': TokenType.AND,
            '||': TokenType.OR,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '=': TokenType.ASSIGN,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '!': TokenType.NOT,
            '&': TokenType.BITWISE_AND,
            '|': TokenType.BITWISE_OR,
            '^': TokenType.BITWISE_XOR,
            '~': TokenType.BITWISE_NOT,
        }
        
        self.delimiters = {
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            '.': TokenType.DOT,
            '#': TokenType.HASH,
        }
        
        self.preprocessor = {
            'include': TokenType.INCLUDE,
            'define': TokenType.DEFINE,
            'ifdef': TokenType.IFDEF,
            'ifndef': TokenType.IFNDEF,
            'endif': TokenType.ENDIF,
            'elif': TokenType.ELIF,
            'else': TokenType.ELSE_PP,
        }
    
    def tokenize(self, source: str) -> List[Token]:
        tokens = []
        current = 0
        line = 1
        column = 1
        
        while current < len(source):
            char = source[current]
            
            # Skip whitespace
            if char.isspace():
                if char == '\n':
                    tokens.append(Token(TokenType.NEWLINE, '\n', line, column))
                    line += 1
                    column = 1
                else:
                    column += 1
                current += 1
                continue
            
            # Handle comments
            if char == '/' and current + 1 < len(source):
                next_char = source[current + 1]
                if next_char == '/':
                    # Single line comment
                    comment_start = current
                    while current < len(source) and source[current] != '\n':
                        current += 1
                    comment = source[comment_start:current]
                    tokens.append(Token(TokenType.COMMENT, comment, line, column))
                    column += len(comment)
                    continue
                elif next_char == '*':
                    # Multi-line comment
                    comment_start = current
                    current += 2  # Skip /*
                    column += 2
                    while current < len(source) - 1:
                        if source[current] == '*' and source[current + 1] == '/':
                            current += 2
                            break
                        if source[current] == '\n':
                            line += 1
                            column = 1
                        else:
                            column += 1
                        current += 1
                    comment = source[comment_start:current]
                    tokens.append(Token(TokenType.COMMENT_BLOCK, comment, line, column))
                    continue
            
            # Handle strings
            if char == '"':
                current += 1
                column += 1
                string_start = current
                while current < len(source) and source[current] != '"':
                    if source[current] == '\n':
                        raise Exception(f"Unterminated string at line {line}, column {column}")
                    current += 1
                
                if current >= len(source):
                    raise Exception(f"Unterminated string at line {line}, column {column}")
                
                string_value = source[string_start:current]
                tokens.append(Token(TokenType.STRING, string_value, line, column))
                current += 1
                column += len(string_value) + 2
                continue
            
            # Handle character literals
            if char == "'":
                current += 1
                column += 1
                char_start = current
                while current < len(source) and source[current] != "'":
                    if source[current] == '\n':
                        raise Exception(f"Unterminated character literal at line {line}, column {column}")
                    current += 1
                
                if current >= len(source):
                    raise Exception(f"Unterminated character literal at line {line}, column {column}")
                
                char_value = source[char_start:current]
                tokens.append(Token(TokenType.CHARACTER, char_value, line, column))
                current += 1
                column += len(char_value) + 2
                continue
            
            # Handle numbers
            if char.isdigit():
                number_start = current
                while current < len(source) and (source[current].isdigit() or source[current] == '.' or 
                                               source[current].lower() in 'abcdef'):
                    current += 1
                number = source[number_start:current]
                tokens.append(Token(TokenType.NUMBER, number, line, column))
                column += len(number)
                continue
            
            # Handle identifiers and keywords
            if char.isalpha() or char == '_':
                identifier_start = current
                while current < len(source) and (source[current].isalnum() or source[current] == '_'):
                    current += 1
                identifier = source[identifier_start:current]
                
                # Check if it's a keyword
                if identifier.lower() in self.keywords:
                    token_type = self.keywords[identifier.lower()]
                    tokens.append(Token(token_type, identifier, line, column))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier, line, column))
                
                column += len(identifier)
                continue
            
            # Handle preprocessor directives
            if char == '#':
                current += 1
                column += 1
                # Skip whitespace after #
                while current < len(source) and source[current].isspace():
                    if source[current] == '\n':
                        line += 1
                        column = 1
                    else:
                        column += 1
                    current += 1
                
                # Read preprocessor directive
                directive_start = current
                while current < len(source) and (source[current].isalnum() or source[current] == '_'):
                    current += 1
                directive = source[directive_start:current].lower()
                
                if directive in self.preprocessor:
                    token_type = self.preprocessor[directive]
                    tokens.append(Token(token_type, directive, line, column))
                else:
                    tokens.append(Token(TokenType.HASH, '#', line, column))
                    current = directive_start  # Reset to read as identifier
                
                column += len(directive)
                continue
            
            # Handle operators and delimiters
            # Try three-character operators first
            if current + 2 < len(source):
                three_char = source[current:current + 3]
                if three_char in self.operators:
                    tokens.append(Token(self.operators[three_char], three_char, line, column))
                    current += 3
                    column += 3
                    continue
            
            # Try two-character operators
            if current + 1 < len(source):
                two_char = source[current:current + 2]
                if two_char in self.operators:
                    tokens.append(Token(self.operators[two_char], two_char, line, column))
                    current += 2
                    column += 2
                    continue
            
            # Try single-character operators and delimiters
            if char in self.operators:
                tokens.append(Token(self.operators[char], char, line, column))
                current += 1
                column += 1
                continue
            
            if char in self.delimiters:
                tokens.append(Token(self.delimiters[char], char, line, column))
                current += 1
                column += 1
                continue
            
            # Unknown character
            raise Exception(f"Unknown character '{char}' at line {line}, column {column}")
        
        tokens.append(Token(TokenType.EOF, '', line, column))
        return tokens 