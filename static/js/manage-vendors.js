let equipmentIndex = 0;
let branchOfficeIndex = 0;
let PICIndex = 0;
let accountBankIndex = 0;

function createVendorDetailsModal(vendor) {
    // Create a modal dialog with all vendor details
    const modal = document.createElement('div');
    modal.id = 'vendorDetailsModal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '8px';
    modalContent.style.width = '80%';
    modalContent.style.maxHeight = '80%';
    modalContent.style.overflowY = 'auto';

    // Detailed vendor information HTML
    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2>Vendor Details</h2>
            <button onclick="document.body.removeChild(document.getElementById('vendorDetailsModal'))" 
                    id="tombol-error">Close
            </button>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h3>Basic Information</h3>
                <p><strong>Vendor ID:</strong> ${vendor._id || 'N/A'}</p>
                <p><strong>Partner Type:</strong> ${vendor.partnerType || 'N/A'}</p>
                <p><strong>Vendor Name:</strong> ${vendor.vendorName || 'N/A'}</p>
                <p><strong>Unit Usaha:</strong> ${vendor.unitUsaha || 'N/A'}</p>
                <p><strong>Address:</strong> ${vendor.address || 'N/A'}</p>
                <p><strong>Country:</strong> ${vendor.country || 'N/A'}</p>
                <p><strong>Province:</strong> ${vendor.province || 'N/A'}</p>
                <p><strong>Phone:</strong> ${vendor.noTelp || 'N/A'}</p>
                <p><strong>Email:</strong> ${vendor.emailCompany || 'N/A'}</p>
                <p><strong>Website:</strong> ${vendor.website || 'N/A'}</p>
                <p><strong>NPWP:</strong> ${vendor.NPWP || 'N/A'}</p>
                <p><strong>Active Status:</strong> ${vendor.activeStatus === 'Y' ? 'Active' : 'Inactive'}</p>
            </div>
            <div>
                <h3>PIC Information</h3>
                <p><strong>Name PIC:</strong> ${vendor.namePIC || 'N/A'}</p>
                <p><strong>Phone PIC:</strong> ${vendor.noTelpPIC || 'N/A'}</p>
                <p><strong>Email PIC:</strong> ${vendor.emailPIC || 'N/A'}</p>
                <p><strong>Position PIC:</strong> ${vendor.positionPIC || 'N/A'}</p>

                <h3>Additional PICs</h3>
                ${(vendor.PIC || []).map(pic => `
                    <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;">
                        <p><strong>Username:</strong> ${pic.username || 'N/A'}</p>
                        <p><strong>Name:</strong> ${pic.name || 'N/A'}</p>
                        <p><strong>Email:</strong> ${pic.email || 'N/A'}</p>
                        <p><strong>Phone:</strong> ${pic.noTelp || 'N/A'}</p>
                    </div>
                `).join('') || 'No additional PICs'}

                <h3>Supporting Equipment</h3>
                ${(vendor.supportingEquipment || []).map(equipment => `
                    <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;">
                        <p><strong>Tool Type:</strong> ${equipment.toolType || 'N/A'}</p>
                        <p><strong>Count:</strong> ${equipment.count || 'N/A'}</p>
                        <p><strong>Merk:</strong> ${equipment.merk || 'N/A'}</p>
                        <p><strong>Condition:</strong> ${equipment.condition || 'N/A'}</p>
                    </div>
                `).join('') || 'No supporting equipment'}

                <h3>Branch Offices</h3>
                ${(vendor.branchOffice || []).map(branch => `
                    <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;">
                        <p><strong>Branch Name:</strong> ${branch.branchName || 'N/A'}</p>
                        <p><strong>Location:</strong> ${branch.location || 'N/A'}</p>
                        <p><strong>Address:</strong> ${branch.address || 'N/A'}</p>
                        <p><strong>Country:</strong> ${branch.country || 'N/A'}</p>
                        <p><strong>Phone:</strong> ${branch.noTelp || 'N/A'}</p>
                    </div>
                `).join('') || 'No branch offices'}

                <h3>Bank Accounts</h3>
                ${(vendor.accountBank || []).map(account => `
                    <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;">
                        <p><strong>Bank:</strong> ${account.bankName || 'N/A'}</p>
                        <p><strong>Account Number:</strong> ${account.accountNumber || 'N/A'}</p>
                        <p><strong>Account Name:</strong> ${account.accountName || 'N/A'}</p>
                    </div>
                `).join('') || 'No bank accounts'}
            </div>
        </div>
        <div style="margin-top: 20px;">
            <h3>Change History</h3>
            <p><strong>Created By:</strong> ${vendor.change?.createUser || 'N/A'}</p>
            <p><strong>Created Date:</strong> ${vendor.change?.createDate || 'N/A'}</p>
            <p><strong>Updated By:</strong> ${vendor.change?.updateUser || 'N/A'}</p>
            <p><strong>Updated Date:</strong> ${vendor.change?.updateDate || 'N/A'}</p>
        </div>
    `;

    modal.appendChild(modalContent);
    document.body.appendChild(modal);
}

function createEditVendorModal(vendor) {
    // Create modal structure
    const modal = document.createElement('div');
    modal.id = 'editVendorModal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '8px';
    modalContent.style.width = '80%';
    modalContent.style.maxHeight = '80%';
    modalContent.style.overflowY = 'auto';

    // Prepare dynamic fields HTML generators
    const generateSupportingEquipmentFields = (equipment = {}) => `
        <div class="dynamic-field">
            <label>Tool Type:</label>
            <input type="text" name="supportingEquipment_toolType[]" value="${equipment.toolType || ''}">
            <label>Count:</label>
            <input type="number" name="supportingEquipment_count[]" value="${equipment.count || ''}">
            <label>Merk:</label>
            <input type="text" name="supportingEquipment_merk[]" value="${equipment.merk || ''}">
            <label>Condition:</label>
            <input type="text" name="supportingEquipment_condition[]" value="${equipment.condition || ''}">
            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
        </div>
    `;

    const generateBranchOfficeFields = (branch = {}) => `
        <div class="dynamic-field">
            <label>Branch Name:</label>
            <input type="text" name="branchOffice_branchName[]" value="${branch.branchName || ''}">
            <label>Location:</label>
            <input type="text" name="branchOffice_location[]" value="${branch.location || ''}">
            <label>Address:</label>
            <input type="text" name="branchOffice_address[]" value="${branch.address || ''}">
            <label>Country:</label>
            <input type="text" name="branchOffice_country[]" value="${branch.country || ''}">
            <label>Phone:</label>
            <input type="text" name="branchOffice_noTelp[]" value="${branch.noTelp || ''}">
            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
        </div>
    `;

    const generatePICFields = (pic = {}) => `
        <div class="dynamic-field">
            <label>Username:</label>
            <input type="text" name="PIC_username[]" value="${pic.username || ''}">
            <label>Name:</label>
            <input type="text" name="PIC_name[]" value="${pic.name || ''}">
            <label>Email:</label>
            <input type="email" name="PIC_email[]" value="${pic.email || ''}">
            <label>Phone:</label>
            <input type="text" name="PIC_noTelp[]" value="${pic.noTelp || ''}">
            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
        </div>
    `;

    // Modal content HTML
    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2>Edit Vendor</h2>
            <button onclick="document.body.removeChild(document.getElementById('editVendorModal'))" id="tombol-error">Close</button>
        </div>
        <form id="editVendorForm" onsubmit="submitEditVendor(event, '${vendor._id}')">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>Basic Information</h3>
                    <div>
                        <label>Vendor Name:</label>
                        <input type="text" name="vendorName" value="${vendor.vendorName || ''}">
                    </div>
                    <div>
                        <label>Unit Usaha:</label>
                        <input type="text" name="unitUsaha" value="${vendor.unitUsaha || ''}">
                    </div>
                    <div>
                        <label>Address:</label>
                        <input type="text" name="address" value="${vendor.address || ''}">
                    </div>
                    <div>
                        <label>Country:</label>
                        <input type="text" name="country" value="${vendor.country || ''}">
                    </div>
                    <div>
                        <label>Phone:</label>
                        <input type="text" name="noTelp" value="${vendor.noTelp || ''}">
                    </div>
                    <div>
                        <label>Email:</label>
                        <input type="email" name="emailCompany" value="${vendor.emailCompany || ''}">
                    </div>
                    <div>
                        <label>Active Status:</label>
                        <select name="activeStatus">
                            <option value="Y" ${vendor.activeStatus === 'Y' ? 'selected' : ''}>Active</option>
                            <option value="N" ${vendor.activeStatus === 'N' ? 'selected' : ''}>Inactive</option>
                        </select>
                    </div>
                </div>
                <div>
                    <h3>Additional Information</h3>
                    <div>
                        <h4>Supporting Equipment</h4>
                        <div id="equipmentFields">
                            ${(vendor.supportingEquipment || []).map(generateSupportingEquipmentFields).join('')}
                        </div>
                        <button type="button" onclick="addSupportingEquipment()" id="tombol-biasa">Add Equipment</button>
                    </div>
                    <div>
                        <h4>Branch Offices</h4>
                        <div id="branchOfficeFields">
                            ${(vendor.branchOffice || []).map(generateBranchOfficeFields).join('')}
                        </div>
                        <button type="button" onclick="addBranchOffice()" id="tombol-biasa">Add Branch Office</button>
                    </div>
                    <div>
                        <h4>PICs</h4>
                        <div id="PICFields">
                            ${(vendor.PIC || []).map(generatePICFields).join('')}
                        </div>
                        <button type="button" onclick="addPIC()" id="tombol-biasa">Add PIC</button>
                    </div>
                </div>
            </div>
            <div style="margin-top: 20px; text-align: right;">
                <button type="submit" id="tombol-biasa">Save Changes</button>
            </div>
        </form>
    `;

    modal.appendChild(modalContent);
    document.body.appendChild(modal);
}

