import numpy as np
from sklearn.linear_model import LinearRegression


def treniraj(srednje_vrijednosti, zadnji_rezultati):
    # treniraj fja bi trebala služiti da se istrenira model koji bude kasnije predviđal rezultat...
    # srednjeVrijednosti je varijabla koja prima srednje vrijednosti zadnjih 4 igri (bez zadnje igre)
    # zadnjiRezultati je varijabla koja prima zadnji broj bodova koji su ucenici ostvarili
    x = np.array(srednje_vrijednosti).reshape((-1, 1))
    y = np.array(zadnji_rezultati)
    model = LinearRegression().fit(srednje_vrijednosti, zadnji_rezultati)

    return model


def predvidi(zadnji_bodovi, model):
    # predvidi je fja koja vraća predviđene bodove koje bi ucenik trebao ostvariti sljedeci put
    # ako posaljes samo zadnji rezultat za jednog ucenika onda predvida samo za njega
    # ak posaljes vise onda je to array pa dobis za vise njih
    x = np.array(zadnji_bodovi).reshape((-1, 1))
    return model.intercept_ + model.coef_ * x
