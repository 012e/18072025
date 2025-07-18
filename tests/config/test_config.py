import os
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from pydantic import HttpUrl

from config.config import Settings, load_config


class TestSettings:
    """Test the Settings pydantic model."""

    def test_settings_with_valid_data(self):
        """Test Settings creation with valid data."""
        # Use environment variable format since Settings uses Field aliases
        with patch.dict(os.environ, {
            "GRAFANA_LOKI_URL": "http://localhost:3100",
            "OPENAI_API_KEY": "test-api-key",
            "SCRAPE_OUTPUT_PATH": "/tmp/test",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "test-password"
        }):
            # Clear cache and test
            load_config.cache_clear()
            settings = load_config()
            
            assert isinstance(settings.grafana_loki_url, HttpUrl)
            assert str(settings.grafana_loki_url) == "http://localhost:3100/"
            assert settings.openai_api_key == "test-api-key"
            assert settings.scrape_output_path == "/tmp/test"
            assert settings.redis_host == "localhost"
            assert settings.redis_port == 6379
            assert settings.redis_password == "test-password"

    def test_settings_with_default_scrape_output_path(self):
        """Test Settings uses default scrape_output_path when not provided."""
        with patch.dict(os.environ, {
            "GRAFANA_LOKI_URL": "http://localhost:3100",
            "OPENAI_API_KEY": "test-api-key",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "test-password"
        }):
            # Remove SCRAPE_OUTPUT_PATH if it exists
            if "SCRAPE_OUTPUT_PATH" in os.environ:
                del os.environ["SCRAPE_OUTPUT_PATH"]
            load_config.cache_clear()
            settings = load_config()
            assert settings.scrape_output_path == "./.tmp"

    def test_settings_with_invalid_url(self):
        """Test Settings validation fails with invalid URL."""
        with patch.dict(os.environ, {
            "GRAFANA_LOKI_URL": "invalid-url",
            "OPENAI_API_KEY": "test-api-key",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "test-password"
        }):
            load_config.cache_clear()
            with pytest.raises(ValidationError) as exc_info:
                load_config()
            assert "Input should be a valid URL" in str(exc_info.value)

    def test_settings_with_invalid_port(self):
        """Test Settings validation fails with invalid port."""
        with patch.dict(os.environ, {
            "GRAFANA_LOKI_URL": "http://localhost:3100",
            "OPENAI_API_KEY": "test-api-key",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "invalid-port",
            "REDIS_PASSWORD": "test-password"
        }):
            load_config.cache_clear()
            with pytest.raises(ValidationError) as exc_info:
                load_config()
            assert "Input should be a valid integer" in str(exc_info.value)

    def test_settings_missing_required_fields(self):
        """Test Settings validation fails when required fields are missing."""
        with patch.dict(os.environ, {
            "GRAFANA_LOKI_URL": "http://localhost:3100",
            # Missing OPENAI_API_KEY, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
        }, clear=True):
            load_config.cache_clear()
            with pytest.raises(ValidationError) as exc_info:
                load_config()
            error_str = str(exc_info.value)
            # In newer Pydantic, missing fields show as "Input should be a valid string" when None
            assert "Input should be a valid" in error_str or "Field required" in error_str


class TestLoadConfig:
    """Test the load_config function."""

    @patch('config.config.os.getenv')
    @patch('builtins.print')
    def test_load_config_success(self, mock_print, mock_getenv):
        """Test successful config loading."""
        mock_getenv.side_effect = lambda key: {
            "GRAFANA_LOKI_URL": "http://localhost:3100",
            "OPENAI_API_KEY": "test-api-key",
            "SCRAPE_OUTPUT_PATH": "/tmp/test",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "test-password"
        }.get(key)
        
        # Clear the cache before testing
        load_config.cache_clear()
        
        settings = load_config()
        
        assert isinstance(settings, Settings)
        assert str(settings.grafana_loki_url) == "http://localhost:3100/"
        assert settings.openai_api_key == "test-api-key"
        assert settings.scrape_output_path == "/tmp/test"
        assert settings.redis_host == "localhost"
        assert settings.redis_port == 6379
        assert settings.redis_password == "test-password"
        
        mock_print.assert_called_with("Configuration validated successfully with Pydantic.")

    @patch('config.config.os.getenv')
    @patch('builtins.print')
    def test_load_config_with_missing_redis_password(self, mock_print, mock_getenv):
        """Test config loading fails when REDIS_PASSWORD is missing."""
        mock_getenv.side_effect = lambda key: {
            "GRAFANA_LOKI_URL": "http://localhost:3100",
            "OPENAI_API_KEY": "test-api-key",
            "SCRAPE_OUTPUT_PATH": "/tmp/test",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            # Missing REDIS_PASSWORD returns None
        }.get(key)
        
        # Clear the cache before testing
        load_config.cache_clear()
        
        with pytest.raises(ValidationError):
            load_config()
        
        # Check that error message was printed
        assert mock_print.call_count >= 1
        assert any("Configuration validation failed" in str(call) for call in mock_print.call_args_list)

    @patch('config.config.os.getenv')
    @patch('builtins.print')
    def test_load_config_with_invalid_url(self, mock_print, mock_getenv):
        """Test config loading fails with invalid URL."""
        mock_getenv.side_effect = lambda key: {
            "GRAFANA_LOKI_URL": "invalid-url",
            "OPENAI_API_KEY": "test-api-key",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "test-password"
        }.get(key)
        
        # Clear the cache before testing
        load_config.cache_clear()
        
        with pytest.raises(ValidationError):
            load_config()

    @patch('config.config.os.getenv')
    def test_load_config_caching(self, mock_getenv):
        """Test that load_config uses LRU cache."""
        mock_getenv.side_effect = lambda key: {
            "GRAFANA_LOKI_URL": "http://localhost:3100",
            "OPENAI_API_KEY": "test-api-key",
            "SCRAPE_OUTPUT_PATH": "/tmp/test",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "test-password"
        }.get(key)
        
        # Clear the cache before testing
        load_config.cache_clear()
        
        # Call load_config twice
        settings1 = load_config()
        settings2 = load_config()
        
        # Should return the same instance due to caching
        assert settings1 is settings2
        
        # os.getenv should only be called once per environment variable due to caching
        expected_calls = 6  # 6 environment variables are accessed now
        assert mock_getenv.call_count == expected_calls

    @patch('config.config.os.getenv')
    def test_load_config_with_none_values(self, mock_getenv):
        """Test config loading when environment variables return None."""
        mock_getenv.return_value = None
        
        # Clear the cache before testing
        load_config.cache_clear()
        
        with pytest.raises(ValidationError):
            load_config()

    def teardown_method(self):
        """Clean up after each test."""
        # Clear the cache after each test
        load_config.cache_clear()
