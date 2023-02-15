from collections import defaultdict
import re
from langdetect import detect
import unicodedata
from nltk.tokenize import RegexpTokenizer
from gensim.parsing.preprocessing import strip_punctuation



# get rid of emoji (faster method)
def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)


# preprocess messages 
def preprocessDocs(docs):
    
    # Remove emoji and reference to users/channels/groups
    docs = [re.sub(r'@[a-zA-Z0-9]+', '', deEmojify(doc)) for doc in docs]

    # Split the documents into tokens.
    tokenizer = RegexpTokenizer(r'\w+')
    for idx in range(len(docs)):
        docs[idx] = docs[idx].lower()  # Convert to lowercase.
        docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words.

    # Normalize Unicode String and convert to lowercase
    docs = [[unicodedata.normalize('NFKD', token).lower() for token in doc] for doc in docs]

    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]

    # Remove words that are only one or two characters.
    docs = [[token for token in doc if len(token) > 2] for doc in docs]

    # Strip punctuation
    docs = [[strip_punctuation(token) for token in doc] for doc in docs]
    
    # join tokens in a string 
    text = [' '.join(doc) for doc in docs]

    return text


# detect the language used in a channel
def detect_language(channel):
    messages = channel['text_messages']
    messages = [messages[key]['message'] for key in messages]
    messages = preprocessDocs(messages)

    dict_lang = defaultdict(int)
    for message in messages:
        if len(message) >= 15:
    
            try:
                lan = detect(message)
                dict_lang[lan] +=1
            except:             
                pass
                
    target_lan = ''
    max_counter = 0
    for lan in dict_lang:
        if dict_lang[lan] > max_counter and dict_lang[lan] > len(messages)/2:
            target_lan = lan
            max_counter = dict_lang[lan]

    return target_lan