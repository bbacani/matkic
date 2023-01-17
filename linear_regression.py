import numpy as np
from sklearn.linear_model import LinearRegression
import random


def treniraj(srednje_vrijednosti, zadnji_rezultati):
    # treniraj fja bi trebala služiti da se istrenira model koji bude kasnije predviđal rezultat...
    # srednjeVrijednosti je varijabla koja prima srednje vrijednosti zadnjih 4 igri (bez zadnje igre)
    # zadnjiRezultati je varijabla koja prima zadnji broj bodova koji su ucenici ostvarili
    x = np.array(srednje_vrijednosti).reshape((-1, 1))
    y = np.array(zadnji_rezultati)
    model = LinearRegression().fit(x, y)

    return model


def predvidi(zadnji_bodovi, model):
    # predvidi je fja koja vraća predviđene bodove koje bi ucenik trebao ostvariti sljedeci put
    # ako posaljes samo zadnji rezultat za jednog ucenika onda predvida samo za njega
    # ak posaljes vise onda je to array pa dobis za vise njih
    x = np.array(zadnji_bodovi).reshape((-1, 1))
    return model.intercept_ + model.coef_ * x


def vrati_poruku(predvidjeni_bodovi, realni_bodovi):
    # fja prima predvidjeni broj bodova i ostvareni broj bodova te ovisno o ostvarenom broju bodova salje poruku
    pozitivne_poruke = ['Bravo! Samo tako nastavi!', 'Odlično, pucaš prema vrhu!', 'Ubrzo ćeš biti na vrhu ljestvice!',
                        'Svaka čašt, majstore!', 'Pa ti ćeš postati pravi matkić.', 'Ostvaren je izvrstan rezultat.',
                        'Rješavaš zadatke kao od šale!', 'Besprijekorno. Ubrzo ćeš postati matkić!',
                        'Genijalan rezultat!', 'Prelagani zadaci! PRebaci se na sljedeću razinu!']
    srednje_poruke = ['Još samo malo vježbe i vidjet ćeš rezultat!', 'Nije loše! Samo nastavi vježbati!',
                      'Ako želiš postati najbolji, samo vježbaj!']
    negativne_poruke = ['Probaj više vježbati kako bi usavršio ovu razinu.',
                        'Ne smiješ odustati! Probaj više vježbati.', 'Vježbom do savršenstva.',
                        'Nemoj tugovati, uspjet ćeš savladati gradivo.', 'Možda da se vratiš na nižu razinu?',
                        'Samo polako i strpljivo! Tako ćeš postati bolji.']
    if realni_bodovi > predvidjeni_bodovi:
        rand = random.randint(0, len(pozitivne_poruke)-1)
        return pozitivne_poruke[rand]
    elif realni_bodovi == predvidjeni_bodovi or realni_bodovi > predvidjeni_bodovi-8:
        rand = random.randint(0, len(srednje_poruke)-1)
        return srednje_poruke[rand]
    else:
        rand = random.randint(0, len(negativne_poruke)-1)
        return negativne_poruke[rand]
