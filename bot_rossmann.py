import requests
import pandas as pd
import json
import re
import telebot
import time
import asyncio
import os, sys
from requests.exceptions import ConnectionError, ReadTimeout

# https://api.telegram.org/bot5905766004:AAGZumQfjsQUZG_QPZtVhoxee6AOuxICEM4/setWebhook?url=

TOKEN = '5905766004:AAGZumQfjsQUZG_QPZtVhoxee6AOuxICEM4'

bot = telebot.TeleBot(TOKEN)

def load_dataset(store_id):
    # loading test dataset
    df10 = pd.read_csv('data/test.csv')
    df_store_raw = pd.read_csv('data/store.csv')

    # merge test dataset + store
    df_test = pd.merge(df10, df_store_raw, how='left', on = 'Store')

    # choose store for prediction
    df_test = df_test[df_test['Store'] == store_id]

    if not df_test.empty:
        # remove closed days
        df_test = df_test[df_test['Open'] != 0]
        df_test = df_test[~df_test['Open'].isnull()]
        df_test = df_test.drop('Id', axis = 1)

        # convert dataframe to json
        data = json.dumps(df_test.to_dict(orient='records'))

    else:
        data = 'error'

    return data

def predict(data):
    # API call
    url = 'https://teste-deploy-render-bc3n.onrender.com/rossmann/predict'

    header = {'Content-type': 'application/json'} # indica qual tipo de dado esta recebendo
    data = data

    r = requests.post( url, data = data, headers = header)
    # metodo POST serve para enviar o dado

    print('Status code {}'.format(r.status_code))
    # para indicar se a request é válida
    # retorno de 200 significa que está tudo okay

    d1 = pd.DataFrame(r.json(), columns=r.json()[0].keys())

    return d1


@bot.message_handler(regexp='[0-9]+')
def responder_2(message):

    store_id = re.findall('[0-9]+',message.text)

    store_id = int(store_id[0])

    #loading data
    data = load_dataset(store_id)

    if data != 'error':

        #prediction
        d1 = predict(data)
        # calcution
        d2 = d1[['store', 'prediction']].groupby('store').sum().reset_index()
        
        # send message
        msg = 'ID Loja {} irá vender R${:,.2f} nas próximas 6 semanas.'.format(
            d2['store'].values[0], d2['prediction'].values[0] )

        bot.send_message(message.chat.id, msg)

        text = """
        Digite outro ID Loja, caso queira outra previsão de vendas.

Para voltar, digite Sair."""

        bot.send_message(message.chat.id, text)

    else:
        bot.send_message(message.chat.id, 'Loja não disponível. Favor, digite outro Loja ID.')

    # bot.reply_to(message, store_id)



def verificar(message):
    return True

@bot.message_handler(func=verificar)
def responder(message):
    text = """
    Olá, Bem vindo ao ROSSMANN BOT.
Aqui é possivel obter as previsões de vendas nas próximas 6 semanas.

Favor, digite o número da loja para obter a previsão de vendas."""

    bot.reply_to(message, text)

bot.launch({
  webhook:{
    host:0.0.0.0,
    domain: "https://api.telegram.org/bot5905766004:AAGZumQfjsQUZG_QPZtVhoxee6AOuxICEM4/setWebhook?url=https://telebot-rossmann.onrender.com",
  	port:5000}})

# bot.infinity_polling(timeout=10, long_polling_timeout = 5)

# try:
#     bot.infinity_polling(timeout=10, long_polling_timeout=5)
# except (ConnectionError, ReadTimeout) as e:
#     sys.stdout.flush()
#     os.execv(sys.argv[0], sys.argv)
# else:
#     bot.infinity_polling(timeout=10, long_polling_timeout=5)

# bot.polling()
# bot.set_webhook()

# if __name__ == '__main__':
#     # bot.polling(none_stop=True, interval=0)
#     # bot.infinity_polling(timeout=10, long_polling_timeout = 5) 
#     while True:
#         try:
#             bot.polling(non_stop=True, interval=0)
#         except Exception as e:
#             print(e)
#             time.sleep(5)
#             continue

