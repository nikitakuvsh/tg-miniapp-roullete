Инструкция для фронта
В директории frontend открыть файл index.html

Инструкция для бекенда
1. Перейти в директорию backend

```
cd backend
```

2. Создать виртуальное окружение env

```
python -m venv env
```

```
cd env/Scripts && activate && cd ../../
```

3. Установить зависимости

```
pip install -r requirements.txt
```

4. Развернуть FastAPI сервер

```
uvicorn main:app
```
