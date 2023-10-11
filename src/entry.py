import argparse

from src.generate.index import GENERATORS
from src.publish.index import PUBLISHERS

# 创建命令行参数解析器
parser = argparse.ArgumentParser(description="命令行工具示例")

# 添加操作参数
parser.add_argument("oper", choices=["generate", "clear", "publish"], help="操作类型")

# 添加生成类型参数
parser.add_argument("--generate-type", choices=["article", "video"], help="生成类型")

# 添加平台参数（仅当操作为'publish'时才需要）
parser.add_argument("--platform", choices=["xhs", "dy", "wx"], help="发布平台")

# 解析命令行参数
args = parser.parse_args()

if args.oper == "generate":
  GENERATORS[args.generate_type].multi_generate()

elif args.oper == "clear":
  GENERATORS[args.generate_type].clear()

elif args.oper == "publish":
  publisher = PUBLISHERS["%s_%s" % (args.platform, args.generate_type)]
  publisher.login()
  publisher.multi_publish()
