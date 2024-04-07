from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix  = 'COTOWN',
    env_switcher   = 'COTOWN_ENV',
    settings_files = ['.settings.toml', '.secrets.toml'],
    environments   = True,
    load_dotenv    = True
)