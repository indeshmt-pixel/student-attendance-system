import os, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
BASE_DIR=os.path.dirname(os.path.abspath(__file__)); DB_PATH=os.path.join(BASE_DIR,'attendance.db')
app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY','change-this-secret-key')
def db():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
def init_db():
 c=db(); c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,roll_no TEXT UNIQUE NOT NULL,course TEXT DEFAULT '',semester TEXT DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER NOT NULL,date TEXT NOT NULL,subject TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('Present','Absent')),created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,UNIQUE(student_id,date,subject));''')
 if not c.execute("SELECT id FROM users WHERE username='admin'").fetchone(): c.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",('admin',generate_password_hash('admin123')))
 c.commit(); c.close()
def login_required(f):
 @wraps(f)
 def w(*a,**k): return f(*a,**k) if 'user_id' in session else redirect(url_for('login'))
 return w
@app.route('/')
def index(): return redirect(url_for('dashboard' if 'user_id' in session else 'login'))
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=request.form.get('username','').strip(); p=request.form.get('password',''); c=db(); user=c.execute('SELECT * FROM users WHERE username=?',(u,)).fetchone(); c.close()
  if user and check_password_hash(user['password_hash'],p): session.clear(); session['user_id']=user['id']; session['username']=u; return redirect(url_for('dashboard'))
  flash('Invalid username or password.','error')
 return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))
@app.route('/dashboard')
@login_required
def dashboard():
 c=db(); total=c.execute('SELECT COUNT(*) n FROM students').fetchone()['n']; today=c.execute("SELECT COUNT(*) n FROM attendance WHERE date=date('now','localtime')").fetchone()['n']; present=c.execute("SELECT COUNT(*) n FROM attendance WHERE date=date('now','localtime') AND status='Present'").fetchone()['n']; absent=c.execute("SELECT COUNT(*) n FROM attendance WHERE date=date('now','localtime') AND status='Absent'").fetchone()['n']; recent=c.execute('SELECT a.*,s.name,s.roll_no FROM attendance a JOIN students s ON s.id=a.student_id ORDER BY a.id DESC LIMIT 8').fetchall(); c.close(); return render_template('dashboard.html',total=total,today=today,present=present,absent=absent,recent=recent)
@app.route('/students',methods=['GET','POST'])
@login_required
def students():
 c=db()
 if request.method=='POST':
  try:
   c.execute('INSERT INTO students(name,roll_no,course,semester) VALUES(?,?,?,?)',(request.form.get('name','').strip(),request.form.get('roll_no','').strip(),request.form.get('course','').strip(),request.form.get('semester','').strip())); c.commit(); flash('Student added successfully.','success')
  except sqlite3.IntegrityError: flash('This roll number already exists.','error')
 q=request.args.get('q','').strip(); rows=c.execute('SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ? OR course LIKE ? ORDER BY id DESC',(f'%{q}%',f'%{q}%',f'%{q}%')).fetchall() if q else c.execute('SELECT * FROM students ORDER BY id DESC').fetchall(); c.close(); return render_template('students.html',students=rows,q=q)
@app.post('/students/<int:i>/delete')
@login_required
def delete_student(i): c=db(); c.execute('DELETE FROM students WHERE id=?',(i,)); c.commit(); c.close(); flash('Student deleted.','success'); return redirect(url_for('students'))
@app.route('/attendance',methods=['GET','POST'])
@login_required
def attendance():
 c=db()
 if request.method=='POST':
  try: c.execute('INSERT INTO attendance(student_id,date,subject,status) VALUES(?,?,?,?)',(request.form.get('student_id'),request.form.get('date'),request.form.get('subject','').strip(),request.form.get('status','Present'))); c.commit(); flash('Attendance saved.','success')
  except sqlite3.IntegrityError: flash('Attendance already exists for this student, date and subject.','error')
 ss=c.execute('SELECT * FROM students ORDER BY name').fetchall(); rr=c.execute('SELECT a.*,s.name,s.roll_no FROM attendance a JOIN students s ON s.id=a.student_id ORDER BY a.date DESC,a.id DESC LIMIT 100').fetchall(); c.close(); return render_template('attendance.html',students=ss,records=rr)
@app.post('/attendance/<int:i>/toggle')
@login_required
def toggle(i):
    c = db()
    r = c.execute(
        'SELECT status FROM attendance WHERE id=?',
        (i,)
    ).fetchone()

    if r:
        new_status = 'Absent' if r['status'] == 'Present' else 'Present'
        c.execute(
            'UPDATE attendance SET status=? WHERE id=?',
            (new_status, i)
        )
        c.commit()

    c.close()
    return redirect(request.referrer or url_for('attendance'))
@app.post('/attendance/<int:i>/delete')
@login_required
def delete_attendance(i): c=db(); c.execute('DELETE FROM attendance WHERE id=?',(i,)); c.commit(); c.close(); flash('Attendance deleted.','success'); return redirect(request.referrer or url_for('attendance'))
@app.route('/reports')
@login_required
def reports():
 q=request.args.get('q','').strip(); status=request.args.get('status',''); date=request.args.get('date',''); sql='SELECT a.*,s.name,s.roll_no,s.course FROM attendance a JOIN students s ON s.id=a.student_id WHERE 1=1'; p=[]
 if q: sql+=' AND (s.name LIKE ? OR s.roll_no LIKE ? OR a.subject LIKE ?)'; p += [f'%{q}%']*3
 if status in ('Present','Absent'): sql+=' AND a.status=?'; p.append(status)
 if date: sql+=' AND a.date=?'; p.append(date)
 sql+=' ORDER BY a.date DESC,a.id DESC'; c=db(); rows=c.execute(sql,p).fetchall(); c.close(); return render_template('reports.html',records=rows,q=q,status=status,date=date)
@app.route('/password',methods=['GET','POST'])
@login_required
def password():
 if request.method=='POST':
  cur=request.form.get('current_password',''); new=request.form.get('new_password',''); con=request.form.get('confirm_password',''); c=db(); u=c.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone()
  if not check_password_hash(u['password_hash'],cur): flash('Current password is incorrect.','error')
  elif len(new)<6: flash('New password must contain at least 6 characters.','error')
  elif new!=con: flash('New passwords do not match.','error')
  else: c.execute('UPDATE users SET password_hash=? WHERE id=?',(generate_password_hash(new),u['id'])); c.commit(); flash('Password changed successfully.','success')
  c.close()
 return render_template('password.html')
@app.get('/health')
def health(): return jsonify(status='ok')
init_db()
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
