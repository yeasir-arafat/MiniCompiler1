# C Language IDE - Mini Compiler Project

A modern, web-based C Language Integrated Development Environment (IDE) built with Django and featuring a futuristic dark theme with green accents. This project provides a complete C development environment with real-time compilation, code analysis, and interactive program execution.

## 🌟 Features

### ✨ Core Functionality
- **Real-time C Code Compilation** using GCC compiler
- **Interactive Program Execution** with input support for `scanf()`, `gets()`, and other input functions
- **Syntax Highlighting** with CodeMirror editor
- **Code Analysis** with detailed explanations of functions, variables, and structure
- **Error Analysis** with categorized error explanations and suggestions

### 🎨 User Interface
- **Futuristic Dark Theme** with green accents (#00ff41)
- **Split-panel Layout** with code editor, output panel, and explanation sections
- **Responsive Design** that works on different screen sizes
- **Professional IDE-like Interface** similar to CodeBlocks or Cursor

### 🔧 Development Features
- **CodeMirror Integration** with C language support
- **Line Numbers** and active line highlighting
- **Bracket Matching** and auto-indentation
- **Keyboard Shortcuts** (Ctrl+Enter to run code)
- **Status Bar** with compilation status and cursor position

### 📊 Analysis & Explanation
- **Code Structure Analysis** - Functions, variables, includes, defines
- **Error Categorization** - Syntax, Runtime, Linker, and System errors
- **Detailed Explanations** for each code component
- **Suggestions** for fixing common compilation errors

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- GCC compiler installed on your system
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yeasir-arafat/MiniCompiler1.git
   cd MiniCompiler1
   ```

2. **Install Python dependencies**
   ```bash
   pip install django
   ```

3. **Run the development server**
   ```bash
   python manage.py runserver
   ```

4. **Open your browser**
   Navigate to `http://localhost:8000`

## 📝 Usage

### Writing and Running C Code

1. **Write your C code** in the editor
2. **Click "Compile & Run"** or press `Ctrl+Enter`
3. **View the output** in the output panel
4. **Check code analysis** in the explanation tabs

### Interactive Programs

For programs that use `scanf()` or other input functions:

1. **Write your interactive C code**
   ```c
   #include <stdio.h>
   
   int main() {
       int num;
       printf("Enter a number: ");
       scanf("%d", &num);
       printf("You entered: %d\n", num);
       return 0;
   }
   ```

2. **Click "Compile & Run"**
3. **Enter input** in the input field that appears
4. **Click "Send Input"** to execute the program

### Code Examples

The IDE includes several example programs:

- **Hello World** - Basic C program structure
- **Function Definitions** - Demonstrating function creation
- **Conditional Statements** - If-else logic examples
- **Interactive Input** - Programs using scanf()

## 🏗️ Project Structure

```
mycompiler_project/
├── code_executor/           # Main Django app
│   ├── static/             # Static files (CSS, JS)
│   │   ├── css/
│   │   │   └── style.css   # Futuristic dark theme styles
│   │   └── js/
│   │       └── script.js   # Frontend JavaScript logic
│   ├── templates/          # HTML templates
│   │   └── code_executor/
│   │       └── index.html  # Main IDE interface
│   ├── c_compiler.py       # C compilation and execution logic
│   ├── lexical_analyzer.py # Tokenization for C code
│   ├── parser.py           # AST generation and parsing
│   ├── views.py            # Django view handlers
│   └── urls.py             # URL routing
├── mycompiler_project/     # Django project settings
│   ├── settings.py         # Django configuration
│   └── urls.py            # Main URL patterns
└── manage.py              # Django management script
```

## 🔧 Technical Details

### Backend Architecture
- **Django Web Framework** for server-side logic
- **GCC Compiler Integration** for C code compilation
- **Subprocess Management** for safe program execution
- **Temporary File Handling** for compilation artifacts
- **JSON API** for frontend-backend communication

### Frontend Technologies
- **CodeMirror 5.65.2** for code editing
- **Vanilla JavaScript** for dynamic functionality
- **CSS3** with custom futuristic styling
- **HTML5** semantic structure

### Code Analysis Features
- **Lexical Analysis** - Tokenization of C source code
- **Abstract Syntax Tree (AST)** - Code structure representation
- **Function Detection** - Automatic identification of functions and parameters
- **Variable Analysis** - Type and declaration tracking
- **Error Classification** - Categorized error explanations

## 🎯 Supported C Features

### Language Constructs
- ✅ **Basic Types** - int, char, float, double, long
- ✅ **Control Structures** - if, else, for, while, do-while
- ✅ **Functions** - Definition, declaration, parameters
- ✅ **Arrays** - Declaration and usage
- ✅ **Pointers** - Basic pointer operations
- ✅ **Structs** - Structure definitions
- ✅ **Preprocessor** - #include, #define directives

### Input/Output Functions
- ✅ **printf()** - Formatted output
- ✅ **scanf()** - Formatted input (interactive)
- ✅ **gets()** - String input (interactive)
- ✅ **getchar()** - Character input (interactive)
- ✅ **fgets()** - File/string input (interactive)

### Standard Libraries
- ✅ **stdio.h** - Standard input/output
- ✅ **stdlib.h** - General utilities
- ✅ **string.h** - String manipulation
- ✅ **math.h** - Mathematical functions

## 🐛 Error Handling

The IDE provides comprehensive error analysis:

### Error Categories
- **Syntax Errors** - Missing semicolons, brackets, syntax issues
- **Runtime Errors** - Program execution failures
- **Linker Errors** - Missing function definitions
- **System Errors** - Compiler not found, timeout issues
- **Warnings** - Unused variables, potential issues

### Error Features
- **Detailed Explanations** for each error type
- **Suggestions** for fixing common issues
- **Line-by-line Analysis** of error locations
- **Categorized Error Display** in dedicated panels

## 🎨 Customization

### Theme Customization
The futuristic dark theme can be customized by modifying:
- `code_executor/static/css/style.css` - Main styling
- Color scheme variables in CSS
- CodeMirror theme integration

### Adding New Features
- **New Language Support** - Extend lexical analyzer and parser
- **Additional Analysis** - Enhance code analysis features
- **Custom Themes** - Modify CSS for different visual styles
- **Plugin System** - Extend with additional functionality

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Test thoroughly before submitting
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CodeMirror** - For the excellent code editor
- **Django** - For the robust web framework
- **GCC** - For the reliable C compiler
- **Open Source Community** - For inspiration and tools

## 📞 Support

If you encounter any issues or have questions:

1. **Check the Issues** section on GitHub
2. **Create a new issue** with detailed description
3. **Include error messages** and steps to reproduce
4. **Provide system information** (OS, Python version, etc.)

## 🔮 Future Enhancements

Planned features for future releases:

- **Multi-file Support** - Multiple source files
- **Debugging Tools** - Step-through debugging
- **Code Templates** - Pre-built code snippets
- **Project Management** - Save and load projects
- **Collaboration** - Real-time collaborative editing
- **Mobile Support** - Responsive mobile interface
- **Dark/Light Theme Toggle** - Theme switching
- **Export Features** - PDF reports, code sharing

---

**Built with ❤️ and ☕ by the development team**

*Last updated: August 2025* 