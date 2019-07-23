import sys
import csv
import random

#Constantes Globales
RUTA_ARCHIVO_TWEETS = "tweets.csv"
RUTA_ARCHIVO_FAVORITOS = "tweets_favoritos.txt"
CADENA_AFIRMACION = "si"
COMANDO_GENERAR = "generar"
COMANDO_TRENDING = "trending"
COMANDO_FAVORITOS = "favoritos"
DELIMITADOR_TWEETS_CSV = "\t"
FIN_DE_ORACION = "fin de oracion"
LISTA_NOMBRE_COMANDOS = [COMANDO_GENERAR, COMANDO_TRENDING, COMANDO_FAVORITOS]

#Main y funciones
def algotweets():
    '''Se encarga de la logica general del manejador de tweets'''
    comando, argumento = leer_comandos()

    if comando == COMANDO_GENERAR:
        usuarios = argumento
        cadenas_markov = leer_archivo_markov(RUTA_ARCHIVO_TWEETS, DELIMITADOR_TWEETS_CSV, usuarios)
        if len(cadenas_markov) == 0:
            print("El usuario que has ingresado es inexistente")
            sys.exit()
        tweet_generado = generar_tweet(cadenas_markov)
        imprimir_tweet(tweet_generado, usuarios)
        pregunta = input("¿Desea agregar a favoritos? [Si/No]: ")
        if pregunta.lower() == CADENA_AFIRMACION:
            agregar_a_favoritos(RUTA_ARCHIVO_FAVORITOS, tweet_generado)


    elif comando == COMANDO_TRENDING:
        cantidad = int(argumento[0])
        hashtags = leer_archivo_hashtags(RUTA_ARCHIVO_TWEETS, DELIMITADOR_TWEETS_CSV)
        imprimir_hashtags(hashtags, cantidad)

    else:
        cantidad = argumento
        try:
            tweets_favoritos = leer_archivo_favoritos(RUTA_ARCHIVO_FAVORITOS)
        except IOError:
            print("No hay tweets favoritos")
            sys.exit()
        imprimir_favoritos(tweets_favoritos, cantidad)
    sys.exit()




def leer_comandos():
    '''Se encarga de leer los comandos ingresados por consola utilizando el modulo sys
       Pre: ---
       Post: Devuelve el comando y el argumento ingresados en caso de ser valido (si
       no se ingreso un argumento este vale None), sino se pide que se ingresen
       de nuevo y luego cortando la ejecuacion
       <comando>:     -Primer argumento del comando pasado por terminal, es una cadena
       <argumento>:   -Segundo argumento hasta N argumentos del comando pasado por terminal, es una lista
    '''
    entrada = sys.argv
    if len(entrada) < 2:
        raise Exception("No le pasaste un parametro")
        sys.exit()
    comando = entrada[1]
    if len(entrada) > 2:
        argumento = entrada[2:]
    else:
        argumento = None
    if es_valido_argumento(comando, argumento):
        return comando, argumento
    print("Comando o Argumento invalidos")
    sys.exit()


def es_valido_argumento(comando, argumento):
    '''Valida si los argumentos cumplen una serie de condiciones devolviendo un booleano
    Pre: Recibe un comando y un argumento que son ingresados por la terminal
    Post: Devuelve True si el comando y argumento son validos y False sino
    '''
    if comando not in LISTA_NOMBRE_COMANDOS:
        return False
    elif comando == COMANDO_TRENDING and(not argumento or not argumento[0].isdigit() or
        len(argumento) != 1):
        return False
    return True


# Generar Tweet

def leer_archivo_markov(ruta, delimitador, usuarios):
    '''Lee el archivo csv una vez, y segun los usuarios solicitados crea un diccionario
    con todas las palabras de los tweets de esos usuarios que adentro contienen
    otro diccionario con las palabras que le sucedieron y su cantidad de veces que
    se repitieron
    Pre: Se le debe pasar la ruta de un archivo csv que este separado por un determinado
    delimitador y opcionalmente una lista con los usuarios solicitados, en caso de no haber
    especificado recibe None
    Post: Devuelve el diccionario mencionado
    '''
    cadenas_markov = {}
    with open(ruta) as archivo_tweets:
        lector_archivo = csv.reader(archivo_tweets,delimiter=delimitador)
        for usuarios_tweets, tweets in lector_archivo:
            if usuarios == None or usuarios_tweets in usuarios:
                palabras = tweets.split(" ")
                generar_cadenas_markov(palabras, cadenas_markov)
        return cadenas_markov



