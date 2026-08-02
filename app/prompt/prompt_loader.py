from pathlib import Path


def prompt_loader(name:str):
    prompt_path = Path(__file__).parents[2] / 'prompts' / f'{name}.prompt'
    return prompt_path.read_text(encoding='utf-8')


if __name__ == '__main__':
    print(prompt_loader('correct_sql'))