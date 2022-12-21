from flask import render_template, request, redirect, flash, url_for
from flask import session
from psycopg2 import OperationalError
import psycopg2
from . import config
import bcrypt
from . import app
import logging
from flask_wtf import Form, FlaskForm
from wtforms import SubmitField, StringField, validators,\
                    DateField, PasswordField, EmailField, \
                    DecimalField, SelectField, TextAreaField, \
                    ValidationError
from decimal import *
import phonenumbers

logging.basicConfig(level=logging.INFO)

class LoginForm(Form):
    login = StringField('login', validators=[validators.input_required()], render_kw={"placeholder": "login"})
    pas = PasswordField('password', validators=[validators.input_required()], render_kw={"placeholder": "password"})
    submit_login = SubmitField('Sign in')

# Функция для проверки телефона, но пока не внедрена
def validate_phone(form, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+7"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')

# Функция для проверки пароля пользователя
def check_password(login: str, entered_password: str) -> bool:

    # Подключаемся к бд как админ, чтобы зайти в пароли пользователь и сверить пароль
    admin_connection = psycopg2.connect(database='income_and_expenses',
                                    user=config.DATABASE_USER, 
                                    password = config.DATABASE_PAS,
                                    host='localhost', 
                                    port=5432)
    # Получаем id пользователя
    with admin_connection:
        with admin_connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT
                user_id
            FROM
                personal_info
            WHERE
                personal_info_login = '{login}'
            """)
            user_id = cursor.fetchone()[0]

    # Получаем пароль
    with admin_connection:
        with admin_connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT
                password_value
            FROM
                passwords
            WHERE
                user_id = {user_id}
            """)
            hashed_password_from_bd = cursor.fetchone()[0]
    
    is_pass_correct = bcrypt.checkpw(entered_password.encode(), hashed_password_from_bd.encode())

    if is_pass_correct:
        #.encode().decode('utf-8')
        session['current_user_login'] = login
        session['current_user_pasw'] = hashed_password_from_bd
        return True
    else:
        return False


class RegisterForm(Form):
    login = StringField(
        'login', 
        validators=[validators.input_required()], 
        render_kw={"placeholder": "login"}
        )

    email = EmailField(
        'email', 
        validators=[validators.input_required()], 
        render_kw={"placeholder": "email"}
        )

    pas = PasswordField(
        'password', 
        validators=[validators.input_required()], 
        render_kw={"placeholder": "password"}
        )

    first_name = StringField(
        'first_name', 
        validators=[validators.input_required()], 
        render_kw={"placeholder": "first name"}
        )

    last_name = StringField(
        'last_name', 
        validators=[validators.input_required()], 
        render_kw={"placeholder": "last name"}
        )

    phone = StringField(
        'phone', 
        validators=[validators.input_required(), 
        validators.Length(min=11, max=12)], 
        render_kw={"placeholder": "phone"}
        )

    submit_sign_up = SubmitField('Sign up')


class AddExpenseModal(Form):

    date = DateField(validators=[validators.input_required()], render_kw={"placeholder": "date"})
    amount = DecimalField(validators=[validators.input_required()], render_kw={"placeholder": "sum"})
    comment = TextAreaField(render_kw={"placeholder": "comment"})
    category = SelectField('Categories', choices=[])
    subcategory = SelectField('Categories', choices=[])
    submit = SubmitField('Внести расход')

class AddIncomeModal(Form):

    date = DateField(validators=[validators.input_required()], render_kw={"placeholder": "date"})
    amount = DecimalField(validators=[validators.input_required()], render_kw={"placeholder": "sum"})
    comment = TextAreaField(render_kw={"placeholder": "comment"})
    category = SelectField('Categories', choices=[])
    subcategory = SelectField('Categories', choices=[])
    submit = SubmitField('Внести доход')

class AddInvestmentModal(Form):

    date = DateField(validators=[validators.input_required()], render_kw={"placeholder": "date"})
    amount = DecimalField(validators=[validators.input_required()], render_kw={"placeholder": "sum"})
    comment = TextAreaField(render_kw={"placeholder": "comment"})
    subcategory = SelectField('Categories', choices=[])
    submit = SubmitField('Внести доход')

        

