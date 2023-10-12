import json
import os
import shutil
import time
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum

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
        file_name = os.path.join(self.output_dir(), "%s.json" % id)
        if not os.path.exists(file_name): return None
        with open(file_name, "r", encoding="utf8") as file:
            return Generation(**json.load(file))

    def _save_generation(self, generation: Generation):
        file_name = os.path.join(self.output_dir(), "%s.json" % generation.id)
        with open(file_name, "w", encoding="utf8") as file:
            json.dump(generation.to_dict(), file)

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

    # endregion
