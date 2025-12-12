from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# 初始化 Flask 應用
app = Flask(__name__)

# session 密鑰，用於登入狀態管理。生產環境應替換為隨機字串。
app.config['SECRET_KEY'] = 'please-change-this-key'

# 設定資料庫 URI，使用 SQLite 儲存資料
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///behavior.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()


class Article(db.Model):
    """文章模型，用於存放行為科學與 AI 應用的教學內容
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self) -> str:
        return f'<Article {self.id} {self.title}>'


class Habit(db.Model):
    """習慣模型，用於儲存習慣名稱、描述與完成狀態
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f'<Habit {self.id} {self.name}>'


#@app.before_first_request
def initialize_database() -> None:
    """在伺服器第一次接收請求前建立資料表。
    """
    db.create_all()

#
@app.route('/')
@app.route('/')
def index():
    """首頁: 列出所有文章。
    """
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template('index.html', articles=articles)

#defndex():
   #"""首頁：列出所有文章。
  ##"""
    #articles = Article.query.order_by(Article.id.desc()).all()
   ##return render_template('index.html', articles=articles)


@app.route('/habit', methods=['GET', 'POST'])

def habit():
    """習慣追蹤頁。可新增習慣與切換完成狀態。
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
if name:
            new_habit = Habit(name=name, description=description)
            db.session.add(new_habit)
            db.session.commit()
        return redirect(url_for('habit'))
    habits = Habit.query.all()
    return render_template('habit.html', habits=habits)


@app.route('/habit/complete/<int:habit_id>')
def complete_habit(habit_id: int):
    """切換習慣完成狀態。
    """
    habit = Habit.query.get_or_404(habit_id)
    habit.completed = not habit.completed
    db.session.commit()
    return redirect(url_for('habit'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """後台登入與管理介面。
    """
    # 登入後顯示管理面板
    if session.get('logged_in'):
        habits = Habit.query.order_by(Habit.id.desc()).all()
        articles = Article.query.order_by(Article.id.desc()).all()
        return render_template('admin.html', habits=habits, articles=articles)
    # 提交登入
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'adminpass':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        # 密碼錯誤
        return render_template('login.html', error='密碼錯誤')
    # 初始載入登入頁
    return render_template('login.html')


@app.route('/admin/add_article', methods=['POST'])
def add_article():
    """後台新增文章。
    """
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    title = request.form.get('title')
    content = request.form.get('content')
    if title and content:
        article = Article(title=title, content=content)
        db.session.add(article)
        db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/add_habit', methods=['POST'])
def add_habit_admin():
    """後台新增習慣。
    """
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    name = request.form.get('name')
    description = request.form.get('description')
    if name:
        habit = Habit(name=name, description=description)
        db.session.add(habit)
        db.session.commit()
    return redirect(url_for('admin'))


@app.route('/logout')
def logout():
    """登出後台。
    """
    session.pop('logged_in', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    # 在本地端開啟 debug 模式便於開發
    app.run(debug=True)
