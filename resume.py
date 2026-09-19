from assistant import lire_pdf, resumer

texte = lire_pdf("notes.pdf")
print(resumer(texte))
