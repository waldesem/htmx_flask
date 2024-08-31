import json
import os
import re
import shutil
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
)
from sqlalchemy import desc, func, select
from werkzeug.security import check_password_hash, generate_password_hash

from ..classes.classes import Regions, Roles
from ..depends.depend import login_required, roles_required
from ..handlers.handler import (
    handle_get_item,
    handle_image,
    handle_json_to_dict,
    handle_post_item,
    handle_take_resume,
    handle_users,
    make_destination,
)
from ..model.models import Person, User, models_tables
from ..model.tables import Checks, Persons, Users, db_session, tables_models

bp = Blueprint("route", __name__)


@bp.get("/auth")
def get_auth():
    """
    Handles GET requests to the /auth endpoint.

    Returns:
        A rendered HTML template for the auth page.
    """
    return render_template("/login/auth.html.jinja")


@bp.route("/auth/<action>", methods=["GET", "POST"])
def login(action):
    """
    Handles user authentication and password changes.

    Parameters:
        action (str): The type of authentication action to perform (e.g. "login", "password").

    Returns:
        A rendered HTML template or a redirect response.
    """
    if request.method == "GET":
        if action == "login":
            return render_template("/login/login.html.jinja")
        else:
            return render_template("/login/password.html.jinja")
    else:
        user = db_session.execute(
            select(Users).where(Users.username == request.form.get("login"))
        ).scalar_one_or_none()
        if not user or user.blocked or user.deleted:
            flash("Полььзователь не найден или заблокирован", "danger")
            return redirect("/auth")

        if not check_password_hash(user.passhash, request.form["password"]):
            if user.attempt < 5:
                user.attempt += 1
            else:
                user.blocked = True
            db_session.commit()
            flash("Неверный логин или пароль", "danger")
            return redirect("/auth")

        if action == "password":
            pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,16}$"
            if re.match(pattern, request.form["new_pswd"]):
                passhash = generate_password_hash(request.form["new_pswd"])
                if user.passhash == passhash:
                    flash("Новый пароль совпадает с текущим", "danger")
                    return redirect("/auth")
                user.passhash = passhash
                user.change_pswd = False
                user.attempt = 0
                db_session.commit()
                flash(
                    "Пароль успешно изменен. Вы можете войти с новым паролем", "success"
                )
                return redirect("/auth")

            flash("Новый пароль не соответствует требованиям", "danger")
            return redirect("/auth")

        delta_change = datetime.now() - user.pswd_create
        if not user.change_pswd and delta_change.days < 365:
            session["user"] = user.to_dict()
            user.attempt = 0
            db_session.commit()
            return redirect("/")
        flash("Пароль устарел и должен быть сменен", "danger")
        return redirect("/auth")


@bp.get("/logout")
def get_logout():
    """
    Handles user logout by clearing the session and redirecting to the authentication page.

    Returns:
        A redirect response to the authentication page.
    """
    session.clear()
    return redirect("/auth")


@bp.route("/users", methods=["GET", "POST"])
@roles_required(Roles.admin.value)
def take_users():
    """
    Handles user data retrieval and rendering of user information pages.

    This function supports both GET and POST requests. If the request method is GET,
    it retrieves all users from the database and renders the users.html.jinja template.
    If the request method is POST, it filters users based on the provided search data
    and renders the info.html.jinja template.

    Args:
        None

    Returns:
        A rendered HTML template with user data.
    """
    stmt = select(Users)
    if request.method == "POST":
        search_data = request.form.get("search")
        if search_data and len(search_data) > 2:
            if re.match(r"^[a-zA-z_]+", search_data):
                stmt = stmt.filter(Users.username.like("%" + search_data + "%"))
            else:
                stmt = stmt.filter(Users.fullname.like("%" + search_data + "%"))
    users = db_session.execute(stmt.order_by(desc(Users.id))).scalars()
    result = [user.to_dict() for user in users]
    if request.method == "POST":
        return render_template("/users/info.html.jinja", users=result)
    return render_template("/users/users.html.jinja", users=result)


