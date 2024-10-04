
import sqlite3
from datetime import datetime, timedelta

from decouple import config

DB = config('DB', '')


def delete_today_study_and_adjust_xp(discord_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # day = datetime.now().strftime('%Y-%m-%d')
    # day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    #
    # # Obter o XP total dos registros de estudo de hoje
    # c.execute('''
    #     SELECT SUM(xp) FROM study
    #     WHERE user = (
    #         SELECT id FROM user WHERE discord_id = ?
    #     )
    #     AND DATE(created_at) = ?
    # ''', (discord_id, day))
    #
    # xp_today = c.fetchone()[0]  # Caso não haja registros, XP de hoje é 0
    # print(xp_today)

    # Subtrair o XP ganho hoje do XP total do usuário
    c.execute('''
        UPDATE user
        SET xp = xp, updated_at = CURRENT_TIMESTAMP
        WHERE id = (
            SELECT id FROM user WHERE discord_id = ?
        )
    ''', (380, discord_id))

    # Deletar os registros de estudo de hoje
    # c.execute('''
    #     DELETE FROM study
    #     WHERE user = (
    #         SELECT id FROM user WHERE discord_id = ?
    #     )
    #     AND DATE(created_at) = ?
    # ''', (discord_id, day))

    # start_time = datetime.combine(
    #     datetime.now() - timedelta(days=1), datetime.min.time()).replace(hour=12).strftime('%Y-%m-%d %H:%M:%S')
    # end_time = datetime.combine(
    #     datetime.now() - timedelta(days=1), datetime.min.time()).replace(hour=15).strftime('%Y-%m-%d %H:%M:%S')
    #
    # c.execute('''
    #     UPDATE study
    #     SET xp = ?, updated_at = CURRENT_TIMESTAMP, start_time = ?, end_time = ?
    #     WHERE user = (
    #         SELECT id FROM user WHERE discord_id = ?
    #     )
    #     AND DATE(created_at) = ?
    # ''', (120, start_time, end_time, discord_id, day))

    conn.commit()
    conn.close()

    print('Finished deleting today\'s study and adjusting XP')


if __name__ == '__main__':
    delete_today_study_and_adjust_xp(1253035647732809770)
