from country_decision_atlas_shared.config import get_settings


def run() -> None:
    settings = get_settings()
    print(f"{settings.app_name} worker is ready in {settings.app_env} mode.")
