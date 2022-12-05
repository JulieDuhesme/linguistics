import random
anges = []
#anges = those who buy the gift
#add all names here and then add "m" for men and "f" for women and the end of each name
#secondly, add a number at the end: The persons that are not supposed to be assigned to each other, get the same number!
#if a person can be assigned to everyone, this person will be the only one with their specific number
protégés = []
#protégés = those who receive the gift
#add the exact same list as 'anges' here (with m/f + number)
vowels = ["A", "E", "I", "O", "U"]
b = "merci de participer aux anges gardiens" #thanks for taking part in secret santa
c = "Tu es l'ange gardien" #You are assigned to
d = "Merci de préparer un petit cadeau. On se réjouit de te retrouver bientôt!" #Thanks for preparing a little gift. We are looking forward to seeing you again soon!

for i in noms:
    j = random.randint(0, (len(protégés)-1))
    while protégés[j] == i or protégés[j][-1] == i[-1]:
        j = random.randint(0, (len(protégés)-1))
    if protégés[j] != i and protégés[j][-1] != i[-1]:
        protégés[j] = protégés[j][:-2]
        i = i[:-1]
        if i[-1] == "m":
            i = i[:-1]
            a = f"Cher {i},\n"
        else:
            i = i[:-1]
            a = f"Chère {i},\n"
    if protégés[j].startswith(tuple(vowels)):
        print (f"{a}{b} {c} d'{protégés[j]}.\n{d}")
    else:
        print (f"{a}{b} {c} de {protégés[j]}.\n{d}")
    protégés.pop(j)