def generar_cadenas_markov(lista_palabras, diccionario):
    '''Recibe una lista de palabras y crea un diccionario con todas las palabras
    que adentro contienen otro diccionario con las palabras que le sucedieron
    y su cantidad de veces que se repitieron
    Pre: Una lista de cadenas
    Post: Devuelve dicho diccionario
    '''
    for i in range(len(lista_palabras)):
        if lista_palabras[i] not in diccionario:
            crear_diccionario_palabras(i, lista_palabras, diccionario)
        else:
            agregar_palabras_diccionario(i, lista_palabras, diccionario)


def crear_diccionario_palabras(i, lista_palabras, diccionario):
        '''Recibe un indice una lista de palabras y un diccionario, y crea un diicionario
        que adentro contienen otro diccionario con la palabra que le procede
        o un fin de oracion en caso de que sea la ultima palabra
        Pre: Un indice, numero natural correspondiente a la longitud de la lista menos uno
        y un diccionario
        Post: Devuelve un diccionario
        '''
        if i < len(lista_palabras)-1:
            diccionario[lista_palabras[i]] = {lista_palabras[i+1]: 1}
        else:
            diccionario[lista_palabras[i]] = {FIN_DE_ORACION: 1}


def agregar_palabras_diccionario(i, lista_palabras, diccionario):
    '''Recibe un indice una lista de palabras y un diccionario con todas las palabras
    que adentro contienen otro diccionario con la palabra que le procedio y agrega
    palabras a ese otro diccionario como claves y su cantidad de veces que se repitieron
    como valor
    Pre: Un indice, numero natural correspondiente a la longitud de la lista menos uno
    y un diccionario ya inicializado
    Post: Devuelve un diccionario de diccionarios con todas las palabras que le sucedieron
    y su cantidad de veces que se repitieron
    '''
    if i < len(lista_palabras)-1:
        diccionario[lista_palabras[i]][lista_palabras[i+1]] = diccionario[lista_palabras[i]].get(lista_palabras[i+1], 0) + 1
    else:
        diccionario[lista_palabras[i]][FIN_DE_ORACION] = diccionario[lista_palabras[i]].get(FIN_DE_ORACION, 0) + 1


def generar_tweet(cadena_markov):
    '''Recibe un diccionario con todas las palabras de los tweets que
    adentro contienen otro diccionario con las palabras que le sucedieron y
    su cantidad de veces que se repitieron y devuelve un tweet pseudo-aleatorio creado
    haciendo una eleccion pesada
    Pre: Un diccionario de diccionarios ya mencionado
    Post: Devuelve un tweet, una cadena de como maximo 280 caracteres
    '''
    tweet = ""
    inicio_oracion = random.choice(list(cadena_markov.keys()))
    caracteres = 0
    palabra_pseudo_aleatoria = inicio_oracion
    while palabra_pseudo_aleatoria != FIN_DE_ORACION:
        caracteres += len(palabra_pseudo_aleatoria) + 1
        if caracteres < 280:
            tweet += palabra_pseudo_aleatoria + " "
        else:
            break
        palabra_pseudo_aleatoria = eleccion_pesada_palabra(cadena_markov[palabra_pseudo_aleatoria])
    return tweet.capitalize().rstrip()


def eleccion_pesada_palabra(diccionario):
    '''Recibe un diccionario con palabras como claves y numeros que representan
    la cantidad de apariciones como valores y devuelve una palabra haciendo
    una eleccion pesada segun la cantidad de apariciones
    Pre: Un diccionario con palabras como claves y numeros naturales como valores
    Post: Devuelve una palabra perteneciente a ese diccionario de la forma ya descripta
    '''
    palabra_aleatoria_pesada = random.choices(list(diccionario.keys()), list(diccionario.values()))[0]
    return palabra_aleatoria_pesada


