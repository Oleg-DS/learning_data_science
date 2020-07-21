
# -*- coding: utf-8 -*-

import telebot
import config
import dbworker
import wbdata
from datetime import datetime
# import pandas as pd
import numpy as np
# from tabulate import tabulate


bot = telebot.TeleBot(config.token)

flag = None
year = None
country = None


def info_getter(fl, yr, cnt=None):
    yr = int(yr)
    d_date = datetime(yr, 1, 1)
    df_gdp = wbdata.get_dataframe({'NY.GDP.MKTP.PP.CD': 'GDP, PPP, $B'}, data_date=d_date)

    index_to_drop = df_gdp.index[:47]
    df_gdp_c = df_gdp.drop(index_to_drop)

    df_gdp_c = df_gdp_c.fillna({'GDP, PPP, $B': 0})
    df_gdp_cs = df_gdp_c.sort_values(['GDP, PPP, $B'], ascending=False)

    df_gdp_cs['GDP, PPP, $B'] = round(df_gdp_cs['GDP, PPP, $B'] / 1000000000).apply(lambda x: int(x))
    df_gdp_cs['GDP, PPP, $B'] = df_gdp_cs['GDP, PPP, $B'].apply(lambda x: '{0:,}'.format(x).replace(',', ' '))

    if fl == 'country':
        ind = np.where(df_gdp_cs.index == cnt)
        pos = ind[0][0] + 1
        gdp = df_gdp_cs.loc[cnt]['GDP, PPP, $B']
        print(cnt, '\nPosition in the World in ', yr, ': ', pos, '\nGPD, PPP: ', gdp, ' $B', sep='')

    if fl == 'top':
        print('Top ten countries in the World by GDP, PPP in ', yr, ':', sep='')
        print(df_gdp_cs.head(10).to_string(header=True))


# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_START.value)
    # state = dbworker.get_current_state(message.chat.id)
    # Под "остальным" понимаем состояние "0" - начало диалога
    bot.send_message(message.chat.id, "Greetings! I'm a \"know-something-about-gdp\" bot! :) \n"
                                      "I know info about countries' GPD (PPP) in 1990-2019.."
                                      "\n"
                                      "You should specify if you want to know info about: \n"
                                      "- what were the top ten countries by their GDP (PPP) in a particular year \n"
                                      "or \n"
                                      "- what position a particular country held in a given year \n"
                                      "\n"
                                      "Type /info to know what I can do for you.\n"
                                      "Type /commands to list the available commands.\n"
                                      "Type /reset to discard previous selections and start again.")


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Let's start from scratch.\n"
                                      "You should specify if you want to know info about: \n"
                                      "- what were the top ten countries by their GDP (PPP) in a particular year \n"
                                      "or \n"
                                      "- what position a particular country held in a given year \n"
                                      "\n"
                                      "Type /info to know what I can do for you.\n"
                                      "Type /commands to list the available commands.\n")
    dbworker.set_state(message.chat.id, config.States.S_START.value)


# По команде /info будем показывать подробную информацию о возможностях бота
@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id, "Info method is used to show you what I am capable of.\n"
                                      "I could provide you with some statistics on the countries' GDP (PPP).\n"
                                      "First you should select if you want data about top ten countries "
                                      "in a particular year, or about position a specified country held "
                                      "in a given year. \n"
                                      "Then it's time to specify what year you are interested in.\n"
                                      "And if you choose to look for the data for a specific country, "
                                      "you should provide its name. \n"
                                      "Type /reset to start anew.")
    bot.send_message(message.chat.id, "There's a number of commands you can use here. \n"
                                      "Type /commands to get the list of available functions.\n"
                                      "Type /reset to start anew.")

@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "/reset - is used to discard previous selections and start anew.\n"
                                      "/start - is used to start a new dialogue from the very beginning.\n"
                                      "/info - is used to know what i can do for you (there's a tree of commands)\n"
                                      "/commands - If you got here, you know what it is used for.\n"
                                      # "/listregions - is used to list regions covered by statistics.\n"
                                      # "/listcountries - is used to list countries covered by statistics.\n"
                                      # "/listfields - is used to list fields available in statistics")