@bp.post("/user")
@roles_required(Roles.admin.value)
def post_user():
    """
    Handles the creation of a new user account.

    This function accepts POST requests to the /user endpoint and attempts to create a new user account based on the provided form data.
    It checks if a user with the same username already exists, and if not, it creates a new user with the default role and region.
    The function returns a rendered HTML template with the user data if the creation is successful, or an error message if the creation fails.

    Args:
        None

    Returns:
        A rendered HTML template with user data or an error message.
    """
    try:
        json_dict = User(**request.form).dict()
        user = db_session.execute(
            select(Users).filter(Users.username == json_dict.get("username"))
        ).all()
        if not user:
            json_dict["role"] = Roles.guest.value
            json_dict["region"] = Regions.main.value
            json_dict["passhash"] = generate_password_hash(
                current_app.config["DEFAULT_PASSWORD"]
            )
            db_session.add(Users(**json_dict))
            db_session.commit()
            return render_template("/users/info.html.jinja", users=handle_users())
        return abort(400)
    except Exception as e:
        print(e)
        return render_template("/users/users.html.jinja", users=handle_users())


@bp.route("/user/<int:user_id>", methods=["GET", "POST"])
@roles_required(Roles.admin.value)
def take_user(user_id):
    """
    Handles user account management for administrators.

    This function accepts GET and POST requests to the /user/<int:user_id> endpoint and allows administrators to manage user accounts.
    It checks if the current user is an administrator and if the requested user ID matches the current user's ID.
    If the request method is GET, it updates the user's account based on the provided query parameters.
    If the request method is POST, it updates the user's role or region based on the provided form data.
    The function returns a rendered HTML template with the updated user data.

    Parameters:
        user_id (int): The ID of the user account to be managed.

    Returns:
        A rendered HTML template with the updated user data or an empty response with a 205 status code.
    """
    if session["user"]["id"] == user_id:
        return "", 205
    user = db_session.get(Users, user_id)
    if request.method == "GET":
        item = request.args.get("item")
        if item == "drop":
            user.passhash = generate_password_hash(
                current_app.config["DEFAULT_PASSWORD"]
            )
            user.attempt = 0
            user.blocked = False
            user.change_pswd = True
        elif item == "block":
            user.blocked = not user.blocked
        elif item == "delete":
            user.deleted = not user.deleted
    else:
        item = request.form
        if "role" in item and item["role"] in [reg.value for reg in Roles]:
            user.role = item["role"]
        elif "region" in item and item["region"] in [reg.value for reg in Regions]:
            user.region = item["region"]
    db_session.commit()
    return render_template("/users/info.html.jinja", users=handle_users())


@bp.get("/")
@login_required()
def route_menu():
    return render_template("/index.html.jinja")


@bp.get("/index")
@bp.route("/index/<int:page>", methods=["GET", "POST"])
@login_required()
def route_personal(page=1):
    """
    Handles GET and POST requests to the /index/<int:page> endpoint for person management.

    This function accepts GET and POST requests and allows users to manage persons.
    It checks if the current user is logged in and if the requested page number is valid.
    If the request method is GET, it updates the person's isbusy based on the provided query parameters.
    If the request method is POST, it searches for persons based on the provided form data.
    The function returns a rendered HTML template with the person data.

    Parameters:
        page (int): The page number of the person list.

    Returns:
        A rendered HTML template with the person data.
    """
    if request.method == "GET":
        return render_template("/persons/personal.html.jinja")

    pagination = 12
    stmt = select(Persons, Users.fullname)
    search_data = request.form.get("search")
    if search_data and len(search_data) > 2:
        if search_data.isdigit():
            stmt.filter(Persons.inn.ilike("%" + search_data + "%"))
        else:
            pattern = r"^\d{2}\.\d{2}\.\d{4}$"
            query = list(map(str.upper, search_data.split()))
            if len(query):
                stmt = stmt.filter(Persons.surname.ilike(f"%{query[0]}%"))
            if len(query) > 1 and not re.match(pattern, query[1]):
                stmt = stmt.filter(Persons.firstname.ilike(f"%{query[1]}%"))
            if len(query) > 2 and not re.match(pattern, query[2]):
                stmt = stmt.filter(Persons.patronymic.ilike(f"%{query[2]}%"))
            if len(query) > 1 and re.match(pattern, query[-1]):
                stmt = stmt.filter(
                    Persons.birthday == datetime.strptime(query[-1], "%d.%m.%Y").date()
                )
    if session["user"]["region"] != Regions.main.value:
        stmt = stmt.filter(Persons.region == session["user"]["region"])
    query = db_session.execute(
        stmt.join(Users)
        .order_by(desc(Persons.id))
        .limit(pagination + 1)
        .offset((page - 1) * pagination)
    ).all()
    result = [row[0].to_dict() | {"username": row[1]} for row in query]
    has_next = len(result) > pagination
    result = result[:pagination] if has_next else result

    return render_template(
        "/persons/info.html.jinja",
        candidates=result,
        has_next=has_next,
        has_prev=page > 1,
        page=page,
    )


