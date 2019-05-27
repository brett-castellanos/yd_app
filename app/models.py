from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    kgs_username = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<User {}>'.format(self.kgs_username)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament = db.Column(db.String(128), index=True)
    round = db.Column(db.Integer, index=True)
    black = db.Column(db.String(64), db.ForeignKey('user.kgs_username'))
    white = db.Column(db.String(64), db.ForeignKey('user.kgs_username'))
    b_win = db.Column(db.Boolean, default=0)
    w_win = db.Column(db.Boolean, default=0)
    yd_game = db.Column(db.Boolean, default=0, index=True)

    black_player = db.relationship(
        'User',
        backref=db.backref('black', order_by=id),
        primaryjoin="Game.black == User.kgs_username"
    )
