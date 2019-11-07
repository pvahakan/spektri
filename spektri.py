import csv
import matplotlib.pyplot as plt
import numpy
import os


data = False # Onko data ladattu
kuvaaja = False # Onko kuvaaja piirretty
eka_piste = "Anna ensimmäinen piste: "
toka_piste = "Anna toinen piste: "
eka_energia = "Anna ensimmäinen integroitava energiaväli: "
toka_energia = "Anna toinen integroitava energiaväli: "
eka_piikki = "Ensimmäisen intensiteettipiikin pinta-ala: {:.2f}"
toka_piikki = "Toisen intensiteettipiikin pinta-ala: {:.2f}"
virhesyote = "Syöte ei kelpaa. Anna syöte muodossa x1 y1" 


def _kysy_pisteet(kehoite, virhe):
    """
    Kysyy käyttäjältä lukuja ja tarkistaa ne sekä palauttaa kysytyt luvut.
    Apufunktio.
    """
    while True:
        # 2x input välilyönnillä erotettuna samalta riviltä
        syote = input(kehoite)
        if syote == "":
            return None, None
        try:
            x, y = syote.split(" ")
            x = float(x)
            y = float(y)
            return x, y
        except ValueError:
            print(virhesyote)


def _jarjesta_tiedostot(polku):
    """
    Ottaa kansiosta oikeanmuotoiset tiedostot ja järjestää ne
    numerojärjestykseen. Ottaa parametrinä kansion polun.
    Palauttaa järjestetyt tiedostot. Apufunktio.
    """
    tiedostonimet = []

    for tiedosto in os.listdir(polku):
        try:
            nimi, paate = tiedosto.split(".")
            nimi, numero = nimi.split("_")
            if nimi == "measurement" and paate == "txt":
                numero = int(numero)
                tiedostonimet.append([nimi, numero,  paate])
        except ValueError:
            pass

    tiedostonimet.sort()
    # Tallennetaan järjestetyt tiedostonimet tiedostot -listaan
    tiedostot = []
    for i in tiedostonimet:
        nimi = i[0] + "_" + str(i[1]) + "." + i[2]
        tiedostot.append(nimi)

    return tiedostot


def _muokkaa_data(energiat, intensiteetit):
    """
    Muokkaa energiat ja intensiteetit haluttuun muotoon.
    Apufunktio.
    """
    earvot = [] # Energiat
    isummat = [] # Energioita vastaavien intensiteettien summat
    try:
        for energia in energiat[0]:
            earvot.append(float(energia))
        for energia in range(len(earvot)):
            lista = [] # Apulista
            # Intensiteetit = [ [] , [] .. ]
            for mittauskerta in range(len(intensiteetit)):
                # Tiettyä mittauskertaa ja energiaa vastaava intensiteetti
                lista.append(float(intensiteetit[mittauskerta][energia]))
            isummat.append(sum(lista))
        return earvot, isummat

    # Jos ei olekkaan oikeita tiedostoja
    except IndexError:
        pass


def lataa_data(polku):
    """
    Lukee datan argumenttina annetusta kansiosta ja palauttaa 
    kaksi taulukkoa. Toisessa energiat ja toisessa ko. 
    energioita vastaavien intensiteettien summat.
    """
    energiat = [] # Jokaisen tiedoston energiat omana alkiona
    intensiteetit = [] # Jokaisen tiedoston intensiteetit omana alkiona

    tiedostot = _jarjesta_tiedostot(polku) # Etsitään oikeat tiedostot

    for datatiedosto in tiedostot:
        # Yksittäisen tiedoston arvot
        tiedoston_energia = []
        tiedoston_intensiteetti = []
        try:
            with open(os.path.join(polku, datatiedosto), newline="") as tiedosto:
                lukija = csv.reader(tiedosto, delimiter=" ")
                for rivi in lukija:
                    tiedoston_energia.append(float(rivi[0]))
                    tiedoston_intensiteetti.append(float(rivi[1]))
                # joka tiedoston energia-osa omana alkiona
                energiat.append(tiedoston_energia)  
            # joka tiedoston intensiteetti-osa omana alkiona
            intensiteetit.append(tiedoston_intensiteetti)
        except IOError:
            pass

    print("Ladattiin", len(tiedostot), "tiedostoa.")
    return energiat, intensiteetit


def piirra_data(x, y):
    """
    Piirtää argumenttina annetun datan kuvaajaksi.
    """
    plt.clf() # Tyhjennetään kuvaaja
    plt.xlabel("Sidosenergia (eV)")
    plt.ylabel("Intensiteetti (elektronien määrä)")
    plt.title("Argonin spektri")
    plt.ion()  # Ohjelman suoritus jatkuu
    plt.plot(x, y)
    plt.draw()


def _laske_parametrit(x1, y1, x2, y2):
    """
    Ottaa argumenttina kahden pisteen koordinaatit. Palauttaa pisteiden
    kautta kulkevan suoran kulmakertoimen ja vakiotermin. Apufunktio.
    """
    if x1 == None or y1 == None or x2 == None or y2 == None:
        print("Arvot pysyy samana")
        return 0, 0 
    try:
        k = (y2 - y1) / (x2 - x1)
        b = (x2 * y1 - x1 * y2) / (x2 - x1)
        return k, b
    except ZeroDivisionError:
        print("Suoraa ei voitu muodostaa.")