@bp.route("/resume", methods=["GET", "POST"])
@roles_required(Roles.user.value)
def take_resume():
    """
    Handles the taking of a resume by a user.

    This function is triggered by a GET or POST request to the "/resume" endpoint.
    If the request is a GET, it renders the create.html.jinja template.
    If the request is a POST, it creates a new Person object from the request form data,
    attempts to handle the taking of the resume, and redirects the user to the index page.

    Returns:
        A rendered template or a redirect response.
    """
    if request.method == "GET":
        return render_template("/profile/create.html.jinja")
    resume = Person(**request.form).dict()
    person_id = handle_take_resume(resume)
    if person_id:
        flash("Резюме успешно добавлено", "success")
    else:
        flash("Некорректные данные", "danger")
    return render_template("/persons/personal.html.jinja")


@bp.get("/profile/<int:person_id>")
@login_required()
def route_profile(person_id):
    """
    Retrieves a person's profile information.

    Parameters:
        person_id (int): The ID of the person for whom to retrieve the profile information.

    Returns:
        A rendered template with the person's profile information.
    """
    standing = request.args.get("standing")
    if standing:
        person = db_session.get(Persons, person_id)
        person.isbusy = not person.isbusy
        db_session.commit()
    result = {item: handle_get_item(item, person_id) for item in tables_models.keys()}
    return render_template("profile/profile.html.jinja", person=result)


@bp.post("/region/<int:person_id>")
@roles_required(Roles.user.value)
def change_region(person_id):
    """
    Change a person's region in the database based on their person ID.

    Parameters:
        person_id (int): The ID of the person.

    Returns:
        The HTTP status code is 200.
    """
    region = request.form.get("region")
    if region:
        person = db_session.get(Persons, person_id)
        if person.destination:
            destination = make_destination(
                region, person.surname, person.firstname, person.patronymic, person.id
            )
            shutil.move(person.destination, destination)
            person.destination = destination
        person.region = region
        db_session.commit()
        result = handle_get_item("persons", person_id)
        return render_template("/profile/divs/persons.html.jinja", items=result)
    return abort(400)


@bp.get("/<item>/<action>/<int:item_id>")
@roles_required(Roles.user.value)
def get_item_id(item, action, item_id):
    """
    Handles HTTP GET requests for a specific item by ID.

    Parameters:
        item (str): The type of item being retrieved.
        item_id (int): The ID of the item being retrieved.

    Returns:
        A rendered HTML template with the retrieved item information.
    """
    if action == "form":
        stmt = select(tables_models[item], Users.fullname).filter(
            tables_models[item].user_id == Users.id
        )
        stmt = stmt.filter(tables_models[item].id == item_id)
        query = db_session.execute(stmt).one_or_none()
        result = query[0].to_dict() | {"username": query[1]}
        print(result)
        return render_template(
            f"profile/forms/{item}.html.jinja",
            id=result["id"] if item != "persons" else None,
            item=result,
        )
    results = handle_get_item(item, item_id)
    return render_template(f"profile/divs/{item}.html.jinja", items=results)


@bp.post("/<item>/<int:item_id>")
@roles_required(Roles.user.value)
def post_item_id(item, item_id):
    """
    Handles HTTP POST requests for a specific item by ID.

    Parameters:
        item (str): The type of item being updated.
        item_id (int): The ID of the item being updated.

    Returns:
        A rendered HTML template with the updated item information.
    """

    data = request.form
    json_dict = models_tables[item](**data).dict()
    handle_post_item(json_dict, item, item_id)
    results = handle_get_item(item, item_id)
    return render_template(f"profile/divs/{item}.html.jinja", items=results)


