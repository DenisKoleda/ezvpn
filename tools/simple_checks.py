# tools/simple_checks.py
import os
from datetime import datetime, timedelta

def test_config_loading():
    print("Testing configuration loading...")
    mock_env_created = False
    original_env_content = None
    env_file_path = ".env"

    try:
        # Check if .env exists, if so, back it up
        if os.path.exists(env_file_path):
            with open(env_file_path, "r") as f:
                original_env_content = f.read()
        
        # Create a mock .env for testing
        print("Creating/Overwriting .env file for config test...")
        with open(env_file_path, "w") as f:
            f.write("BOT_TOKEN=\"test_bot_token\"\n") # Ensure quotes for string values if they contain special chars or just good practice
            f.write("DB_URL=\"mongodb://localhost:27017/testvpn\"\n")
            f.write("DB_NAME=\"testvpn\"\n")
            f.write("YOO_TOKEN=\"test_yoo_token\"\n")
            f.write("VPN_API_URL_SRV1_RUS_1=\"http://testhost:8000/api\"\n")
            # VPN_API_HEADERS uses default_factory, so no need to set it in .env for this test
        mock_env_created = True
        
        # Important: settings module might be already loaded.
        # For a robust test, you'd need to ensure it's reloaded,
        # or run this script in a separate process. Python's import system caches modules.
        # For this simple check, we assume it's the first time or changes are picked up.
        # A more advanced way: `import importlib; importlib.reload(src.bot.config)`
        try:
            import src.bot.config
            import importlib
            importlib.reload(src.bot.config) # Attempt to reload
            settings = src.bot.config.settings
        except ImportError: # If src.bot.config not found initially
             from src.bot.config import settings


        assert settings.bot_token.get_secret_value() == "test_bot_token", f"Bot token not loaded correctly. Got: {settings.bot_token.get_secret_value()}"
        assert settings.db_url == "mongodb://localhost:27017/testvpn", f"DB URL not loaded. Got: {settings.db_url}"
        assert settings.db_name == "testvpn", f"DB Name not loaded. Got: {settings.db_name}"
        assert settings.yoo_token.get_secret_value() == "test_yoo_token", f"Yoo token not loaded. Got: {settings.yoo_token.get_secret_value()}"
        assert str(settings.vpn_api_url_srv1_rus_1) == "http://testhost:8000/api", f"VPN API URL not loaded. Got: {settings.vpn_api_url_srv1_rus_1}"
        assert settings.vpn_api_headers['Authorization'] == 'Bearer secret', f"Default API headers incorrect. Got: {settings.vpn_api_headers}"
        print("Configuration loading test PASSED.")
        return True
    except Exception as e:
        print(f"Configuration loading test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up: remove mock .env or restore original
        if mock_env_created:
            if original_env_content is not None:
                print(f"Restoring original {env_file_path} file.")
                with open(env_file_path, "w") as f:
                    f.write(original_env_content)
            else:
                print(f"Cleaning up mocked {env_file_path} file.")
                os.remove(env_file_path)


def test_db_user_model():
    print("\nTesting DB User model...")
    try:
        from src.bot.db.models import User
        from pydantic import ValidationError

        user_data_ok = {
            "telegram_id": 12345,
            "tg_link": "testuser",
            "tg_name": "Test User",
            "tarif": "Premium",
            "tarif_exp": datetime.now() + timedelta(days=30),
            "registration_date": datetime.now(),
            "test_active": True
        }
        user = User(**user_data_ok)
        assert user.telegram_id == 12345
        assert user.tarif_exp > datetime.now()
        print("DB User model instantiation with valid data PASSED.")

        user_data_bad_type = user_data_ok.copy()
        user_data_bad_type["telegram_id"] = "not_an_int" # Invalid type
        try:
            User(**user_data_bad_type)
            # If Pydantic v1, this might pass due to type coercion. Pydantic v2 is stricter.
            # For this test, we expect ValidationError for a clear type mismatch.
            print(f"Model created with bad type: {User(**user_data_bad_type).telegram_id}") # Log what happened
            raise AssertionError("Pydantic ValidationError not raised for bad telegram_id type 'not_an_int'")
        except ValidationError as ve:
            # Check if the error is specifically for telegram_id
            error_locs = [err['loc'][0] for err in ve.errors()]
            assert "telegram_id" in error_locs, f"Validation error raised, but not for telegram_id. Errors: {ve.errors()}"
            print("DB User model validation for bad telegram_id type PASSED (ValidationError raised as expected).")
        
        # Test missing required field (registration_date)
        user_data_missing_field = user_data_ok.copy()
        del user_data_missing_field["registration_date"]
        try:
            User(**user_data_missing_field)
            raise AssertionError("Pydantic ValidationError not raised for missing required field 'registration_date'")
        except ValidationError as ve:
            error_locs = [err['loc'][0] for err in ve.errors()]
            assert "registration_date" in error_locs, f"Validation error raised, but not for registration_date. Errors: {ve.errors()}"
            print("DB User model validation for missing required field PASSED (ValidationError raised as expected).")

        return True
    except Exception as e:
        print(f"DB User model test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running simple checks...")
    # Add src to path for module resolution if script is run from tools/
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    config_ok = test_config_loading()
    model_ok = test_db_user_model()

    if config_ok and model_ok:
        print("\nAll simple checks PASSED.")
    else:
        print("\nSome simple checks FAILED.")
