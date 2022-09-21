import regex
import pandas as pd
import numpy as np
import emoji
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# conversation = 'C:/Users/hp/PycharmProjects\WhataAppChatAnalysis/WhatsApp Chat with Aloha.txt'
def date_time(s):
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -'
    result = regex.match(pattern, s)
    if result:
        return True
    return False


def find_author(s):
    s = s.split(":")
    if len(s) == 2:
        return True
    else:
        return False


def getDatapoint(line):
    splitline = line.split(' - ')
    dateTime = splitline[0]
    date, time = dateTime.split(", ")
    message = " ".join(splitline[1:])
    if find_author(message):
        splitmessage = message.split(": ")
        author = splitmessage[0]
        message = " ".join(splitmessage[1:])
    else:
        author = None
    return date, time, author, message


data = []
conversation = 'C:/Users/hp/PycharmProjects/WhataAppChatAnalysis/WhatsApp Chat with Sue.txt'
with open(conversation, encoding="utf-8") as fp:
    infer_datetime_format = True
    fp.readline()
    messageBuffer = []
    date, time, author = None, None, None
    while True:
        line = fp.readline()
        if not line:
            break
        line = line.strip()
        if date_time(line):
            if len(messageBuffer) > 0:
                infer_datetime_format = True
                data.append([date, time, author, ' '.join(messageBuffer)])
            messageBuffer.clear()
            date, time, author, message = getDatapoint(line)
            messageBuffer.append(message)
        else:
            messageBuffer.append(line)

df = pd.DataFrame(data, columns=["Date", 'Time', 'Author', 'Message'])
df['Date'] = pd.to_datetime(df['Date'])
total_messages = df.shape[0]
# print(df.info())
# print(total_messages)
# print(df.tail(20))
# print(df.Author.unique())
media_messages = df[df["Message"] == '<Media omitted']


# print(media_messages)

def split_count(text):
    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.EMOJI_DATA for char in word):
            emoji_list.append(word)
    return emoji_list


df['emoji'] = df["Message"].apply(split_count)

emojis = sum(df['emoji'].str.len())
print(emojis)
URLPATTERN = r'(https?://\S+)'
df['urlcount'] = df.Message.apply(lambda x: regex.findall(URLPATTERN, x)).str.len()
links = np.sum(df.urlcount)

# print("chats between ALOHA AND JOHN")
# print("Total Messages: ", total_messages)
# print("Number of Media Shared", media_messages)
# print("Number of Emojis shared", emojis)
# print("Number of Links Shared", links)
media_messages_df = df[df['Message'] == '<media ommitted']
messages_df = df.drop(media_messages_df.index)
messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s: len(s))
messages_df['Word_Count'] = messages_df['Message'].apply(lambda s: len(s.split(' ')))
messages_df["MessageCount"] = 1

total_emojis_list = list(set([a for b in messages_df.emoji for a in b]))
total_emojis = len(total_emojis_list)

total_emojis_list = list([a for b in messages_df.emoji for a in b])
emoji_dict = dict(Counter(total_emojis_list))
emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
# for i in emoji_dict:
#     print(i)

emoji_df = pd.DataFrame(emoji_dict, columns=['emoji', 'count'])
import plotly.express as px

fig = px.pie(emoji_df, values='count', names='emoji')
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()

text = " ".join(review for review in messages_df.Message)
print("There are {} words in all the  messages.".format(len(text)))
stopwords = set(STOPWORDS)
# Generate word cloud Image
wordcloud = WordCloud(stopwords=stopwords, background_color="White").generate(text)
#Display the generated image
# the matplotlib way
plt.figure(figsize=(10,5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()