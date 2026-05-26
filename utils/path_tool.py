# 为整个项目提供统一的绝对路径
import os

def get_project_root() -> str:
    # 获取项目根目录
    current_file = os.path.abspath(__file__) # 当前文件绝对路径
    current_dir = os.path.dirname(current_file) # 当前文件所在目录
    project_root = os.path.dirname(current_dir) # 项目根目录

    return project_root

def get_abs_path(relative_path: str) -> str:
    # 传递相对路径，返回绝对路径
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)

