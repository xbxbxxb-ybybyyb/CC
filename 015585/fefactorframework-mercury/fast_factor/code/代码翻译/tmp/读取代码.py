def read_py_file_to_string(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code_string = file.read()
        return code_string
    except FileNotFoundError:
        return "文件未找到，请检查路径是否正确。"
    except Exception as e:
        return f"读取文件时发生错误: {e}"

# 示例用法
file_path = "/data/user/015585/fefactorframework-mercury/fast_factor/code/代码翻译/tmp/factor_ttick_sample.py"  # 替换为你的 .py 文件路径
code_content = read_py_file_to_string(file_path)
print(code_content)