@app.route('/', methods=['POST', 'GET'])
def index():
    session.clear()
    logging.info('We are in index()')
    login_form  = LoginForm(request.form)
    register_form = RegisterForm(request.form)


    if request.method == 'POST':
        if login_form.submit_login.data and login_form.validate():
            logging.info("login_form submitted")

            session['sign_in_login'] = login_form.login.data
            session['sign_in_pasw'] = login_form.pas.data
            
            return redirect(url_for('login'))
            
        elif register_form.submit_sign_up.data and register_form.validate():
            logging.info("register_form submitted")
            
            session['sign_up_login'] = register_form.login.data
            session['sign_up_pasw'] = register_form.pas.data
            session['sign_up_email'] = register_form.email.data
            session['sign_up_first_name'] = register_form.first_name.data
            session['sign_up_last_name'] = register_form.last_name.data
            session['sign_up_phone'] = register_form.phone.data

            return redirect(url_for('register'))
    else:
        return render_template('index.html', login_form=login_form, register_form=register_form)
        
@app.route('/register', methods=['POST', 'GET'])
def register():
    logging.info('we are at register()')

    login = session['sign_up_login']
    entered_password = session['sign_up_pasw']
    email = session['sign_up_email']
    first_name = session['sign_up_first_name']
    last_name = session['sign_up_last_name']
    phone = session['sign_up_phone']

    if login and entered_password and email:
        connection = psycopg2.connect(database='income_and_expenses',
                                    user=config.DATABASE_USER, 
                                    password = config.DATABASE_PAS,
                                    host='localhost', 
                                    port=5432)
        connection.set_session(autocommit=1)
        
        hashed_password = bcrypt.hashpw(entered_password.encode(), bcrypt.gensalt())

        with connection:
            with connection.cursor() as c:
                c.execute(
                    f'''
                        CALL create_user('{login}', '{email}', '{hashed_password.decode()}', '{first_name}', '{last_name}', '{phone}')
                    '''
                )

                c.execute(f"""SELECT 
                                users.user_login,
                                passwords.password_value
                            FROM 
                                users
                                INNER JOIN passwords ON users.user_id = passwords.user_id
                            WHERE user_login = '{login}';""")

                result = c.fetchall()

                session['current_user_login'] = result[0][0]
                session['current_user_pasw'] = result[0][1]

                return redirect(url_for('dashboard'))
    else:
        sign_up_err = 'Enter all data'
        return render_template('index.html', sign_up_err=sign_up_err, login_form=login_form, register_form=register_form)

@app.route('/login', methods=["POST", "GET"])
def login():
    logging.info('we are at login()')
    login_form  = LoginForm(request.form)
    register_form = RegisterForm(request.form)

    login = session['sign_in_login']
    entered_password = session['sign_in_pasw']
    is_pas_correct = check_password(login, entered_password)

    if is_pas_correct:
        logging.info("PASSWORD IS CORRECT")
    else:
        logging.info("PASSWORD IS NOT CORRECT")

    print(session.get('current_user_login'))
    print(session.get('current_user_pasw'))

    if login and entered_password and is_pas_correct:
        connection = psycopg2.connect(database='income_and_expenses',
                                    user=f"{session.get('current_user_login')}", 
                                    password = f"{session.get('current_user_pasw')}",
                                    host='localhost', 
                                    port=5432)
        
        if connection:
            logging.info(f"we are conneted to db with login: {session.get('current_user_login')}")
        
        with connection:
            with connection.cursor() as c:
                c.execute(f"""SELECT 
                                    user_id 
                            FROM 
                                personal_info 
                            WHERE 
                                personal_info_login = '{session['current_user_login']}'
                """)

                session['current_user_id'] = c.fetchone()[0]
                logging.info(f"user_id: {session['current_user_id']}")

        return redirect(url_for('dashboard'))
    else:
        login_err = 'Enter all data'
        return render_template('index.html', login_err=login_err, login_form=login_form, register_form=register_form)

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    logging.info("we are in dashboard()")

    if 'current_user_login' in session:
        conn= psycopg2.connect(database='income_and_expenses',
                                user=f'''{session['current_user_login']}''', 
                                password = f'''{session['current_user_pasw']}''',
                                host='localhost', port=5432)

        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT
                        category_name,
                        sum(income_amount)
                    FROM 
                        incomes
                        INNER JOIN categories ON incomes.category_id = categories.category_id
                        INNER JOIN personal_info ON categories.user_id = personal_info.user_id
                    WHERE
                        personal_info.personal_info_login = '{session['current_user_login']}'
                    GROUP BY
                        category_name;
                    """)
                incomes = cur.fetchall()
            
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT
                        subcategory_name,
                        sum(expense_amount)
                    FROM 
                        subcategories
                        INNER JOIN expenses ON subcategories.subcategory_id = expenses.subcategory_id
                        INNER JOIN personal_info ON personal_info.user_id = expenses.user_id 
                    WHERE
                        personal_info_login = '{session['current_user_login']}'
                    GROUP BY
                        subcategory_name;
                    """)
                expenses = cur.fetchall()

        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT
                        date_trunc('month', expense_date)::date,
                        sum(expense_amount)
                    FROM 
                        expenses
                        INNER JOIN personal_info ON personal_info.user_id = expenses.user_id 
                    WHERE
                        personal_info_login = '{session['current_user_login']}'
                    GROUP BY 
                        date_trunc('month', expense_date)
                    ORDER BY
                        1;
                    """)
                expenses_to_dates = cur.fetchall()


        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT
                        date_trunc('month', income_date)::date,
                        sum(income_amount)
                    FROM 
                        incomes
                        inner join accounts on incomes.account_id = accounts.account_id
                        INNER JOIN personal_info ON personal_info.user_id = accounts.user_id 
                    WHERE
                        personal_info_login = '{session['current_user_login']}'
                    GROUP BY 
                        date_trunc('month', income_date)
                    ORDER BY
                        1;
                    """)
                incomes_to_dates = cur.fetchall()


        return render_template('dashboard.html',
                                incomes=incomes, 
                                expenses=expenses,
                                expenses_to_dates=expenses_to_dates,
                                incomes_to_dates=incomes_to_dates)