@bp.get("/delete/<item>/<int:item_id>")
@roles_required(Roles.user.value)
def delete_item(item, item_id):
    """
    Handles HTTP GET requests to delete a specific item by ID.

    Parameters:
        item (str): The type of item being deleted.
        item_id (int): The ID of the item being deleted.

    Returns:
        A rendered HTML template with the updated item information after deletion.
    """

    row = db_session.get(tables_models[item], item_id)
    if not row:
        return abort(400)
    db_session.delete(row)
    db_session.commit()
    if item == "persons":
        return render_template("/persons/personal.html.jinja")
    results = handle_get_item(item, row.person_id)
    return render_template(
        f"profile/divs/{item}.html.jinja", items=results, id=row.person_id
    )


@bp.get("/image/<int:person_id>")
def get_image(person_id):
    """
    Retrieves an image from the specified path and sends it as a response.

    Args:
        image (str): The path to the image.

    Returns:
        send_file: The image file as a response.
    """
    person = db_session.get(Persons, person_id)
    if person.destination:
        file_path = os.path.join(person.destination, "image", "image.jpg")
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True, mimetype="image/jpg")
    return send_file("static/no-photo.png", as_attachment=True, mimetype="image/jpg")


@bp.post("/file/<item>/<int:item_id>")
@roles_required(Roles.user.value)
def post_file(item, item_id):
    """
    Handles HTTP POST requests to upload files for a specific item by ID.

    Parameters:
        item (str): The type of item being uploaded.
        item_id (int): The ID of the item being uploaded.

    Returns:
        A rendered HTML template or a redirect with a status code.
    """
    files = request.files
    if not files:
        return abort(400)

    if item == "anketa":
        json_dict = json.load(files["json"])
        anketa = handle_json_to_dict(json_dict)
        if not anketa:
            flash("Некорректные данные", "danger")
            return render_template("/persons/personal.html.jinja")
        person_id = handle_take_resume(anketa["resume"])
        if not person_id:
            flash("Некорректные данные", "danger")
            return render_template("/persons/personal.html.jinja")
        for table, contents in anketa.items():
            if contents and table != "resume":
                for content in contents:
                    if content:
                        handle_post_item(content, table, person_id)
        flash("Резюме успешно добавлено", "success")
        return render_template("/persons/personal.html.jinja")

    person = db_session.get(Persons, item_id)
    if not person:
        return abort(400)
    if not person.destination:
        destination = make_destination(
            session["user"]["region"],
            person.surname,
            person.firstname,
            person.patronymic,
            item_id,
        )
        person.destination = destination
        db_session.commit()
    if not os.path.isdir(person.destination):
        os.mkdir(person.destination)

    item_dir = os.path.join(person.destination, item)
    if not os.path.isdir(item_dir):
        os.mkdir(item_dir)

    if item == "image":
        new_file = handle_image(files["image"], item_dir)
        if new_file:
            return render_template(
                "/profile/divs/photo.html.jinja", person_id=person.id
            )
        else:
            return abort(400)

    date_subfolder = os.path.join(
        item_dir,
        datetime.now().strftime("%Y-%m-%d"),
    )
    if not os.path.isdir(date_subfolder):
        os.mkdir(date_subfolder)

    filelist = files.getlist(item + "-file-" + str(item_id))
    for file in filelist:
        file.save(os.path.join(date_subfolder, file.filename))
    return ""


@bp.route("/information", methods=["GET", "POST"])
@login_required()
def take_info():
    """
    Handles retrieval of information based on the provided date range and region.

    This function supports both GET and POST requests. If the request method is GET,
    it retrieves information for the last 30 days in the user's region. If the request
    method is POST, it filters information based on the provided start date, end date,
    and region.

    Args:
        None

    Returns:
        A rendered HTML template with information data.
    """
    if request.method == "GET":
        start, end, region = (
            datetime.now() - timedelta(days=30),
            datetime.now(),
            session["user"]["region"],
        )
    else:
        data = request.form
        start, end, region = data.get("start"), data.get("end"), data.get("region")

    results = db_session.execute(
        select(Checks.conclusion, func.count(Checks.id))
        .join(Persons, Checks.person_id == Persons.id)
        .filter(
            Checks.created.between(start, end),
            Persons.region == region,
        )
        .group_by(Checks.conclusion),
    ).all()
    if request.method == "GET":
        return render_template(
            "/information/information.html.jinja",
            results=[list(result) for result in results],
            start=datetime.strftime(start, "%Y-%m-%d"),
            end=datetime.strftime(end, "%Y-%m-%d"),
            region=region,
        )
    else:
        return render_template(
            "/information/info.html.jinja", results=[list(result) for result in results]
        )
