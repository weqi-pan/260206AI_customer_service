from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from utils.config_handler import prompts_conf

# 加载系统提示词
def load_system_prompt():
    try:
        system_prompt_path = get_abs_path(prompts_conf["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompt]yml缺少配置项: main_prompt_path")
        raise e
    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompt]解析系统提示词失败，{str(e)}")
        raise e

# 加载rag提示词
def load_rag_prompt():
    try:
        rag_prompt_path = get_abs_path(prompts_conf["rag_summary_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompt]yml缺少配置项: rag_summary_prompt_path")
        raise e
    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompt]解析rag总结提示词失败，{str(e)}")
        raise e

# 加载报告提示词
def load_report_prompt():
    try:
        report_prompt_path = get_abs_path(prompts_conf["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompt]yml缺少配置项: report_prompt_path")
        raise e
    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompt]解析报告生成提示词失败，{str(e)}")
        raise e