@app.route('/expenses', methods=['POST', 'GET'])
def show_expenses():
    logging.info("we are at show_expenses()")
    add_expense_form = AddExpenseModal(request.form)
    
    if 'current_user_login' in session:
        conn= psycopg2.connect(database='income_and_expenses',
                                user=f'''{session['current_user_login']}''', 
                                password = f'''{session['current_user_pasw']}''',
                                host='localhost', port=5432)

        # Выбираем все данные из таблицы расходов для нашего пользователя
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""SELECT
                                    category_name,
                                    TO_CHAR(expense_date, 'DD.MM.YYYY'),
                                    expense_amount,
                                    expense_comment
                                FROM 
                                    expenses
                                    INNER JOIN categories ON expenses.category_id = categories.category_id
                                    INNER JOIN personal_info ON categories.user_id = personal_info.user_id
                                WHERE
                                    personal_info.personal_info_login = '{session['current_user_login']}'
                                ORDER BY
                                    expense_id DESC;""")
                expenses = cur.fetchall()
        
        # categories of our user
        with conn:
            with conn.cursor() as c:
                c.execute(f"""SELECT
                                category_name
                            FROM 
                                categories
                                INNER JOIN categories_classifier ON categories.categories_classifier_id = categories_classifier.categories_classifier_id
                            WHERE 
                                user_id = {session['current_user_id']}
                                AND categories_classifier_name = 'Расходы'

                """)
                categories = c.fetchall()

        # cleaning our data
        clean_categories = []
        for item in categories:
            clean_categories.append(item[0])

        logging.info(f"CLEAN CATEGORIES: {clean_categories}")

        # subcategories of our user
        with conn:
            with conn.cursor() as c:
                c.execute(f"""SELECT
                                subcategory_name
                            FROM 
                                subcategories
                                INNER JOIN categories ON subcategories.category_id = categories.category_id
                                INNER JOIN categories_classifier ON categories.categories_classifier_id = categories_classifier.categories_classifier_id
                            WHERE 
                                categories.user_id = {session['current_user_id']}
                                AND categories_classifier_name = 'Расходы'
                """)
                subcategories = c.fetchall()
        
        # cleaning our data
        clean_subcategories = []
        for item in subcategories:
            clean_subcategories.append(item[0])

        logging.info(f"CLEAN SUBCATEGORIES: {clean_subcategories}")

        
        add_expense_form.category.choices=clean_categories
        add_expense_form.subcategory.choices=clean_subcategories


        # Проверяем нашу форму (модальное окно) для добавляения расхода 
        if request.method == "POST":
            logging.info("add_expense_form POST")
            arr_to_db = []
            for item in add_expense_form.data.values():
                # Переводим из Decimal в int (естественно stuckOverflow)
                if type(item) == Decimal:
                    list_d = str(item).split('.')

                    if len(list_d) == 2:
                        number = int(list_d[0] + list_d[1])
                    else:
                        str_dec = list_d[0].rstrip()
                        number = int(str_dec)

                    arr_to_db.append(number)
                else:
                    arr_to_db.append(item)

            logging.info(f"OUR ARRAY: {arr_to_db}")
            logging.info(f"OUR INPUT DATA: {add_expense_form.data.values()}")
            if add_expense_form.submit.data and add_expense_form.validate():
                logging.info("add_expense_form submitted")

                with conn:
                    with conn.cursor() as c:
                        c.execute(f"""CALL add_expense('{arr_to_db[0]}', 
                                                        {arr_to_db[1]}, 
                                                        '{arr_to_db[2]}', 
                                                        '{arr_to_db[3]}', 
                                                        '{arr_to_db[4]}',
                                                        {session['current_user_id']})
                                                        """)
                        logging.info("expense added successfully")
                
            return redirect(url_for('show_expenses'))


        return render_template('expenses.html', expenses=expenses, user=session['current_user_login'], add_expense_form=add_expense_form)

@app.route('/incomes', methods=['POST', 'GET'])
def show_incomes():
    logging.info("we are at show_incomes()")
    add_income_form = AddIncomeModal(request.form)

    if 'current_user_login' in session:
        conn= psycopg2.connect(database='income_and_expenses',
                                user=f'''{session['current_user_login']}''', 
                                password = f'''{session['current_user_pasw']}''',
                                host='localhost', port=5432)

        # Выбираем все доходы нашего пользователя
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT
                        category_name,
                        subcategory_name,
                        TO_CHAR(income_date, 'DD.MM.YYYY'),
                        income_amount,
                        income_comment
                    FROM 
                        incomes
                        INNER JOIN categories ON incomes.category_id = categories.category_id
                        INNER JOIN subcategories ON incomes.subcategory_id = subcategories.subcategory_id
                        INNER JOIN personal_info ON subcategories.user_id = personal_info.user_id
                    WHERE
                        personal_info.personal_info_login = '{session['current_user_login']}'
                    ORDER BY
                        income_date DESC;
                    """)
                incomes = cur.fetchall()
        
        # Категории доходов нашего пользователя
        with conn:
            with conn.cursor() as c:
                c.execute(f"""SELECT
                                category_name
                            FROM 
                                categories
                                INNER JOIN categories_classifier ON categories.categories_classifier_id = categories_classifier.categories_classifier_id
                            WHERE 
                                user_id = {session['current_user_id']}
                                AND categories_classifier_name = 'Доходы'

                """)
                categories = c.fetchall()

        # cleaning our data
        clean_categories = []
        for item in categories:
            clean_categories.append(item[0])

        logging.info(f"CLEAN CATEGORIES: {clean_categories}")

        # Подкатегории нашего пользователя
        with conn:
            with conn.cursor() as c:
                c.execute(f"""SELECT
                                subcategory_name
                            FROM 
                                subcategories
                                INNER JOIN categories ON subcategories.category_id = categories.category_id
                                INNER JOIN categories_classifier ON categories.categories_classifier_id = categories_classifier.categories_classifier_id
                            WHERE 
                                categories.user_id = {session['current_user_id']}
                                AND categories_classifier_name = 'Доходы'
                """)
                subcategories = c.fetchall()
        
        # cleaning our data
        clean_subcategories = []
        for item in subcategories:
            clean_subcategories.append(item[0])

        logging.info(f"CLEAN SUBCATEGORIES: {clean_subcategories}")\

        add_income_form.category.choices = clean_categories
        add_income_form.subcategory.choices = clean_subcategories

        # Проверяем нашу форму (модальное окно) для добавляения расхода 
        if request.method == "POST":
            logging.info("add_expense_form POST")
            arr_to_db = []
            for item in add_income_form.data.values():
                # Переводим из Decimal в int (естественно stackOverflow)
                if type(item) == Decimal:
                    list_d = str(item).split('.')

                    if len(list_d) == 2:
                        number = int(list_d[0] + list_d[1])
                    else:
                        str_dec = list_d[0].rstrip()
                        number = int(str_dec)

                    arr_to_db.append(number)
                else:
                    arr_to_db.append(item)

            logging.info(f"OUR ARRAY: {arr_to_db}")
            logging.info(f"OUR INPUT DATA: {add_income_form.data.values()}")
            if add_income_form.submit.data and add_income_form.validate():
                logging.info("add_expense_form submitted")
                with conn:
                    with conn.cursor() as c:
                        c.execute(f"""CALL add_income('{arr_to_db[0]}', 
                                                        {arr_to_db[1]}, 
                                                        '{arr_to_db[2]}', 
                                                        '{arr_to_db[3]}', 
                                                        '{arr_to_db[4]}',
                                                        {session['current_user_id']})
                                                        """)
                        logging.info("income added successfully")
                
            return redirect(url_for('show_incomes'))


        return render_template('incomes.html', incomes=incomes, user=session['current_user_login'], add_income_form=add_income_form)


