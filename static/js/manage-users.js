function loadUsers() {
    const includedContent = document.getElementById('includedContent');
    
    // First, fetch the session role
    fetch('/api/session-role', { credentials: 'include' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch session role');
            }
            return response.json();
        })
        .then(session => {
            const currentRole = session.role;

            // Then fetch users
            return fetch('/api/users', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(users => {
                let html = `
                    <h1>Manage Users</h1>
                    <button onclick="showAddUserForm()" id="tombol-biasa">Add New User</button>
                    <table border="1">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Active Status</th>
                                <th>Created At</th>
                                <th>Last Login</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                users.forEach(user => {
                    const disableActions = currentRole === 'Admin' && user.role === 'DBA';
                    html += `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.role}</td>
                            <td>${user.active ? 'Active' : 'Inactive'}</td>
                            <td>${user.created_at}</td>
                            <td>${user.last_login || 'Haven\'t logged in'}</td>
                            <td>
                                <button 
                                    onclick="editUser('${user.username}')" 
                                    ${disableActions ? 'disabled' : ''} id="tombol-biasa">Edit</button>
                                <button 
                                    onclick="deleteUser('${user.username}')" 
                                    ${disableActions ? 'disabled' : ''} id="tombol-error">Delete</button>
                            </td>
                        </tr>
                    `;
                });

                html += `</tbody></table>`;
                includedContent.innerHTML = html;
            });
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('includedContent').innerHTML = `
                <p style="color: red">Error loading users: ${error.message}</p>
            `;
        });
}

function showAddUserForm() {
    const includedContent = document.getElementById('includedContent');

    fetch('/api/session-role', { credentials: 'include' })
        .then(response => response.json())
        .then(session => {
            const currentRole = session.role;
            
            const dbaOption = currentRole === 'Admin' 
                ? '<option value="DBA" disabled>DBA (Not Allowed)</option>'
                : '<option value="DBA">DBA</option>';

            includedContent.innerHTML = `
                <h1>Add New User</h1>
                <form id="addUserForm" onsubmit="submitNewUser(event)">
                    <div>
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div>
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div>
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <div>
                        <label for="role">Role:</label>
                        <select id="role" name="role" required>
                            ${dbaOption}
                            <option value="Admin">Admin</option>
                            <option value="Vendor">Vendor</option>
                            <option value="Finance">Finance</option>
                        </select>
                    </div>
                    <button type="submit" id="tombol-biasa">Add User</button>
                    <button type="button" onclick="loadUsers()" id="tombol-error">Cancel</button>
                </form>
            `;
        })
        .catch(error => {
            console.error('Error fetching session role:', error);
            alert('Error fetching session role');
        });
}

function editUser(username) {
    fetch(`/api/users/${username}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        return response.json();
    })
    .then(user => {
        const includedContent = document.getElementById('includedContent');

        fetch('/api/session-role', { credentials: 'include' })
            .then(response => response.json())
            .then(session => {
                const currentRole = session.role;

                if (currentRole === 'Admin' && user.role === 'DBA') {
                    alert('Admins cannot edit users with the DBA role.');
                    return;
                }

                includedContent.innerHTML = `
                    <h1>Edit User</h1>
                    <form id="editUserForm" onsubmit="submitEditUser(event, '${username}')">
                        <div>
                            <label for="email">Email:</label>
                            <input type="email" id="email" name="email" value="${user.email}" required>
                        </div>
                        <div>
                            <label for="role">Role:</label>
                            <select id="role" name="role" required>
                                ${user.role === 'DBA' ? '<option value="DBA" selected disabled>DBA</option>' : ''}
                                <option value="Admin" ${user.role === 'Admin' ? 'selected' : ''}>Admin</option>
                                <option value="Vendor" ${user.role === 'Vendor' ? 'selected' : ''}>Vendor</option>
                                <option value="Finance" ${user.role === 'Finance' ? 'selected' : ''}>Finance</option>
                            </select>
                        </div>
                        <button type="submit" id="tombol-biasa">Save Changes</button>
                        <button type="button" onclick="loadUsers()" id="tombol-error">Cancel</button>
                    </form>
                `;
            });
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error fetching user data');
    });
}

function deleteUser(username) {
    fetch(`/api/users/${username}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        return response.json();
    })
    .then(user => {
        fetch('/api/session-role', { credentials: 'include' })
            .then(response => response.json())
            .then(session => {
                const currentRole = session.role;

                if (currentRole === 'Admin' && user.role === 'DBA') {
                    alert('Admins cannot delete users with the DBA role.');
                    return;
                }

                if (confirm(`Are you sure you want to delete user ${username}?`)) {
                    fetch(`/api/users/${username}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to delete user');
                        }
                        alert('User deleted successfully');
                        loadUsers();
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error deleting user');
                    });
                }
            });
    });
}

function submitNewUser(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const userData = {
        username: formData.get('username'),
        password: formData.get('password'),
        role: formData.get('role'),
        email: formData.get('email')
    };

    fetch('/api/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Failed to add user');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('User added successfully');
            loadUsers();
        } else {
            throw new Error(data.error || 'Failed to add user');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error adding user: ${error.message}`);
    });
}

function submitEditUser(event, username) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const userData = {
        email: formData.get('email'),
        role: formData.get('role')
    };

    fetch(`/api/users/${username}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to update user');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('User updated successfully');
            loadUsers();
        } else {
            throw new Error(data.error || 'Failed to update user');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error updating user: ${error.message}`);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
});