import re
import unicodedata
import spacy
from os import listdir
from os.path import isfile
from nltk.tokenize import sent_tokenize
import nltk

path_resenas = "/home/link/Escritorio/PLN/Final/musica/"

def ls1(path):
    return [obj for obj in listdir(path) if isfile(path + obj)]

def agrupa(path):
    files = ls1(path)
    yes_files = []
    no_files = []
    for file in files:
        if('yes' in file):
            yes_files.append(file)
        else:
            no_files.append(file)
    return yes_files, no_files

def lee(file_names, origin):
    string_total_reviews = ""
    for file in file_names:
        f = open(origin + file, encoding='latin-1')
        contenido=""
        while(True):
            linea = f.readline()
            if linea !="" and linea !=" " and linea !="\n":
                linea= linea.replace("\n","")
                linea=linea.replace("\t","")
                linea=linea.replace("/","")
                linea=linea.replace("\x86","")
                linea=linea.replace("®","")
                linea=linea.replace("D\'","")
                contenido=contenido+linea
            if not linea:
                break
        f.close()        
        string_total_reviews = string_total_reviews + contenido
    return string_total_reviews

def limpiar(a):
    cadena=a
    cadena.replace("' , '","")
    cadena.replace(", '","")
    cadena.replace("\'","")
    return cadena

def parse_document(document):
    document = re.sub('\n', ' ', document)
    if isinstance(document, str):
        document = document
    elif isinstance(document, str):
        return unicodedata.normalize('NFKD', document).encode('ascii', 'ignore')
    else:
        raise ValueError('Document is not string or unicode!')
    document = document.strip()
    sentences = sent_tokenize(document)
    sentences = [sentence.strip() for sentence in sentences]    
    return sentences

if __name__ == '__main__':
    yes_files, no_files = agrupa(path_resenas)
    yes_string = lee(yes_files, path_resenas)
    no_string = lee(no_files, path_resenas)
    total= limpiar(yes_string+no_string)
    enunciados= parse_document(total)
    nlp=spacy.load('es')
    lista_nominales=[]
    lista_posesion=[]
    
    enunciados_taggeados=[]
    for enunciado in enunciados:
        tag_enunciado=[]
        en=nlp(enunciado)
        for token in en:
            s=(token.text,token.pos_)
            tag_enunciado.append(s)
        enunciados_taggeados.append(tag_enunciado)
    
    grammar = r"""
    NP: {<DET|PROPN\$>?<ADJ>*<NOUN>}
        {<PROPN>+}
    """
    cp=nltk.RegexpParser(grammar)
    for enunciado in enunciados_taggeados:
        x= cp.parse(enunciado) 
        for nominal in x:
            z=limpiar(str(nominal))
            if z[1]=='N' and z[2]=='P':
                z=z.replace('(',"")
                z=z.replace(')',"")
                lista_nominales.append(z)
    
    posesion = r"""
    NP: {<DET|PROPN\$>?<ADJ>*<NOUN>}
        {<PROPN>+}
    CK: {<NP><ADP><NP>}
    """
    cp=nltk.RegexpParser(posesion)
    for enunciado in enunciados_taggeados:
        x= cp.parse(enunciado)
        for posesion in x:
            z=str(posesion)
            if z[1]=='C' and z[2]=='K':
                z=z.replace('(',"")
                z=z.replace(')',"")
                z=z.replace("\n","")
                z=z.replace("  "," ")
                index=z.find("ADP")
                if z[index-2]=='e' or z[index-2]=='E' and z[index-3]=='d' or z[index-3]=='D':    
                    lista_posesion.append(z)
                    
    with open('Frases_Nominales.txt', 'w') as f:
        f.write("FRASES NOMINALES\n")
        for item in lista_nominales:
            f.write("%s\n" % item)
    print('Frases Nominales guardadas en el archivo: Frases_Nominales.txt')
    
    with open('Relaciones_Posesion.txt', 'w') as f:
        f.write("RELACIONES DE POSESION\n")
        for item in lista_posesion:
            f.write("%s\n" % item)
    print('Relaciones de posesión guardadas en el archivo: Relaciones_Posesion.txt')
