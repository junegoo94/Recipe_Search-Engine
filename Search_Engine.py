import json
import numpy as np
import string

### Open json file
with open('recipes.json', 'r') as f:
    recipes = json.load(f)

# Store recipes only with strings
recipes_lst = []
dic_key = ['title', 'categories', 'ingredients', 'directions']

# Tokenisation
translator_punc = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
translator_digit = str.maketrans(string.digits, ' ' * len(string.digits))
for i in range(len(recipes)):
    ind_recipe = []
    for j in dic_key:
        values = recipes[i].get(j)
        if isinstance(values, list):
            # If the type of value of certain key is a list, remove list
            values = ' '.join([str(e) for e in values])
            punc_dig = values.translate(translator_punc)  # Remove punctuation
            punc_dig = punc_dig.translate(translator_digit)  # Remove digits
            punc_dig = punc_dig.split()  # Split all words
            punc_dig = [s for s in punc_dig if len(s) >= 3]  # Remove tokens which length is less than 3
            punc_dig = [x.lower() for x in punc_dig]  # Replace upper case letters to lower case
            ind_recipe.append(punc_dig)
        elif isinstance(values, type(None)) == False:
            punc_dig = values.translate(translator_punc)  # Remove punctuation
            punc_dig = punc_dig.translate(translator_digit)  # Remove digits
            punc_dig = punc_dig.split()  # Split all words
            punc_dig = [s for s in punc_dig if len(s) >= 3]  # Remove tokens which length is less than 3
            punc_dig = [x.lower() for x in punc_dig]  # Replace upper case letters to lower case
            ind_recipe.append(punc_dig)

        elif isinstance(values, type(None)) == True:
            values = ['none']  # Define none type as 'none'
            ind_recipe.append(values)

    recipes_lst.append(ind_recipe)

### Inverted index
d = {}
for i, recipe in enumerate(recipes_lst):

    for j, key_dic in enumerate(recipe):
        # Allocate scores for each key (title -> 8, categories -> 4, ingredients -> 2, directions -> 1)
        if j == 0: score = 8
        if j == 1: score = 4
        if j == 2: score = 2
        if j == 3: score = 1
        # Store location of each word in dictionary
        for word in key_dic:
            if word not in d:
                d[word] = {}
                d[word][i] = score
            elif word in d:
                if i in d[word].keys():
                    # Add score if there exist identical recipe
                    d[word][i] = d[word].get(i, 0) + score
                elif i not in d[word].keys():
                    d[word][i] = score


### Search function
def search(query, ordering='normal', count=10):
    # Tokenisation for queries
    translator_punc = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    translator_digit = str.maketrans(string.digits, ' ' * len(string.digits))

    if isinstance(query, type(None)) == False:
        punc_dig = query.translate(translator_punc)
        punc_dig = punc_dig.translate(translator_digit)
        punc_dig = punc_dig.split()
        punc_dig = [s for s in punc_dig if len(s) >= 3]
        punc_dig = [x.lower() for x in punc_dig]
        for token in punc_dig:
            if token not in d:
                punc_dig.remove(token)
    # If there is no query to search, return nothing
    if len(punc_dig) == 0:
        return
    #########finding intersection (recipes) of queries
    intersection_recipe = set(d[punc_dig[0]].keys())
    if len(punc_dig) > 1:
        for q in punc_dig[1:]:
            q_recipes = set(d[q].keys())
            intersection_recipe = intersection_recipe.intersection(q_recipes)

    ########## Searching method : 'normal'
    if ordering == 'normal':
        score_lst = []
        for i in intersection_recipe:
            score = 0
            for q in punc_dig:
                score = score + d[q][i]
            # Add rating
            if not (recipes[i].get("rating") is None):
                score = score + recipes[i]['rating']
            elif recipes[i].get("rating") is None:
                score = score + 0
            # Append score and recipe in a list
            score_lst.append([score, i])
        # Rank by a score (from the best score)
        score_rank = sorted(score_lst, reverse=True)
        score_rank = score_rank[0:count]

        for i, j in enumerate(score_rank):
            print(recipes[score_rank[i][1]]['title'])

    ########## Searching method : 'simple'
    if ordering == 'simple':
        score_lst = []
        for k, i in enumerate(intersection_recipe):
            num_ing = len(recipes[i].get('ingredients', []))
            num_direc = len(recipes[i].get('directions', []))
            # Run if both ingresients and directions exist
            if (num_ing > 1) and (num_direc > 1):
                score = num_ing * num_direc
                score_lst.append([score, i])
        # Rank by score (From the smallest score)
        score_rank = sorted(score_lst)
        score_rank = score_rank[:count]
        for i, j in enumerate(score_rank):
            print(recipes[score_rank[i][1]]['title'])

    ########## Searching method : 'healthy'
    if ordering == 'healthy':
        score_lst = []
        for i in intersection_recipe:
            cals = recipes[i].get('calories')  # calories of the recipe
            prot = recipes[i].get('protein')  # protein of the recipe
            fat = recipes[i].get('fat')  # fat of the recipe
            # Run if these three values exist
            if ('calories' in recipes[i]) and ('protein' in recipes[i]) and ('fat' in recipes[i]):
                score = ((1 / 510) * np.abs(cals - 510)) + 2 * ((1 / 18) * np.abs(prot - 18)) + 4 * (
                            (1 / 150) * np.abs(fat - 150))
                score_lst.append([score, i])
        # Rank by score (From the smallest score)
        score_rank = sorted(score_lst)
        score_rank = score_rank[:count]

        for i, j in enumerate(score_rank):
            print(recipes[score_rank[i][1]]['title'])