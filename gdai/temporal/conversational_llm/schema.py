from dataclasses import dataclass


@dataclass
class PromptInput:
    user_prompt: str
    system_prompt: str
