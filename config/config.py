from dataclasses import dataclass

from environs import Env

@dataclass
class TgBot:
    token: str

@dataclass
class LogSettings:
    level: str
    format: str

@dataclass
class Config:
    bot: TgBot
    log: LogSettings


def load_config() -> Config:
    env = Env()
    env.read_env()

    return Config(
        bot=TgBot(token=env.str("BOT_TOKEN")),
        log=LogSettings(
            level=env.str("LOG_LEVEL", default="INFO"),
            format=env.str("LOG_FORMAT")
        )
    )