import re

class CAInterpreterError(Exception):
    pass

class CAInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output_buffer = []

    def _reset(self):
        self.variables = {}
        self.functions = {}
        self.output_buffer = []

    def _tokenize(self, code):
        # Very basic tokenizer: separates keywords, identifiers, numbers, operators, strings
        # This is a highly simplified tokenizer. Real tokenizers use more robust regex or tools like PLY.
        tokens = []
        # Regex for strings (simple: anything between double quotes)
        # numbers (integers only for simplicity)
        # identifiers/keywords
        # operators/separators
        token_patterns = [
            (r'"[^"]*"', 'STRING'),
            (r'\d+', 'NUMBER'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
            (r'==|!=|<=|>=|<|>|=|\+|-|\*|/|%|:|\(|\)|\[|\]|,', 'OPERATOR_OR_SEPARATOR'),
            (r'#.*', 'COMMENT'), # Comments start with #
            (r'\s+', None) # Whitespace, ignore
        ]

        # Flatten code into single line, remove comments
        lines = code.split('\n')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith('#') or not line:
                continue # Skip comments and empty lines
            processed_lines.append(line)
        code = "\n".join(processed_lines)

        position = 0
        while position < len(code):
            match = None
            for pattern, token_type in token_patterns:
                regex = re.compile(pattern)
                m = regex.match(code, position)
                if m:
                    if token_type: # Ignore whitespace
                        value = m.group(0)
                        if token_type == 'IDENTIFIER':
                            # Check for keywords
                            if value in ['func', 'return', 'if', 'else', 'loop', 'true', 'false', 'main', 'print']:
                                token_type = value.upper()
                        tokens.append({'type': token_type, 'value': value})
                    position = m.end()
                    match = True
                    break
            if not match:
                raise CAInterpreterError(f"Lexer error: Unexpected character '{code[position]}' at position {position}")
        return tokens

    def _parse(self, tokens):
        # A very simple, top-down parser for functions and main block
        ast = {'functions': {}, 'main': []}
        current_token_index = 0

        def peek():
            if current_token_index < len(tokens):
                return tokens[current_token_index]
            return None

        def consume(expected_type=None, expected_value=None):
            nonlocal current_token_index
            if current_token_index >= len(tokens):
                raise CAInterpreterError("Parser error: Unexpected end of input.")
            token = tokens[current_token_index]
            if expected_type and token['type'] != expected_type:
                raise CAInterpreterError(f"Parser error: Expected token type '{expected_type}', got '{token['type']}' ('{token['value']}')")
            if expected_value and token['value'] != expected_value:
                 raise CAInterpreterError(f"Parser error: Expected token value '{expected_value}', got '{token['value']}'")
            current_token_index += 1
            return token

        def parse_expression():
            # Simplistic: handles identifiers, numbers, strings, basic arithmetic, comparisons
            # Does not handle operator precedence or complex nested expressions
            parts = []
            while peek() and peek()['type'] not in ['OPERATOR_OR_SEPARATOR', 'COLON', 'IF', 'ELSE', 'LOOP', 'RETURN', 'END_OF_STATEMENT']:
                token = peek()
                if token['type'] in ['NUMBER', 'STRING', 'TRUE', 'FALSE', 'IDENTIFIER']:
                    parts.append(consume())
                elif token['value'] == '(': # Function call or parenthesized expression
                    consume('OPERATOR_OR_SEPARATOR', '(')
                    func_name = parts.pop()['value'] if parts else None # Assume last identifier was func name
                    args = []
                    while peek() and peek()['value'] != ')':
                        args.append(parse_expression()) # Recursive call for arguments
                        if peek() and peek()['value'] == ',':
                            consume('OPERATOR_OR_SEPARATOR', ',')
                    consume('OPERATOR_OR_SEPARATOR', ')')
                    parts.append({'type': 'CALL', 'name': func_name, 'args': args}) # Represent as a call node
                elif token['value'] == '[': # Array access or definition
                    # This is very rudimentary for array definition or access
                    consume('OPERATOR_OR_SEPARATOR', '[')
                    elements = []
                    while peek() and peek()['value'] != ']':
                        elements.append(parse_expression())
                        if peek() and peek()['value'] == ',':
                            consume('OPERATOR_OR_SEPARATOR', ',')
                    consume('OPERATOR_OR_SEPARATOR', ']')
                    parts.append({'type': 'ARRAY_LITERAL', 'elements': elements})
                else:
                    break
            
            # Simple handling of operators: assumes left-to-right, no precedence
            while peek() and peek()['value'] in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=']:
                op = consume('OPERATOR_OR_SEPARATOR')
                right_operand = peek()
                if right_operand and right_operand['type'] in ['NUMBER', 'STRING', 'TRUE', 'FALSE', 'IDENTIFIER']:
                    parts.append(op)
                    parts.append(consume())
                else:
                    break # Not a simple operand after operator
            return parts

        def parse_statement():
            statement = {}
            if peek() is None:
                return None

            token = peek()

            if token['type'] == 'IDENTIFIER':
                var_name = consume('IDENTIFIER')['value']
                if peek() and peek()['value'] == '=':
                    consume('OPERATOR_OR_SEPARATOR', '=')
                    value_parts = parse_expression()
                    statement = {'type': 'ASSIGN', 'name': var_name, 'value': value_parts}
                elif peek() and peek()['value'] == '(': # Function call as a statement
                    consume('OPERATOR_OR_SEPARATOR', '(')
                    args = []
                    while peek() and peek()['value'] != ')':
                        args.append(parse_expression())
                        if peek() and peek()['value'] == ',':
                            consume('OPERATOR_OR_SEPARATOR', ',')
                    consume('OPERATOR_OR_SEPARATOR', ')')
                    statement = {'type': 'CALL_STATEMENT', 'name': var_name, 'args': args}
                else:
                    raise CAInterpreterError(f"Parser error: Expected '=' or '(' after identifier '{var_name}'")
            elif token['type'] == 'PRINT':
                consume('PRINT')
                consume('OPERATOR_OR_SEPARATOR', '(')
                expr = parse_expression()
                consume('OPERATOR_OR_SEPARATOR', ')')
                statement = {'type': 'PRINT', 'expression': expr}
            elif token['type'] == 'RETURN':
                consume('RETURN')
                expr = parse_expression()
                statement = {'type': 'RETURN', 'expression': expr}
            elif token['type'] == 'IF':
                consume('IF')
                consume('OPERATOR_OR_SEPARATOR', '(')
                condition = parse_expression()
                consume('OPERATOR_OR_SEPARATOR', ')')
                consume('OPERATOR_OR_SEPARATOR', ':')
                body = parse_block()
                else_body = []
                if peek() and peek()['type'] == 'ELSE':
                    consume('ELSE')
                    consume('OPERATOR_OR_SEPARATOR', ':')
                    else_body = parse_block()
                statement = {'type': 'IF', 'condition': condition, 'body': body, 'else_body': else_body}
            elif token['type'] == 'LOOP':
                consume('LOOP')
                consume('OPERATOR_OR_SEPARATOR', '(')
                condition = parse_expression()
                consume('OPERATOR_OR_SEPARATOR', ')')
                consume('OPERATOR_OR_SEPARATOR', ':')
                body = parse_block()
                statement = {'type': 'LOOP', 'condition': condition, 'body': body}
            else:
                return None # No statement found

            return statement

        def parse_block():
            block_statements = []
            # In a real language, indentation or explicit end markers would define a block.
            # For simplicity, we'll assume a block continues until a new 'func', 'main', or end of file.
            # This is extremely brittle. A robust parser needs proper block delimiters.
            # For now, we'll try to collect statements until a 'func', 'main', 'else' or EOF.
            # This requires careful token advance in parse_function and parse_main to not over-consume.
            # For this simple example, we'll rely on the top-level loop for main block.
            # For if/loop bodies, we'll stop when the next token implies end of block (e.g., 'else' or another 'func').
            # This needs a better block definition in the language. Let's assume a simple structure for now.
            # We'll use implicit block ending for now, requiring careful ordering of statements.
            # A better approach would be explicit 'end' or indentation based parsing.
            return [] # This will be handled implicitly by the main parse loop for now

        def parse_function():
            consume('FUNC')
            func_name = consume('IDENTIFIER')['value']
            consume('OPERATOR_OR_SEPARATOR', '(')
            params = []
            if peek() and peek()['type'] == 'IDENTIFIER':
                params.append(consume('IDENTIFIER')['value'])
                while peek() and peek()['value'] == ',':
                    consume('OPERATOR_OR_SEPARATOR', ',')
                    params.append(consume('IDENTIFIER')['value'])
            consume('OPERATOR_OR_SEPARATOR', ')')
            consume('OPERATOR_OR_SEPARATOR', ':')

            body_statements = []
            while peek() and peek()['type'] not in ['FUNC', 'MAIN']:
                stmt = parse_statement()
                if stmt:
                    body_statements.append(stmt)
                else: # Skip empty statements or unknown tokens until next major block
                    current_token_index += 1
            return {'name': func_name, 'params': params, 'body': body_statements}

        # Main parsing loop
        while current_token_index < len(tokens):
            token = tokens[current_token_index]
            if token['type'] == 'FUNC':
                func_node = parse_function()
                ast['functions'][func_node['name']] = func_node
            elif token['type'] == 'MAIN':
                consume('MAIN')
                consume('OPERATOR_OR_SEPARATOR', ':')
                while current_token_index < len(tokens):
                    stmt = parse_statement()
                    if stmt:
                        ast['main'].append(stmt)
                    else: # If it's not a recognized statement, just advance for now (error or end of input)
                        current_token_index += 1 # Consume to prevent infinite loop on unknown tokens
            else:
                raise CAInterpreterError(f"Parser error: Unexpected token at top level '{token['value']}'")
        return ast

    def _evaluate_expression(self, expression_parts, scope):
        # This is extremely simplified and does not handle operator precedence
        # or complex nesting. It evaluates left-to-right.
        if not expression_parts:
            return None

        # Handle single token expressions (literals, variables, true/false)
        if len(expression_parts) == 1:
            token = expression_parts[0]
            if token['type'] == 'NUMBER':
                return int(token['value'])
            elif token['type'] == 'STRING':
                return token['value'].strip('"')
            elif token['type'] == 'TRUE':
                return True
            elif token['type'] == 'FALSE':
                return False
            elif token['type'] == 'IDENTIFIER':
                val = scope.get(token['value'], self.variables.get(token['value']))
                if val is None:
                    raise CAInterpreterError(f"Runtime error: Undefined variable '{token['value']}'")
                return val
            elif token['type'] == 'CALL':
                return self._execute_call(token, scope)
            elif token['type'] == 'ARRAY_LITERAL':
                return [self._evaluate_expression([elem], scope) for elem in token['elements']]
            else:
                raise CAInterpreterError(f"Runtime error: Cannot evaluate expression part of type {token['type']}")

        # Handle simple binary operations (left-to-right)
        # This is a very primitive way to do this. A real parser would build an expression tree.
        result = self._evaluate_expression([expression_parts[0]], scope)
        i = 1
        while i < len(expression_parts):
            op_token = expression_parts[i]
            if op_token['type'] != 'OPERATOR_OR_SEPARATOR':
                raise CAInterpreterError(f"Runtime error: Expected operator, got {op_token['type']}")
            
            operand2 = self._evaluate_expression([expression_parts[i+1]], scope)
            op = op_token['value']

            if op == '+':
                result += operand2
            elif op == '-':
                result -= operand2
            elif op == '*':
                result *= operand2
            elif op == '/':
                if operand2 == 0:
                    raise CAInterpreterError("Runtime error: Division by zero.")
                result /= operand2
            elif op == '%':
                result %= operand2
            elif op == '==':
                result = (result == operand2)
            elif op == '!=':
                result = (result != operand2)
            elif op == '<':
                result = (result < operand2)
            elif op == '>':
                result = (result > operand2)
            elif op == '<=':
                result = (result <= operand2)
            elif op == '>=':
                result = (result >= operand2)
            else:
                raise CAInterpreterError(f"Runtime error: Unknown operator '{op}'")
            i += 2
        return result

    def _execute_call(self, call_node, scope):
        func_name = call_node['name']
        args_values = [self._evaluate_expression([arg], scope) for arg in call_node['args']]

        # Built-in functions
        if func_name == 'to_lower':
            if len(args_values) != 1 or not isinstance(args_values[0], str):
                raise CAInterpreterError("Runtime error: to_lower expects one string argument.")
            return args_values[0].lower()
        elif func_name == 'replace_char':
            if len(args_values) != 3 or not all(isinstance(arg, str) for arg in args_values):
                raise CAInterpreterError("Runtime error: replace_char expects three string arguments (text, old, new).")
            return args_values[0].replace(args_values[1], args_values[2])
        elif func_name == 'reverse':
            if len(args_values) != 1 or not isinstance(args_values[0], str):
                raise CAInterpreterError("Runtime error: reverse expects one string argument.")
            return args_values[0][::-1]
        elif func_name == 'len': # For arrays/strings
            if len(args_values) != 1:
                raise CAInterpreterError("Runtime error: len expects one argument.")
            return len(args_values[0])
        elif func_name == 'sum':
            if len(args_values) != 1 or not isinstance(args_values[0], list):
                raise CAInterpreterError("Runtime error: sum expects one array argument.")
            return sum(args_values[0])
        elif func_name == 'max':
            if len(args_values) != 1 or not isinstance(args_values[0], list):
                raise CAInterpreterError("Runtime error: max expects one array argument.")
            if not args_values[0]: raise CAInterpreterError("Runtime error: max on empty array.")
            return max(args_values[0])
        elif func_name == 'min':
            if len(args_values) != 1 or not isinstance(args_values[0], list):
                raise CAInterpreterError("Runtime error: min expects one array argument.")
            if not args_values[0]: raise CAInterpreterError("Runtime error: min on empty array.")
            return min(args_values[0])


        # User-defined functions
        if func_name in self.functions:
            func_node = self.functions[func_name]
            if len(args_values) != len(func_node['params']):
                raise CAInterpreterError(f"Runtime error: Function '{func_name}' expects {len(func_node['params'])} arguments, got {len(args_values)}.")
            
            # Create a new scope for the function call
            func_scope = dict(scope) # Inherit outer scope, then override with params
            for i, param_name in enumerate(func_node['params']):
                func_scope[param_name] = args_values[i]
            
            return_value = None
            for statement in func_node['body']:
                result = self._execute_statement(statement, func_scope)
                if statement['type'] == 'RETURN':
                    return result # Return value from the statement itself
            return return_value # If no explicit return, None

        raise CAInterpreterError(f"Runtime error: Undefined function '{func_name}'")

    def _execute_statement(self, statement, scope):
        if statement['type'] == 'ASSIGN':
            val = self._evaluate_expression(statement['value'], scope)
            scope[statement['name']] = val # Assign to current scope
        elif statement['type'] == 'PRINT':
            val = self._evaluate_expression(statement['expression'], scope)
            self.output_buffer.append(str(val))
        elif statement['type'] == 'RETURN':
            return self._evaluate_expression(statement['expression'], scope)
        elif statement['type'] == 'CALL_STATEMENT':
            self._execute_call(statement, scope) # Execute call, ignore return
        elif statement['type'] == 'IF':
            condition_result = self._evaluate_expression(statement['condition'], scope)
            if condition_result:
                for stmt in statement['body']:
                    return_val = self._execute_statement(stmt, scope)
                    if stmt['type'] == 'RETURN':
                        return return_val
            else:
                for stmt in statement['else_body']:
                    return_val = self._execute_statement(stmt, scope)
                    if stmt['type'] == 'RETURN':
                        return return_val
        elif statement['type'] == 'LOOP':
            while self._evaluate_expression(statement['condition'], scope):
                for stmt in statement['body']:
                    return_val = self._execute_statement(stmt, scope)
                    if stmt['type'] == 'RETURN': # Loop can't return from outer function directly, but if return is used, it breaks the loop
                        return return_val
        
        return None # No specific return for most statements

    def execute(self, code):
        self._reset() # Clear state for a new execution
        try:
            tokens = self._tokenize(code)
            ast = self._parse(tokens)

            # Populate top-level functions
            self.functions = ast['functions']

            # Execute main block
            global_scope = self.variables # Global variables
            for statement in ast['main']:
                self._execute_statement(statement, global_scope)
            
            return "\n".join(self.output_buffer)

        except CAInterpreterError as e:
            return f"Compiler Error: {e}"
        except Exception as e:
            import traceback
            return f"Unexpected Interpreter Error: {e}\n{traceback.format_exc()}"