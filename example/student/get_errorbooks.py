# 以下代码参考: https://github.com/RICHARDCJ249/zhixue_errorbook

from zhixuewang import login_student
import jinja2
import os
import datetime
from zhixuewang.account import load_account
import subprocess


WKHTMLTOPDF_PATH = r'wkhtmltopdf.exe' # wkhtmltopdf 地址
if not os.path.exists("wkhtmltopdf.exe"):
    print("请在release上下载wkhtmltopdf.exe后放到本目录")

# PDF参数
PRARMETER_PDF = '--page-size "B5" --margin-top "0.25in" --margin-right "0.25in" --margin-bottom "0.25in" --margin-left "0.3in" --encoding "UTF-8" --no-outline --footer-center "·[page]·"'


class FullModel():
    def __init__(self, name, subjectName, examName, rank, errorbook):
        self.name = name
        self.subjectName = subjectName
        self.examName = examName
        self.rank = rank
        self.errorbooks = errorbook

def fullTemplate(model):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
    tep = env.get_template("errorbook_templates.html")
    return tep.render(model=model)

def htmlToPdf(file_name, subject):
    name = f"{subject.name}-{datetime.datetime.now().strftime('%Y-%m-%d')}-错题本.pdf"
    command = f'{WKHTMLTOPDF_PATH} {PRARMETER_PDF} {file_name} {name}'
    subprocess.run(command, shell=True)

def clean(subjects):
    for subject in subjects:
        if os.path.exists(f"{subject.name}.html"):
            os.remove(f"{subject.name}.html")

if __name__ == "__main__":
    print('尝试登陆中······')
    if os.path.exists("user.data"):
        zxw = load_account()
    else:
        username = input('用户名: ').strip()
        password = input('密码: ').strip()
        zxw = login_student(username, password)
        print("自动将账号密码加密保存在当前目录下")
        zxw.save_account()
    print('登陆成功')

    exams = zxw.get_page_exam(1)[0]
    print('考试名称:')
    for i, exam in enumerate(exams):
        print(f"{i}. {exam.name}")
    exam_num = int(input('请输入您要生成错题本的考试: ').strip())
    cur_exam = exams[exam_num]

    subjects = zxw.get_subjects(cur_exam.id)

    mark = zxw.get_self_mark(cur_exam, has_total_score=False)
    for subject in subjects:
        cur_subject_rank = mark.find(lambda t: t.subject.code == subject.code).class_rank
        try:
            error_book = zxw.get_errorbook(cur_exam.id, subject.id)
        except Exception:
            continue
        errorbookHtml = fullTemplate(FullModel(zxw.name, subject.name, cur_exam.name, cur_subject_rank, error_book))
        with open(f"{subject.name}.html", 'w', encoding='utf-8') as f:
            f.write(errorbookHtml)
        htmlToPdf(f"{subject.name}.html",subject)
    clean(subjects)