@bot.message_handler(commands=["listregions"])
def cmd_listregions(message):
    x = stat()['Country']
    bot.send_message(message.chat.id, ", ".join(i for i in list(x[:8]) if i != ''))


@bot.message_handler(commands=["listcountries"])
def cmd_listcountries(message):
    x = stat()['Country'][8:220]
    bot.send_message(message.chat.id, ', '.join([e+'\n' if i%6 == 5 else e for i,e in enumerate(x)]).replace('\n,', ',\n'))


@bot.message_handler(commands=["listfields"])
def cmd_listfields(message):
    x = list(stat()[['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths',
                     'TotalRecovered', 'ActiveCases', 'SeriousCritical']].columns)
    bot.send_message(message.chat.id, ", ".join(x))


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_DAY.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def get_day(message):
    dbworker.del_state(str(message.chat.id)+'day') # Если в базе когда-то был день, удалим (мы же новый пишем)
    if message.text.lower().strip() == '/yesterday':
        # day = 1
        bot.send_message(message.chat.id, "Ok, we've specified the date of statistics. It's time to go further. \n"
                                          "Do you want to know things about /regions or /countries?\n"
                                          "You could also type /info to know more about me.\n"
                                          "Type /reset to start anew.")
        dbworker.set_state(str(message.chat.id)+'day', 'yesterday') #запишем день в базу
        dbworker.set_state(message.chat.id, config.States.S_COUNTRY_OR_REGION.value)
    elif message.text.lower().strip() == '/today':
        # day = 0
        bot.send_message(message.chat.id, "Ok, we've specified the date for statistics. It's time to go further. \n"
                                          "Do you want to know things about /regions or /countries?\n"
                                          "You could also type /info to know more about me.\n"
                                          "Type /reset to start anew.")

        dbworker.set_state(str(message.chat.id) + 'day', 'today')  # запишем день в базу
        dbworker.set_state(message.chat.id, config.States.S_COUNTRY_OR_REGION.value)
    else:
        bot.send_message(message.chat.id, "Seems like you've already got acquainted with me.\n"
                                          "Now you gotta specify the date for statistics.\n"
                                          "I have information for /yesterday and /today \n"
                                          "To recollect what we are doing now type /info.\n"
                                          "Type /reset to start anew.")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_COUNTRY_OR_REGION.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def country_or_region(message):
    dbworker.del_state(str(message.chat.id) + 'country') # Если в базе когда-то был выбор стран, удалим (мы же новый пишем)
    if message.text.lower().strip() == '/countries':
        # country = 0
        bot.send_message(message.chat.id, "Ok, you want to get statistics by country. \n"
                                          "Enter the list of countries delimited with a comma or just a single country.\n"
                                          "Type /listcountries to get the list of available fields.\n"
                                          "You could also type /info to recollect what we are doing now.\n"
                                          "Type /reset to start anew.")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_COUNTRY_OR_REGION.value)
        dbworker.set_property(str(message.chat.id)+'country', 'countries')  #запишем выбор стран в базу
    elif message.text.lower().strip() == '/regions':
        # country = 1
        bot.send_message(message.chat.id, "Ok, you want to get statistics by region. \n"
                                          "Enter the list of regions delimited with a comma or just a single region.\n"
                                          "Type /listregions to get the list of available fields.\n"
                                          "You could also type /info to recollect what we are doing now.\n"
                                          "Type /reset to start anew.")

        dbworker.set_state(message.chat.id, config.States.S_ENTER_COUNTRY_OR_REGION.value)
        dbworker.set_property(str(message.chat.id) + 'country', 'regions') #запишем выбор регионов в базу

    else:
        bot.send_message(message.chat.id, "Something has gone wrong! Type either countries or regions.\n"
                                          "Type /info to recollect what we are doing now.\n"
                                          "Type /reset to start anew.")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_COUNTRY_OR_REGION.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def enter_country_or_region(message):
    # global countries, country
    dbworker.del_state(str(message.chat.id) + 'countries')  # Если в базе когда-то был выбор списка стран, удалим (мы же новый пишем)
    countries = [x.strip() for x in re.split(',', message.text)]
    country = dbworker.get_current_state(str(message.chat.id)+'country')

    bot.send_message(message.chat.id, 'Thank you, I\'m checkin\' your info.')
    x = stat()['Country']
    if country.strip() == 'regions':
        lst = [i for i in list(x[:8]) if i != '']
    else:
        lst = [i for i in x[8:220]]
    # bot.send_message(message.chat.id,', '.join(lst))
    errors = [i for i in countries if i not in lst]

    if errors == []:
        if countries != []:
            bot.send_message(message.chat.id, "Ok, Now you gotta specify the information you need. \n"
                                              "Enter the list of fields\n"
                                              "Type /listfields to get the list of available fields.\n"
                                              "You could type /info to recollect what we are doing now.\n"
                                              "Type /reset to start anew.")
            dbworker.set_state(str(message.chat.id)+'countries', ', '.join(countries))
            dbworker.set_state(message.chat.id, config.States.S_ENTER_FIELD_LIST.value)
        else:
            bot.send_message(message.chat.id, "Something has gone wrong! Enter the list of countries/regions properly")
    else:
        bot.send_message(message.chat.id, "There\'s a number of countries/regions with typos or something that\'s not in our list.\n"
                                          "Here they are:" + ", ".join(errors)+"\n"
                                          "To get lists of available regions/countries use /listcountries or /listregions")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_FIELD_LIST.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def enter_field_list(message):
    # global fields
    fields = re.findall(r'\w+', message.text)
    bot.send_message(message.chat.id, 'Thank you, I\'m checkin\' your info.')

    lst = list(stat()[['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths',
                       'TotalRecovered', 'ActiveCases', 'SeriousCritical']].columns)
    t = dbworker.get_current_state(str(message.chat.id) + 'day')
    if dbworker.get_current_state(str(message.chat.id)+'day').strip() == 'today':
        day = 0
    elif dbworker.get_current_state(str(message.chat.id)+'day').strip() == 'yesterday':
        day = 1
    else:
        pass
    # country = dbworker.get_current_state(str(message.chat.id) + 'country')
    countries = dbworker.get_current_state(str(message.chat.id) + 'countries').split(', ')

    errors = [i for i in fields if i not in lst]
    # print(errors)
    if errors == []:
        if fields != []:
            dbworker.set_state(message.chat.id, config.States.S_START.value)
            df = stat(day)
            for_sending = df[df.Country.isin(countries)][['Country', *fields]]
            dbworker.del_state(str(message.chat.id) + 'day')
            dbworker.del_state(str(message.chat.id) + 'country')
            dbworker.del_state(str(message.chat.id) + 'countries')
            bot.send_message(message.chat.id, tabulate(for_sending, headers=for_sending.columns, tablefmt="pipe"))
        else:
            bot.send_message(message.chat.id, "Something has gone wrong! Enter the list of fields properly")

    else:
        bot.send_message(message.chat.id,
                         "There\'s a number of fields with typos or something that\'s not in our list.\n"
                         "Here they are:" + ", ".join(errors) + "\n"
                         "To get lists of available fields use /listfields")


@bot.message_handler(func=lambda message: message.text not in ('/reset', '/info', '/start', '/commands',
                                                              '/listregions', '/listregions',
                                                              '/listfields'))
def cmd_sample_message(message):
    bot.send_message(message.chat.id, "Hey there, I'm coronabot!\n"
                                      "I'm not that smart, sorry :(\n"
                                      "But I guess you want some statistics on COVID-19.\n"
                                      "That's what I can help you with!.\n"
                                      "If so, type /start and let's get some. \n"
                                      "Type /info to know what i can do for you.\n"
                                      "Type /commands to list available commands :).")
    bot.send_photo(message.chat.id, pict[randint(0, 5)])


if __name__ == "__main__":
    bot.infinity_polling()
