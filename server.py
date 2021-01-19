from flask import Flask
from flask_login import LoginManager
from user import get_user

import view

lm = LoginManager()

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    app.add_url_rule("/", view_func=view.home_page)
    app.add_url_rule("/signUp", view_func=view.signUp_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=view.login_page, methods=["GET", "POST"])
    app.add_url_rule("/main", view_func=view.main_page, methods=["GET", "POST"])
    app.add_url_rule("/logout/<value>", view_func=view.logout_page, methods=["GET", "POST"])
    app.add_url_rule("/adminRanks", view_func=view.admin_Ranks, methods=["GET", "POST"])
    app.add_url_rule("/regularRanks", view_func=view.regular_Ranks, methods=["GET", "POST"])
    app.add_url_rule("/profile/<id>", view_func=view.profile, methods=["GET", "POST"])
    app.add_url_rule("/ask/<id>", view_func=view.ask, methods=["GET", "POST"])
    app.add_url_rule("/answer/<id>", view_func=view.answer, methods=["GET", "POST"])
    app.add_url_rule("/submit/<sender_id>/<receiver_id>/<entry_id>", view_func=view.submit, methods=["GET", "POST"])
    app.add_url_rule("/delete/<entry_id>/<privilege>/<id>", view_func=view.delete_entry, methods=["GET", "POST"])
    app.add_url_rule("/change_name/<user_id>", view_func=view.change_name, methods=["GET", "POST"])
    app.add_url_rule("/change_surname/<user_id>", view_func=view.change_surname, methods=["GET", "POST"])
    app.add_url_rule("/change_email/<user_id>", view_func=view.change_email, methods=["GET", "POST"])
    app.add_url_rule("/change_phone/<user_id>", view_func=view.change_phone, methods=["GET", "POST"])
    app.add_url_rule("/delete_user/<user_id>/<privilege>", view_func=view.delete_user, methods=["GET", "POST"])
    app.add_url_rule("/add_image/<user_id>", view_func=view.add_image, methods=["GET", "POST"])

    lm.init_app(app)
    lm.login_view = "login_page"
    return app


if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)