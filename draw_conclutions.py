import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Функция для загрузки данных из базы данных
def load_data():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM purchases", conn)
    conn.close()
    return df

# Функция для создания дашборда
def create_dashboard(df):
    # Преобразуем столбец amount_spent в числовой формат
    df['amount_spent'] = pd.to_numeric(df['amount_spent'], errors='coerce')

    # Общая сумма затрат за период
    total_spent = df['amount_spent'].sum()

    # Группируем данные по типу покупки и суммируем затраты
    grouped = df.groupby('purchase_type')['amount_spent'].sum().reset_index()

    # Создаем PDF для дашборда
    with PdfPages('dashboard.pdf') as pdf:
        # Страница 1: Общая сумма затрат и круговая диаграмма
        plt.figure(figsize=(10, 6))
        plt.suptitle('Дашборд затрат')

        plt.subplot(1, 2, 1)
        plt.text(0.5, 0.5, f'Всего потрачено за период: {total_spent:.2f}', horizontalalignment='center', verticalalignment='center', fontsize=12)
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.pie(grouped['amount_spent'], labels=grouped['purchase_type'], autopct='%1.1f%%', startangle=140)
        plt.title('Распределение затрат по категориям')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        pdf.savefig()
        plt.close()

        # Страницы 2+: Список всех затрат с возможностью листать страницы
        rows_per_page = 20
        num_pages = (len(df) // rows_per_page) + 1

        for page in range(num_pages):
            start_row = page * rows_per_page
            end_row = start_row + rows_per_page

            plt.figure(figsize=(10, 6))
            plt.suptitle('Список всех затрат')

            table = plt.table(cellText=df.iloc[start_row:end_row].values,
                              colLabels=df.columns,
                              cellLoc='center',
                              loc='center')

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.2)

            plt.axis('off')
            pdf.savefig()
            plt.close()

if __name__ == '__main__':
    df = load_data()
    create_dashboard(df)