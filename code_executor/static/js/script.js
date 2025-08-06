// C Language IDE JavaScript

// Initialize CodeMirror
let editor;

// First, ensure the textarea is visible and working
const textarea = document.getElementById('code-editor');
textarea.style.display = 'block';
textarea.style.width = '100%';
textarea.style.height = '400px';
textarea.style.fontFamily = 'Consolas, Monaco, Courier New, monospace';
textarea.style.fontSize = '14px';
textarea.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
textarea.style.color = '#00ff41';
textarea.style.border = '1px solid #00ff41';
textarea.style.padding = '10px';
textarea.style.resize = 'none';

// Test if textarea is working
textarea.addEventListener('input', function() {
    console.log('Textarea input detected:', this.value.length, 'characters');
});

try {
    editor = CodeMirror.fromTextArea(textarea, {
        mode: 'text/x-csrc',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        showTrailingSpace: true,
        styleActiveLine: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        foldGutter: true,
        gutters: ['CodeMirror-linenumbers'],
        extraKeys: {
            'Ctrl-Space': 'autocomplete',
            'Tab': function(cm) {
                if (cm.somethingSelected()) {
                    cm.indentSelection('add');
                } else {
                    cm.replaceSelection('    ', 'end');
                }
            }
        }
    });
    
    // Ensure editor is properly initialized
    if (!editor) {
        throw new Error('CodeMirror editor failed to initialize');
    }
    
    console.log('CodeMirror editor initialized successfully');
    
    // Test editor functionality
    editor.on('change', function() {
        console.log('CodeMirror change detected');
    });
    
} catch (error) {
    console.error('Error initializing CodeMirror:', error);
    
    // Create a simple editor interface
    editor = {
        getValue: () => textarea.value,
        setValue: (value) => { textarea.value = value; },
        on: () => {},
        refresh: () => {},
        getCursor: () => ({ line: 0, ch: 0 })
    };
    
    console.log('Using fallback textarea editor');
}

// Set initial content
try {
    editor.setValue(`#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function to check if a string is palindrome
int is_palindrome(const char* str) {
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        if (str[i] != str[len - 1 - i]) {
            return 0; // Not palindrome
        }
    }
    return 1; // Is palindrome
}

// Function to calculate factorial
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Main function
int main() {
    printf("=== C Language IDE Demo ===\\n");
    
    // Test palindrome function
    char str1[] = "racecar";
    char str2[] = "hello";
    
    printf("Is '%s' palindrome? %s\\n", str1, is_palindrome(str1) ? "Yes" : "No");
    printf("Is '%s' palindrome? %s\\n", str2, is_palindrome(str2) ? "Yes" : "No");
    
    // Test factorial function
    int n = 5;
    printf("Factorial of %d is: %d\\n", n, factorial(n));
    
    // Array operations
    int arr[] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0; i < 5; i++) {
        sum += arr[i];
    }
    printf("Sum of array elements: %d\\n", sum);
    
    return 0;
}`);
    console.log('Initial content set successfully');
} catch (error) {
    console.error('Error setting initial content:', error);
}

// Update line info
editor.on('cursorActivity', function() {
    try {
        const pos = editor.getCursor();
        document.getElementById('line-info').textContent = `Line ${pos.line + 1}, Column ${pos.ch + 1}`;
    } catch (error) {
        console.error('Error updating cursor position:', error);
    }
});

// Handle keyboard shortcuts
editor.on('keydown', function(cm, event) {
    try {
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();
            runCode();
        }
    } catch (error) {
        console.error('Error handling keyboard shortcut:', error);
    }
});

// Add a test function to verify editor is working
window.testEditor = function() {
    try {
        const content = editor.getValue();
        console.log('Editor content length:', content.length);
        alert('Editor is working! Content length: ' + content.length);
    } catch (error) {
        console.error('Editor test failed:', error);
        alert('Editor test failed: ' + error.message);
    }
};

