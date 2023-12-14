import random
anges = []
#anges = those who buy the gift
#add all names here and then add "m" for men and "f" for women and the end of each name
#secondly, add a two-digit number at the end: The persons that are not supposed to be assigned to each other, get the same number!
#if a person can be assigned to everyone, this person will be the only one with their specific number
protégés = []
#protégés = those who receive the gift
#add the exact same list as 'anges' here (with m/f + number)
vowels = ["A", "E", "I", "O", "U"]
b = "merci de participer aux anges gardiens." #thanks for taking part in secret santa
c = "Tu es l'ange gardien" #You are assigned to
d = "Merci de lui préparer un petit cadeau. On se réjouit de te retrouver bientôt !" #Thanks for preparing a little gift. We are looking forward to seeing you again soon!

for i in anges:
    j = random.randint(0, (len(protégés)-1))
    while protégés[j] == i or protégés[j][-2:] == i[-2:]: #making sure no one is assigned to oneself or person with same number
        j = random.randint(0, (len(protégés)-1))
    if protégés[j] != i and protégés[j][-2:] != i[-2:]:
        protégés[j] = protégés[j][:-2]
        i = i[:-2]
        if i[-1] == "m":
            i = i[:-1]
            a = f"Cher {i},\n" #French: in order to distinguish between men and women
        else:
            i = i[:-1]
            a = f"Chère {i},\n"
    if protégés[j].startswith(tuple(vowels)):
        with open(f"{i}.txt", "a") as f:
            print(f"{a}{b} {c} d'{protégés[j][:-1]}.\n{d}", file=f)
    else:
        with open(f"{i}.txt", "a") as f:
            print(f"{a}{b} {c} de {protégés[j][:-1]}.\n{d}", file=f)
    protégés.pop(j)




