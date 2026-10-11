import pytest
from sqlalchemy import text


@pytest.mark.postgres
@pytest.mark.behavior("compatibility")
def test_real_postgresql_environment_is_available(app):
    assert app.state.engine.dialect.name == "postgresql"
    with app.state.engine.connect() as connection:
        assert connection.scalar(text("SELECT current_database()")) == "slotwise_test"
