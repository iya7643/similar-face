import io
import os
import uuid

import psycopg2
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from flask import Flask, render_template, request, redirect, url_for, flash, session

import repositories

app = Flask(__name__)
app.secret_key = 'suzuki.hisashi@rococo.co.jp'

face_repository = repositories.Face()

mtcnn = MTCNN(image_size=1024, margin=0)
resnet = InceptionResnetV1(pretrained='vggface2').eval()


@app.get('/')
def index():
    faces = face_repository.all()
    return render_template("index.html", faces=faces)


@app.get('/search')
def search():
    name = request.args.get('face_name')
    session['face_name'] = name
    if name is None or name == '':
        return redirect(url_for('index'))

    faces = face_repository.search_by_name(name)
    return render_template("index.html", faces=faces, is_similar=False)


@app.get('/similar')
def similar():
    name = request.args.get('face_name')
    session['face_name'] = name
    if name is None or name == '':
        return redirect(url_for('index'))

    faces = face_repository.similar_by_name(name)
    return render_template("index.html", faces=faces, is_similar=True)


@app.post('/')
def store():
    face_name = request.form.get('face_name')
    if face_name is None or face_name == '':
        flash("氏名を入力してください。")
        return redirect(url_for('index'))

    file = request.files['face_image']
    if not file:
        flash("画像を選択してください。")
        return redirect(url_for('index'))

    try:
        file_data = file.read()
        img = Image.open(io.BytesIO(file_data))
        if img.mode != "RGB":
            img = img.convert("RGB")

        embedding = str(
            resnet(mtcnn(img).unsqueeze(0)).detach().numpy().tolist()
        )[1:-1]

        _, file_extension = os.path.splitext(file.filename)

        face_repository.store({
            "id": str(uuid.uuid4()),
            "name": face_name,
            "image": psycopg2.Binary(file_data),
            "image_extension": file_extension,
            "embedding": embedding
        })
    except Exception as e:
        flash("画像から顔を検出できませんでした。")
        return redirect(url_for('index'))

    flash("顔画像を登録しました。")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
