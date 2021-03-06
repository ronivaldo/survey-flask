#import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request
import pandas as pd

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

def fix_telefone(tel):
    telefone = ''.join(i for i in tel if i.isdigit())
    if telefone:
        while len(telefone) < len('85987654321'):
            telefone = telefone[:2] + '9' + telefone[2:]
    return telefone

telefones = []
def load_telefones():
    global telefones
    f = open('telefones.txt', 'r', encoding='utf-8')
    for line in f.readlines():
        telefone = fix_telefone(line)
        if telefone:
            telefones.append(telefone)

projetos = []
def load_projetos():
    global projetos
    f = open('projetos.txt', 'r')
    for line in f.readlines():
        projetos.append(line.strip())

def ja_votou(telefone):
    df = pd.read_csv('votacao.csv')
    if len(df[df['telefone'] == int(telefone)]) > 0:
        return True
    return False


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    global projetos
    if projetos == []:
        load_telefones()
        load_projetos()
    return redirect("/form")

@app.route("/form", methods=["GET"])
def get_form():
    global projetos
    if projetos == []:
        load_telefones()
        load_projetos()
    return render_template("form.html", projects=projetos)

@app.route("/form", methods=["POST"])
def post_form():

    telefone = request.form.get("telefone")
    telefone = fix_telefone(telefone)
    if telefone == "":
        return render_template("error.html", message=f"Preencha o Telefone. Apenas telefones cadastrados nos ingressos do Arduino Day podem ser utilizados.")

    if telefone not in telefones:
        return render_template("error.html", message=f"Telefone {telefone} n??o encontrado no Sympla. Apenas telefones cadastrados nos ingressos do Arduino Day podem ser utilizados.")

    if ja_votou(telefone):
        return render_template("error.html", message=f"Telefone {telefone} j?? votou. Apenas ?? permitido um voto por telefone cadastrado.")


    projeto = request.form.get("projeto")
    if projeto == "" or projeto is None:
        return render_template("error.html", message=f"Escolha um projeto.")

    if projeto not in projetos:
        return render_template("error.html", message=f"Projeto {projeto} n??o encontrado nos projetos cadastrados.")



    csvF = open("votacao.csv", "a")
    writer = csv.writer(csvF)
    writer.writerow([telefone, projeto.strip()])
    csvF.close()

    return render_template("success.html", message=f"Voto no Projeto {projeto} realizado com sucesso.")

@app.route("/sheet", methods=["GET"])
def get_sheet():
    return tableAppend("")

def tableAppend(success):
    df = pd.read_csv('votacao.csv')
    df['projeto'].value_counts()

    classificados = df['projeto'].value_counts().to_dict()
    return render_template("sheet.html", classificados=classificados,message=success)


if __name__ == '__main__':
    app.run(debug=True)

