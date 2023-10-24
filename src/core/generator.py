import os
import shutil
import time
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum

import openpyxl
from dataclasses_json import dataclass_json

from src.config import config_loader
from src.config.config_loader import get
from src.core.state_manager import initial_state, get_state, set_state
from src.utils import openai_utils, api_utils

INPUT_ROOT = config_loader.file("./input")
OUTPUT_ROOT = config_loader.file("./output")

TITLE_PROMPT_FILE = "./title_prompt.txt"
CONTENT_PROMPT_FILE = "./content_prompt.txt"


class GenerateType(Enum):
    Article = "article"
    Video = "video"


@dataclass_json(undefined="exclude")
@dataclass
class Generation:
    id: str
    type: GenerateType
    titlePrompt: str
    contentPrompt: str
    title: str
    content: str
    urls: list

    createdAt: str
    updatedAt: str


class Generator:
    generate_type: GenerateType

    title_prompt: str
    content_prompt: str

    def __init__(self, generate_type):
        self.generate_type = generate_type

        self.title_prompt = None
        self.content_prompt = None

        if "generate" not in initial_state: initial_state["generate"] = {}
        initial_state["generate"][self.name()] = []

    def name(self):
        return self.generate_type.value

    # region Config

    def section_name(self):
        return "Generate %s" % self.generate_type.name

    def load_config(self, key, type):
        return get(self.section_name(), key, type)

    def interval(self):
        return self.load_config("interval", "int")

    def max_count(self):
        return self.load_config("max_count", "int")

    # endregion

    # region State

    def generation_ids(self) -> list:
        return get_state("generate", self.name(), default=[])

    def gen_count(self):
        return len(self.generation_ids())

    def _add_count(self, id):
        generation_ids = self.generation_ids()
        generation_ids.append(id)
        set_state(generation_ids, "generate", self.name())

    def _clear_count(self):
        set_state([], "generate", self.name())

    # endregion

    # region Input

    def get_prompts(self) -> (str, str):
        if self.title_prompt is None:
            with open(os.path.join(INPUT_ROOT, TITLE_PROMPT_FILE), "r", encoding="utf8") as file:
                self.title_prompt = file.read()
        if self.content_prompt is None:
            with open(os.path.join(INPUT_ROOT, CONTENT_PROMPT_FILE), "r", encoding="utf8") as file:
                self.content_prompt = file.read()

        return self.title_prompt, self.content_prompt

    # endregion

    # region Output

    def output_dir(self):
        return os.path.join(OUTPUT_ROOT, self.name())

    def get_output(self, id) -> Generation | None:
        file_name = os.path.join(self.output_dir(), 'output.xlsx')
        if not os.path.exists(file_name): return None
        with open(file_name, "r", encoding="utf8") as file:
            # 获取excel中编号为id的一行数据
            for row in openpyxl.load_workbook(file_name).active.rows:
                if row[0].value == id:
                    # 分开获取url转为列表
                    temp_urls = []
                    for i in range(3, len(row) - 4):
                        temp_urls.append(row[i].value)
                    return Generation(
                        id=row[0].value,
                        type=self.generate_type,
                        title=row[1].value,
                        content=row[2].value,
                        urls=temp_urls,
                        titlePrompt=row[-4].value,
                        contentPrompt=row[-3].value,
                        createdAt=row[-2].value,
                        updatedAt=row[-1].value
                    )

    def _save_generation(self, generation: Generation):
        file_name = os.path.join(self.output_dir(), "output.xlsx")
        # 若不存在文件，则创建文件
        if not os.path.exists(file_name):
            open(file_name, "w", encoding="utf8").close()
        try:
            # 如果表为空，则写入表头
            if os.path.getsize(file_name) == 0:
                # 创建一个新的Excel工作簿
                workbook = openpyxl.Workbook()
                # 选择默认的工作表
                worksheet = workbook.active
                header = ['ID', '标题', '内容']
                for i in range(len(generation.urls)):
                    header.append("图片%d" % (i + 1))
                header.extend(['标题提示词', '内容提示词', '创建时间', '更新时间'])
                worksheet.append(header)
                # 保存Excel文件
                workbook.save(file_name)

            # 加载Excel文件
            workbook = openpyxl.load_workbook(file_name)
            # 选择默认的工作表
            worksheet = workbook.active
            new_row = [generation.id, generation.title, generation.content]
            for url in generation.urls:
                new_row.append(url)
            new_row.extend(
                [generation.titlePrompt, generation.contentPrompt, generation.createdAt, generation.updatedAt])
            worksheet.append(new_row)

            # 保存Excel文件
            workbook.save(file_name)
            print("Excel文件保存成功！")

        except Exception as e:
            print("保存Excel文件时出现异常：", str(e))

    # endregion

    # region Generate

    generating_count: int

    def generate(self):
        if self.gen_count() >= self.max_count(): return True

        self.generating_count = self.gen_count() + 1

        print("Start generate %s: %d/%d" % (
            self.name(), self.generating_count, self.max_count()
        ))

        title_prompt, content_prompt, title, content = self._generate_title_content()
        urls = self._generate_media()

        generation = self._upload_generation(title_prompt, content_prompt, title, content, urls)

        self._save_generation(generation)
        self._add_count(generation.id)

        print("End generate %s: %d/%d -> %s" % (
            self.name(), self.generating_count, self.max_count(), generation
        ))

    def _generate_title_content(self):
        title_prompt, content_prompt = self.get_prompts()
        title = openai_utils.generate_completion(title_prompt)

        content_prompt_with_title = content_prompt.replace("%s", title)
        content = openai_utils.generate_completion(content_prompt_with_title)

        return title_prompt, content_prompt, title, content

    @abstractmethod
    def _generate_media(self) -> list:
        pass

    def _upload_generation(self, title_prompt, content_prompt, title, content, urls) -> Generation:
        return Generation(**api_utils.generate({
            "type": self.generate_type.value,
            "titlePrompt": title_prompt,
            "contentPrompt": content_prompt,
            "title": title,
            "content": content,
            "urls": urls
        }))

    def multi_generate(self):
        while self.gen_count() < self.max_count():
            self.generate()
            time.sleep(self.interval())

    def clear(self):
        if os.path.exists(self.output_dir()):
            shutil.rmtree(self.output_dir())
            os.mkdir(self.output_dir())

        self._clear_count()
        self._clear_publisher()

    def _clear_publisher(self):
        from src.publish.index import PUBLISHERS

        for key in PUBLISHERS:
            if key.endswith(self.name()):
                PUBLISHERS[key].clear()

    # endregion
