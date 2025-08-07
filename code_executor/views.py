import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .c_compiler import CCompiler

def code_editor(request):
    """
    Renders the front-end code editor.
    """
    return render(request, 'code_executor/index.html')

def code_editor(request):
    """
    Renders the front-end code editor.
    """
    return render(request, 'code_executor/index.html')

@csrf_exempt
def execute_code(request):
    """
    Receives C code from the front-end, compiles it, and returns the output.
    """
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            c_code = data.get('c_code', '')
            program_input = data.get('program_input', '')
            
            compiler = CCompiler()
            result = compiler.compile_and_run(c_code, program_input)
            
            if result['success']:
                # Compilation and execution successful
                response_data = {
                    'success': True,
                    'output': result['output'],
                    'error': '',
                    'analysis': result['analysis']
                }
                # Include requires_input field if it exists
                if 'requires_input' in result:
                    response_data['requires_input'] = result['requires_input']
                    print(f"Backend: requires_input = {result['requires_input']}")
                else:
                    print(f"Backend: requires_input not found in result")
                print(f"Backend: sending response_data = {response_data}")
                return JsonResponse(response_data)
            else:
                # Compilation failed
                return JsonResponse({
                    'success': False,
                    'output': '',
                    'error': '\n'.join(result['errors']),
                    'analysis': result['analysis']
                })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def send_input(request):
    """
    Handle program input for interactive C programs.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('input', '')
            c_code = data.get('c_code', '')  # We need the original code
            
            if not c_code:
                return JsonResponse({'error': 'No C code provided.'}, status=400)
            
            if not user_input:
                return JsonResponse({'error': 'No input provided.'}, status=400)
            
            # Use the C compiler to run the program with input
            compiler = CCompiler()
            result = compiler.compile_and_run(c_code, user_input)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'output': result['output']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '\n'.join(result['errors'])
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)