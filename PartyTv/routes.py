from PartyTv import app, database, bcrypt
from flask import render_template, request, flash, redirect, url_for
from PartyTv.forms import FormCriarConta, FormLogin, FormEditarPerfil
from PartyTv.models import Usuario, Filmes
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
import secrets
import os


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criar_conta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrardados)
            flash(f'Login feito com sucesso no e-mail {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no login E-mail ou senha incorretos!', 'alert-danger')
    if form_criar_conta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senhabc = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuario(username=form_criar_conta.username.data, email=form_criar_conta.email.data,
                          senha=senhabc)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso no E-mail {form_criar_conta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criar_conta=form_criar_conta)


@app.route('/filmes')
@login_required
def filmes():
    lista_filmes = Filmes.query.all()
    return render_template('filmes.html', filmes=lista_filmes)


@app.route('/usuarios')
@login_required
def usuarios():
    us = Usuario.query.all()
    return render_template('usuarios.html', usuarios=us)


@app.route('/recentes')
@login_required
def recentes():
    lista_filmes = []
    for filmes_assistidos in current_user.filmes_assistidos.split(';'):
        filme_assistido = Filmes.query.filter_by(nome=filmes_assistidos).first()
        lista_filmes.append(filme_assistido)
    return render_template('recentes.html', filmes=lista_filmes)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso!', 'alert-success')
    return redirect(url_for('home'))


@app.route('/lancamentos')
@login_required
def lancamentos():
    filmess = Filmes.query.all()
    lista = []
    ultimo_filme = len(filmess)
    for c in range(1, 11):
        lista.append(filmess[ultimo_filme - c])
    return render_template('lancamentos.html', filmes=lista)


@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')



def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extencao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extencao
    caminho_completo = os.path.join(app.root_path, 'static/fotos', nome_arquivo)
    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo



@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(imagem=form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        database.session.commit()
        flash('Perfil atualizado com sucesso!', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    return render_template('editarperfil.html', form=form)


@app.route('/filme/<filme_id>')
@login_required
def exibir_filme(filme_id):
    filme = Filmes.query.get(filme_id)
    return render_template('exibirfilme.html', filme=filme)


@app.route('/recentes/adicionar/<id_filme>')
@login_required
def recentes_adicionar(id_filme):
    filme = Filmes.query.get(id_filme)
    if current_user.filmes_assistidos != 'nenhum filmes assistido':
        lista = []
        for filmess in current_user.filmes_assistidos.split(';'):
            lista.append(filmess)
        lista.append(filme.nome)
        current_user.filmes_assistidos = ';'.join(lista)
        database.session.commit()
    else:
        lista = [filme.nome]
        current_user.filmes_assistidos = ';'.join(lista)
        database.session.commit()
    flash(f'Filme {filme.nome} adicionado com sucesso!', 'alert-success')
    return redirect(url_for('recentes'))