def _laske_pisteet_suoralla(kulmakerroin, vakiotermi, x_pisteet):
    """
    Ottaa argumentteina suoran kulmakertoimen, vakiotermin sekä listan 
    x-akselin pisteitä. Palauttaa listana x-akselin pisteitä vastaavat 
    suoran arvot. Apufunktio.
    """
    y_arvot = []

    for x_arvo in x_pisteet:
        y_piste = kulmakerroin * x_arvo + vakiotermi
        y_arvot.append(y_piste)

    return y_arvot


def poista_tausta(energiat, intensiteetit):
    """
    Kysyy käyttäjältä kaksi pistettä ja sovittaa näihin pisteisiin suoran.
    Vähentää kyseistä suoraa vastaavat arvot ohjelman muistissa olevasta
    spektristä.
    """
    korjatut_intensiteetit = []

    x1, y1 = _kysy_pisteet(eka_piste, virhesyote)
    x2, y2 = _kysy_pisteet(toka_piste, virhesyote)
    kulmakerroin, vakio = _laske_parametrit(x1, y1, x2, y2)
    y_arvot = _laske_pisteet_suoralla(kulmakerroin, vakio, energiat)
    for i in range(len(intensiteetit)):
        korjatut_intensiteetit.append(intensiteetit[i] - y_arvot[i])

    return korjatut_intensiteetit


def laske_intensiteetit(x, y):
    """
    Ottaa argumenttina mittausdatan. Kysyy käyttäjältä
    kaksi energiaväliä ja laskee intensiteetit numeerisesti
    integroimalla käyttäen puolisuunnikassääntöä.
    Palauttaa intensiteettien suhteen.
    """
    y1 = []
    y2 = []
    energia_11, energia_12 = _kysy_pisteet(eka_energia, virhesyote)
    if energia_11 < x[0] or energia_12 > x[len(x)-1]:
        print("Annettu energiaväli ei ole mittausalueella.")
    else:
        for energia in x:
            if energia >= energia_11 and energia <= energia_12:
                y1.append(y[x.index(energia)])

        piikki_1 = round(numpy.trapz(y1, dx=0.01), 6)
        print(eka_piikki.format(piikki_1))

        energia_21, energia_22 = _kysy_pisteet(toka_energia, virhesyote)
        if energia_21 < x[0] or energia_22 > x[len(x)-1]:
            print("Annettu energiaväli ei ole mittausalueella.")
        else:
            for energia2 in x:
                if energia2 >= energia_21 and energia2 <= energia_22:
                    y2.append(y[x.index(energia2)])

            piikki_2 = round(numpy.trapz(y2, dx=0.01), 6)
            if piikki_2 == 0:
                pass
            else:
                print(toka_piikki.format(piikki_2))
                return piikki_1 / piikki_2


def tallenna_kuvaaja():
    """
    Tallentaa kuvaajan, joka on piirrettynä ohjelman muistiin.
    """
    if data == False:
        print("Dataa ei ladattu")
    elif kuvaaja == False:
        print("Ohjelman muistissa ei ole kuvaajaa")
    else:
        print("Kuva tallennetaan .png -tiedostona")
        nimi = input("Anna tiedostonimi ilman päätettä ")
        if len(nimi.split(".")) >= 2:
            print("Ei tiedostopäätteitä.")
            print("Kuvaajaa ei tallennettu.")
        else:
            plt.savefig(nimi + ".png")



if __name__ == "__main__":
    print("Tämä ohjelma lataa datan tiedostosta ja piirtää siitä kuvaajan.")
    print("Käytössä on seuraavat valinnat:")
    print(" (l) Lataa data tiedostosta")
    print(" (p) Piirrä kuvaaja muistissa olevasta datasta")
    print(" (t) Poista lineaarinen tausta")
    print(" (i) Laske piikkien intensiteetit")
    print(" (s) Tallenna kuvaaja")
    print(" (q) Lopeta")

    try:
        while True:
            valinta = input(" >> ")
            try:
                if valinta == "l":
                    poloku = input("Anna hakemistopolku: ")
                    if os.path.exists(poloku):
                        e, i = lataa_data(poloku)
                        energia, intensiteetti = _muokkaa_data(e, i)
                        data = True
                    else:
                        print("Hakemistopolkua ei löydetty")

                elif valinta == "p":
                    piirra_data(energia, intensiteetti)
                    plt.show()
                    kuvaaja = True

                elif valinta == "t":
                    intensiteetti = poista_tausta(energia, intensiteetti)
                    print("Piirrä kuvaaja painamalla (p)")

                elif valinta == "i":
                    isuhde = laske_intensiteetit(energia, intensiteetti)
                    if isuhde == None:
                        print("Suhdetta ei voida laskea")
                    else:
                        print("Intensiteettipiikkien suhde: ", isuhde)

                elif valinta == "s":
                    tallenna_kuvaaja()

                elif valinta == "q":
                    print("Kiitos hei!")
                    break

                else:
                    print("Mahdolliset valinnat ovat:")
                    print("(l), (p), (t), (i), (s), (q)")

            except NameError:
                print("Dataa ei ladattu")

            except TypeError:
                pass

    # Näppäimistökeskeytykset otetaan kiinni vaikka
    # oltaisiin if-rakenteen sisällä
    except EOFError:
        print("\nKiitos hei!")
    except KeyboardInterrupt:
        print("\nKiitos hei!")

   
