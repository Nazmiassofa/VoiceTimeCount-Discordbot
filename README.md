# Discord Bot/VoiceTimeCounter

## 🧑‍💻 Author
**Nazmiassofa**

## 📄 Description
**VoiceTimeCount** Discord Bot for count your voice time.

---

## 🚀 Installation

### 🔹 Database Requirements
   - Postgresql 
   - Table needed : voicecounter, dailyvoicecounter

   EXAMPLE 
                                    Table "voicecounter"
    Column     |            Type             | Collation | Nullable |      Default      
---------------+-----------------------------+-----------+----------+-------------------
 member_id     | bigint                      |           | not null | 
 username      | text                        |           | not null | 
 message_count | integer                     |           |          | 0
 voice_time    | bigint                      |           |          | 0
 poin          | integer                     |           |          | 0
 last_activity | timestamp without time zone |           |          | CURRENT_TIMESTAMP
 voice_count   | integer                     |           |          | 0
Indexes:
    "leveling_pkey" PRIMARY KEY, btree (member_id)


### 🔹 Option 1: Docker Installation

1. Clone repository:
   ```bash
	- git clone https://github.com/Nazmiassofa/VoiceTimeCount.git

2. Masuk ke direktori:
   ```bash
	- cd /folder/path

3. Build Your Image:
   ```bash
	- docker build -t <yourimagename> .
