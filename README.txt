
Tilastokerääjän tarkoitus on helpottaa Mikroväylän palvelun laskemien Yliopiston kirjaston tilojen kävijämäärien
keräämistä yhteen tiedostoon, joka muuten pitää tehdä pitkänä prosessina käsin. Tilastokerääjä yhdistää itsensä
Mikroväylän palveluun (BMA-api, api.bma.fi), ja hakee sen kautta tietonsa HTTP-kutsuina.

---------------------------------------------

Ennen käyttöä:
Tilastokerääjäsovellus tarvitsee toimiakseen Python-asennuksen, jonka voi asentaa esim. Software Centeristä. 
Sovellusta tehdessä käytössä oli Python 3.11.4.

Lisäksi pitää ladata tarvittavat koodikirjastot:
Koodikirjastojen asennus onnistuu ajamalla tilastokeraaja-kansion "installDependencies"-komentokuvake. 
Tämä noutaa tarvittavat asiat misc\requirements.txt-tiedoston perusteella.

(jos vahingossa ajaa installDependencies-komentokuvakkeen uudelleen, ei haittaa, lataus suorittaa itsensä 
vain tarvittaessa)

---------------------------------------------

Käyttö:

Tuplaklikkaa Tilastokerääjä-pikakuvaketta, tai lähdekoodikansion index.pyw -Python-tiedostoa.

Tämä avaa käyttöliittymän, johon syötetään alku- ja loppupäivämäärät ja -ajat, sekä sijainti/sijainnit,
joista tietoa haetaan. Halutessaan voi hakea vaikka kaikista neljästä (Kaisa, Kumpula, Viikki, Terkko).

Päivämäärien tulee olla muotoa PP.KK.VVVV, esim 01.02.2024, 12.10.2015 tms.
Aikojen tulee olla muotoa TT.MM, esim. 03:45, 15:30, 22:05 tms.

Järjestelmä näyttää virheen, mikäli jokin tieto on väärässä muodossa, tai sijaintia ei ole valittu.

Sovelluksessa pystyy myös valitsemaan tulostiedoston kohdekansion painamalla käyttöliittymän tiedostopolkunappia.
Oletuksena on käyttäjän Ladatut tiedostot -kansio ("Downloads"). Valinnan voi peruuttaa Peruuta-napilla ("Cancel")

Kun kaikki on paikallaan, paina Hae, jolloin haku alkaa. Haussa voi kestää jokin hetki, ja varsinkin Kaisan haussa
voi kestää uuvuttava aika. Jos hakee Kaisasta tilastoja kuukaudelta kerralla tai suuremmaltakin aikaväliltä,
kannattaa keittää kupponen kahvia tms. koska siinä voi kestää muutamakin minuutti.

Muut kampukset ovat suht. nopeita.

Haku kirjoittaa tuloksensa jo olemassa olevaan, tai luomaansa "tulokset.xlsx"-excel-tiedostoon, joka on samaa
muotoilua kuin P-aseman kävijätilasto-excelit. 
Näin ollen tulokset voi kopioida suoraan. Tietoja liittäessä, kannattaa käyttää "Paste values"-liittämisvaihtoehtoa,
niin mikään tyylittely ja formatointi ei ylikirjoitu, vaan vain itse kävijäuvut.

Tulostiedosto luodaan oletuksena käyttäjän Ladatut tiedostot -kansioon, tai käyttäjän erikseen valitsemaan kansioon.

Jo olemassa olevan tulostiedoston ohjelma ylitsekirjoittaa, joten tallenna tarvittaessa muualle.

Sovellus suljetaan perinteisesti X-napista.

- ML