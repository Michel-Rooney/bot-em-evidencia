import sqlite3
from datetime import datetime

from decouple import config

DB = config('DB', '')


def zera_xp_today(discord_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    c.execute('''
            UPDATE study
            SET xp = 0, updated_at = CURRENT_TIMESTAMP
            WHERE user = (
                SELECT id FROM user WHERE discord_id = ?
            )
            AND DATE(created_at) = ?
        ''', (discord_id, today))

    conn.commit()
    conn.close()

    print('Finish')


if __name__ == '__main__':
    zera_xp_today()
