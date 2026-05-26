from datetime import datetime

from db.init_db import initialize_database
from db.repositories import get_user
from utils.config_handler import agent_conf


class DemoExternalProvider:
    def __init__(self):
        self.default_user_id = str(agent_conf.get("default_user_id", "1001"))
        self.default_city = str(agent_conf.get("default_city", "上海"))
        self.demo_month = agent_conf.get("demo_month")

    def get_user_id(self) -> str:
        return self.default_user_id

    def get_user_location(self) -> str:
        return self.default_city

    def get_current_month(self) -> str:
        if self.demo_month:
            return str(self.demo_month)
        return datetime.now().strftime("%Y-%m")

    def get_weather(self, city: str) -> str:
        weather = agent_conf.get("demo_weather", {})
        condition = weather.get("condition", "晴天")
        temperature = weather.get("temperature", "26摄氏度")
        humidity = weather.get("humidity", "78%")
        wind = weather.get("wind", "南风2级")
        aqi = weather.get("aqi", "21")
        rain_probability = weather.get("rain_probability", "低")
        return (
            f"城市{city}的天气是{condition}，气温为{temperature}，"
            f"空气湿度为{humidity}，{wind}，AQI{aqi}，"
            f"最近六小时降雨概率{rain_probability}"
        )


class SQLiteExternalProvider(DemoExternalProvider):
    def __init__(self):
        super().__init__()
        initialize_database()

    def get_user_id(self) -> str:
        return self.default_user_id

    def get_user_location(self) -> str:
        user = get_user(self.default_user_id)
        if user and user.get("city"):
            return user["city"]
        return super().get_user_location()


def get_external_provider():
    provider_type = agent_conf.get("external_provider", "demo")
    if provider_type == "demo":
        return DemoExternalProvider()
    if provider_type == "sqlite":
        return SQLiteExternalProvider()
    raise ValueError(f"暂不支持的外部服务 provider：{provider_type}")
