from typing import Dict, List, Any, Optional
from .lexical_analyzer import LexicalAnalyzer
from .parser import Parser, ASTNode

class Environment:
    def __init__(self, parent=None):
        self.variables = {}
        self.functions = {}
        self.parent = parent
    
    def define_variable(self, name: str, value: Any):
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise Exception(f"Undefined variable: {name}")
    
    def define_function(self, name: str, params: List[str], body: ASTNode):
        self.functions[name] = {
            'params': params,
            'body': body
        }
    
    def get_function(self, name: str) -> Dict:
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise Exception(f"Undefined function: {name}")

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.output = []
        self.setup_builtins()
    
    def setup_builtins(self):
        """Setup built-in functions"""
        # Built-in print function
        self.global_env.define_function('print', ['value'], None)
        
        # Built-in len function
        self.global_env.define_function('len', ['array'], None)
        
        # Built-in sum function
        self.global_env.define_function('sum', ['array'], None)
        
        # Built-in max function
        self.global_env.define_function('max', ['array'], None)
        
        # Built-in min function
        self.global_env.define_function('min', ['array'], None)
        
        # String functions
        self.global_env.define_function('to_lower', ['string'], None)
        self.global_env.define_function('replace_char', ['string', 'old', 'new'], None)
        self.global_env.define_function('reverse', ['string'], None)
    
    def interpret(self, source: str) -> str:
        """Interpret CA language source code"""
        try:
            # Lexical analysis
            lexer = LexicalAnalyzer()
            tokens = lexer.tokenize(source)
            
            # Parsing
            parser = Parser(tokens)
            ast = parser.parse()
            
            if ast.node_type == "ERROR":
                return f"Parser Error: {ast.value}"
            
            # Execution
            self.output = []
            self.execute_program(ast)
            
            return '\n'.join(self.output)
            
        except Exception as e:
            return f"Runtime Error: {str(e)}"
    
    def execute_program(self, node: ASTNode):
        """Execute a program node"""
        for child in node.children:
            self.execute_node(child)
    
    def execute_node(self, node: ASTNode) -> Any:
        """Execute a single AST node"""
        if node.node_type == "FUNCTION":
            return self.execute_function_definition(node)
        elif node.node_type == "MAIN":
            return self.execute_main_block(node)
        elif node.node_type == "BLOCK":
            return self.execute_block(node)
        elif node.node_type == "IF":
            return self.execute_if_statement(node)
        elif node.node_type == "LOOP":
            return self.execute_loop_statement(node)
        elif node.node_type == "RETURN":
            return self.execute_return_statement(node)
        elif node.node_type == "PRINT":
            return self.execute_print_statement(node)
        elif node.node_type == "ASSIGNMENT":
            return self.execute_assignment(node)
        elif node.node_type == "FUNCTION_CALL":
            return self.execute_function_call(node)
        elif node.node_type == "BINARY_OP":
            return self.execute_binary_operation(node)
        elif node.node_type == "NUMBER":
            return node.value
        elif node.node_type == "STRING":
            return node.value
        elif node.node_type == "BOOLEAN":
            return node.value
        elif node.node_type == "IDENTIFIER":
            return self.global_env.get_variable(node.value)
        elif node.node_type == "ARRAY":
            return [self.execute_node(child) for child in node.children]
        else:
            raise Exception(f"Unknown node type: {node.node_type}")
    
    def execute_function_definition(self, node: ASTNode):
        """Execute a function definition"""
        name = node.value
        params_node = node.children[0]
        body = node.children[1]
        
        params = params_node.value
        self.global_env.define_function(name, params, body)
    
    def execute_main_block(self, node: ASTNode):
        """Execute the main block"""
        body = node.children[0]
        return self.execute_node(body)
    
    def execute_block(self, node: ASTNode):
        """Execute a block of statements"""
        result = None
        for child in node.children:
            result = self.execute_node(child)
        return result
    
    def execute_if_statement(self, node: ASTNode):
        """Execute an if statement"""
        condition = self.execute_node(node.children[0])
        then_block = node.children[1]
        else_block = node.children[2] if len(node.children) > 2 else None
        
        if self.is_truthy(condition):
            return self.execute_node(then_block)
        elif else_block:
            return self.execute_node(else_block)
        return None
    
    def execute_loop_statement(self, node: ASTNode):
        """Execute a loop statement"""
        condition = node.children[0]
        body = node.children[1]
        
        while self.is_truthy(self.execute_node(condition)):
            try:
                self.execute_node(body)
            except Exception as e:
                if "break" in str(e):
                    break
                raise e
        return None
    
    def execute_return_statement(self, node: ASTNode):
        """Execute a return statement"""
        if node.children:
            value = self.execute_node(node.children[0])
            raise ReturnException(value)
        raise ReturnException(None)
    
    def execute_print_statement(self, node: ASTNode):
        """Execute a print statement"""
        value = self.execute_node(node.children[0])
        self.output.append(str(value))
        return None
    
    def execute_assignment(self, node: ASTNode):
        """Execute an assignment"""
        name = node.value
        value = self.execute_node(node.children[0])
        self.global_env.define_variable(name, value)
        return value
    
    def execute_function_call(self, node: ASTNode):
        """Execute a function call"""
        name = node.value
        args = [self.execute_node(child) for child in node.children]
        
        # Handle built-in functions
        if name == 'print':
            self.output.append(str(args[0]))
            return None
        elif name == 'len':
            return len(args[0])
        elif name == 'sum':
            return sum(args[0])
        elif name == 'max':
            return max(args[0])
        elif name == 'min':
            return min(args[0])
        elif name == 'to_lower':
            return str(args[0]).lower()
        elif name == 'replace_char':
            return str(args[0]).replace(str(args[1]), str(args[2]))
        elif name == 'reverse':
            return str(args[0])[::-1]
        
        # Handle user-defined functions
        try:
            func_info = self.global_env.get_function(name)
            params = func_info['params']
            body = func_info['body']
            
            if len(args) != len(params):
                raise Exception(f"Function {name} expects {len(params)} arguments, got {len(args)}")
            
            # Create new environment for function execution
            func_env = Environment(self.global_env)
            for param_name, arg_value in zip(params, args):
                func_env.define_variable(param_name, arg_value)
            
            # Execute function body
            old_env = self.global_env
            self.global_env = func_env
            
            try:
                result = self.execute_node(body)
                return result
            finally:
                self.global_env = old_env
                
        except Exception as e:
            if "Undefined function" in str(e):
                raise Exception(f"Undefined function: {name}")
            raise e
    
    def execute_binary_operation(self, node: ASTNode):
        """Execute a binary operation"""
        left = self.execute_node(node.children[0])
        right = self.execute_node(node.children[1])
        operator = node.value
        
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise Exception("Division by zero")
            return left / right
        elif operator == '%':
            return left % right
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '<':
            return left < right
        elif operator == '<=':
            return left <= right
        elif operator == '>':
            return left > right
        elif operator == '>=':
            return left >= right
        elif operator == 'and':
            return self.is_truthy(left) and self.is_truthy(right)
        elif operator == 'or':
            return self.is_truthy(left) or self.is_truthy(right)
        else:
            raise Exception(f"Unknown operator: {operator}")
    
    def is_truthy(self, value: Any) -> bool:
        """Check if a value is truthy"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return len(value) > 0
        elif isinstance(value, list):
            return len(value) > 0
        else:
            return value is not None

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__("return") 