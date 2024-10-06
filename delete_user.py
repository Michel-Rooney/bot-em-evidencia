import sqlite3

from decouple import config

DB = config('DB', '')


def delete_user(discord_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    user = c.execute('''
        SELECT * FROM user WHERE discord_id = ?
    ''', (discord_id,)).fetchall()

    study = c.execute('''
        SELECT user FROM study
        WHERE user = (
            SELECT id FROM user WHERE discord_id = ?
        )
    ''', (discord_id,)).fetchall()

    print(user)
    print(study)

    c.execute('''
            DELETE FROM study
            WHERE user = (
                SELECT id FROM user WHERE discord_id = ?
            )
        ''', (discord_id,))

    c.execute('''
            DELETE FROM user WHERE discord_id = ?
        ''', (discord_id,))

    conn.commit()
    conn.close()

    print('Finish')


if __name__ == '__main__':
    delete_user(830530156048285716)
