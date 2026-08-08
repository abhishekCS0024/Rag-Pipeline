from src.shared.config import Settings


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_cors_origins_list_splits_and_strips_whitespace():
    settings = _settings(cors_origins="http://a.com, http://b.com ,")

    assert settings.cors_origins_list == ["http://a.com", "http://b.com"]


def test_cors_origins_list_empty_string_yields_empty_list():
    settings = _settings(cors_origins="")

    assert settings.cors_origins_list == []


def test_allowed_file_types_list_lowercases_and_strips():
    settings = _settings(allowed_file_types=" PDF, Docx ,txt")

    assert settings.allowed_file_types_list == ["pdf", "docx", "txt"]


def test_database_url_assembles_from_postgres_fields():
    settings = _settings(
        postgres_user="u",
        postgres_password="p",
        postgres_host="h",
        postgres_port=1234,
        postgres_db="d",
    )

    assert settings.database_url == "postgresql+psycopg://u:p@h:1234/d"