// Add a test function to verify input section is working
window.testInputSection = function() {
    try {
        const inputSection = document.getElementById('input-section');
        console.log('Input section element:', inputSection);
        console.log('Input section display:', inputSection.style.display);
        
        // Force show the input section
        inputSection.style.display = 'block';
        console.log('Input section display after show:', inputSection.style.display);
        
        // Test if the textarea is accessible
        const inputField = document.getElementById('program-input');
        console.log('Input field element:', inputField);
        if (inputField) {
            inputField.value = 'Test input';
            console.log('Input field value set to:', inputField.value);
            alert('Input section test successful! Input field found and value set.');
        } else {
            alert('Input field not found!');
        }
    } catch (error) {
        console.error('Input section test failed:', error);
        alert('Input section test failed: ' + error.message);
    }
};

let isRunning = false;
let currentProgramInput = '';
let isWaitingForInput = false;

// Run code function
async function runCode() {
    if (isRunning) return;
    
    isRunning = true;
    const runBtn = document.getElementById('runBtn');
    const statusText = document.getElementById('status-text');
    const loadingIndicator = document.getElementById('loading-indicator');
    const outputContent = document.getElementById('output-content');
    const inputSection = document.getElementById('input-section');
    console.log('Input section element found:', inputSection);
    
    // Hide input section initially
    if (inputSection) {
        inputSection.style.display = 'none';
        console.log('Input section hidden initially');
    } else {
        console.error('Input section element not found!');
    }
    
    // Update UI
    runBtn.disabled = true;
    runBtn.textContent = '⏳ Compiling...';
    statusText.textContent = 'Compiling...';
    loadingIndicator.style.display = 'flex';
    outputContent.textContent = 'Compiling your C code...';
    outputContent.className = 'output-content';
    
    try {
        const code = editor.getValue();
        
        // Analyze code for explanation
        const analysis = analyzeCode(code);
        generateCodeExplanation(analysis);
        
        const response = await fetch('/execute_code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 
                c_code: code,
                program_input: currentProgramInput 
            })
        });
        
        const result = await response.json();
        console.log('Backend response:', result);
        console.log('Result success:', result.success);
        console.log('Result requires_input:', result.requires_input);
        
        if (result.success) {
            if (result.requires_input) {
                // Show input section for interactive programs
                console.log('Showing input section for interactive program');
                console.log('Input section element:', inputSection);
                if (inputSection) {
                    inputSection.style.display = 'block';
                    console.log('Input section display set to block');
                } else {
                    console.error('Input section element is null when trying to show it!');
                }
                outputContent.textContent = result.output;
                outputContent.className = 'output-content';
                statusText.textContent = 'Waiting for input...';
                isWaitingForInput = true;
            } else {
                outputContent.textContent = result.output;
                outputContent.className = 'output-content success';
                statusText.textContent = 'Compilation Successful';
                switchTab('code-explanation');
            }
        } else {
            outputContent.textContent = result.error;
            outputContent.className = 'output-content error';
            statusText.textContent = 'Compilation Failed';
            analyzeError(result.error);
            switchTab('error-explanation');
        }
        
    } catch (error) {
        console.error('Error running code:', error);
        outputContent.textContent = 'Error: ' + error.message;
        outputContent.className = 'output-content error';
        statusText.textContent = 'Error';
    } finally {
        isRunning = false;
        runBtn.disabled = false;
        runBtn.textContent = '▶ Compile & Run';
        loadingIndicator.style.display = 'none';
    }
}

