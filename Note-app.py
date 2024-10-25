import sqlite3
from datetime import datetime
from enum import Enum

db_filename = "notes.db"


class Message(Enum):
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    LIST = "list"
    QUIT = "quit"
    BACK = "back"


def initialize_db():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE NOT NULL,
        text TEXT NOT NULL,
        created_time TEXT NOT NULL,
        updated_time TEXT NOT NULL
    )
    ''')
    conn.commit()
    return conn


def note_exists(conn, title):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM notes WHERE title = ? OR id = ?', (title, title))
    return cursor.fetchone() is not None


def insert_or_update_note(conn, title, text, new_title=None):
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if note_exists(conn, title):
            new_title = new_title or title
            cursor.execute('''
                UPDATE notes 
                SET text = ?, updated_time = ?, title = ?
                WHERE title = ? OR id = ?
            ''', (text, current_time, new_title, title, title))
            print(f"Note '{title}' updated successfully.")
        else:
            cursor.execute('''
                INSERT INTO notes (title, text, created_time, updated_time) 
                VALUES (?, ?, ?, ?)
            ''', (title, text, current_time, current_time))
            print(f"Note '{title}' added successfully.")
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Database error: {e}")


def delete_note(conn, title):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE title = ? OR id = ?', (title, title))
    conn.commit()
    print(f"Note '{title}' deleted successfully.")


def get_note_text(conn, title):
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM notes WHERE title = ? OR id = ?', (title, title))
    result = cursor.fetchone()
    return result[0] if result else None

def get_note_title(conn, title):
    cursor = conn.cursor()
    cursor.execute('SELECT title FROM notes WHERE title = ? OR id = ?', (title, title))
    result = cursor.fetchone()
    return result[0] if result else None


def load_notes(conn, sort_type):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes')
    notes = cursor.fetchall()

    sort_key = {
        'id': lambda x: x[0],
        'create time': lambda x: x[3],
        'update time': lambda x: x[4]
    }.get(sort_type, lambda x: x[0])

    for note in sorted(notes, key=sort_key):
        note_id, title, text, created_time, updated_time = note
        print(
            f"ID: {note_id}\nTitle: {title}\nText: {text}\nCreated Time: {created_time}\nUpdated Time: {updated_time}")
        print("-" * 30)


def create_note_flow(conn):
    while True:
        title = input("Please write title for your note: ")
        if title == Message.BACK.value:
            break
        if note_exists(conn, title):
            print(f"Note '{title}' already exists.")
            continue
        text = input("Please write text for your note: ")
        if text == Message.BACK.value:
            break
        insert_or_update_note(conn, title, text)
        break


def edit_note_flow(conn):
    while True:
        title = input("Please write title or ID of the note you want to edit: ")
        if title == Message.BACK.value:
            break
        if not note_exists(conn, title):
            print(f"Note '{title}' does not exist.")
            continue

        edit_title = input("Enter new title (or type 'skip' to keep current): ")
        if edit_title == Message.BACK.value:
            break
        elif edit_title == 'skip':
            edit_title = get_note_title(conn, title)
        elif note_exists(conn, edit_title):
            print(f"Note '{edit_title}' already exists.")
            continue

        text = input("Enter new text (or type 'skip' to keep current): ")
        if text == Message.BACK.value:
            break
        elif text == 'skip':
            text = get_note_text(conn, title)

        insert_or_update_note(conn, title, text, edit_title)
        break


def delete_note_flow(conn):
    while True:
        title = input("Please write title or ID of the note you want to delete: ")
        if title == Message.BACK.value:
            break
        if not note_exists(conn, title):
            print(f"Note '{title}' does not exist.")
            continue
        delete_note(conn, title)
        break


def list_notes_flow(conn):
    while True:
        sort_type = input("Type of sorting: id, create time, or update time: ")
        if sort_type in {'id', 'create time', 'update time'}:
            load_notes(conn, sort_type)
            break
        else:
            print(f"Sorting '{sort_type}' is not valid.")


def main():
    conn = initialize_db()
    try:
        while True:
            message = input("create - edit - delete - list - quit (or 'back' to return): ")
            if message == Message.CREATE.value:
                create_note_flow(conn)
            elif message == Message.EDIT.value:
                edit_note_flow(conn)
            elif message == Message.DELETE.value:
                delete_note_flow(conn)
            elif message == Message.LIST.value:
                list_notes_flow(conn)
            elif message == Message.QUIT.value:
                break
            else:
                print("Invalid input.")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
