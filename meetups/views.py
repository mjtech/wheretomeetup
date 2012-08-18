from . import app, meetup, mongo
from flask import render_template, redirect, url_for, request, session, flash
from flask.ext.login import login_required, login_user, logout_user

from .logic import sync_user
from .models import User


@app.route('/clear/')
def clear():
    session.clear()
    return redirect('/')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/have/')
def have():
    return render_template('have.html')


@app.route('/login/', methods=('GET', 'POST'))
def login():
    return meetup.authorize(callback=url_for('login_meetup_return'))


@app.route('/login/meetup/return/', methods=('GET',))
@meetup.authorized_handler
def login_meetup_return(oauth_response):
    next_url = url_for('index')

    session['meetup_token'] = (
        oauth_response['oauth_token'],
        oauth_response['oauth_token_secret']
    )
    session['member_id'] = oauth_response['member_id']

    user = sync_user(oauth_response['member_id'])
    login_user(user, remember=True)

    flash('You are now signed in!', 'success')
    return redirect(next_url)


@app.route('/logout/')
def logout():
    session.pop('meetup_token', None)
    session.pop('meetup_member_id', None)
    logout_user()
    return redirect(url_for('.index'))


@app.route('/need/')
def need():
    return render_template('need.html')


@meetup.tokengetter
def get_twitter_token():
    return session.get('meetup_token')
