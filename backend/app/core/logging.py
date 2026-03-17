"""日志配置工具。"""

import logging


def configure_logging() -> None:
    # 先使用统一的基础日志格式，后续可以再扩展文件日志和请求链路日志。
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
