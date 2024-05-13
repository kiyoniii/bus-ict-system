from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from apps.app import db
from apps.notice.forms import AuthForm
from apps.crud.models import Bus, User
from datetime import timedelta

notice = Blueprint(
    "notice", __name__, template_folder="templates", static_folder="static"
)


@notice.route("/auth", methods=["GET", "POST"])
def auth():
    form = AuthForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user is not None and user.password == form.password.data:
            # 認証後、セッション変数に格納し、notifyにリダイレクト
            session["username"] = form.username.data
            return redirect(url_for("notice.notify"))
        else:
            # 認証不可の場合、エラー文と共にページを返す
            flash("ユーザ名またはパスワードが間違っています。")
            return redirect(url_for("notice.auth"))
    return render_template("notice/auth.html", form=form)


@notice.route("/noUser", methods=["GET"])
def delete_value():
    session["username"] = "ゲスト"
    return redirect(url_for("notice.notify"))


# 送迎バス運行状況を表示
@notice.route("/notify", methods=["GET"])
def notify():
    current_bus = db.session.query(Bus).order_by(Bus.id.desc()).first()
    username = "ゲスト"
    if "username" in session:
        username = session["username"]
    # レコードが何もない(初期状態)の時は停止中のページを表示する
    if current_bus is None:
        return render_template("notice/inactivate.html", username=username)
    loc = current_bus.location
    ope = current_bus.operation_status
    # 送迎状態でない時
    if ope is False:
        return render_template("notice/inactivate.html", username=username)
    # 送迎状態の時
    else:
        # ゲスト参加の場合はバスの位置情報と到着予想時刻は表示しない
        if username == "ゲスト":
            return render_template("notice/unauth_activate.html")
        user = db.session.query(User).filter_by(username=username).first()
        # バスは送迎中だが降車済みの場合
        if user.is_on is False:
            return render_template("notice/is_off.html", username=username)

        # これ以降はバス送迎中+園児乗車中の場合を指す
        # 前回の所要時間を計算
        id = current_bus.id
        at = current_bus.created_at
        if db.session.query(Bus).filter_by(id=id - 7).first():
            front_at = db.session.query(Bus).filter_by(id=id - 7).first().created_at
            back_at = db.session.query(Bus).filter_by(id=id - 6).first().created_at
            # timedelta型のデータを取得
            cost = back_at - front_at
            # seconds属性しか使えないため、分と秒に変換する作業が必要
            sec = cost.seconds
            est_m, est_s = divmod(sec, 60)
            # 予想時刻を計算
            est_at = at + timedelta(minutes=est_m)
            return render_template(
                "notice/activate.html",
                username=username,
                loc=loc,
                at=at.strftime("%H時%M分"),
                est_at=est_at.strftime("%H時%M分"),
                est_m=est_m,
                est_s=est_s,
            )
        else:
            return render_template(
                "notice/activate.html",
                username=username,
                loc=loc,
                at=at.strftime("%H時%M分"),
                est_at="-",
                est_m="-",
                est_s="-",
            )


# M5Stackとの通信.送迎完了時、乗車中の園児がいればM5Stackに知らせる
@notice.route("/location", methods=["POST"])
def bus_location():
    json_location = request.get_json()
    print(json_location)
    bus = Bus(
        location=json_location["location"],
        operation_status=json_location["operation_status"],
    )
    db.session.add(bus)
    db.session.commit()

    # countingシステムの初期化 is_onを全てFalseにする
    if json_location["location"] == 0:
        user_objects = db.session.query(User).all()
        # コメント外す
        for user_object in user_objects:
            user_object.is_on = False
            db.session.add(user_object)
        db.session.commit()

    # 送迎完了時、is_on=Trueのユーザーがいれば...
    elif json_location["operation_status"] is False:
        is_on_objects = db.session.query(User).filter_by(is_on=True).all()
        if is_on_objects:
            is_on_str = ""
            for obj in is_on_objects:
                is_on_str = is_on_str + "," + obj.username
            return "1" + is_on_str
        else:
            return "0"
    return "0"
