
from src.core.generator import GenerateType
from src.generate.index import GENERATORS

if __name__ == '__main__':
    generator = GENERATORS[GenerateType.Article.value]
    generator.generate()
