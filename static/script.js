const API_BASE = '/auth';
const PASSWORDS_API = '/passwords';
const ADMIN_API = '/admin';
let authToken = localStorage.getItem('auth_token');
let isAdmin = false;


function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}


if (authToken) {
    const payload = parseJwt(authToken);
    if (payload && payload.is_admin !== undefined) {
        isAdmin = payload.is_admin;
    }
    showApp();
    loadPasswords();
} else {
    showAuth();
}

function showMessage(text, isError = false) {
    const el = document.getElementById('message');
    el.textContent = text;
    el.style.color = isError ? 'red' : 'green';
    setTimeout(() => el.textContent = '', 3000);
}

function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
}

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

async function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            showMessage('Регистрация успешна! Войдите.');
            showLogin();
        } else {
            const error = await response.json();
            showMessage(`Ошибка: ${error.detail || 'Неизвестная ошибка'}`, true);
        }
    } catch (err) {
        showMessage('Ошибка сети', true);
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('auth_token', data.access_token);
            authToken = data.access_token;


            const payload = parseJwt(authToken);
            isAdmin = payload && payload.is_admin;

            showApp();
            loadPasswords();
            if (isAdmin) {
                loadAllUsers();
            }
        } else {
            showMessage('Неверный логин или пароль', true);
        }
    } catch (err) {
        showMessage('Ошибка сети', true);
    }
}

function logout() {
    localStorage.removeItem('auth_token');
    authToken = null;
    isAdmin = false;
    showAuth();
}

function showAuth() {
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('app-section').style.display = 'none';
    document.getElementById('admin-section').style.display = 'none';
}

function showApp() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('app-section').style.display = 'block';

    const adminSection = document.getElementById('admin-section');
    if (adminSection) {
        adminSection.style.display = isAdmin ? 'block' : 'none';
        if (isAdmin) {
            loadAllUsers();
        }
    }
}


async function loadPasswords() {
    try {
        const response = await fetch(PASSWORDS_API, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (response.ok) {
            const passwords = await response.json();
            renderPasswords(passwords);
        } else {
            showMessage('Ошибка загрузки паролей', true);
        }
    } catch (err) {
        showMessage('Ошибка сети', true);
    }
}

function renderPasswords(passwords) {
    const container = document.getElementById('passwords-container');
    if (passwords.length === 0) {
        container.innerHTML = '<p>Нет сохранённых паролей</p>';
        return;
    }

    container.innerHTML = passwords.map(p => `
        <div style="border:1px solid #eee; padding:10px; margin-bottom:10px;">
            <strong>${p.service}</strong><br>
            Логин: ${p.username}<br>
            Пароль: <span id="pwd-${p.id}">${p.password}</span>
            <button onclick="copyPassword(${p.id})" style="margin-left:10px;">📋 Копировать</button>
            <button onclick="deletePassword(${p.id})" class="delete-btn">Удалить</button>
        </div>
    `).join('');
}


function copyPassword(id) {
    const pwdElement = document.getElementById(`pwd-${id}`);
    if (pwdElement) {
        navigator.clipboard.writeText(pwdElement.textContent)
            .then(() => showMessage('Пароль скопирован!'))
            .catch(err => showMessage('Ошибка копирования', true));
    }
}

async function addPassword() {
    const service = document.getElementById('service').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(PASSWORDS_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ service, username, password })
        });

        if (response.ok) {
            showMessage('Пароль сохранён!');
            document.getElementById('service').value = '';
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            loadPasswords();
        } else {
            showMessage('Ошибка сохранения', true);
        }
    } catch (err) {
        showMessage('Ошибка сети', true);
    }
}

async function deletePassword(id) {
    if (!confirm('Удалить пароль?')) return;

    try {
        const response = await fetch(`${PASSWORDS_API}/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (response.ok) {
            showMessage('Пароль удалён');
            loadPasswords();
        } else {
            showMessage('Ошибка удаления', true);
        }
    } catch (err) {
        showMessage('Ошибка сети', true);
    }
}


async function loadAllUsers() {
    try {
        const response = await fetch(`${ADMIN_API}/users`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (response.ok) {
            const users = await response.json();
            renderUsers(users);
        } else {
            const error = await response.json();
            showMessage(`Ошибка загрузки пользователей: ${error.detail}`, true);
        }
    } catch (err) {
        showMessage('Ошибка сети', true);
    }
}

function renderUsers(users) {
    const container = document.getElementById('users-container');
    if (users.length === 0) {
        container.innerHTML = '<p>Нет пользователей</p>';
        return;
    }


    const currentUserId = parseJwt(authToken)?.sub;

    container.innerHTML = users.map(user => `
        <div style="border:1px solid #eee; padding:10px; margin-bottom:10px;">
            <strong>${user.username}</strong>
            ${user.is_admin ? '<span class="admin-badge">Админ</span>' : ''}
            ${user.username !== currentUserId ?
              `<button onclick="deleteUser(${user.id})" class="delete-btn">Удалить</button>` :
              '<span style="color:gray;">(текущий аккаунт)</span>'}
        </div>
    `).join('');
}

async function deleteUser(userId) {
    if (!confirm('Удалить пользователя? Это действие нельзя отменить!')) return;

    try {
        const response = await fetch(`${ADMIN_API}/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (response.ok) {
            showMessage('Пользователь удалён');
            loadAllUsers();
        } else {
            const error = await response.json();
            showMessage(`Ошибка: ${error.detail}`, true);
        }
    } catch (err) {
        showMessage('Ошибка сети', true);
    }
}