"""
Скрипт для телеграм бота
Бирет данные из таблиц с предсказание и таблицы с генерацией высчитывая метрики
Строит график матрицы путанности и процент правильно предсказанных значение

ПО команде /start предлагает варианты вывода
"""


import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден! Передай его через переменные окружения Docker")

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'dbname': 'sensors',
    'user': 'admin',
    'password': 'admin'
}

def get_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT p.id, p.final_prediction, d.diagnosis
        FROM predictions_table_2 p
        JOIN diagnosis_2 d ON p.id = d.id;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Метрики", callback_data="metrics")],
        [InlineKeyboardButton("Confusion Matrix", callback_data="cmatrix")],
        [InlineKeyboardButton("Pie Chart", callback_data="pie")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    df = get_data()
    y_true = df["diagnosis"]
    y_pred = df["final_prediction"]

    if query.data == "metrics":
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

        text = (
            f"Метрики модели:\n\n"
            f"Accuracy: {acc:.3f}\n"
            f"Precision: {prec:.3f}\n"
            f"Recall: {rec:.3f}\n"
            f"F1-score: {f1:.3f}"
        )
        await query.edit_message_text(text=text)

    elif query.data == "cmatrix":
        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Pred 0", "Pred 1"], yticklabels=["True 0", "True 1"])
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.title("Confusion Matrix")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        await query.message.reply_photo(photo=buf)

    elif query.data == "pie":
        correct = (y_true == y_pred).sum()
        incorrect = (y_true != y_pred).sum()

        plt.figure(figsize=(5, 5))
        plt.pie([correct, incorrect], labels=["Правильно", "Неправильно"], autopct="%1.1f%%", startangle=90, colors=["#4CAF50", "#F44336"])
        plt.title("Доля классификаций")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        await query.message.reply_photo(photo=buf)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()
