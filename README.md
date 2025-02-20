# README: Instructions for Running and Testing the Rasa Chatbot

## Prerequisites

Before running the bot, ensure you have the following installed:

- **Python** 3.8+ (recommended 3.9 or 3.10 for compatibility with Rasa).
- **Virtual environment** (optional but recommended).
- **API key from OpenWeatherMap** (stored in `config.py` as `API_KEY`).

## Step-by-Step Instructions

### 1. Cloning or Preparing the Project

Clone the GitHub repository:

```bash
git clone https://github.com/Bodomerka/weather-bot-rasa
cd weather-bot-rasa
```

If you have local files, simply navigate to the project folder:

```bash
cd d:\weather-bot-rasa
```

### 2. Creating and Activating a Virtual Environment

Create a virtual environment:

```bash
python -m venv weather-bot-rasa
```

Activate it:

- **Windows:**
  ```bash
  weather-bot-rasa\Scripts\activate
  ```
- **Linux/Mac:**
  ```bash
  source weather-bot-rasa/bin/activate
  ```

### 3. Installing Dependencies

Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Ensure that `requirements.txt` includes the following essential libraries:

```
rasa>=3.1.0
requests>=2.28.0
dateparser>=1.1.0
```

### 4. Configuring the API Key

Ensure that `config.py` contains the following line:

```python
API_KEY = "your_openweathermap_api_key"
```

If the file does not exist, create it in the project root and add your key. Obtain the key from [OpenWeatherMap](https://openweathermap.org/api).

### 5. Checking the File Structure

Make sure the following files are present:

- `actions.py` (action code for weather responses).
- `domain.yml` (intents, entities, slots, responses, actions).
- `stories.yml` (stories for training).
- `config.yml` (model configuration).
- `test_stories.yml` (test stories).

### 6. Training the Model

Train the bot by running:

```bash
rasa train
```

After completion, a model file will appear in the `models/` directory, for example:

```
models/xxxxxxxx-xxxxxx-tattered-tunnel.tar.gz
```

### 7. Running the Action Server

In a separate terminal, activate the virtual environment (as in step 2) and start the action server:

```bash
rasa run actions
```

Ensure the server is running (you should see the message `Action server is running...`).

### 8. Running the Bot

In another terminal, activate the virtual environment and start the bot:

```bash
rasa shell
```

Try commands such as:

```
What is the temperature in Kyiv now?
Will it be sunny in Bangkok tomorrow?
```

### 9. Testing the Bot

Run tests to verify the stories:

```bash
rasa test core
```

Test results will be saved in the `results/` directory:

- `failed_test_stories.yml` – failed stories.
- `story_report.json` – accuracy report.

### 10. Shutting Down

Close the terminals (`Ctrl+C`) and deactivate the virtual environment:

```bash
deactivate
```

