
import openai

from src.config import config_loader

openai.api_key = config_loader.get('Common', 'openai_key')
openai.api_base = config_loader.get('Common', 'openai_base')

base_options = {
  "temperature": 1,
  "max_tokens": 4096,
  "top_p": 1,
  "frequency_penalty": 0,
  "presence_penalty": 0
}

def update_options(**kwargs):
  base_options.update(kwargs)

def generate_completion(prompt, **kwargs):
  print("[generate_completion] %s" % prompt)

  options = {**base_options, **kwargs}
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[{ "role": "user", "content": prompt }],
    **options
  )

  message = response.choices[0].message.content.strip()
  print("[generate_completion] result: %s" % message)

  return message

def generate_chat_completion(messages, **kwargs):
  print("[generate_chat_completion] %s" % messages)

  options = {**base_options, **kwargs}
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=messages,
    **options
  )

  message = response.choices[0].message.content.strip()
  print("[generate_chat_completion] result: %s" % message)

  return message

