from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default=None)
    kgs_username = db.Column(db.String(64), index=True, unique=True)
    ayd_member = db.Column(db.Boolean, default=False, index=True)
    eyd_member = db.Column(db.Boolean, default=False, index=True)

    def __repr__(self):
        return '<User {}>'.format(self.kgs_username)


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    tournament = db.Column(db.String(128), index=True)
    date = db.Column(db.DateTime, index=True, default=None)
    round = db.Column(db.Integer, index=True)
    black = db.Column(db.String(64), db.ForeignKey('user.kgs_username'))
    white = db.Column(db.String(64), db.ForeignKey('user.kgs_username'))
    b_win = db.Column(db.Boolean, default=0)
    w_win = db.Column(db.Boolean, default=0)
    ayd_game = db.Column(db.Boolean, default=0, index=True)
    eyd_game = db.Column(db.Boolean, default=0, index=True)

    __tableargs__ = (
        db.UniqueConstraint(
            'tournament',
            'round',
            'black',
            'white',
            name='uniq_game_con'
        ),
    )

    black_player = db.relationship(
        'User',
        backref=db.backref('black', order_by=id),
        primaryjoin="Game.black == User.kgs_username"
    )

    white_player = db.relationship(
        'User',
        backref=db.backref('white', order_by=id),
        primaryjoin="Game.white == User.kgs_username"
    )
