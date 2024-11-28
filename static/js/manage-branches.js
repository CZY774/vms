function loadBranches() {
    const includedContent = document.getElementById('includedContent');
    fetch('/api/branches', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch branches');
        }
        return response.json();
    })
    .then(branches => {
        const includedContent = document.getElementById('includedContent');
        let html = `
            <h1>Manage Branches</h1>
            <button onclick="showAddBranchForm()" id="tombol-biasa">Add New Branch</button>
            <table border="1">
                <thead>
                    <tr>
                        <th>Branch Code</th>
                        <th>Branch Name</th>
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

        branches.forEach(branch => {
            html += `
                <tr>
                    <td>${branch._id}</td>
                    <td>${branch.BranchName || 'N/A'}</td>
                    <td>${branch.activeStatus === 'Y' ? 'Active' : 'Inactive'}</td>
                    <td>${branch.setup.createDate}</td>
                    <td>${branch.setup.createUser}</td>
                    <td>${branch.setup.updateDate || 'Has not been updated'}</td>
                    <td>${branch.setup.updateUser || 'Has not been updated'}</td>
                    <td>
                        <button onclick="editBranch('${branch._id}')" id="tombol-biasa">Edit</button>
                        <button onclick="deleteBranch('${branch._id}')" id="tombol-error">Delete</button>
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
            <p style="color: red">Error loading branches: ${error.message}</p>
        `;
    });
}

function showAddBranchForm() {
    const includedContent = document.getElementById('includedContent');
    includedContent.innerHTML = `
        <h1>Add New Branch</h1>
        <form id="addBranchForm" onsubmit="submitNewBranch(event)">
            <div>
                <label for="branch_code">Branch Code:</label>
                <input type="text" id="branch_code" name="_id" required>
            </div>
            <div>
                <label for="branch_name">Branch Name:</label>
                <input type="text" id="branch_name" name="BranchName" required>
            </div>
            <button type="submit" id="tombol-biasa">Add Branch</button>
            <button type="button" onclick="loadBranches()" id="tombol-error">Cancel</button>
        </form>
    `;
}

function submitNewBranch(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const branchData = Object.fromEntries(formData.entries());

    fetch('/api/branches', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(branchData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to add branch');
        }
        return response.json();
    })
    .then(data => {
        alert('Branch added successfully');
        loadBranches();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error adding branch: ${error.message}`);
    });
}

function editBranch(branchId) {
    fetch(`/api/branches/${branchId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to fetch branch details for ID: ${branchId}`);
        }
        return response.json();
    })
    .then(branch => {
        showEditBranchForm(branch);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error fetching branch details: ${error.message}`);
    });
}

function showEditBranchForm(branch) {
    const includedContent = document.getElementById('includedContent');
    includedContent.innerHTML = `
        <h1>Edit Branch</h1>
        <form id="editBranchForm" onsubmit="submitEditBranch(event, '${branch._id}')">
            <div>
                <label for="branch_code">Branch Code:</label>
                <input type="text" id="branch_code" value="${branch._id}" disabled>
            </div>
            <div>
                <label for="branch_name">Branch Name:</label>
                <input type="text" id="branch_name" name="BranchName" value="${branch.BranchName || ''}" required>
            </div>
            <div>
                <label for="active_status">Active Status:</label>
                <select id="active_status" name="activeStatus">
                    <option value="Y" ${branch.activeStatus === 'Y' ? 'selected' : ''}>Active</option>
                    <option value="N" ${branch.activeStatus === 'N' ? 'selected' : ''}>Inactive</option>
                </select>
            </div>
            <button type="submit" id="tombol-biasa">Update Branch</button>
            <button type="button" onclick="loadBranches()" id="tombol-error">Cancel</button>
        </form>
    `;
}

function submitEditBranch(event, branchId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const branchData = Object.fromEntries(formData.entries());

    fetch(`/api/branches/${branchId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(branchData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to update branch');
        }
        return response.json();
    })
    .then(data => {
        alert('Branch updated successfully');
        loadBranches();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error updating branch: ${error.message}`);
    });
}

function deleteBranch(branchId) {
    if (!confirm('Are you sure you want to delete this branch?')) {
        return;
    }

    fetch(`/api/branches/${branchId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete branch');
        }
        return response.json();
    })
    .then(data => {
        alert('Branch deleted successfully');
        loadBranches();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error deleting branch: ${error.message}`);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadBranches();
});