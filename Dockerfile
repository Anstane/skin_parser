FROM nikolaik/python-nodejs:python3.11-nodejs20

ENV POETRY_VERSION=1.7.0
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=true
ENV POETRY_VIRTUALENVS_IN_PROJECT=false

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

CMD ["poetry", "run", "python", "-m", "app.main"]