// Send input function
async function sendInput() {
    if (!isWaitingForInput) return;
    
    const inputField = document.getElementById('program-input');
    const userInput = inputField.value;
    
    if (!userInput.trim()) {
        alert('Please enter some input for your program.');
        return;
    }
    
    try {
        const response = await fetch('/send_input/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 
                input: userInput,
                c_code: editor.getValue()  // Send the original C code
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('output-content').textContent = result.output;
            document.getElementById('input-section').style.display = 'none';
            document.getElementById('status-text').textContent = 'Program completed';
            isWaitingForInput = false;
            inputField.value = '';
        } else {
            alert('Error: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error sending input:', error);
        alert('Error sending input: ' + error.message);
    }
}

// Clear output function
function clearOutput() {
    document.getElementById('output-content').textContent = 'Output cleared.';
    document.getElementById('output-content').className = 'output-content';
}

// Toggle help panel
function toggleHelp() {
    const helpPanel = document.getElementById('helpPanel');
    helpPanel.style.display = helpPanel.style.display === 'none' ? 'block' : 'none';
}

// Switch tabs
function switchTab(tabName) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.explanation-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.explanation-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected tab and content
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    document.getElementById(tabName + '-content').classList.add('active');
}

// Analyze code for explanation
function analyzeCode(code) {
    const analysis = {
        functions: [],
        keywords: [],
        strings: [],
        comments: [],
        includes: [],
        defines: [],
        variables: [],
        structures: []
    };
    
    const lines = code.split('\n');
    
    lines.forEach((line, index) => {
        const trimmedLine = line.trim();
        
        // Check for includes
        if (trimmedLine.startsWith('#include')) {
            analysis.includes.push(trimmedLine);
        }
        
        // Check for defines
        if (trimmedLine.startsWith('#define')) {
            analysis.defines.push(trimmedLine);
        }
        
        // Check for comments
        if (trimmedLine.startsWith('//')) {
            analysis.comments.push({ line: index + 1, text: trimmedLine });
        } else if (trimmedLine.includes('/*') || trimmedLine.includes('*/')) {
            analysis.comments.push({ line: index + 1, text: trimmedLine });
        }
        
        // Check for function definitions
        const functionMatch = trimmedLine.match(/(\w+)\s+(\w+)\s*\([^)]*\)\s*\{?/);
        if (functionMatch && !trimmedLine.startsWith('//')) {
            analysis.functions.push({
                name: functionMatch[2],
                type: functionMatch[1],
                line: index + 1
            });
        }
        
        // Check for variable declarations
        const varMatch = trimmedLine.match(/(int|char|float|double|long)\s+(\w+)/);
        if (varMatch && !trimmedLine.startsWith('//')) {
            analysis.variables.push({
                name: varMatch[2],
                type: varMatch[1],
                line: index + 1
            });
        }
        
        // Check for C keywords
        const cKeywords = ['int', 'char', 'float', 'double', 'long', 'short', 'unsigned', 'signed', 'const', 'static', 'extern', 'auto', 'register', 'volatile', 'void', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue', 'goto', 'struct', 'union', 'enum', 'typedef', 'sizeof', 'printf', 'scanf', 'malloc', 'free', 'NULL', 'true', 'false'];
        
        cKeywords.forEach(keyword => {
            if (trimmedLine.includes(keyword) && !trimmedLine.startsWith('//')) {
                if (!analysis.keywords.includes(keyword)) {
                    analysis.keywords.push(keyword);
                }
            }
        });
        
        // Check for string literals
        const stringMatches = trimmedLine.match(/"([^"]*)"/g);
        if (stringMatches) {
            stringMatches.forEach(match => {
                analysis.strings.push(match);
            });
        }
    });
    
    return analysis;
}