function viewVendorDetails(vendorId) {
    // Fetch full vendor details
    fetch(`/api/vendors/${vendorId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch vendor details');
        }
        return response.json();
    })
    .then(vendor => {
        createVendorDetailsModal(vendor);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error fetching vendor details: ${error.message}`);
    });
}

function loadVendors() {
    const includedContent = document.getElementById('includedContent');
    fetch('/api/vendors', {
        method: 'GET',
        headers: { 
            'Content-Type': 'application/json' 
        },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const vendors = Array.isArray(data) ? data : [];
        
        const tableBody = vendors.map(vendor => `
            <tr>
                <td>${vendor._id || ''}</td>
                <td>${vendor.vendorName || ''}</td>
                <td>${vendor.unitUsaha || ''}</td>
                <td>${vendor.address || ''}</td>
                <td>${vendor.country || ''}</td>
                <td>${vendor.noTelp || ''}</td>
                <td>${vendor.emailCompany || ''}</td>
                <td>${vendor.change?.createUser || ''}</td>
                <td>${vendor.change?.createDate || ''}</td>
                <td>${vendor.change?.updateUser || ''}</td>
                <td>${vendor.change?.updateDate || ''}</td>
                <td>
                    <button onclick="viewVendorDetails('${vendor._id}')" id="tombol-biasa">View Details</button>
                    <button onclick="editVendor('${vendor._id}')" id="tombol-biasa">Edit</button>
                    <button onclick="deleteVendor('${vendor._id}')" id="tombol-error">Delete</button>
                </td>
            </tr>
        `).join('');

        includedContent.innerHTML = `
            <h1>Manage Vendors</h1>
            <button onclick="showAddVendorModal()" id="tombol-biasa">Add New Vendor</button>
            <table border="1">
                <thead>
                    <tr>
                        <th>Vendor ID</th>
                        <th>Vendor Name</th>
                        <th>Unit Usaha</th>
                        <th>Address</th>
                        <th>Country</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th>Create User</th>
                        <th>Create Date</th>
                        <th>Update User</th>
                        <th>Update Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>${tableBody}</tbody>
            </table>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('includedContent').innerHTML = `
            <p style="color: red">Error loading vendors: ${error.message}</p>
        `;
    });
}

// Function to show Add Vendor Form
function showAddVendorForm() {
    const includedContent = document.getElementById('includedContent');
    includedContent.innerHTML = `
        <h1>Add New Vendor</h2>
        <form id="addVendorForm" onsubmit="submitNewVendor(event)">
            <div>
                <label for="vendor_id">Vendor ID:</label>
                <input type="text" id="vendor_id" name="_id" required>
            </div>
            <div>
                <label for="partner_type">Partner Type:</label>
                <input type="text" id="partner_type" name="partnerType" required>
            </div>
            <div>
                <label for="vendor_name">Vendor Name:</label>
                <input type="text" id="vendor_name" name="vendorName" required>
            </div>
            <div>
                <label for="unit_usaha">Unit Usaha:</label>
                <input type="text" id="unit_usaha" name="unitUsaha" required>
            </div>
            <div>
                <label for="address">Address:</label>
                <input type="text" id="address" name="address" required>
            </div>
            <div>
                <label for="country">Country:</label>
                <input type="text" id="country" name="country" required>
            </div>
            <div>
                <label for="no_telp">Phone:</label>
                <input type="text" id="no_telp" name="noTelp" required>
            </div>
            <div>
                <label for="email_company">Email:</label>
                <input type="email" id="email_company" name="emailCompany" required>
            </div>
            <div>
                <h3>Supporting Equipment</h3>
                <div id="equipmentFields"></div>
                <button type="button" onclick="addSupportingEquipment()" id="tombol-biasa">Add Equipment</button>
            </div>

            <div>
                <h3>Branch Office</h3>
                <div id="branchOfficeFields"></div>
                <button type="button" onclick="addBranchOffice()" id="tombol-biasa">Add Branch Office</button>
            </div>

            <div>
                <h3>PIC</h3>
                <div id="PICFields"></div>
                <button type="button" onclick="addPIC()" id="tombol-biasa">Add PIC</button>
            </div>

            <div>
                <h3>Account Bank</h3>
                <div id="accountBankFields"></div>
                <button type="button" onclick="addAccountBank()" id="tombol-biasa">Add Account Bank</button>
            </div>

            <button type="submit" id="tombol-biasa">Save Vendor</button>
        </form>
    `;

    // Load active banks
    fetch('/api/banks?status=ACTIVE', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(activeBanks => {
        const accountBankFields = document.getElementById('accountBankFields');
        const bankSelect = document.createElement('select');
        bankSelect.id = 'bankSelect';
        bankSelect.innerHTML = '<option value="">Select Bank</option>';
        
        activeBanks.forEach(bank => {
            const option = document.createElement('option');
            option.value = bank._id;
            option.textContent = bank.bankDesc;
            bankSelect.appendChild(option);
        });

        // Store for later use in addAccountBank
        window.activeBanks = activeBanks;
    })
    .catch(error => {
        console.error('Error loading banks:', error);
        alert('Failed to load bank list.');
    });
}



// Dynamic Field Addition Functions
function addSupportingEquipment() {
    const equipmentFields = document.getElementById("equipmentFields");
    equipmentFields.insertAdjacentHTML("beforeend", `
        <div class="dynamic-field">
            <label>Tool Type:</label>
            <input type="text" name="supportingEquipment_toolType[${equipmentIndex}]">
            <label>Count:</label>
            <input type="number" name="supportingEquipment_count[${equipmentIndex}]">
            <label>Merk:</label>
            <input type="text" name="supportingEquipment_merk[${equipmentIndex}]">
            <label>Condition:</label>
            <input type="text" name="supportingEquipment_condition[${equipmentIndex}]">
            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
        </div>
    `);
    equipmentIndex++;
}

function addBranchOffice() {
    const branchOfficeFields = document.getElementById("branchOfficeFields");
    branchOfficeFields.insertAdjacentHTML("beforeend", `
        <div class="dynamic-field">
            <label>Branch Name:</label>
            <input type="text" name="branchOffice_branchName[${branchOfficeIndex}]">
            <label>Location:</label>
            <input type="text" name="branchOffice_location[${branchOfficeIndex}]">
            <label>Address:</label>
            <input type="text" name="branchOffice_address[${branchOfficeIndex}]">
            <label>Country:</label>
            <input type="text" name="branchOffice_country[${branchOfficeIndex}]">
            <label>No Telp:</label>
            <input type="text" name="branchOffice_noTelp[${branchOfficeIndex}]">
            <label>Website:</label>
            <input type="text" name="branchOffice_website[${branchOfficeIndex}]">
            <label>Email:</label>
            <input type="email" name="branchOffice_email[${branchOfficeIndex}]">
            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
        </div>
    `);
    branchOfficeIndex++;
}

function addPIC() {
    const PICFields = document.getElementById("PICFields");
    PICFields.insertAdjacentHTML("beforeend", `
        <div class="dynamic-field">
            <label>Username</label>
            <input type="text" name="PIC_username[${PICIndex}]">
            <label>Name:</label>
            <input type="text" name="PIC_name[${PICIndex}]">
            <label>Email:</label>
            <input type="email" name="PIC_email[${PICIndex}]">
            <label>No Telp:</label>
            <input type="text" name="PIC_noTelp[${PICIndex}]">
            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
        </div>
    `);
    PICIndex++;
}

function addAccountBank() {
    const accountBankFields = document.getElementById("accountBankFields");
    
    // Create bank select element if not already created
    let bankSelect = document.getElementById('bankSelect');
    if (!bankSelect) {
        bankSelect = document.createElement('select');
        bankSelect.id = 'bankSelect';
        bankSelect.innerHTML = '<option value="">Select Bank</option>';
        
        (window.activeBanks || []).forEach(bank => {
            const option = document.createElement('option');
            option.value = bank._id;
            option.textContent = bank.bankDesc;
            bankSelect.appendChild(option);
        });
    }

    accountBankFields.insertAdjacentHTML("beforeend", `
        <div class="dynamic-field">
            <label>Bank Name:</label>
            ${bankSelect.outerHTML}
            <label>Account Number:</label>
            <input type="text" name="accountBank_accountNumber[${accountBankIndex}]" required>
            <label>Account Name:</label>
            <input type="text" name="accountBank_accountName[${accountBankIndex}]" required>
            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
        </div>
    `);
    accountBankIndex++;
}

// Parse Array Fields
function parseArrayFields(formData, keyPrefix) {
    const result = [];
    const regex = new RegExp(`^${keyPrefix}_\\w+\\[\\d+\\]$`);
    
    for (const [key, value] of formData.entries()) {
        if (regex.test(key)) {
            const matches = key.match(`${keyPrefix}_(\\w+)\\[(\\d+)\\]`);
            if (matches) {
                const fieldName = matches[1];
                const index = parseInt(matches[2], 10);
                
                if (!result[index]) result[index] = {};
                result[index][fieldName] = value;
            }
        }
    }
    
    return result.filter(item => Object.keys(item).length > 0);
}

// Submit Vendor Form
function showAddVendorModal() {
    // Create modal container
    const modal = document.createElement('div');
    modal.id = 'addVendorModal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';
    modal.style.overflowY = 'auto';
    modal.style.padding = '20px 0';

    // Modal content
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '8px';
    modalContent.style.width = '80%';
    modalContent.style.maxWidth = '800px';
    modalContent.style.maxHeight = '90%';
    modalContent.style.overflowY = 'auto';

    // Modal HTML content
    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2>Add New Vendor</h2>
            <button onclick="document.body.removeChild(document.getElementById('addVendorModal'))" id="tombol-error">Close</button>
        </div>

        <form id="addVendorForm">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>Basic Information</h3>
                    <div style="display: grid; gap: 10px;">
                        <div>
                            <label>Vendor ID:</label>
                            <input type="text" id="vendor_id" name="_id" required style="width: 100%;">
                        </div>
                        <div>
                            <label>Partner Type:</label>
                            <input type="text" id="partner_type" name="partnerType" required style="width: 100%;">
                        </div>
                        <div>
                            <label>Vendor Name:</label>
                            <input type="text" id="vendor_name" name="vendorName" required style="width: 100%;">
                        </div>
                        <div>
                            <label>Unit Usaha:</label>
                            <input type="text" id="unit_usaha" name="unitUsaha" required style="width: 100%;">
                        </div>
                        <div>
                            <label>Address:</label>
                            <input type="text" id="address" name="address" required style="width: 100%;">
                        </div>
                        <div>
                            <label>Country:</label>
                            <input type="text" id="country" name="country" required style="width: 100%;">
                        </div>
                        <div>
                            <label>Phone:</label>
                            <input type="text" id="no_telp" name="noTelp" required style="width: 100%;">
                        </div>
                        <div>
                            <label>Email:</label>
                            <input type="email" id="email_company" name="emailCompany" required style="width: 100%;">
                        </div>
                    </div>
                </div>
                
                <div>
                    <div>
                        <h3>Additional Information</h3>
                        <div style="display: grid; gap: 10px;">
                            <div>
                                <h4>Supporting Equipment 
                                    <button type="button" onclick="addSupportingEquipment()" id="tombol-biasa" style="margin-left: 10px;">Add</button>
                                </h4>
                                <div id="equipmentFields" style="max-height: 200px; overflow-y: auto;"></div>
                            </div>
                            
                            <div>
                                <h4>Branch Offices 
                                    <button type="button" onclick="addBranchOffice()" id="tombol-biasa" style="margin-left: 10px;">Add</button>
                                </h4>
                                <div id="branchOfficeFields" style="max-height: 200px; overflow-y: auto;"></div>
                            </div>
                            
                            <div>
                                <h4>PICs 
                                    <button type="button" onclick="addPIC()" id="tombol-biasa" style="margin-left: 10px;">Add</button>
                                </h4>
                                <div id="PICFields" style="max-height: 200px; overflow-y: auto;"></div>
                            </div>
                            
                            <div>
                                <h4>Bank Accounts 
                                    <button type="button" onclick="addAccountBank()" id="tombol-biasa" style="margin-left: 10px;">Add</button>
                                </h4>
                                <div id="accountBankFields" style="max-height: 200px; overflow-y: auto;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div style="margin-top: 20px; text-align: right;">
                <button type="button" onclick="submitNewVendor(event)" id="tombol-biasa">Save Vendor</button>
                <button type="button" onclick="document.body.removeChild(document.getElementById('addVendorModal'))" id="tombol-error">Cancel</button>
            </div>
        </form>
    `;

    // Append modal to body
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Load active banks
    fetch('/api/banks?status=ACTIVE', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(activeBanks => {
        const bankSelect = document.createElement('select');
        bankSelect.id = 'bankSelect';
        bankSelect.innerHTML = '<option value="">Select Bank</option>';
        
        activeBanks.forEach(bank => {
            const option = document.createElement('option');
            option.value = bank._id;
            option.textContent = bank.bankDesc;
            bankSelect.appendChild(option);
        });

        // Store for later use in addAccountBank
        window.activeBanks = activeBanks;
    })
    .catch(error => {
        console.error('Error loading banks:', error);
        alert('Failed to load bank list.');
    });
}

// Modify the existing functions to work with the modal
function submitNewVendor(event) {
    const form = document.getElementById('addVendorForm');
    const formData = new FormData(form);

    // Create vendor data object with required fields
    const vendorData = {
        _id: document.getElementById('vendor_id').value,
        partnerType: document.getElementById('partner_type').value,
        vendorName: document.getElementById('vendor_name').value,
        unitUsaha: document.getElementById('unit_usaha').value,
        address: document.getElementById('address').value,
        country: document.getElementById('country').value,
        noTelp: document.getElementById('no_telp').value,
        emailCompany: document.getElementById('email_company').value,
    };

    // Parse dynamic fields (same as before)
    vendorData.supportingEquipment = parseArrayFields(formData, "supportingEquipment") || [];
    vendorData.branchOffice = parseArrayFields(formData, "branchOffice") || [];
    vendorData.PIC = parseArrayFields(formData, "PIC") || [];
    
    // Handle Account Banks
    vendorData.accountBank = [];
    const accountBankFields = document.querySelectorAll('#accountBankFields .dynamic-field');
    accountBankFields.forEach((field) => {
        const bankSelect = field.querySelector('select');
        const accountNumber = field.querySelector('input[name^="accountBank_accountNumber"]');
        const accountName = field.querySelector('input[name^="accountBank_accountName"]');
        
        vendorData.accountBank.push({
            bankId: bankSelect.value,
            accountNumber: accountNumber.value,
            accountName: accountName.value
        });
    });

    // Send data to server
    fetch("/api/vendors", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(vendorData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.error || "Failed to create vendor");
            });
        }
        return response.json();
    })
    .then(data => {
        alert("Vendor created successfully");
        // Remove modal
        document.body.removeChild(document.getElementById('addVendorModal'));
        // Reload vendors list
        loadVendors();
        // Reset indexes
        equipmentIndex = 0;
        branchOfficeIndex = 0;
        PICIndex = 0;
        accountBankIndex = 0;
    })
    .catch(error => {
        console.error("Error:", error.message);
        alert(`Error creating vendor: ${error.message}`);
    });
}



