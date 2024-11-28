function loadBanks() {
    const includedContent = document.getElementById('includedContent');
    fetch('/api/banks', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch banks');
        }
        return response.json();
    })
    .then(banks => {
        const includedContent = document.getElementById('includedContent');
        let html = `
            <h1>Manage Banks</h1>
            <button onclick="showAddBankForm()" id="tombol-biasa">Add New Bank</button>
            <table>
                <thead>
                    <tr>
                        <th>Bank Code</th>
                        <th>Description</th>
                        <th>Active Status</th>
                        <th>Create Date</th>
                        <th>Create User</th>
                        <th>Update Date</th>
                        <th>Update User</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        banks.forEach(bank => {
            const setup = bank.setup || {}; // Ensure setup is not undefined
            html += `
                <tr>
                    <td>${bank._id}</td>
                    <td>${bank.bankDesc || 'No description'}</td>
                    <td>${bank.activeStatus === 'Y' ? 'Active' : 'Inactive'}</td>
                    <td>${setup.createDate || 'No data'}</td>
                    <td>${setup.createUser || 'No data'}</td>
                    <td>${setup.updateDate || 'No data'}</td>
                    <td>${setup.updateUser || 'No data'}</td>
                    <td>
                        <button onclick="editBank('${bank._id}')" id="tombol-biasa">Edit</button>
                        <button onclick="deleteBank('${bank._id}')" id="tombol-error">Delete</button>
                    </td>
                </tr>
            `;
        });


        html += `
                </tbody>
            </table>
        `;

        includedContent.innerHTML = html;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('includedContent').innerHTML = `
            <p style="color: red">Error loading banks: ${error.message}</p>
        `;
    });
}

function showAddBankForm() {
    const includedContent = document.getElementById('includedContent');
    includedContent.innerHTML = `
        <h1>Add New Bank</h1>
        <form id="addBankForm" onsubmit="submitNewBank(event)">
            <div>
                <label for="bank_code">Bank Code:</label>
                <input type="text" id="bank_code" name="_id" required>
            </div>
            <div>
                <label for="bank_desc">Description:</label>
                <textarea id="bank_desc" name="bankDesc" rows="4" required></textarea>
            </div>
            <div>
                <button type="submit" id="tombol-biasa">Add Bank</button>
                <button type="button" onclick="loadBanks()" id="tombol-error">Cancel</button>
            </div>
        </form>
    `;
}

function submitNewBank(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const bankData = Object.fromEntries(formData.entries());

    fetch('/api/banks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(bankData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to add bank');
        }
        return response.json();
    })
    .then(data => {
        alert('Bank added successfully');
        loadBanks();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error adding bank: ${error.message}`);
    });
}

function editBank(bankId) {
    fetch(`/api/banks/${bankId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || `Failed to fetch details for bank ID: ${bankId}`);
            });
        }
        return response.json();
    })
    .then(bank => {
        showEditBankForm(bank);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error fetching bank details: ${error.message}`);
    });
}

function showEditBankForm(bank) {
    const includedContent = document.getElementById('includedContent');
    includedContent.innerHTML = `
        <h1>Edit Bank</h1>
        <form id="editBankForm" onsubmit="submitEditBank(event, '${bank._id}')">
            <div>
                <label for="bank_code">Bank Code:</label>
                <input type="text" id="bank_code" value="${bank._id}" disabled>
            </div>
            <div>
                <label for="bank_desc">Description:</label>
                <textarea id="bank_desc" name="bankDesc" rows="4" required>${bank.bankDesc || ''}</textarea>
            </div>
            <div>
                <label for="active_status">Active Status:</label>
                <select id="active_status" name="activeStatus">
                    <option value="Y" ${bank.activeStatus === 'Y' ? 'selected' : ''}>Active</option>
                    <option value="N" ${bank.activeStatus === 'N' ? 'selected' : ''}>Inactive</option>
                </select>
            </div>
            <div>
                <button type="submit" id="tombol-biasa">Update Bank</button>
                <button type="button" onclick="loadBanks()" id="tombol-error">Cancel</button>
            </div>
        </form>
    `;
}

function submitEditBank(event, bankId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const bankData = Object.fromEntries(formData.entries());

    fetch(`/api/banks/${bankId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(bankData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to update bank');
        }
        return response.json();
    })
    .then(data => {
        alert('Bank updated successfully');
        loadBanks();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error updating bank: ${error.message}`);
    });
}

function deleteBank(bankId) {
    if (!confirm('Are you sure you want to delete this bank?')) {
        return;
    }

    fetch(`/api/banks/${bankId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete bank');
        }
        return response.json();
    })
    .then(data => {
        alert('Bank deleted successfully');
        loadBanks();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error deleting bank: ${error.message}`);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadBanks();
});