def imprimir_tweet(tweet, usuarios):
    '''Se encarga de imprimir el tweet generado
    Pre: Recibe un tweet, (una cadena) y opcionalmente una lista con los usuarios ingresados
    Post: Imprime el tweet
    '''
    if usuarios == None:
        imprimir_usuarios = "Todos los usuarios"
    else:
        imprimir_usuarios = str(usuarios).strip("[]")
    print(f"""Generando tweet a partir de: {imprimir_usuarios}...\n\n'''{tweet}'''\n""")


def agregar_a_favoritos(ruta, tweet):
    '''Dada una ruta de donde se desea guardar en un archivo los tweets,
    escribe el archivo si no esta lo crea, escribiendo al final los tweets favoritos
    Pre: Una ruta donde se desea guardar los archivos favoritos
    Post: Guarda el tweet (una cadena) en una linea en el archivo
    '''
    with open(ruta, "a+") as archivo_favoritos:
        archivo_favoritos.write(tweet + "\n")
    print("Tweet agregado a favoritos")



# Trending

def leer_archivo_hashtags(ruta, delimitador):
    '''lee el archivo de tweets una vez, busca hashtags y los guarda en un diccionario
    Pre: Recibe la ruta del archivo tweets.csv
    Post: Devuelve un diccionario con hashtags como claves y su cantidad de
    apariciones como valor
    '''
    hashtags = {}
    with open(ruta) as archivo_tweet:
        lector_archivo = csv.reader(archivo_tweet, delimiter=delimitador)
        for linea in lector_archivo:
            tweet = linea[1]
            palabras = tweet.split(" ")
            for i in range(len(palabras)):
                for letra in palabras[i]:
                    if letra == "#":
                        palabra_sin_puntos = palabras[i].rstrip(",.:")
                        hashtags[palabra_sin_puntos] = hashtags.get(palabra_sin_puntos, 0) + 1
    return hashtags


def imprimir_hashtags(diccionario, cantidad):
    '''Recibe un diccionario y lo imprime
    Pre: Recibe un diccionario siendo sus claves cadenas
    Post: imprime el diccionario
    '''
    lista_hashtags_mas_usados = sorted(diccionario, key=diccionario.get, reverse=True)
    print("Temas mas comunes:")
    for i in range(cantidad):
        print(f"""{lista_hashtags_mas_usados[i]}""")



# Tweets Favoritos

def leer_archivo_favoritos(ruta):
    '''Lee el archivo donde se guardaron los tweets favoritos una vez, y crea una
    lista que tiene como primer elemento el ultimo tweet, asi siguiendo hasta el primer tweet
    Pre: Recibe una ruta donde se guardaron los tweets favoritos
    Post: Devuelve una lista como ya se especifico
    '''
    with open(ruta) as archivo_favoritos:
        tweets_favoritos = []
        for linea in archivo_favoritos:
            tweets_favoritos.append(linea.rstrip("\n"))
        tweets_favoritos.reverse()
    return tweets_favoritos

def imprimir_favoritos(lista, cantidad):
    '''Dado una lista que contiene tweets favoritos y la cantidad que se desea
    imprimir, imprime los tweets favoritos de mas reciente a mas viejo. Si se
    ingresa una cantidad mayor de la que hay imprime todos los tweets favoritos
    Pre: Una lista que tiene como elementos tweets (cadena), siendo
    el tweet mas reciente el primer elemento y el mas lejano el ultimo elemento
    Post: Imprime los tweets favoritos
    '''
    if cantidad == None:
        cantidad = len(lista)
    elif cantidad[0].isdigit():
        if int(cantidad[0]) <= len(lista):
            cantidad = int(cantidad[0])
        else:
            cantidad = len(lista)
    else:
        print("Argumento invalido")
        sys.exit()
    for i in range(cantidad):
        print(lista[i])


algotweets()