@app.route('/investments', methods=['POST', 'GET'])
def show_investments():
    logging.info("we are at show_investments()")
    add_investment_form = AddInvestmentModal(request.form)

    if 'current_user_login' in session:
        logging.info("current_user in session")
        conn= psycopg2.connect(database='income_and_expenses',
                                user=f'''{session['current_user_login']}''', 
                                password = f'''{session['current_user_pasw']}''',
                                host='localhost', port=5432)

        # Выбираем все инвестиции нашего пользователя
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    select
                        subcategory_name,
                        TO_CHAR(investment_date, 'DD.MM.YYYY'),
                        investment_amount,
                        investment_comment
                    from 
                        investments i 
                        INNER JOIN categories c ON i.category_id = c.category_id
                        INNER JOIN subcategories s ON i.subcategory_id = s.subcategory_id
                        INNER JOIN personal_info ON s.user_id = personal_info.user_id
                    where
                        personal_info.personal_info_login = '{session['current_user_login']}';
                    """)
                investments = cur.fetchall()

        # Смотрим, заплатил ли нам наш пользователь (является ли он премимум или нет)
        with conn:
            with conn.cursor() as c:
                c.execute(f"""select
                                is_paid_user 
                            from
                                personal_info pi2
                                where personal_info_login = '{session['current_user_login']}'
                """)
                is_paid_user = c.fetchone()[0]


        # Подкатегории нашего пользователя
        with conn:
            with conn.cursor() as c:
                c.execute(f"""
                SELECT
                    subcategory_name
                FROM 
                    subcategories
                    INNER JOIN categories ON subcategories.category_id = categories.category_id
                WHERE
                    subcategories.category_id = 7
                    AND categories.user_id = {session['current_user_id']}
                """)
                subcategories = c.fetchall()
        
        # cleaning our data
        clean_subcategories = []
        for item in subcategories:
            clean_subcategories.append(item[0])

        logging.info(f"CLEAN SUBCATEGORIES: {clean_subcategories}")
        add_investment_form.subcategory.choices = clean_subcategories

        # Проверяем нашу форму (модальное окно) для добавляения инвестиции 
        if request.method == "POST":
            logging.info("add_investment_form POST")
            arr_to_db = []
            for item in add_investment_form.data.values():
                # Переводим из Decimal в int (естественно stuckOverflow)
                if type(item) == Decimal:
                    list_d = str(item).split('.')

                    if len(list_d) == 2:
                        number = int(list_d[0] + list_d[1])
                    else:
                        str_dec = list_d[0].rstrip()
                        number = int(str_dec)

                    arr_to_db.append(number)
                else:
                    arr_to_db.append(item)

            logging.info(f"OUR ARRAY: {arr_to_db}")
            logging.info(f"OUR INPUT DATA: {add_investment_form.data.values()}")
            if add_investment_form.submit.data and add_investment_form.validate():
                logging.info("add_expense_form submitted")

                with conn:
                    with conn.cursor() as c:
                        c.execute(f"""CALL add_investment('{arr_to_db[0]}', 
                                                        {arr_to_db[1]}, 
                                                        '{arr_to_db[2]}', 
                                                        '{arr_to_db[3]}', 
                                                        '{session['current_user_login']}')
                                                        """)
                        logging.info("expense added successfully")
                
            return redirect(url_for('show_investments'))

        print("WE ARE HERE BEATCH")
        return render_template('investments.html', investments=investments, user=session['current_user_login'], paid_user=is_paid_user, add_investment_form=add_investment_form)