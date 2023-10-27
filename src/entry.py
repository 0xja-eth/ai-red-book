import argparse

from src.generate.index import GENERATORS
from src.publish.index import PUBLISHERS

if __name__ == '__main__':

  # 创建命令行参数解析器
  parser = argparse.ArgumentParser(description="AI自媒体助手")

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
    import asyncio

    publisher = PUBLISHERS["%s_%s" % (args.platform, args.generate_type)]

    async def main():
      await publisher.login()
      await publisher.multi_publish()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
