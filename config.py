import os
bot_token = "6202814497:AAH5YxaUT8HzXf3ZomNaySkhwkq0dQDXk0g"

redis_host = os.environ.get("REDISHOST", "localhost")
redis_port = os.environ.get("REDISPORT", 6490)
redis_password = os.environ.get("REDISPASSWORD")
