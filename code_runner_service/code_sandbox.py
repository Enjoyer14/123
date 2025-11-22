import subprocess
import tempfile
import os
import time
import logging
import psutil

logger = logging.getLogger(__name__)

def get_memory_usage(pid):
    """Получить использование памяти процессом и его потомками в KB"""
    try:
        process = psutil.Process(pid)
        memory_info = process.memory_info()
        # Получаем всех потомков
        children = process.children(recursive=True)
        
        total_memory = memory_info.rss  # RSS в байтах
        
        for child in children:
            try:
                child_memory = child.memory_info()
                total_memory += child_memory.rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return total_memory / 1024  # Конвертируем в KB
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.warning(f"Could not get memory usage for pid {pid}: {e}")
        return 0

def execute_code_in_sandbox_docker(code: str, input_data: str, time_limit_ms: int,
                                   memory_limit_mb: int, language: str = "python"):
    start_time = time.time()
    result = {
        'status': 'UNKNOWN', 
        'output': '', 
        'error': '', 
        'execution_time_ms': 0,
        'memory_used_kb': 0
    }

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_command = []
            memory_file = None
            
            if language == "python":
                # Создаем Python файл
                code_path = os.path.join(tmp_dir, "code.py")
                with open(code_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                base_command = ['python', code_path]
                
            elif language == "cpp":
                # Создаем C++ файл
                code_path = os.path.join(tmp_dir, "code.cpp")
                with open(code_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                executable_path = os.path.join(tmp_dir, 'a.out')
                
                # Компилируем
                compile_process = subprocess.run(
                    ['g++', '-std=c++17', '-O2', code_path, '-o', executable_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    encoding='utf-8'
                )
                
                if compile_process.returncode != 0:
                    result['status'] = 'COMPILATION_ERROR'
                    result['error'] = compile_process.stderr
                    return result
                
                base_command = [executable_path]
                
            elif language == "javascript":
                # Создаем JavaScript файл
                code_path = os.path.join(tmp_dir, "code.js")
                with open(code_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                base_command = ['node', code_path]
                
            else:
                result['status'] = 'UNSUPPORTED_LANGUAGE'
                result['error'] = f"Язык '{language}' не поддерживается"
                return result

            # Создаем файл для измерения памяти
            memory_file = os.path.join(tmp_dir, 'memory_usage.txt')
            
            # Команда для выполнения с измерением памяти
            full_command = [
                '/usr/bin/time', '-v', '-o', memory_file,
                'timeout', str(time_limit_ms/1000)
            ] + base_command

            # Выполняем код
            process_start_time = time.time()
            process = subprocess.run(
                full_command,
                input=input_data,
                text=True,
                capture_output=True,
                timeout=(time_limit_ms/1000) + 2,
                encoding='utf-8',
                cwd=tmp_dir
            )
            
            # Читаем использование памяти из файла
            memory_used_kb = 0
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_content = f.read()
                    # Ищем строку с Maximum resident set size
                    for line in memory_content.split('\n'):
                        if 'Maximum resident set size (kbytes):' in line:
                            try:
                                memory_used_kb = int(line.split(':')[-1].strip())
                                break
                            except ValueError:
                                logger.warning(f"Could not parse memory usage from: {line}")

            # Обрабатываем результат
            if process.returncode == 0:
                result['status'] = 'SUCCESS'
                result['output'] = process.stdout.strip()
            elif process.returncode == 124:  # timeout
                result['status'] = 'TIME_LIMIT_EXCEEDED'
                result['error'] = 'Time limit exceeded'
            else:
                result['status'] = 'RUNTIME_ERROR'
                result['error'] = process.stderr.strip()

            result['execution_time_ms'] = int((time.time() - process_start_time) * 1000)
            result['memory_used_kb'] = memory_used_kb

            # Проверяем превышение лимита памяти
            if memory_used_kb > memory_limit_mb * 1024:  # Конвертируем MB в KB
                result['status'] = 'MEMORY_LIMIT_EXCEEDED'
                result['error'] = f'Memory limit exceeded: {memory_used_kb/1024:.2f}MB > {memory_limit_mb}MB'

    except subprocess.TimeoutExpired:
        result['status'] = 'TIME_LIMIT_EXCEEDED'
        result['error'] = 'Time limit exceeded'
        result['execution_time_ms'] = int((time.time() - start_time) * 1000)
    except Exception as e:
        result['status'] = 'INTERNAL_ERROR'
        result['error'] = str(e)
        logger.error(f"Error in code execution: {e}")
        result['execution_time_ms'] = int((time.time() - start_time) * 1000)

    return result