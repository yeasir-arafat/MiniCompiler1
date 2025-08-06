import subprocess
import tempfile
import os
import re
from typing import Dict, List, Tuple, Optional
from .lexical_analyzer import LexicalAnalyzer
from .parser import Parser, ASTNode

class CCompiler:
    def __init__(self):
        self.lexer = LexicalAnalyzer()
        self.parser = None
        self.output = []
        self.errors = []
        self.warnings = []
        
    def compile_and_run(self, source_code: str, program_input: str = '') -> Dict:
        """Compile and run C code, return results"""
        result = {
            'success': False,
            'output': '',
            'errors': [],
            'warnings': [],
            'analysis': {},
            'requires_input': False
        }
        
        try:
            # First, analyze the code
            analysis = self.analyze_code(source_code)
            result['analysis'] = analysis
            
            # Check if program requires interactive input
            if self._detect_interactive_input(source_code):
                if not program_input:
                    # First run - show input prompt
                    result['output'] = "🔵 INTERACTIVE PROGRAM DETECTED\n\n"
                    result['output'] += "This program uses scanf() or other input functions.\n"
                    result['output'] += "Please provide input in the input field below.\n\n"
                    result['output'] += "Example input for your program:\n"
                    result['output'] += "- For scanf(\"%d\", &num): Enter a number like '42'\n"
                    result['output'] += "- For scanf(\"%s\", str): Enter text like 'hello'\n"
                    result['output'] += "- For multiple inputs: Enter each value on a new line\n\n"
                    result['output'] += "Enter your input and click 'Send Input' to run the program."
                    result['success'] = True
                    result['requires_input'] = True
                    return result
                else:
                    # Second run - execute with input
                    return self._run_with_input(source_code, program_input)
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as c_file:
                c_file.write(source_code)
                c_file_path = c_file.name
            
            exe_path = c_file_path.replace('.c', '.exe')
            
            # Compile the code
            compile_result = self.compile_code(c_file_path, exe_path)
            
            if compile_result['success']:
                # Run the compiled program
                run_result = self.run_program(exe_path)
                result['output'] = run_result['output']
                result['success'] = True
            else:
                result['errors'] = compile_result['errors']
                result['warnings'] = compile_result['warnings']
            
            # Clean up temporary files
            try:
                os.unlink(c_file_path)
                if os.path.exists(exe_path):
                    os.unlink(exe_path)
            except:
                pass
                
        except Exception as e:
            result['errors'].append(f"Compiler Error: {str(e)}")
        
        return result
    
    def analyze_code(self, source_code: str) -> Dict:
        """Analyze C code for structure and potential issues"""
        analysis = {
            'functions': [],
            'variables': [],
            'includes': [],
            'defines': [],
            'structures': [],
            'comments': [],
            'lines': len(source_code.split('\n')),
            'complexity': 0
        }
        
        try:
            # Lexical analysis
            tokens = self.lexer.tokenize(source_code)
            
            # Parse the code
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            
            # Analyze the AST
            self.analyze_ast(ast, analysis)
            
        except Exception as e:
            analysis['parse_error'] = str(e)
        
        return analysis
    
    def analyze_ast(self, node: ASTNode, analysis: Dict):
        """Recursively analyze AST nodes"""
        if node.node_type == "FUNCTION_DEFINITION":
            func_name = "unknown"
            if node.children and len(node.children) > 0:
                if node.children[0].node_type == "FUNCTION_DECLARATOR":
                    func_name = node.children[0].value
            
            analysis['functions'].append({
                'name': func_name,
                'type': node.value,
                'parameters': self.extract_parameters(node),
                'has_body': True
            })
            analysis['complexity'] += 1
            
        elif node.node_type == "FUNCTION_DECLARATION":
            func_name = "unknown"
            if node.children and len(node.children) > 0:
                if node.children[0].node_type == "FUNCTION_DECLARATOR":
                    func_name = node.children[0].value
            
            analysis['functions'].append({
                'name': func_name,
                'type': node.value,
                'parameters': self.extract_parameters(node),
                'has_body': False
            })
            
        elif node.node_type == "VARIABLE_DECLARATION":
            var_name = "unknown"
            if node.children and len(node.children) > 0:
                if node.children[0].node_type == "VARIABLE_DECLARATOR":
                    var_name = node.children[0].value
            
            analysis['variables'].append({
                'name': var_name,
                'type': node.value
            })
            
        elif node.node_type == "INCLUDE":
            analysis['includes'].append(node.value)
            
        elif node.node_type == "DEFINE":
            analysis['defines'].append({
                'name': node.value,
                'value': node.children[0].value if node.children else None
            })
            
        elif node.node_type == "STRUCT_DEFINITION":
            analysis['structures'].append({
                'name': node.value,
                'members': len(node.children)
            })
            
        elif node.node_type == "COMMENT":
            analysis['comments'].append(node.value)
            
        elif node.node_type in ["IF_STATEMENT", "FOR_STATEMENT", "WHILE_STATEMENT", "DO_WHILE_STATEMENT"]:
            analysis['complexity'] += 1
        
        # Recursively analyze children
        for child in node.children:
            self.analyze_ast(child, analysis)
    
    def extract_parameters(self, node: ASTNode) -> List[Dict]:
        """Extract function parameters from AST node"""
        parameters = []
        if node.children and len(node.children) > 0:
            declarator = node.children[0]
            if declarator.node_type == "FUNCTION_DECLARATOR" and declarator.children:
                for param in declarator.children:
                    if param.node_type == "PARAMETER":
                        param_info = {
                            'type': param.value,
                            'name': param.children[0].value if param.children else None
                        }
                        parameters.append(param_info)
        return parameters
    
    def compile_code(self, c_file_path: str, exe_path: str) -> Dict:
        """Compile C code using GCC"""
        result = {
            'success': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Compile with GCC
            cmd = [
                'gcc',
                '-o', exe_path,
                c_file_path,
                '-Wall',  # Enable all warnings
                '-Wextra',  # Enable extra warnings
                '-std=c99',  # Use C99 standard
                '-lm'  # Link math library
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                result['success'] = True
            else:
                # Parse compiler errors and warnings
                output_lines = process.stderr.split('\n')
                
                for line in output_lines:
                    if line.strip():
                        if 'warning:' in line.lower():
                            result['warnings'].append(line.strip())
                        elif 'error:' in line.lower():
                            result['errors'].append(line.strip())
                        else:
                            # Treat unknown messages as errors
                            result['errors'].append(line.strip())
                            
        except subprocess.TimeoutExpired:
            result['errors'].append("Compilation timeout - code may be too complex or contain infinite loops")
        except FileNotFoundError:
            result['errors'].append("GCC compiler not found. Please install GCC to compile C code.")
        except Exception as e:
            result['errors'].append(f"Compilation error: {str(e)}")
        
        return result
    
    def run_program(self, exe_path: str) -> Dict:
        """Run the compiled C program"""
        result = {
            'output': '',
            'error': ''
        }
        
        try:
            
            process = subprocess.run(
                [exe_path],
                capture_output=True,
                text=True,
                timeout=10  # 10 second timeout
            )
            
            result['output'] = process.stdout
            if process.stderr:
                result['error'] = process.stderr
                
        except subprocess.TimeoutExpired:
            result['error'] = "Program execution timeout - possible infinite loop"
        except Exception as e:
            result['error'] = f"Runtime error: {str(e)}"
        
        return result
    
    def _detect_interactive_input(self, source_code: str) -> bool:
        """Check if the source code requires interactive input"""
        # Check for common input functions
        input_functions = [
            'scanf(', 'gets(', 'fgets(', 'getchar(', 'getc(',
            'read(', 'fread(', 'getline('
        ]
        
        source_lower = source_code.lower()
        
        for func in input_functions:
            if func in source_lower:
                return True
        
        # Check for specific patterns that indicate user input
        patterns = [
            r'scanf\s*\(',
            r'gets\s*\(',
            r'fgets\s*\(',
            r'getchar\s*\(',
            r'getc\s*\(',
            r'read\s*\(',
            r'fread\s*\(',
            r'getline\s*\('
        ]
        
        for pattern in patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                return True
        
        return False
    
    def _run_with_input(self, source_code: str, program_input: str) -> Dict:
        """Run C program with provided input"""
        result = {
            'success': False,
            'output': '',
            'errors': [],
            'warnings': [],
            'analysis': {}
        }
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as c_file:
                c_file.write(source_code)
                c_file_path = c_file.name
            
            exe_path = c_file_path.replace('.c', '.exe')
            
            # Compile the code
            compile_result = self.compile_code(c_file_path, exe_path)
            
            if compile_result['success']:
                # Run the compiled program with input
                run_result = self.run_program_with_input(exe_path, program_input)
                result['output'] = run_result['output']
                result['success'] = True
            else:
                result['errors'] = compile_result['errors']
                result['warnings'] = compile_result['warnings']
            
            # Clean up temporary files
            try:
                os.unlink(c_file_path)
                if os.path.exists(exe_path):
                    os.unlink(exe_path)
            except:
                pass
                
        except Exception as e:
            result['errors'].append(f"Compiler Error: {str(e)}")
        
        return result
    
    def run_program_with_input(self, exe_path: str, program_input: str) -> Dict:
        """Run the compiled C program with input"""
        result = {
            'output': '',
            'error': ''
        }
        
        try:
            process = subprocess.run(
                [exe_path],
                input=program_input,
                capture_output=True,
                text=True,
                timeout=10  # 10 second timeout
            )
            
            result['output'] = process.stdout
            if process.stderr:
                result['error'] = process.stderr
                
        except subprocess.TimeoutExpired:
            result['error'] = "Program execution timeout - possible infinite loop"
        except Exception as e:
            result['error'] = f"Runtime error: {str(e)}"
        
        return result
    
    def generate_code_explanation(self, analysis: Dict) -> str:
        """Generate human-readable explanation of the C code"""
        explanation = []
        
        explanation.append("## C Code Analysis")
        
        # Program structure
        explanation.append(f"\n### Program Structure")
        explanation.append(f"- **Total Lines**: {analysis['lines']}")
        explanation.append(f"- **Cyclomatic Complexity**: {analysis['complexity']}")
        
        # Functions
        if analysis['functions']:
            explanation.append(f"\n### Functions ({len(analysis['functions'])})")
            for func in analysis['functions']:
                explanation.append(f"- **{func['name']}** (returns {func['type']})")
                if func['parameters']:
                    params = ", ".join([f"{p['type']} {p['name']}" for p in func['parameters']])
                    explanation.append(f"  - Parameters: {params}")
                explanation.append(f"  - Has implementation: {'Yes' if func['has_body'] else 'No'}")
        
        # Variables
        if analysis['variables']:
            explanation.append(f"\n### Variables ({len(analysis['variables'])})")
            for var in analysis['variables']:
                explanation.append(f"- **{var['name']}** ({var['type']})")
        
        # Includes
        if analysis['includes']:
            explanation.append(f"\n### Header Files ({len(analysis['includes'])})")
            for include in analysis['includes']:
                explanation.append(f"- `{include}`")
        
        # Defines
        if analysis['defines']:
            explanation.append(f"\n### Preprocessor Definitions ({len(analysis['defines'])})")
            for define in analysis['defines']:
                if define['value']:
                    explanation.append(f"- `{define['name']}` = `{define['value']}`")
                else:
                    explanation.append(f"- `{define['name']}`")
        
        # Structures
        if analysis['structures']:
            explanation.append(f"\n### Structures ({len(analysis['structures'])})")
            for struct in analysis['structures']:
                explanation.append(f"- **{struct['name']}** ({struct['members']} members)")
        
        # Comments
        if analysis['comments']:
            explanation.append(f"\n### Comments ({len(analysis['comments'])})")
            for comment in analysis['comments'][:5]:  # Show first 5 comments
                explanation.append(f"- `{comment}`")
            if len(analysis['comments']) > 5:
                explanation.append(f"- ... and {len(analysis['comments']) - 5} more")
        
        return "\n".join(explanation)
    
    def generate_error_explanation(self, errors: List[str]) -> str:
        """Generate detailed explanation of compilation errors"""
        explanation = []
        
        explanation.append("## Compilation Error Analysis")
        
        for error in errors:
            explanation.append(f"\n### Error: `{error}`")
            
            # Common error patterns and explanations
            if "undefined reference to" in error.lower():
                explanation.append("- **Type**: Linker Error")
                explanation.append("- **Cause**: Function or variable is used but not defined")
                explanation.append("- **Solution**: Implement the missing function or include the correct header")
                
            elif "expected" in error.lower() and "before" in error.lower():
                explanation.append("- **Type**: Syntax Error")
                explanation.append("- **Cause**: Missing semicolon, bracket, or other syntax element")
                explanation.append("- **Solution**: Check the line mentioned and add missing syntax")
                
            elif "implicit declaration" in error.lower():
                explanation.append("- **Type**: Function Declaration Error")
                explanation.append("- **Cause**: Function is used without being declared")
                explanation.append("- **Solution**: Add function prototype or include appropriate header")
                
            elif "unused variable" in error.lower():
                explanation.append("- **Type**: Warning")
                explanation.append("- **Cause**: Variable is declared but never used")
                explanation.append("- **Solution**: Remove unused variable or use it in your code")
                
            elif "control reaches end" in error.lower():
                explanation.append("- **Type**: Warning")
                explanation.append("- **Cause**: Function doesn't return a value in all code paths")
                explanation.append("- **Solution**: Add return statement or ensure all paths return a value")
                
            else:
                explanation.append("- **Type**: Compilation Error")
                explanation.append("- **Cause**: Syntax or semantic error in the code")
                explanation.append("- **Solution**: Review the error message and fix the indicated issue")
        
        return "\n".join(explanation) 