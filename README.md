# Discord Bot/VoiceTimeCounter

## 🧑‍💻 Author
**Nazmiassofa**

## 📄 Description
**VoiceTimeCount** 
Discord Bot for count your voice time.

---

## 🚀 Installation

### 🔹 Database Requirements
   - Postgresql 
   - search 'MAIN_TABLE' and 'DAILY_TABLE' in /voicecounter and replace it with your own table

### 🔹 Option 1: Docker Installation

1. Clone the repository

2. Masuk ke direktori:
   ```bash
	- cd /folder/path

3. Build Your Image:
   ```bash
	- docker build -t <yourimagename> .
    - setup your compose file

4. Run your container
   ```bash
   - docker compose up -d

### 🔹 Option 2: Local Installation

1. Clone the repository

2. Enter directory :
   ```bash
	- python3 -m venv <your_venv_foldername>

3. Activate the python venv:
   ```bash
	- source /<your_venv_foldername>/bin/activate

4. Run the code
   ```bash
   - python <main_file>