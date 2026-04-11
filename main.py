"""
Точка входа для деплоя на сервер.
Kuberns и другие платформы ищут main.py
"""
import asyncio
import logging
import sys
import os

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Добавляем теку директорию в путь
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Импортируем и запускаем бота
    from bot import main
    asyncio.run(main())
