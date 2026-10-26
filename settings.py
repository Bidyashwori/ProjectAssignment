import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("WEB_BASE_URL", "https://www.mumzworld.com/en").rstrip("/")
    email: str = os.getenv("MUMZWORLD_EMAIL", "")
    password: str = os.getenv("MUMZWORLD_PASSWORD", "")
    browser: str = os.getenv("BROWSER", "chrome").lower()
    headless: bool = env_bool("HEADLESS")
    search_term: str = os.getenv("SEARCH_TERM", "diaper")
    timeout: int = int(os.getenv("WAIT_TIMEOUT", "15"))

    appium_url: str = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    android_device_name: str = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
    android_platform_version: str = os.getenv("ANDROID_PLATFORM_VERSION", "")
    android_package: str = os.getenv("ANDROID_APP_PACKAGE", "")
    android_activity: str = os.getenv("ANDROID_APP_ACTIVITY", "")
    android_apk: str = os.getenv("ANDROID_APP_PATH", "")

    def require_credentials(self) -> None:
        missing = [name for name, value in (
            ("MUMZWORLD_EMAIL", self.email),
            ("MUMZWORLD_PASSWORD", self.password),
        ) if not value.strip()]
        if missing:
            raise RuntimeError("Set the following values in .env before running sign-in tests: " + ", ".join(missing))

    def validate_android(self) -> None:
        if not self.android_apk and not self.android_package:
            raise RuntimeError(
                "Set ANDROID_APP_PACKAGE for an installed app or ANDROID_APP_PATH for an APK in .env. "
                "The app package is not assumed because it can vary by release."
            )


settings = Settings()
