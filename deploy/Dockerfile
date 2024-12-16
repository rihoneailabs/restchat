FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
COPY pyproject.toml  .

# Install dependencies
RUN pip install -r requirements.txt && \
    pip install -U --prefer-binary tokenizers anthropic && \
    pip install .

# Copy the rest of the application
COPY public/ ./public
COPY .chainlit/ ./.chainlit
COPY README.md LICENSE ./
COPY restchat/ ./restchat
COPY app.py setup.py ./

# Set environment variables
ENV PYTHONUNBUFFERED 1
EXPOSE 5500
ARG PORT=5500

# Command to run the app
CMD python -m chainlit run app.py -h --host 0.0.0.0 --port ${PORT}

# Alternatively: Use entrypoint file
# COPY entrypoint.sh .
# RUN chmod +x ./entrypoint.sh
# ENTRYPOINT ["./entrypoint.sh"]