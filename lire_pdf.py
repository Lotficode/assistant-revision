from pypdf import PdfReader

lecteur = PdfReader("notes.pdf")

texte = ""

for page in lecteur.pages:
    texte = texte + page.extract_text()

print(texte)