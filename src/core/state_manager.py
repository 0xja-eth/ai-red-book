import json
import os.path

from src.config import config_loader

STATE_FILE = config_loader.file("./state.json")

state = None

initial_state: dict = {}

def init_state():
  global state
  if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf8") as file: state = json.load(file)
  else:
    state = initial_state
    save_state()

def save_state():
  with open(STATE_FILE, "w", encoding="utf8") as file: json.dump(state, file)

def get_state(*keys):
  if state is None: init_state()
  if len(keys) <= 0: return state

  tmp_state = state
  for key in keys:
    if key not in tmp_state: return None
    tmp_state = tmp_state[key]
  return tmp_state

def set_state(value, *keys):
  if state is None: init_state()
  tmp_state = state
  for i in range(len(keys) - 1):
    key = keys[i]
    if key not in tmp_state: tmp_state[key] = {}
    tmp_state = tmp_state[key]

  tmp_state[keys[-1]] = value

  save_state()

if __name__ == '__main__':

  # Test
  set_state(1, "publish_count", "xhs_article")
  print(get_state("publish_count", "xhs_article"))
  set_state(2, "publish_count", "xhs_article")
  print(get_state("publish_count", "xhs_article"))
  set_state(5, "publish_count", "dy_article")
  print(get_state("publish_count", "dy_article"))
  print(get_state("publish_count"))
  print(get_state())
