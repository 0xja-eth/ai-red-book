import json
import os
import time
from abc import abstractmethod
from enum import Enum
from typing import Any

from dataclasses_json import dataclass_json

from src.config import config_loader
from src.config.config_loader import get_int, get
from src.core.state_manager import initial_state, get_state, set_state
from src.utils import openai_utils
from dataclasses import dataclass

INPUT_ROOT = config_loader.file("./input")
OUTPUT_ROOT = config_loader.file("./output")
PROMPT_FILE = config_loader.file("./prompt.json")

class GenerateType(Enum):
  Article = "article"
  Video = "video"

@dataclass_json
@dataclass
class Prompts:
  title: str
  content: str

@dataclass_json
@dataclass
class Generation:
  id: str
  type: GenerateType
  titlePrompt: str
  contentPrompt: str
  title: str
  content: str
  urls: list

class Generator:

  generate_type: GenerateType

  def __init__(self, generate_type):
    self.generate_type = generate_type

    if "generate" not in initial_state: initial_state["generate"] = {}
    initial_state["generate"][self.name()] = []

  def name(self): return self.generate_type.value

  # region Config

  def section_name(self): return "Generate %s" % self.generate_type.name

  def load_config(self, key, type): return get(self.section_name(), key, type)

  def interval(self): return self.load_config("interval", "int")
  def max_count(self): return self.load_config("max_count", "int")

  # endregion

  # region State

  def generation_ids(self) -> list: return get_state("generate", self.name())
  def gen_count(self): return len(self.generation_ids())

  def _add_generation_id(self, id):
    generation_ids = self.generation_ids()
    generation_ids.append(id)
    set_state(generation_ids, "generate", self.name())

  # endregion

  # region Input

  _prompts: Prompts

  def prompts(self) -> Prompts:
    if self._prompts is None:
      with open(os.path.join(INPUT_ROOT, PROMPT_FILE), encoding="utf8") as file:
        self._prompts = Prompts(**json.load(file))
    return self._prompts

  # endregion

  # region Output

  def output_dir(self): return os.path.join(OUTPUT_ROOT, self.name())

  def get_output(self, id) -> Generation | None:
    file_name = os.path.join(self.output_dir(), "%d.json" % id)
    if not os.path.exists(file_name): return None
    with open(file_name, "r", encoding="utf8") as file:
      return Generation(**json.load(file))

  def _save_generation(self, generation: Generation):
    file_name = os.path.join(self.output_dir(), "%d.json" % generation.id)
    with open(file_name, "w", encoding="utf8") as file:
      json.dump(generation.to_json(), file)

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
    self._add_generation_id(generation.id)

    print("End generate %s: %d/%d -> %s" % (
      self.name(), self.generating_count, self.max_count(), generation
    ))

  def _generate_title_content(self):
    prompts = self.prompts()

    title_prompt, content_prompt = prompts.title, prompts.content

    title = openai_utils.generate_completion(title_prompt)
    content = openai_utils.generate_completion(content_prompt % title)

    return title_prompt, content_prompt, title, content

  @abstractmethod
  def _generate_media(self) -> list: pass

  def _upload_generation(self, title_prompt, content_prompt, title, content, urls) -> Generation:
    # TODO: 构建并上传Generation
    pass

  def multi_generate(self):
    while self.gen_count() < self.max_count():
        self.generate()
        time.sleep(self.interval())

  # endregion
