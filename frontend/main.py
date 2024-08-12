from __future__ import annotations as _annotations

import asyncio
import json
import os
from dataclasses import asdict
from typing import Annotated, Literal, TypeAlias

from fastapi import APIRouter, Depends, Request
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.auth import AuthRedirect
from fastui.events import AuthEvent, GoToEvent, PageEvent
from fastui.forms import fastui_form
from httpx import AsyncClient
from pydantic import BaseModel, EmailStr, Field, SecretStr

from src.auth.models import User

router = APIRouter()


@router.get('/login/{kind}', response_model=FastUI, response_model_exclude_none=True)
def auth_login(
        kind: LoginKind,
        user: Annotated[User | None, Depends(User.from_request_opt)],
) -> list[AnyComponent]:
    if user is not None:
        # already logged in
        raise AuthRedirect('/auth/profile')

    return demo_page(
        c.LinkList(
            links=[
                c.Link(
                    components=[c.Text(text='Password Login')],
                    on_click=PageEvent(name='tab', push_path='/auth/login/password', context={'kind': 'password'}),
                    active='/auth/login/password',
                ),
            ],
            mode='tabs',
            class_name='+ mb-4',
        ),
        c.ServerLoad(
            path='/auth/login/content/{kind}',
            load_trigger=PageEvent(name='tab'),
            components=auth_login_content(kind),
        ),
        title='Authentication',
    )


@router.get('/login/content/{kind}', response_model=FastUI, response_model_exclude_none=True)
def auth_login_content(kind: LoginKind) -> list[AnyComponent]:
    match kind:
        case 'password':
            return [
                c.Heading(text='Password Login', level=3),
                c.Paragraph(
                    text=(
                        'This is a very simple demo of password authentication, '
                        'here you can "login" with any email address and password.'
                    )
                ),
                c.Paragraph(text='(Passwords are not saved and is email stored in the browser via a JWT only)'),
                c.ModelForm(model=LoginForm, submit_url='/api/auth/login', display_mode='page'),
            ]
        case _:
            raise ValueError(f'Invalid kind {kind!r}')


class LoginForm(BaseModel):
    email: EmailStr = Field(
        title='Email Address', description='Enter whatever value you like', json_schema_extra={'autocomplete': 'email'}
    )
    password: SecretStr = Field(
        title='Password',
        description='Enter whatever value you like, password is not checked',
        json_schema_extra={'autocomplete': 'current-password'},
    )


@router.post('/login', response_model=FastUI, response_model_exclude_none=True)
async def login_form_post(form: Annotated[LoginForm, fastui_form(LoginForm)]) -> list[AnyComponent]:
    user = User(email=form.email, extra={})
    token = user.encode_token()
    return [c.FireEvent(event=AuthEvent(token=token, url='/auth/profile'))]


@router.get('/profile', response_model=FastUI, response_model_exclude_none=True)
async def profile(user: Annotated[User, Depends(User.from_request)]) -> list[AnyComponent]:
    return demo_page(
        c.Paragraph(text=f'You are logged in as "{user.email}".'),
        c.Button(text='Logout', on_click=PageEvent(name='submit-form')),
        c.Heading(text='User Data:', level=3),
        c.Code(language='json', text=json.dumps(asdict(user), indent=2)),
        c.Form(
            submit_url='/api/auth/logout',
            form_fields=[c.FormFieldInput(name='test', title='', initial='data', html_type='hidden')],
            footer=[],
            submit_trigger=PageEvent(name='submit-form'),
        ),
        title='Authentication',
    )


@router.post('/logout', response_model=FastUI, response_model_exclude_none=True)
async def logout_form_post() -> list[AnyComponent]:
    return [c.FireEvent(event=AuthEvent(token=False, url='/auth/login/password'))]