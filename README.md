# Assignment 2: Multi-Database Manager

A web app that connects to **three separate SQLite databases** and lets the user
pick a database, browse its tables, and **create, read, update and delete** rows.

| Database | File | Tables |
|---|---|---|
| Library | `data/library.db` | `books`, `members` |
| School | `data/school.db` | `students`, `courses` |
| Store | `data/store.db` | `products`, `orders` |

Each database file is created and filled with dummy data by `seed.py`.

## Tech
- **Back end:** Python 3 + Flask, REST API (`app.py`)
- **Databases:** SQLite, one file per database (`data/*.db`)
- **Front end:** HTML/CSS/JavaScript single page (`templates/index.html`)

## Run it
```bash
pip install -r requirements.txt
python seed.py      # creates the 3 databases with dummy data (optional: app.py does this on first run)
python app.py       # then open http://127.0.0.1:5000
```

## Features
- Sidebar to **select which database** you're working in
- Tabs for each table in the selected database, with live row counts
- **Read:** view all rows, with instant search
- **Create:** "+ Add row" opens a form generated from the table's columns
- **Update:** "Edit" on any row
- **Delete:** "Delete" on any row (with confirmation)
- **Reset data:** restores the selected database to its original dummy data

## API
| Method | Endpoint | Action |
|---|---|---|
| GET | `/api/databases` | List databases, tables and row counts |
| GET | `/api/<db>/<table>` | Read columns and rows |
| POST | `/api/<db>/<table>` | Insert a row |
| PUT | `/api/<db>/<table>/<id>` | Update a row |
| DELETE | `/api/<db>/<table>/<id>` | Delete a row |
| POST | `/api/<db>/reset` | Re-seed a database |

Database and table names are checked against the real schema before use, and all
values are passed as SQL parameters, so the API isn't open to SQL injection.

## Demo video
[`demo-video.mp4`](demo-video.mp4) is a 2-minute recording of the app working: reading, searching, and
creating, updating and deleting rows across all three databases, then reloading to show the changes were saved.