function editVendor(vendorId) {
    fetch(`/api/vendors/${vendorId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.error || `Failed to fetch vendor details for ID: ${vendorId}`);
            });
        }
        return response.json();
    })
    .then(vendor => {
        createEditVendorModal(vendor);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    });
}

function showEditVendorForm(vendor) {
    const includedContent = document.getElementById('includedContent');
    const supportingEquipmentRows = (vendor.supportingEquipment || []).map(equipment => `
        <div>
            <label>Tool Type:</label>
            <input type="text" name="supportingEquipment_toolType[]" value="${equipment.toolType || ''}">
            <label>Count:</label>
            <input type="number" name="supportingEquipment_count[]" value="${equipment.count || ''}">
            <label>Merk:</label>
            <input type="text" name="supportingEquipment_merk[]" value="${equipment.merk || ''}">
            <label>Condition:</label>
            <input type="text" name="supportingEquipment_condition[]" value="${equipment.condition || ''}">
        </div>
    `).join('');

    const branchOfficeRows = (vendor.branchOffice || []).map(branch => `
        <div>
            <label>Branch Name:</label>
            <input type="text" name="branchOffice_branchName[]" value="${branch.branchName || ''}">
            <label>Location:</label>
            <input type="text" name="branchOffice_location[]" value="${branch.location || ''}">
            <label>Address:</label>
            <input type="text" name="branchOffice_address[]" value="${branch.address || ''}">
            <label>Country:</label>
            <input type="text" name="branchOffice_country[]" value="${branch.country || ''}">
            <label>Phone:</label>
            <input type="text" name="branchOffice_noTelp[]" value="${branch.noTelp || ''}">
            <label>Website:</label>
            <input type="text" name="branchOffice_website[]" value="${branch.website || ''}">
            <label>Email:</label>
            <input type="email" name="branchOffice_email[]" value="${branch.email || ''}">
        </div>
    `).join('');

    const PICRows = (vendor.PIC || []).map(PIC => `
        <div>
            <label>Username:</label>
            <input type="text" name="PIC_username[]" value="${PIC.username || ''}">
            <label>Name:</label>
            <input type="text" name="PIC_name[]" value="${PIC.name || ''}">
            <label>Email:</label>
            <input type="email" name="PIC_email[]" value="${PIC.email || ''}">
            <label>Phone:</label>
            <input type="text" name="PIC_noTelp[]" value="${PIC.noTelp || ''}">
        </div>
    `).join('');

    const accountBankRows = (vendor.accountBank || []).map(account => `
        <div>
            <label>Bank Code:</label>
            <input type="text" name="accountBank_bankCode[]" value="${account.bankCode || ''}" disabled>
            <label>Bank Name:</label>
            <input type="text" name="accountBank_bankName[]" value="${account.bankName || ''}" disabled>
            <label>Account Number:</label>
            <input type="text" name="accountBank_accountNumber[]" value="${account.accountNumber || ''}">
            <label>Account Name:</label>
            <input type="text" name="accountBank_accountName[]" value="${account.accountName || ''}">
        </div>
    `).join('');

    includedContent.innerHTML = `
        <h1>Edit Vendor</h1>
        <form id="editVendorForm" onsubmit="submitEditVendor(event, '${vendor._id}')">
            <div>
                <label>Partner Type:</label>
                <input type="text" name="partnerType" value="${vendor.partnerType || ''}">
            </div>
            <div>
                <label>Vendor Name:</label>
                <input type="text" name="vendorName" value="${vendor.vendorName || ''}">
            </div>
            <div>
                <label>Unit Usaha:</label>
                <input type="text" name="unitUsaha" value="${vendor.unitUsaha || ''}">
            </div>
            <div>
                <label>Address:</label>
                <input type="text" name="address" value="${vendor.address || ''}">
            </div>
            <div>
                <label>Country:</label>
                <input type="text" name="country" value="${vendor.country || ''}">
            </div>
            <div>
                <label>Province:</label>
                <input type="text" name="province" value="${vendor.province || ''}">
            </div>
            <div>
                <label>Phone:</label>
                <input type="text" name="noTelp" value="${vendor.noTelp || ''}">
            </div>
            <div>
                <label>Company Email:</label>
                <input type="email" name="emailCompany" value="${vendor.emailCompany || ''}">
            </div>
            <div>
                <label>Website:</label>
                <input type="text" name="website" value="${vendor.website || ''}">
            </div>
            <div>
                <label>Name PIC:</label>
                <input type="text" name="namePIC" value="${vendor.namePIC || ''}">
            </div>
            <div>
                <label>Phone PIC:</label>
                <input type="text" name="noTelpPIC" value="${vendor.noTelpPIC || ''}">
            </div>
            <div>
                <label>Email PIC:</label>
                <input type="email" name="emailPIC" value="${vendor.emailPIC || ''}">
            </div>
            <div>
                <label>Position PIC:</label>
                <input type="text" name="positionPIC" value="${vendor.positionPIC || ''}">
            </div>
            <div>
                <label>NPWP:</label>
                <input type="text" name="NPWP" value="${vendor.NPWP || ''}">
            </div>
            <div>
                <label>Active Status:</label>
                <select id="active_status" name="activeStatus">
                    <option value="Y" ${vendor.activeStatus === 'Y' ? 'selected' : ''}>Active</option>
                    <option value="N" ${vendor.activeStatus === 'N' ? 'selected' : ''}>Inactive</option>
                </select>
            </div>
            <div>
                <h3>Supporting Equipment</h3>
                <div id="equipmentFields">
                    ${(vendor.supportingEquipment || []).map(equipment => `
                        <div>
                            <label>Tool Type:</label>
                            <input type="text" name="supportingEquipment_toolType[]" value="${equipment.toolType || ''}">
                            <label>Count:</label>
                            <input type="number" name="supportingEquipment_count[]" value="${equipment.count || ''}">
                            <label>Merk:</label>
                            <input type="text" name="supportingEquipment_merk[]" value="${equipment.merk || ''}">
                            <label>Condition:</label>
                            <input type="text" name="supportingEquipment_condition[]" value="${equipment.condition || ''}">
                            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
                        </div>
                    `).join('')}
                </div>
                <button type="button" onclick="addSupportingEquipment()" id="tombol-biasa">Add Equipment</button>
            </div>
            <div>
                <h3>Branch Office</h3>
                <div id="branchOfficeFields">
                    ${(vendor.branchOffice || []).map(branch => `
                        <div>
                            <label>Branch Name:</label>
                            <input type="text" name="branchOffice_branchName[]" value="${branch.branchName || ''}">
                            <label>Location:</label>
                            <input type="text" name="branchOffice_location[]" value="${branch.location || ''}">
                            <label>Address:</label>
                            <input type="text" name="branchOffice_address[]" value="${branch.address || ''}">
                            <label>Country:</label>
                            <input type="text" name="branchOffice_country[]" value="${branch.country || ''}">
                            <label>No Telp:</label>
                            <input type="text" name="branchOffice_noTelp[]" value="${branch.noTelp || ''}">
                            <label>Website:</label>
                            <input type="text" name="branchOffice_website[]" value="${branch.website || ''}">
                            <label>Email:</label>
                            <input type="email" name="branchOffice_email[]" value="${branch.email || ''}">
                            <button type="button" onclick="this.parentElement.remove() id="tombol-error">Remove</button>
                        </div>
                    `).join('')}
                </div>
                <button type="button" onclick="addBranchOffice()" id="tombol-biasa">Add Branch Office</button>
            </div>
            <div>
                <h3>PIC</h3>
                <div id="PICFields">
                    ${(vendor.PIC || []).map(PIC => `
                        <div>
                            <label>Username:</label>
                            <input type="text" name="PIC_username[]" value="${PIC.username || ''}">
                            <label>Name:</label>
                            <input type="text" name="PIC_name[]" value="${PIC.name || ''}">
                            <label>Email:</label>
                            <input type="email" name="PIC_email[]" value="${PIC.email || ''}">
                            <label>No Telp:</label>
                            <input type="text" name="PIC_noTelp[]" value="${PIC.noTelp || ''}">
                            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
                        </div>
                    `).join('')}
                </div>
                <button type="button" onclick="addPIC()" id="tombol-biasa">Add PIC</button>
            </div>
            <div>
                <h3>Account Bank</h3>
                <div id="accountBankFields">
                    ${(vendor.accountBank || []).map(account => `
                        <div>
                            <label>Bank Code:</label>
                            <input type="text" name="accountBank_bankCode[]" value="${account.bankCode || ''}" disabled>
                            <label>Bank Name:</label>
                            <input type="text" name="accountBank_bankName[]" value="${account.bankName || ''}" disabled>
                            <label>Account Number:</label>
                            <input type="text" name="accountBank_accountNumber[]" value="${account.accountNumber || ''}">
                            <label>Account Name:</label>
                            <input type="text" name="accountBank_accountName[]" value="${account.accountName || ''}">
                            <button type="button" onclick="this.parentElement.remove()" id="tombol-error">Remove</button>
                        </div>
                    `).join('')}
                </div>
                <button type="button" onclick="addAccountBank()" id="tombol-biasa">Add Account Bank</button>
            </div>
            <button type="submit" id="tombol-biasa">Save</button>
            <button type="button" onclick="loadVendors()" id="tombol-error">Cancel</button>
        </form>
    `;

    // Load active banks
    fetch('/api/banks?status=ACTIVE', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(activeBanks => {
        const accountBankFields = document.getElementById('accountBankFields');
        const bankSelect = document.createElement('select');
        bankSelect.id = 'bankSelect';
        bankSelect.innerHTML = '<option value="">Select Bank</option>';
        
        activeBanks.forEach(bank => {
            const option = document.createElement('option');
            option.value = bank._id;
            option.textContent = bank.bankDesc;
            bankSelect.appendChild(option);
        });

        // Store for later use in addAccountBank
        window.activeBanks = activeBanks;
    })
    .catch(error => {
        console.error('Error loading banks:', error);
        alert('Failed to load bank list.');
    });
}

function submitEditVendor(event, vendorId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const vendorData = Object.fromEntries(formData.entries());

    // Remove empty fields
    Object.keys(vendorData).forEach(key => {
        if (vendorData[key] === '') {
            delete vendorData[key];
        }
    });

    fetch(`/api/vendors/${vendorId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(vendorData)
    })
    .then(response => {
        if (!response.ok) {
            // Try to parse error message from server
            return response.json().then(errorData => {
                throw new Error(errorData.error || 'Failed to update vendor');
            });
        }
        return response.json();
    })
    .then(data => {
        alert('Vendor updated successfully');
        loadVendors();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error updating vendor: ${error.message}`);
    });
}

function deleteVendor(vendorId) {
    if (!confirm('Are you sure you want to delete this vendor?')) {
        return;
    }

    fetch(`/api/vendors/${vendorId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete vendor');
        }
        return response.json();
    })
    .then(data => {
        alert('Vendor deleted successfully');
        loadVendors();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error deleting vendor: ${error.message}`);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadVendors();
});