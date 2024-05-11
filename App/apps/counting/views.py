from flask import Blueprint, render_template, request, redirect, url_for, flash
from apps.app import db
from apps.crud.models import User, Bus
from apps.counting.forms import NewUserForm

counting = Blueprint(
    "counting", __name__, static_folder="static", template_folder="templates"
)


# ユーザーとバスの運行状況を簡易表示
@counting.route("/users")
def users():
    users = db.session.query(User).all()
    bus = db.session.query(Bus).order_by(Bus.id.desc()).first()
    if bus is None:
        at = ""
    else:
        at = bus.created_at.strftime("%H時%M分")
    return render_template("counting/users.html", users=users, bus=bus, at=at)


# ユーザーの新規作成フォーム
@counting.route("/register", methods=["GET", "POST"])
def register_card():
    form = NewUserForm()
    if form.validate_on_submit():
        form_id = request.form.get("radio-id")
        if form_id is None:
            flash("IDを選択してください")
            return redirect(url_for("counting.register_card"))
        if db.session.query(User).filter_by(id=form_id).first():
            user = db.session.query(User).filter_by(id=form_id).first()
            user.username = form.username.data
            user.password = form.password.data
        else:
            user = User(
                id=form_id,
                username=form.username.data,
                password=form.password.data,
            )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("counting.users"))
    users = db.session.query(User).all()
    id_list = [user.id for user in users]
    return render_template("counting/create_user.html", form=form, id_list=id_list)


# M5Stackとの通信.乗車人数を返す
@counting.route("/on", methods=["POST"])
def get_on():
    card_json = request.get_json()
    print("POSTデータ:" + str(card_json))
    # IDが空文字列となるエラーを回避（空文字列はFalseを返す）
    user = None
    if not card_json["id"]:
        pass
    elif db.session.query(User).filter_by(id=card_json["id"]).first():
        user = db.session.query(User).filter_by(id=card_json["id"]).first()
        user.is_on = True
        db.session.add(user)
        db.session.commit()
    else:
        # タグのIDが未登録ならtest,helloを設定して登録する
        user = User(
            id=card_json["id"], username="undefined", password="undefined", is_on=True
        )
        db.session.add(user)
        db.session.commit()
    num_is_on = db.session.query(User).filter_by(is_on=True).count()
    user = db.session.query(User).filter_by(id=card_json["id"]).first()
    user_name = user.username
    return str(num_is_on) + "," + str(user_name)


# M5Stackとの通信.乗車人数を返す
@counting.route("/off", methods=["POST"])
def get_off():
    card_json = request.get_json()
    print("POSTデータ:" + str(card_json))
    if not card_json["id"]:
        pass
    elif db.session.query(User).filter_by(id=card_json["id"]).first():
        user = db.session.query(User).filter_by(id=card_json["id"]).first()
        user.is_on = False
        db.session.add(user)
        db.session.commit()
    else:
        # タグのIDが未登録ならundefinedを設定して登録する
        user = User(
            id=card_json["id"], username="undefined", password="undefined", is_on=False
        )
        db.session.add(user)
        db.session.commit()
    num_is_on = db.session.query(User).filter_by(is_on=True).count()
    user = db.session.query(User).filter_by(id=card_json["id"]).first()
    user_name = user.username
    return str(num_is_on) + "," + str(user_name)
