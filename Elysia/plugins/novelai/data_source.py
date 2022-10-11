from Elysia.rule import is_in_service
from Elysia.service import Service

from .config import baseTag, lowQuality


class novelai(Service):
    def __init__(self, **kwargs):
        Service.__init__(self, "生成色图", "AI生成色图", rule=is_in_service("生成色图"))

    @staticmethod
    def txt2body(seed, inputs: str):
        return {
            "input": inputs + baseTag,
            "model": "safe-diffusion",
            "parameters": {
                "width": 512,
                "height": 768,
                "scale": 12,
                "sampler": "k_euler_ancestral",
                "steps": 28,
                "seed": seed,
                "n_samples": 1,
                "ucPreset": 0,
                "uc": lowQuality,
            },
        }
