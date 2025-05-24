from datetime import timedelta
import random
from urllib.parse import urlencode
import bcrypt
from flask import Blueprint, redirect, request, jsonify, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
import os
from sqlalchemy import func
from models.user import User
from extensions import discord, oauth
from models import db

oauth_bp = Blueprint('oauth_bp', __name__)

@oauth_bp.route('/api/login/discord')
def login_discord():
    return discord.create_session(scope=["identify", "email"])

@oauth_bp.route('/api/login/github')
def login_github():
    redirect_uri = url_for('oauth_bp.auth_github', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@oauth_bp.route('/api/auth/discord')
def auth_discord():
    try:
        error = request.args.get("error")
        if error == "access_denied":
            response = redirect(f"{os.getenv('URL')}/login")
            response.delete_cookie("session")
            return response
        
        token = discord.callback()
        discord_user = discord.fetch_user()

        discord_id = str(discord_user.id)
        username = discord_user.name
        email = discord_user.email
        avatar_url = discord_user.avatar_url
        
        if not email:
            return jsonify({"message": "Nie udało się pobrać adresu email z Discord."}), 400
        
        user = User.query.filter((User.discord_id == discord_id) | (func.lower(User.username) == username.lower()) | (func.lower(User.email) == email.lower())).first()

        if user:
            if not user.discord_id:
                user.discord_id = discord_id
            if not user.avatar and avatar_url:
                user.avatar = avatar_url
            db.session.commit()
        else:
            if User.query.filter_by(username=username).first():
                username = f"{username}_{random.randint(1000,9999)}"
                
            random_password = bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
            user = User(
                username=username, 
                email=email, 
                password=random_password, 
                avatar=avatar_url,
                discord_id=discord_id
            )
            db.session.add(user)
            db.session.commit()
        
        access_token_expiresIn = "00:00:10:00"
        refresh_token_expiresIn = "01:00:00:00"

        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=10))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=1))

        params = {
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_time": str(access_token_expiresIn),
            "refresh_expire_time": str(refresh_token_expiresIn)
        }
        query = urlencode(params)
        return redirect(f"{os.getenv('URL')}/auth-callback?{query}")

    except Exception as e:
        return jsonify({"message": f"Błąd podczas autentykacji Discord: {str(e)}"}), 500

@oauth_bp.route('/api/auth/github')
def auth_github():
    error = request.args.get("error")
    if error == "access_denied":
        response = redirect("/login")
        response.delete_cookie("session")
        
        return response

    token = oauth.github.authorize_access_token()
    user_data = oauth.github.get('user').json()
    github_id = str(user_data.get("id"))
    email = user_data.get("email")
    username = user_data.get("login")
    avatar_url = user_data.get("avatar_url")
    
    if not email:
        emails = oauth.github.get('user/emails').json()
        for em in emails:
            if em.get("primary") and em.get("verified"):
                email = em.get("email")
                break
    if not email:
        return jsonify({"message": "Nie udało się pobrać adresu email z GitHub."}), 400

    link_account = request.args.get("link", "false").lower() == "true"
    if link_account:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Brak tokenu JWT do powiązania konta."}), 401
        try:
            token_str = auth_header.split(" ")[1]
            decoded = decode_token(token_str)
            current_user_id = decoded['sub']
        except Exception as e:
            return jsonify({"message": "Nieprawidłowy token JWT."}), 401

        current_user = User.query.get(current_user_id)
        if current_user is None:
            return jsonify({"message": "Użytkownik nie istnieje."}), 404

        if current_user.github_id and current_user.github_id != github_id:
            return jsonify({"message": "Twoje konto jest już powiązane z innym GitHub."}), 400

        current_user.github_id = github_id
        if not current_user.avatar and avatar_url:
            current_user.avatar = avatar_url
        db.session.commit()
        return jsonify({"message": "Konto GitHub zostało pomyślnie powiązane."}), 200

    user = User.query.filter((User.github_id == github_id) | (func.lower(User.username) == username.lower()) | (func.lower(User.email) == email.lower())).first()

    if user:
        if not user.github_id:
            user.github_id = github_id
        if not user.avatar and avatar_url:
            user.avatar = avatar_url
        db.session.commit()

        access_token_expiresIn = "00:00:10:00"
        refresh_token_expiresIn = "01:00:00:00"

        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=10))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=1))

        params = {
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_time": str(access_token_expiresIn),
            "refresh_expire_time": str(refresh_token_expiresIn)
        }
        query = urlencode(params)
        return redirect(f"{os.getenv('URL')}/auth-callback?{query}")
    else:
        username = user_data.get("login")
        if User.query.filter_by(username=username).first():
            username = f"{username}_{random.randint(1000,9999)}"
        random_password = bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
        new_user = User(username=username, email=email, password=random_password, avatar=avatar_url, github_id=github_id)
        db.session.add(new_user)
        db.session.commit()

        access_token_expiresIn = "00:00:10:00"
        refresh_token_expiresIn = "01:00:00:00"

        access_token = create_access_token(identity=str(new_user.id), expires_delta=timedelta(minutes=10))
        refresh_token = create_refresh_token(identity=str(new_user.id), expires_delta=timedelta(days=1))

        params = {
            "username": new_user.username,
            "email": new_user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_time": str(access_token_expiresIn),
            "refresh_expire_time": str(refresh_token_expiresIn)
        }
        query = urlencode(params)
        return redirect(f"{os.getenv('URL')}/auth-callback?{query}")