// Generate code explanation
function generateCodeExplanation(analysis) {
    const content = document.getElementById('code-explanation-content');
    
    let html = '<div class="code-explanation">';
    html += '<h3>Code Analysis</h3>';
    
    if (analysis.includes.length > 0) {
        html += '<h4>Header Files</h4><ul>';
        analysis.includes.forEach(include => {
            html += `<li><span class="keyword">${include}</span></li>`;
        });
        html += '</ul>';
    }
    
    if (analysis.defines.length > 0) {
        html += '<h4>Preprocessor Definitions</h4><ul>';
        analysis.defines.forEach(define => {
            html += `<li><span class="keyword">${define}</span></li>`;
        });
        html += '</ul>';
    }
    
    if (analysis.functions.length > 0) {
        html += '<h4>Functions Defined</h4><ul>';
        analysis.functions.forEach(func => {
            html += `<li><span class="function">${func.type} ${func.name}()</span> (Line ${func.line})</li>`;
        });
        html += '</ul>';
    }
    
    if (analysis.variables.length > 0) {
        html += '<h4>Variables Declared</h4><ul>';
        analysis.variables.forEach(variable => {
            html += `<li><span class="keyword">${variable.type}</span> <span class="function">${variable.name}</span> (Line ${variable.line})</li>`;
        });
        html += '</ul>';
    }
    
    if (analysis.keywords.length > 0) {
        html += '<h4>C Keywords Used</h4><ul>';
        analysis.keywords.forEach(keyword => {
            html += `<li><span class="keyword">${keyword}</span></li>`;
        });
        html += '</ul>';
    }
    
    if (analysis.strings.length > 0) {
        html += '<h4>String Literals</h4><ul>';
        analysis.strings.forEach(string => {
            html += `<li><span class="string">${string}</span></li>`;
        });
        html += '</ul>';
    }
    
    if (analysis.comments.length > 0) {
        html += '<h4>Comments</h4><ul>';
        analysis.comments.forEach(comment => {
            html += `<li><span class="comment">${comment.text}</span> (Line ${comment.line})</li>`;
        });
        html += '</ul>';
    }
    
    html += '</div>';
    content.innerHTML = html;
}

// Analyze errors
function analyzeError(errorText) {
    const content = document.getElementById('error-explanation-content');
    
    let html = '<div class="error-explanation">';
    html += '<h3>Error Analysis</h3>';
    
    if (errorText.includes('undefined reference')) {
        html += '<div class="error-type"><strong>Error Type:</strong> Linker Error</div>';
        html += '<div class="suggestion"><strong>Suggestion:</strong> Missing function definition or library. Make sure all functions are defined and required libraries are included.</div>';
    } else if (errorText.includes('expected') || errorText.includes('syntax error')) {
        html += '<div class="error-type"><strong>Error Type:</strong> Syntax Error</div>';
        html += '<div class="suggestion"><strong>Suggestion:</strong> Check for missing semicolons, brackets, or incorrect syntax. Verify all statements end with semicolons.</div>';
    } else if (errorText.includes('implicit declaration')) {
        html += '<div class="error-type"><strong>Error Type:</strong> Function Declaration Error</div>';
        html += '<div class="suggestion"><strong>Suggestion:</strong> Function used before declaration. Add function prototype or move function definition before its usage.</div>';
    } else if (errorText.includes('unused variable')) {
        html += '<div class="error-type"><strong>Error Type:</strong> Warning</div>';
        html += '<div class="suggestion"><strong>Suggestion:</strong> Remove unused variables or use them in your code to avoid warnings.</div>';
    } else if (errorText.includes('gcc: command not found')) {
        html += '<div class="error-type"><strong>Error Type:</strong> System Error</div>';
        html += '<div class="suggestion"><strong>Suggestion:</strong> GCC compiler not installed. Install GCC or use an online C compiler.</div>';
    } else {
        html += '<div class="error-type"><strong>Error Type:</strong> Compilation Error</div>';
        html += '<div class="suggestion"><strong>Suggestion:</strong> Review the error message and fix the indicated issues in your code.</div>';
    }
    
    html += '<p><strong>Error Details:</strong></p>';
    html += `<pre style="color: #ff4444; background: rgba(255, 68, 68, 0.1); padding: 10px; border-radius: 4px; margin: 10px 0;">${errorText}</pre>`;
    html += '</div>';
    
    content.innerHTML = html;
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 