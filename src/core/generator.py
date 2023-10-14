import os
import shutil
import time
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum

import openpyxl
from dataclasses_json import dataclass_json
from openpyxl.styles import Font, Alignment

from src.config import config_loader
from src.config.config_loader import get
from src.core.state_manager import initial_state, get_state, set_state
from src.utils import openai_utils, api_utils

INPUT_ROOT = config_loader.file("./input")
OUTPUT_ROOT = config_loader.file("./output")

TITLE_PROMPT_FILE = "./title_prompt.txt"
CONTENT_PROMPT_FILE = "./content_prompt.txt"

COL_WIDTH = {
    "ID": 12,
    "标题": 32,
    "内容": 128,
    "素材": 16,
    "标题提示词": 32,
    "内容提示词": 32,
    "创建时间": 16,
    "更新时间": 16
}


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

        self._cache_output = {}

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

    _cache_output = {}
    def get_output(self, id) -> Generation | None:
        if id in self._cache_output: return self._cache_output[id]

        file_name = os.path.join(self.output_dir(), 'output.xlsx')
        if not os.path.exists(file_name): return None

        self._cache_output[id] = None

        # 获取excel中编号为id的一行数据
        for row in openpyxl.load_workbook(file_name).active.rows:
            if row[0].value == id:
                # 分开获取url转为列表
                temp_urls = [
                    row[i].value for i in range(3, len(row) - 4) if row[i].value != "-"
                ]
                # for i in range(3, len(row) - 4):
                #     if row[i].value != "-":
                #         temp_urls.append(row[i].value)

                self._cache_output[id] = Generation(
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
                break
        # with open(file_name, "r", encoding="utf8") as file:

        return self._cache_output[id]

    def _save_generation(self, generation: Generation):
        file_name = os.path.join(self.output_dir(), "output.xlsx")

        # 如果文件不存在，创建它
        is_new_file = not os.path.exists(file_name)
        if is_new_file: open(file_name, "w", encoding="utf8").close()

        try:
            workbook = openpyxl.Workbook() if is_new_file else openpyxl.load_workbook(file_name)
            worksheet = workbook.active

            link_font = Font(color="0000FF", underline="single")

            generation_headers = (['ID', '标题', '内容'] +
                       ["素材 #%d" % (i + 1) for i in range(len(generation.urls))] +
                       ['标题提示词', '内容提示词', '创建时间', '更新时间'])
            generation_col = len(generation_headers)

            max_col = worksheet.max_column
            # 确定最大col数量
            real_max_col = max([max_col, generation_col])
            real_url_col = real_max_col - 7

            if is_new_file:
                worksheet.append(generation_headers)
            else:
                # 如果需要，更新标题
                if max_col < real_max_col:
                    # 更新工作表标题
                    for col_num, header_value in enumerate(generation_headers, 1):
                        worksheet.cell(row=1, column=col_num, value=header_value)

                # 更新现有的行以确保每行都有相同数量的列
                for row_num in range(2, worksheet.max_row + 1):
                    curr_row_len = len([cell for cell in worksheet[row_num] if cell.value is not None])
                    if real_max_col == curr_row_len: continue

                    for i in range(4):
                        last_val = worksheet.cell(row=row_num, column=curr_row_len - i).value
                        worksheet.cell(row=row_num, column=real_max_col - i, value=last_val)

                    for i in range(real_max_col - curr_row_len):
                        worksheet.cell(row=row_num, column=curr_row_len - 3 + i, value="-")
                # for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, values_only=False):
                #     while len(row) < header_len:
                #         worksheet.cell(row=row[0].row, column=len(row) + 1, value="")

            # 添加新数据
            new_row = ([generation.id, generation.title, generation.content] +
                       generation.urls + ["-"] * (real_url_col - len(generation.urls)) +
                       [generation.titlePrompt, generation.contentPrompt, generation.createdAt, generation.updatedAt])
            worksheet.append(new_row)

            new_row_cells = worksheet[worksheet.max_row]

            new_row_cells[1].alignment = Alignment(wrapText=True)
            new_row_cells[2].alignment = Alignment(wrapText=True)
            new_row_cells[real_max_col - 3].alignment = Alignment(wrapText=True)
            new_row_cells[real_max_col - 4].alignment = Alignment(wrapText=True)

            for i, url in enumerate(generation.urls, 3):
                if url:
                    new_row_cells[i].hyperlink = os.path.abspath(url)
                    new_row_cells[i].font = link_font

            real_headers = [cell.value for cell in worksheet[1]]
            col_widths = [COL_WIDTH[key.split(" ")[0]] for key in real_headers]

            for (i, col) in enumerate(worksheet.columns):
                column = col[0].column_letter
                worksheet.column_dimensions[column].width = col_widths[i]

            # 保存工作簿
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
