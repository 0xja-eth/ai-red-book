import os
import shutil

from src.core.generator import Generator, GenerateType

clearer = Generator(GenerateType.Video)

if __name__ == '__main__':
    clearer.clear()
