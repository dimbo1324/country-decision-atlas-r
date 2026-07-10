import os


# Settings.app_env defaults to "production" (the fail-safe choice for
# unconfigured deployments — see P1-10, Аудит-эпизод 6), and neither this
# test suite nor CI's plain `pytest` step sets APP_ENV. Without this, every
# bare Settings()/get_settings() call in the test process would inherit
# app_env="production" together with the local-dev default secrets and trip
# the new fail-fast validator. Module-level so it runs before any test
# module in this directory imports app.* code.
os.environ.setdefault("APP_ENV", "local")
